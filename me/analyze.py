import csv
import json
import os
import yaml

def analyze_bq_jobs(input_file, output_dir):
    recommendations = []
    cost_analysis = []
    inefficient_queries = []

    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Cost Analysis
            cost_analysis.append({
                'job_id': row['job_id'],
                'user_email': row['user_email'],
                'total_bytes_billed': row['total_bytes_billed'],
                'total_slot_ms': row['total_slot_ms'],
            })

            # Performance and Inefficiency Analysis
            try:
                job_stages_str = row['job_stages'].replace("'", '"').replace('True', 'true').replace('False', 'false').replace('None', 'null')
                job_stages = json.loads(job_stages_str)
            except (json.JSONDecodeError, AttributeError):
                job_stages = []

            try:
                if row['query_info']:
                    query_info_str = row['query_info'].replace("'", '"').replace('True', 'true').replace('False', 'false').replace('None', 'null')
                    query_info = json.loads(query_info_str)
                else:
                    query_info = {}
            except (json.JSONDecodeError, AttributeError):
                query_info = {}


            # Check for slot contention
            if 'performance_insights' in query_info and 'stage_performance_standalone_insights' in query_info['performance_insights']:
                for insight in query_info['performance_insights']['stage_performance_standalone_insights']:
                    if insight.get('slot_contention'):
                        recommendations.append({
                            'job_id': row['job_id'],
                            'recommendation': 'Slot contention detected. Consider using a reservation with more slots or optimizing the query to use fewer resources.',
                            'details': f"Stage {insight['stage_id']} experienced slot contention."
                        })

            # Check for shuffle spill
            for stage in job_stages:
                if int(stage.get('shuffle_output_bytes_spilled', 0)) > 0:
                    recommendations.append({
                        'job_id': row['job_id'],
                        'recommendation': 'Shuffle spill detected. This can significantly impact performance. Consider increasing the shuffle capacity or optimizing the query to reduce the amount of data being shuffled.',
                        'details': f"Stage {stage['id']} spilled {stage['shuffle_output_bytes_spilled']} bytes to disk."
                    })
                    inefficient_queries.append({
                        'job_id': row['job_id'],
                        'reason': 'Shuffle spill',
                        'details': f"Stage {stage['id']} spilled {stage['shuffle_output_bytes_spilled']} bytes to disk."
                    })

            # Check for high read/write ratio
            if row['total_bytes_processed'] and row['total_bytes_billed'] and int(row['total_bytes_billed']) > 0:
                 if (int(row['total_bytes_processed']) / int(row['total_bytes_billed'])) > 100:
                    inefficient_queries.append({
                        'job_id': row['job_id'],
                        'reason': 'High read to billed ratio',
                        'details': f"Processed {row['total_bytes_processed']} bytes but billed for {row['total_bytes_billed']} bytes."
                    })


    # Write reports
    with open(os.path.join(output_dir, 'recommendations.json'), 'w') as f:
        json.dump(recommendations, f, indent=4)

    with open(os.path.join(output_dir, 'cost_analysis.csv'), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['job_id', 'user_email', 'total_bytes_billed', 'total_slot_ms'])
        writer.writeheader()
        writer.writerows(cost_analysis)

    with open(os.path.join(output_dir, 'inefficient_queries.yaml'), 'w') as f:
        yaml.dump(inefficient_queries, f)

    # Create manifest
    manifest_content = """
# Analysis Report Manifest

This directory contains the analysis of the BigQuery job results.

- `recommendations.json`: Contains a list of recommendations for improving query performance and reducing costs.
- `cost_analysis.csv`: Provides a cost breakdown for each query, including the total bytes billed and total slot milliseconds.
- `inefficient_queries.yaml`: Lists queries that have been identified as inefficient, along with the reason for the inefficiency.
"""
    with open(os.path.join(output_dir, 'manifest.md'), 'w') as f:
        f.write(manifest_content)

if __name__ == '__main__':
    input_file = 'job_runs/20250904_005643/query_results.csv'
    output_dir = 'job_runs/20250904_005643/analysis'
    analyze_bq_jobs(input_file, output_dir)
