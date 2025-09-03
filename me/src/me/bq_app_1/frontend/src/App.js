import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import RecommendationDetail from './components/RecommendationDetail';
import Header from './components/Header';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/recommendations/:id" element={<RecommendationDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
