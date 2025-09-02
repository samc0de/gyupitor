import functions_framework
from google.cloud import bigquery
from google.cloud import firestore

@functions_framework.http
def process_bigquery_data(request):
    client = bigquery.Client()
    firestore_client = firestore.Client()

    # Placeholder for the BigQuery query
    # In a real scenario, this query would be more complex and optimized
    query = """
        SELECT
            creation_time,
            user_email,
            job_type,
            total_bytes_processed,
            total_slot_ms,
            project_id
        FROM
            `bigquery-public-data.austin_bikeshare.bikeshare_trips`
        LIMIT 100
    """

    query_job = client.query(query)
    rows = query_job.result()

    # Placeholder for storing results in Firestore
    # In a real scenario, data would be structured and batched for efficiency
    doc_ref = firestore_client.collection('bq_cost_data').document('latest')
    data_to_store = []
    for row in rows:
        data_to_store.append(dict(row))
    
    doc_ref.set({"data": data_to_store})

    return 'BigQuery data processed and stored in Firestore!', 200
