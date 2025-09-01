import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

function RecommendationDetail() {
  const { id } = useParams();
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('newTableSql'); // For future tabs

  const fetchRecommendation = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/recommendations/${id}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setRecommendation(data);
    } catch (e) {
      setError('Failed to fetch recommendation: ' + e.message);
      console.error("Failed to fetch recommendation:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendation();
  }, [id]);

  const handleStatusUpdate = async (newStatus) => {
    try {
      const response = await fetch(`/api/recommendations/${id}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ new_status: newStatus }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      // Update the local state with the new status
      setRecommendation(prev => ({ ...prev, status: newStatus }));
    } catch (e) {
      setError('Failed to update status: ' + e.message);
      console.error("Failed to update status:", e);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'new': return 'bg-warning text-white';
      case 'implemented': return 'bg-success text-white';
      case 'dismissed': return 'bg-info text-white';
      default: return 'bg-gray-200 text-gray-800';
    }
  };

  if (loading) {
    return <div className="text-center py-10">Loading recommendation details...</div>;
  }

  if (error) {
    return <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
      <strong className="font-bold">Error!</strong>
      <span className="block sm:inline"> {error}</span>
    </div>;
  }

  if (!recommendation) {
    return <div className="text-center py-10 text-text-secondary">Recommendation not found.</div>;
  }

  return (
    <div className="recommendation-detail-container">
      <nav className="text-sm text-gray-500 mb-4">
        <ol className="list-none p-0 inline-flex">
          <li className="flex items-center">
            <Link to="/" className="text-primary hover:underline">Dashboard</Link>
            <svg className="fill-current w-3 h-3 mx-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M285.476 272.971L91.132 467.314c-9.373 9.373-24.569 9.373-33.941 0l-22.667-22.667c-9.357-9.357-9.375-24.522-.04-33.901L188.505 256 34.484 71.256c-9.335-9.379-9.317-24.544.04-33.901l22.667-22.667c9.373-9.373 24.569-9.373 33.941 0L285.475 239.03c9.373 9.372 9.373 24.568.001 33.941z"/></svg>
          </li>
          <li>Recommendation {recommendation.recommendation_id}</li>
        </ol>
      </nav>

      <div className="flex justify-between items-center mb-4">
        <h1 className="text-3xl font-bold text-text-primary">
          {recommendation.details.description || recommendation.recommendation_type}
        </h1>
        <span className={`px-3 py-1 text-sm font-semibold rounded-full ${getStatusColor(recommendation.status)}`}>
          {recommendation.status}
        </span>
      </div>
      <h3 className="text-xl font-semibold text-success mb-6">
        Estimated Savings: ${recommendation.estimated_savings_usd.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} / month
      </h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          <div className="bg-surface p-6 rounded-lg shadow-sm border border-border-color">
            <h2 className="text-xl font-semibold text-text-primary mb-4">Details</h2>
            <div className="mb-3">
              <p className="text-xs text-text-secondary">Recommendation ID</p>
              <p className="text-sm text-text-primary font-mono break-all">{recommendation.recommendation_id}</p>
            </div>
            <div className="mb-3">
              <p className="text-xs text-text-secondary">Project ID</p>
              <p className="text-sm text-text-primary font-mono">{recommendation.project_id}</p>
            </div>
            <div className="mb-3">
              <p className="text-xs text-text-secondary">Recommendation Type</p>
              <p className="text-sm text-text-primary font-mono">{recommendation.recommendation_type}</p>
            </div>
            <h2 className="text-xl font-semibold text-text-primary mt-6 mb-2">Description</h2>
            <p className="text-sm text-text-primary leading-relaxed">
              {recommendation.details.description || "No detailed description available."}
            </p>
          </div>

          <div className="bg-surface p-6 rounded-lg shadow-sm border border-border-color">
            <h2 className="text-xl font-semibold text-text-primary mb-4">Actions</h2>
            <div className="flex space-x-3">
              {recommendation.status !== 'implemented' && (
                <button 
                  onClick={() => handleStatusUpdate('implemented')}
                  className="bg-primary hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-md shadow-sm"
                >
                  Mark as Implemented
                </button>
              )}
              {recommendation.status !== 'dismissed' && (
                <button 
                  onClick={() => handleStatusUpdate('dismissed')}
                  className="bg-gray-200 hover:bg-gray-300 text-text-primary font-bold py-2 px-4 rounded-md shadow-sm"
                >
                  Dismiss
                </button>
              )}
              {recommendation.status !== 'new' && ( /* Option to revert to new */
                <button 
                  onClick={() => handleStatusUpdate('new')}
                  className="bg-gray-100 hover:bg-gray-200 text-text-secondary font-bold py-2 px-4 rounded-md shadow-sm text-sm"
                >
                  Revert to New
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <div className="bg-surface p-6 rounded-lg shadow-sm border border-border-color">
            <h2 className="text-xl font-semibold text-text-primary mb-4">Suggested Implementation</h2>
            {/* Tabs for multiple SQL options could go here */}
            {recommendation.details.suggested_sql ? (
              <div className="bg-gray-800 text-white font-mono text-sm p-4 rounded-md relative">
                <pre className="overflow-x-auto custom-scrollbar"><code>{recommendation.details.suggested_sql}</code></pre>
                <button 
                  onClick={() => navigator.clipboard.writeText(recommendation.details.suggested_sql)}
                  className="absolute top-2 right-2 bg-gray-700 hover:bg-gray-600 text-white text-xs px-2 py-1 rounded"
                >
                  Copy Code
                </button>
              </div>
            ) : (
              <p className="text-sm text-text-secondary">No suggested SQL available for this recommendation type.</p>
            )}
          </div>

          <div className="bg-surface p-6 rounded-lg shadow-sm border border-border-color">
            <h2 className="text-xl font-semibold text-text-primary mb-4">Evidence: Top Associated Queries</h2>
            {
              recommendation.details.evidence_jobs && recommendation.details.evidence_jobs.length > 0 ? (
                <div className="divide-y divide-border-color">
                  {recommendation.details.evidence_jobs.map((job, index) => (
                    <details key={index} className="py-3 cursor-pointer group">
                      <summary className="flex justify-between items-center text-sm font-medium text-text-primary list-none">
                        <span>Hash: {job.normalized_query_hash} | Billed: {(job.total_bytes_billed_sum / (1024**4)).toFixed(2)} TB</span>
                        <svg className="fill-current text-gray-500 w-3 h-3 rotate-0 transition-transform duration-200 group-open:rotate-90" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 512"><path d="M224.3 273c-9.4 9.4-24.6 9.4-33.9 0L128 183.1l-62.6 62.6c-9.4 9.4-24.6 9.4-33.9 0s-9.4-24.6 0-33.9L110.1 140c9.4-9.4 24.6-9.4 33.9 0L224.3 239.1c9.4 9.4 9.4 24.6 0 33.9z"/></svg>
                      </summary>
                      {job.representative_query && (
                        <div className="bg-gray-100 font-mono text-xs p-3 mt-2 rounded-md overflow-x-auto custom-scrollbar">
                          <pre><code>{job.representative_query}</code></pre>
                        </div>
                      )}
                    </details>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-text-secondary">No specific job evidence available for this recommendation.</p>
              )
            }
          </div>
        </div>
      </div>
    </div>
  );
}

export default RecommendationDetail;
