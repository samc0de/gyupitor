document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/queries')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#queries-table tbody');
            data.forEach(query => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${query.query_hash}</td>
                    <td>${query.timestamp}</td>
                    <td>${query.total_slot_ms}</td>
                    <td>${query.total_bytes_processed}</td>
                    <td>${query.total_rows}</td>
                    <td><pre>${query.query_text}</pre></td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error fetching queries:', error));
});