import React, { useState, useEffect } from 'react';

interface CatalystData {
  id: string;
  ticker: string;
  name: string;
  type: string;
  date: string;
}

interface AlphaData {
  id: string;
  ticker: string;
  company_name: string;
  current_price: number;
  target_price: number;
  confidence_score: number;
}

const SimpleApp: React.FC = () => {
  const [catalysts, setCatalysts] = useState<CatalystData[]>([]);
  const [opportunities, setOpportunities] = useState<AlphaData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch catalysts
        const catalystResponse = await fetch('http://localhost:8000/api/catalyst-discovery');
        if (catalystResponse.ok) {
          const catalystData = await catalystResponse.json();
          setCatalysts(catalystData.catalysts || []);
        }

        // Fetch opportunities
        const alphaResponse = await fetch('http://localhost:8000/api/alpha-discovery');
        if (alphaResponse.ok) {
          const alphaData = await alphaResponse.json();
          setOpportunities(alphaData.opportunities || []);
        }
      } catch (error) {
        console.warn('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading AI Trading Platform...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                🚀 Catalyst Trading Platform
              </h1>
            </div>
            <div className="text-sm text-green-600 font-medium">
              ✅ Live Data Connected
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          
          {/* Catalyst Events */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              📅 Active Catalysts ({catalysts.length})
            </h2>
            <div className="bg-white rounded-lg shadow overflow-hidden">
              {catalysts.length > 0 ? (
                <div className="divide-y divide-gray-200">
                  {catalysts.map((catalyst) => (
                    <div key={catalyst.id} className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="text-lg font-medium text-gray-900">
                            {catalyst.ticker} - {catalyst.type}
                          </h3>
                          <p className="text-gray-600">{catalyst.name}</p>
                          <p className="text-sm text-gray-500">
                            Date: {new Date(catalyst.date).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                          {catalyst.type}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-6 text-center text-gray-500">
                  No catalysts available
                </div>
              )}
            </div>
          </section>

          {/* Trade Opportunities */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              💎 Alpha Opportunities ({opportunities.length})
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {opportunities.map((opportunity) => (
                <div key={opportunity.id} className="bg-white rounded-lg shadow p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-gray-900">
                      {opportunity.ticker}
                    </h3>
                    <div className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm font-medium">
                      {Math.round(opportunity.confidence_score * 100)}% Confidence
                    </div>
                  </div>
                  
                  <p className="text-gray-600 mb-4">{opportunity.company_name}</p>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Current Price:</span>
                      <span className="font-medium">${opportunity.current_price.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Target Price:</span>
                      <span className="font-medium text-green-600">${opportunity.target_price.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Potential Upside:</span>
                      <span className="font-medium text-green-600">
                        {(((opportunity.target_price - opportunity.current_price) / opportunity.current_price) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  
                  <button className="w-full mt-4 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                    View Details
                  </button>
                </div>
              ))}
            </div>
          </section>

          {/* Status */}
          <section>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">System Status</h3>
                  <p className="text-gray-600">Real-time catalyst discovery and alpha generation</p>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-green-600 font-medium">Live</span>
                </div>
              </div>
            </div>
          </section>

        </div>
      </main>
    </div>
  );
};

export default SimpleApp;