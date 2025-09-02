-- This SQL script represents an expensive BigQuery query
-- that would be run on a schedule and its results stored in Firestore.

-- Example: Get daily cost per project/user
SELECT
    DATE(creation_time) AS query_date,
    project_id,
    user_email,
    SUM(total_bytes_processed) AS total_bytes_processed,
    SUM(total_slot_ms) AS total_slot_ms,
    -- Approximate cost calculation (adjust based on actual pricing)
    SUM(total_bytes_processed / (1024 * 1024 * 1024 * 1024) * 5) AS estimated_cost_usd -- $5 per TB
FROM
    `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE
    creation_time BETWEEN TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY) AND CURRENT_TIMESTAMP()
    AND job_type = 'QUERY'
    AND statement_type != 'SCRIPT'
GROUP BY
    1, 2, 3
ORDER BY
    query_date DESC, estimated_cost_usd DESC;
