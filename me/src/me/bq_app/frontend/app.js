document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://localhost:8000'; // FastAPI backend URL

    const recommendationsTableBody = document.querySelector('#recommendationsTable tbody');
    const potentialSavingsElement = document.querySelector('#potentialSavings');
    const activeRecommendationsElement = document.querySelector('#activeRecommendations');
    const dataScannedElement = document.querySelector('#dataScanned');

    async function fetchRecommendations() {
        try {
            const response = await fetch(`${API_BASE_URL}/recommendations`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const recommendations = await response.json();
            console.log('Fetched recommendations:', recommendations);
            updateDashboard(recommendations);
        } catch (error) {
            console.error('Error fetching recommendations:', error);
            // Display error in UI or use mock data if API fails
            alert('Failed to load recommendations. Please ensure the backend is running at ' + API_BASE_URL);
            // Fallback to hardcoded mock data for demonstration if API fails
            const mockData = [
                {
                    id: 'f9d1b6e8-2a1c-4b5d-8e7f-0c9a8b7c6d5e',
                    project_id: 'tlabs-finops',
                    user_email: 'sa-tlabs-finops-vm@tlabs-finops.iam.gserviceaccount.com',
                    job_id: 'job-12345-abcde',
                    query_hash: 'a'.repeat(64),
                    query_text: 'SELECT ... cloud_pricing_export ...',
                    total_billed_gb: 290.34,
                    estimated_cost_usd: 1.42,
                    inefficiency_type: 'FULL_TABLE_SCAN',
                    recommendation_title: 'Optimize `cloud_pricing_export` Table and Queries',
                    recommendation_details: 'Recreate the `cloud_pricing_export` table with partitioning...', 
                    status: 'NEW',
                    created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
                    updated_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
                },
                {
                    id: 'e8c7b6d5-a4b3-c2d1-e0f9-8a7b6c5d4e3f',
                    project_id: 'tlabs-finops',
                    user_email: 'sa-tlabs-finops-vm@tlabs-finops.iam.gserviceaccount.com',
                    job_id: 'job-67890-fghij',
                    query_hash: 'b'.repeat(64),
                    query_text: 'SELECT ... gcp_billing_export_resource ...',
                    total_billed_gb: 276.51,
                    estimated_cost_usd: 1.35,
                    inefficiency_type: 'PARTITION_MISMATCH',
                    recommendation_title: 'Optimize `gcp_billing_export_resource` Table and Queries',
                    recommendation_details: 'Recreate the table with partitioning on `export_time`...', 
                    status: 'NEW',
                    created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
                    updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
                },
            ];
            updateDashboard(mockData);
        }
    }

    function updateDashboard(recommendations) {
        let totalPotentialSavings = 0;
        let totalBilledGb = 0;
        let activeRecommendationsCount = 0;

        recommendationsTableBody.innerHTML = ''; // Clear existing rows

        recommendations.forEach(rec => {
            totalPotentialSavings += rec.estimated_cost_usd;
            totalBilledGb += rec.total_billed_gb;
            if (rec.status === 'NEW' || rec.status === 'ACKNOWLEDGED') {
                activeRecommendationsCount++;
            }

            const row = recommendationsTableBody.insertRow();
            row.innerHTML = `
                <td>${rec.recommendation_title}</td>
                <td>${rec.project_id}</td>
                <td>~$${rec.estimated_cost_usd.toFixed(2)}/mo</td>
                <td><span class="tag tag-new">${rec.status}</span></td>
                <td>${timeAgo(new Date(rec.created_at))}</td>
            `;
            // Make row clickable to navigate to a mock detail view (not implemented yet)
            row.style.cursor = 'pointer';
            row.onclick = () => {
                alert('Navigating to detail for: ' + rec.recommendation_title + '\n(Detail view not yet implemented)');
            };
        });

        potentialSavingsElement.textContent = `$${totalPotentialSavings.toFixed(2)} /mo`;
        activeRecommendationsElement.textContent = activeRecommendationsCount;
        dataScannedElement.textContent = `${totalBilledGb.toFixed(2)} GB`;
    }

    function timeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        let interval = seconds / 31536000; // years
        if (interval > 1) { return Math.floor(interval) + " years ago"; }
        interval = seconds / 2592000; // months
        if (interval > 1) { return Math.floor(interval) + " months ago"; }
        interval = seconds / 86400; // days
        if (interval > 1) { return Math.floor(interval) + " days ago"; }
        interval = seconds / 3600; // hours
        if (interval > 1) { return Math.floor(interval) + " hours ago"; }
        interval = seconds / 60; // minutes
        if (interval > 1) { return Math.floor(interval) + " minutes ago"; }
        return Math.floor(seconds) + " seconds ago";
    }

    fetchRecommendations();
});
