import React, { useState, useEffect } from 'react';
import ApexCharts from 'react-apexcharts';
import { Link } from 'react-router-dom';

function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterProject, setFilterProject] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/metrics');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setMetrics(data);
    } catch (e) {
      setError('Failed to fetch metrics: ' + e.message);
      console.error("Failed to fetch metrics:", e);
    }
  };

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    const params = new URLSearchParams();
    if (searchQuery) params.append('q', searchQuery);
    if (filterProject) params.append('project_id', filterProject);
    if (filterType) params.append('recommendation_type', filterType);
    if (filterStatus) params.append('status', filterStatus);

    try {
      const response = await fetch(`/api/recommendations?${params.toString()}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setRecommendations(data);
    } catch (e) {
      setError('Failed to fetch recommendations: ' + e.message);
      console.error("Failed to fetch recommendations:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    fetchRecommendations();
  }, []); // Initial fetch

  useEffect(() => {
    const handler = setTimeout(() => {
      fetchRecommendations();
    }, 500); // Debounce search
    return () => clearTimeout(handler);
  }, [searchQuery, filterProject, filterType, filterStatus]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'new': return 'bg-warning text-white';
      case 'implemented': return 'bg-success text-white';
      case 'dismissed': return 'bg-info text-white';
      default: return 'bg-gray-200 text-gray-800';
    }
  };

  // Chart data setup (assuming metrics are fetched)
  const costTrendSeries = metrics ? [{
    name: 'Daily BQ Cost',
    data: metrics.cost_trend.map(item => ({ x: item.date, y: item.cost }))
  }] : [];

  const savingsTrendSeries = metrics ? [{
    name: 'Cumulative Potential Savings',
    data: metrics.savings_trend.map(item => ({ x: item.date, y: item.savings }))
  }] : [];

  const costTrendOptions = {
    chart: {
      id: 'cost-savings-trend',
      toolbar: { show: false }
    },
    xaxis: {
      type: 'datetime',
    },
    colors: ['#3B82F6'],
    dataLabels: { enabled: false },
    stroke: { curve: 'smooth' },
    tooltip: { x: { format: 'dd MMM' } },
    fill: { type: 'gradient', gradient: { opacityFrom: 0.6, opacityTo: 0.8 } }
  };

  const savingsByTypeSeries = metrics ? metrics.savings_by_type.map(item => item.savings) : [];
  const savingsByTypeOptions = {
    chart: {
      type: 'donut',
    },
    labels: metrics ? metrics.savings_by_type.map(item => item.type) : [],
    colors: ['#3B82F6', '#10B981', '#F59E0B', '#0EA5E9', '#EF4444'],
    responsive: [{
      breakpoint: 480,
      options: {
        chart: {
          width: 200
        },
        legend: {
          position: 'bottom'
        }
      }
    }],
    legend: { show: true, position: 'bottom' },
  };


  return (
    <div className="dashboard-container">
      <h1 className="text-3xl font-bold text-text-primary mb-6">Dashboard</h1>

      {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
        <strong className="font-bold">Error!</strong>
        <span className="block sm:inline"> {error}</span>
      </div>}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-surface p-6 rounded-lg shadow-sm border border-border-color">
          <h3 className="text-lg font-semibold text-text-secondary">Total Spend (30d)</h3>
          <p className="text-3xl font-bold text-text-primary mt-2">{metrics ? `$${metrics.total_spend_30d.toLocaleString()}` : 'Loading...'}</p>
        </div>
        <div className="bg-surface p-6 rounded-lg shadow-sm border border-border-color">
          <h3 className="text-lg font-semibold text-text-secondary">Potential Savings</h3>
          <p className="text-3xl font-bold text-success mt-2">{metrics ? `$${metrics.potential_savings_monthly.toLocaleString()} / mo` : 'Loading...'}</p>
        </div>
        <div className="bg-surface p-6 rounded-lg shadow-sm border border-border-color">
          <h3 className="text-lg font-semibold text-text-secondary">Recommendations</h3>
          <p className="text-3xl font-bold text-text-primary mt-2">{metrics ? `${metrics.recommendations_implemented} of ${metrics.total_recommendations} Implemented` : 'Loading...'}</p>
        </div>
        <div className="bg-surface p-6 rounded-lg shadow-sm border border-border-color">
          <h3 className="text-lg font-semibold text-text-secondary">Savings Realized</h3>
          <p className="text-3xl font-bold text-success mt-2">{metrics ? `$${metrics.savings_realized_monthly.toLocaleString()} / mo` : 'Loading...'}</p>
        </div>
      </div>

      {/* Visualization Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-surface p-6 rounded-lg shadow-sm border border-border-color">
          <h2 className="text-xl font-semibold text-text-primary mb-4">Cost & Savings Trend (Last 30 Days)</h2>
          {metrics ? (
            <ApexCharts options={costTrendOptions} series={costTrendSeries} type="area" height={300} />
          ) : (
            <div className="text-center py-10">Loading chart...</div>
          )}
        </div>
        <div className="bg-surface p-6 rounded-lg shadow-sm border border-border-color">
          <h2 className="text-xl font-semibold text-text-primary mb-4">Savings by Type</h2>
          {metrics ? (
            <ApexCharts options={savingsByTypeOptions} series={savingsByTypeSeries} type="donut" height={300} />
          ) : (
            <div className="text-center py-10">Loading chart...</div>
          )}
        </div>
      </div>

      {/* Actionable Recommendations Table */}
      <div className="bg-surface p-6 rounded-lg shadow-sm border border-border-color">
        <h2 className="text-xl font-semibold text-text-primary mb-4">Actionable Recommendations</h2>
        
        {/* Filters and Search */}
        <div className="flex flex-wrap gap-4 mb-4 items-center">
          <input
            type="text"
            placeholder="Search by keyword..."
            className="flex-grow p-2 border border-border-color rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <select
            className="p-2 border border-border-color rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            value={filterProject}
            onChange={(e) => setFilterProject(e.target.value)}
          >
            <option value="">Filter by Project</option>
            <option value="gcp-sales">gcp-sales</option>
            <option value="gcp-finance">gcp-finance</option>
            <option value="gcp-product">gcp-product</option>
            <option value="gcp-backend">gcp-backend</option>
          </select>
          <select
            className="p-2 border border-border-color rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            <option value="">Filter by Type</option>
            <option value="PARTITION_TABLE">Partition Table</option>
            <option value="CREATE_MATERIALIZED_VIEW">Create Materialized View</option>
            <option value="REWRITE_QUERY">Rewrite Query</option>
            <option value="CLUSTER_TABLE">Cluster Table</option>
            <option value="OPTIMIZE_WILDCARD_QUERY">Optimize Wildcard Query</option>
          </select>
          <select
            className="p-2 border border-border-color rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="">Filter by Status</option>
            <option value="new">New</option>
            <option value="implemented">Implemented</option>
            <option value="dismissed">Dismissed</option>
          </select>
        </div>

        {/* Table */}
        {loading ? (
          <div className="text-center py-10">Loading recommendations...</div>
        ) : recommendations.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-border-color">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Status</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Recommendation</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Project ID</th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-text-secondary uppercase tracking-wider">Est. Savings/Mo</th>
                  <th scope="col" className="relative px-6 py-3"><span className="sr-only">Actions</span></th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-border-color">
                {recommendations.map((rec) => (
                  <tr key={rec.recommendation_id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(rec.status)}`}>
                        {rec.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-text-primary">
                      {rec.details.description || rec.recommendation_type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-text-secondary">
                      {rec.project_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-text-primary text-right">
                      ${rec.estimated_savings_usd.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <Link to={`/recommendations/${rec.recommendation_id}`} className="text-primary hover:text-blue-800">View</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-10 text-text-secondary">No recommendations found.</div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
