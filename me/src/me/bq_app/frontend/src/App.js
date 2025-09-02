import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [message, setMessage] = useState('Loading...');
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    // Fetch the root API message
    fetch('/api/')
      .then(response => response.json())
      .then(data => setMessage(data))
      .catch(error => setMessage(`Error fetching API root: ${error.toString()}`))

    // Fetch dashboard summary
    fetch('/api/dashboard_summary/')
      .then(response => response.json())
      .then(data => setSummary(data))
      .catch(error => {
        console.error('Error fetching summary:', error);
        setSummary({ error: 'Could not load summary data.' });
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to BQ Cost Optimizer!</h1>
        <p><i>Backend status: {message}</i></p>
        <div className="summary-card">
          <h2>Dashboard Summary</h2>
          {summary ? (
            summary.error ? (
              <p>{summary.error}</p>
            ) : (
              <ul>
                <li>Total Cost (TB): {summary.total_cost_tb ? summary.total_cost_tb.toFixed(4) : 'N/A'}</li>
                <li>Total Queries Analyzed: {summary.total_queries_analyzed}</li>
                <li>Top Spender: {summary.top_spender_email || 'N/A'}</li>
                <li>Top Spender Cost (TB): {summary.top_spender_cost_tb ? summary.top_spender_cost_tb.toFixed(4) : 'N/A'}</li>
                <li>Last Analyzed Date: {summary.last_analyzed_date ? new Date(summary.last_analyzed_date).toLocaleString() : 'N/A'}</li>
              </ul>
            )
          ) : (
            <p>Loading summary...</p>
          )}
        </div>
      </header>
    </div>
  );
}

export default App;