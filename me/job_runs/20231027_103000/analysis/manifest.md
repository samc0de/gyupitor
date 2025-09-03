# BigQuery Job Analysis

This directory contains the analysis of BigQuery jobs, with a focus on cost and performance optimization.

## Files

*   `inefficient_queries.yaml`: A list of inefficient queries identified from the BigQuery job logs. Each entry includes the query hash and the number of times the query was executed.

*   `cost_analysis.csv`: A CSV file containing a cost analysis of the BigQuery jobs. It includes the project ID, job ID, user email, total bytes billed, and the estimated cost in USD.

*   `recommendations.json`: A JSON file with detailed recommendations for optimizing the inefficient queries. Each recommendation includes the query hash, a description of the issue, and a suggested remedy.
