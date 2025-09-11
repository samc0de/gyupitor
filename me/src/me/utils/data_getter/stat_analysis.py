import os
import json
import argparse
from collections import defaultdict
from pathlib import Path
from google.cloud import bigquery
from tqdm import tqdm
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def aggregate_timeline_metrics(timeline: list[dict]) -> dict:
    """
    Aggregates the timeline snapshots of a BigQuery job into a single summary
    of key performance and cost indicators.
    """
    if not timeline:
        return {}

    # --- Key Metrics Calculation ---
    last_entry = timeline[-1]
    total_runtime_ms = last_entry.get("elapsed_ms", 0)
    slot_ms_consumed = last_entry.get("total_slot_ms", 0)
    final_completed_units = last_entry.get("completed_units", 0)
    
    peak_slots = max(t.get("active_units", 0) or 0 for t in timeline)
    queue_pressure = max(t.get("pending_units", 0) or 0 for t in timeline)
    
    # --- Throughput Calculation (units per second) ---
    throughput = (final_completed_units / (total_runtime_ms / 1000)) if total_runtime_ms > 0 else 0

    # --- Concurrency Trend (Slope of active_units vs. time) ---
    n = len(timeline)
    if n > 1:
        x = [t.get("elapsed_ms", 0) or 0 for t in timeline]
        y = [t.get("active_units", 0) or 0 for t in timeline]
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi**2 for xi in x)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = n * sum_x2 - sum_x**2
        
        slope = numerator / denominator if denominator != 0 else 0
    else:
        slope = 0

    return {
        "total_runtime_ms": total_runtime_ms,
        "peak_slots_used": peak_slots,
        "slot_ms_consumed": slot_ms_consumed,
        "concurrency_trend_slope": round(slope, 4),
        "max_queue_pressure": queue_pressure,
        "throughput_units_per_sec": round(throughput, 2)
    }

class BQJobsDataGetter:
    """A class to fetch, process, and save BigQuery job data."""
    def __init__(self, output_dir: str):
        self.client = bigquery.Client()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.raw_file_path = self.output_dir / "bq_jobs_raw.jsonl"
        self.minimized_file_path = self.output_dir / "bq_jobs_minimized.json" # Changed to .json
        self.queries_temp_path = self.output_dir / "all_queries.jsonl"
        self.final_queries_path = self.output_dir / "unique_queries.json"
        
        logging.info(f"Output directory set to: {self.output_dir}")

    def _initialize_output_files(self):
        logging.info("Initializing output files...")
        for path in [self.raw_file_path, self.minimized_file_path, self.queries_temp_path, self.final_queries_path]:
            if path.exists():
                path.unlink()
            path.touch()

    def _fetch_top_job_ids(self):
        # ... (Implementation is correct and unchanged) ...
        queries = [
            """
            SELECT total_bytes_billed AS bill, job_id, project_id
            FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_ORGANIZATION
            WHERE reservation_id IS NULL AND statement_type != 'SCRIPT'
            ORDER BY bill DESC
            LIMIT 1000;
            """,
            """
            SELECT total_slot_ms AS slot_usage, job_id, project_id
            FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_ORGANIZATION
            WHERE reservation_id IS NOT NULL AND statement_type != 'SCRIPT'
            ORDER BY slot_usage DESC
            LIMIT 1000;
            """
        ]
        project_jobs = defaultdict(list)
        for query in queries:
            try:
                results = self.client.query(query).result()
                for row in results:
                    project_jobs[row.project_id].append(row.job_id)
            except Exception as e:
                logging.error(f"An error occurred while fetching job IDs: {e}")
        for project_id in project_jobs:
            project_jobs[project_id] = sorted(list(set(project_jobs[project_id])))
        logging.info(f"Found {sum(len(v) for v in project_jobs.values())} unique jobs across {len(project_jobs)} projects.")
        return project_jobs


    def _fetch_and_process_jobs(self, project_jobs: defaultdict) -> list:
        minimized_job_list = []
        for project_id, job_ids in tqdm(project_jobs.items(), desc="Processing projects"):
            batch_size = 100
            for i in tqdm(range(0, len(job_ids), batch_size), desc=f"Batches for {project_id}", colour='yellow', leave=False):
                batch_job_ids = job_ids[i:i + batch_size]
                job_id_list_str = "', '".join(batch_job_ids)
                query = f"SELECT * FROM `{project_id}.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT` WHERE job_id IN ('{job_id_list_str}')"
                
                try:
                    results = self.client.query(query).result()
                    batch_data = [dict(row.items()) for row in results]
                    if not batch_data: continue

                    with open(self.raw_file_path, 'a') as f_raw, open(self.queries_temp_path, 'a') as f_q:
                        for job in batch_data:
                            f_raw.write(json.dumps(job, default=str) + '\n')
                            
                            query_text = job.get('query')
                            if query_text:
                                f_q.write(json.dumps({'query': query_text}) + '\n')
                            
                            # Process for minimized version
                            if 'timeline' in job and isinstance(job.get('timeline'), list):
                                job['timeline_summary'] = aggregate_timeline_metrics(job['timeline'])
                            job.pop('timeline', None)
                            job.pop('query', None)
                            job.pop('job_stages', None)
                            minimized_job_list.append(job)
                except Exception as e:
                    logging.error(f"Could not process jobs from project {project_id}. Error: {e}")
        return minimized_job_list

    def _finalize_unique_queries(self):
        logging.info("Finalizing unique queries...")
        unique_queries = set()
        try:
            with open(self.queries_temp_path, 'r') as f:
                for line in f:
                    unique_queries.add(json.loads(line)['query'])
            with open(self.final_queries_path, 'w') as f:
                json.dump(sorted(list(unique_queries)), f, indent=4)
        finally:
            if self.queries_temp_path.exists():
                self.queries_temp_path.unlink()

    def run(self):
        """Main method to execute the data gathering and processing workflow."""
        self._initialize_output_files()
        project_jobs = self._fetch_top_job_ids()
        if not project_jobs:
            logging.warning("No job IDs were fetched. Exiting.")
            return

        minimized_jobs = self._fetch_and_process_jobs(project_jobs)
        
        logging.info(f"Saving {len(minimized_jobs)} minimized job records to {self.minimized_file_path}...")
        with open(self.minimized_file_path, 'w') as f:
            json.dump(minimized_jobs, f, indent=4, default=str)
        
        self._finalize_unique_queries()
        logging.info("BigQuery data gathering process finished.")


def process_raw_file_for_testing(input_path: str, output_path: str):
    """
    Reads a _raw.jsonl file, applies timeline aggregation and minimization,
    and writes the result to a single .json file.
    """
    logging.info(f"Starting test processing from: {input_path}")
    minimized_jobs = []
    try:
        with open(input_path, 'r') as f:
            # Read all lines first to use tqdm effectively
            lines = f.readlines()
            for line in tqdm(lines, desc="Processing raw file"):
                try:
                    job = json.loads(line)
                    if 'timeline' in job and isinstance(job.get('timeline'), list):
                        job['timeline_summary'] = aggregate_timeline_metrics(job['timeline'])
                    job.pop('timeline', None)
                    job.pop('query', None)
                    job.pop('job_stages', None)
                    minimized_jobs.append(job)
                except json.JSONDecodeError:
                    logging.warning(f"Skipping malformed JSON line: {line[:100]}...")
    
        logging.info(f"Processed {len(minimized_jobs)} jobs. Writing to {output_path}...")
        with open(output_path, 'w') as f:
            json.dump(minimized_jobs, f, indent=4, default=str)
        logging.info("Test processing finished successfully.")
    except FileNotFoundError:
        logging.error(f"Input file not found: {input_path}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BigQuery Job Data Getter and Processor.")
    parser.add_argument(
        '--process-raw',
        type=str,
        metavar='PATH',
        help='Path to a _raw.jsonl file to process for testing aggregation logic.'
    )
    args = parser.parse_args()

    job_run_dir = os.getenv('JOB_RUN_DIR', 'job_runs/latest')
    output_path = Path(job_run_dir) / 'bq_results'

    if args.process_raw:
        input_file = Path(args.process_raw)
        output_file = input_file.parent / f"{input_file.stem}_minimized_test.json"
        process_raw_file_for_testing(str(input_file), str(output_file))
    else:
        logging.info("Starting BigQuery data gathering process...")
        data_getter = BQJobsDataGetter(output_dir=str(output_path))
        data_getter.run()

