const API_BASE_URL = 'http://backend:8000'; // Assuming backend runs on this port

async function checkApiStatus() {
    const responseElement = document.getElementById('apiStatusResponse');
    responseElement.textContent = 'Loading...';
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        const data = await response.json();
        responseElement.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        responseElement.textContent = `Error: ${error.message}. Make sure the backend is running.`;
        console.error('Error checking API status:', error);
    }
}

async function sendQuery(queryId) {
    const responseElement = document.getElementById('queryResponse');
    responseElement.textContent = 'Loading...';
    try {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query_id: queryId }),
        });
        const data = await response.json();
        if (response.ok) {
            responseElement.textContent = JSON.stringify(data, null, 2);
        } else {
            responseElement.textContent = `Error: ${data.detail || response.statusText}`; 
        }
    } catch (error) {
        responseElement.textContent = `Error: ${error.message}. Make sure the backend is running.`;
        console.error('Error sending query:', error);
    }
}