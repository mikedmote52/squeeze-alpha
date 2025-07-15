import React, { useState, useEffect } from 'react';
import StockAnalysisModal from './StockAnalysisModal';

interface Position {
  symbol: string;
  qty: number;
  market_value: number;
  current_price: number;
  unrealized_pl: number;
  unrealized_plpc: number;
  cost_basis?: number;
  entry_date?: string;
}

interface Performance {
  totalEquity: number;
  dayPL: number;
  totalPL: number;
  totalPLPercent?: number;
  winRate?: number;
}

interface Trade {
  symbol: string;
  side: 'buy' | 'sell';
  qty: number;
  price: number;
  timestamp: string;
  catalyst_reason?: string;
}

const PortfolioApp: React.FC = () => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [performance, setPerformance] = useState<Performance | null>(null);
  const [recentTrades, setRecentTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshTime, setRefreshTime] = useState<Date>(new Date());
  const [showAIAnalysis, setShowAIAnalysis] = useState(false);

  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      
      // Get portfolio positions
      const positionsResponse = await fetch('http://localhost:8000/api/portfolio/positions');
      if (positionsResponse.ok) {
        const positionsData = await positionsResponse.json();
        setPositions(positionsData.positions || []);
      }

      // Get performance data
      const performanceResponse = await fetch('http://localhost:8000/api/portfolio/performance');
      if (performanceResponse.ok) {
        const performanceData = await performanceResponse.json();
        setPerformance(performanceData);
      }

      setRefreshTime(new Date());
    } catch (error) {
      console.warn('Error fetching portfolio data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolioData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchPortfolioData, 30000);
    return () => clearInterval(interval);
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatPercent = (percent: number) => {
    return `${percent >= 0 ? '+' : ''}${percent.toFixed(2)}%`;
  };

  if (loading && positions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading Your Portfolio...</p>
        </div>
      </div>
    );
  }

  const totalValue = performance?.totalEquity || 0;
  const dayChange = performance?.dayPL || 0;
  const totalPL = performance?.totalPL || 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">📈 AI Trading Portfolio</h1>
              <p className="text-sm text-gray-500">Real-time performance tracking</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowAIAnalysis(true)}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors font-medium"
              >
                🤖 Ask AI About Any Stock
              </button>
              <div className="text-right">
                <div className="text-sm text-gray-500">Last Updated</div>
                <div className="text-sm font-medium">{refreshTime.toLocaleTimeString()}</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Portfolio Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500 uppercase tracking-wide">Total Value</div>
            <div className="mt-2 text-3xl font-bold text-gray-900">
              {formatCurrency(totalValue)}
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500 uppercase tracking-wide">Today's P&L</div>
            <div className={`mt-2 text-3xl font-bold ${dayChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {dayChange >= 0 ? '+' : ''}{formatCurrency(dayChange)}
            </div>
            <div className={`text-sm ${dayChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatPercent((dayChange / (totalValue - dayChange)) * 100)}
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500 uppercase tracking-wide">Total P&L</div>
            <div className={`mt-2 text-3xl font-bold ${totalPL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {totalPL >= 0 ? '+' : ''}{formatCurrency(totalPL)}
            </div>
            <div className={`text-sm ${totalPL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatPercent((totalPL / (totalValue - totalPL)) * 100)}
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500 uppercase tracking-wide">Positions</div>
            <div className="mt-2 text-3xl font-bold text-gray-900">{positions.length}</div>
            <div className="text-sm text-gray-500">Active holdings</div>
          </div>
        </div>

        {/* Positions Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">🎯 Current Positions</h2>
          </div>
          
          {positions.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Symbol
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Shares
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Current Price
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Market Value
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Unrealized P&L
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      % Return
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {positions.map((position, index) => (
                    <tr key={position.symbol} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="font-bold text-lg text-gray-900">{position.symbol}</div>
                        <div className="text-sm text-gray-500">AI Recommended</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                        {position.qty.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                        {formatCurrency(position.current_price)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                        {formatCurrency(position.market_value)}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-right text-sm font-bold ${
                        position.unrealized_pl >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {position.unrealized_pl >= 0 ? '+' : ''}{formatCurrency(position.unrealized_pl)}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-right text-sm font-bold ${
                        position.unrealized_plpc >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {formatPercent(position.unrealized_plpc)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-6 text-center text-gray-500">
              <div className="text-4xl mb-4">💼</div>
              <div className="text-lg font-medium">No positions found</div>
              <div className="text-sm">Start trading to see your portfolio here</div>
            </div>
          )}
        </div>

        {/* AI System Performance */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">🤖 AI System Performance</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {totalPL >= 0 ? '+' : ''}{((totalPL / (totalValue - totalPL)) * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-green-600 font-medium">Total Return</div>
              <div className="text-xs text-gray-500">Since AI activation</div>
            </div>
            
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {positions.length > 0 ? Math.round((positions.filter(p => p.unrealized_pl > 0).length / positions.length) * 100) : 0}%
              </div>
              <div className="text-sm text-blue-600 font-medium">Win Rate</div>
              <div className="text-xs text-gray-500">Profitable positions</div>
            </div>
            
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {formatCurrency(Math.abs(dayChange))}
              </div>
              <div className="text-sm text-purple-600 font-medium">Daily Activity</div>
              <div className="text-xs text-gray-500">Today's movement</div>
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="mt-6 bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-gray-900">AI Trading System Active</span>
              <span className="text-xs text-gray-500">• Monitoring {positions.length} positions • Last update: {refreshTime.toLocaleTimeString()}</span>
            </div>
            <button 
              onClick={fetchPortfolioData}
              className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>
      </main>

      {/* AI Analysis Modal */}
      <StockAnalysisModal
        isOpen={showAIAnalysis}
        onClose={() => setShowAIAnalysis(false)}
      />
    </div>
  );
};

export default PortfolioApp;