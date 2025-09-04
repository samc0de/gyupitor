# BigQuery Cost Optimization Analysis Report

This directory contains the output of the FinOps cost optimization analysis for BigQuery jobs.

## File Descriptions:

- **`recommendations.json`**: 
  - **Format**: JSON
  - **Content**: A list of detailed, actionable recommendations to reduce BigQuery costs. Each recommendation includes a priority, a description of the problem, a proposed solution, and an estimated financial impact.

- **`cost_analysis.csv`**: 
  - **Format**: CSV
  - **Content**: A tabular breakdown of the most expensive queries identified during the analysis. It includes metrics such as `query_hash`, `user_email`, `total_bytes_billed`, `estimated_cost_usd`, and performance indicators like `shuffle_output_bytes_spilled` and `slot_contention_detected`.

- **`inefficient_queries.yaml`**: 
  - **Format**: YAML
  - **Content**: A human-readable summary of the most inefficient queries. This file groups queries by their normalized hash and provides key metrics, source/destination tables, and a summary of the findings for each problematic query pattern.