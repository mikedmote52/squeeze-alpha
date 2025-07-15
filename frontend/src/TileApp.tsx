import React, { useState, useEffect } from 'react';
import StockAnalysisModal from './StockAnalysisModal';

interface Position {
  symbol: string;
  qty: number;
  market_value: number;
  current_price: number;
  unrealized_pl: number;
  unrealized_plpc: number;
  cost_basis: number;
  avg_entry_price: number;
}

interface StockTileProps {
  position: Position;
  onTileClick: (position: Position) => void;
}

const StockTile: React.FC<StockTileProps> = ({ position, onTileClick }) => {
  const isProfit = position.unrealized_pl >= 0;
  const percentChange = position.unrealized_plpc;
  
  return (
    <div 
      onClick={() => onTileClick(position)}
      className={`relative p-4 rounded-2xl shadow-lg cursor-pointer transform transition-all duration-200 hover:scale-105 hover:shadow-xl ${
        isProfit ? 'bg-gradient-to-br from-green-500 to-green-600' : 'bg-gradient-to-br from-red-500 to-red-600'
      }`}
    >
      {/* Stock Symbol */}
      <div className="text-white font-bold text-xl mb-2">{position.symbol}</div>
      
      {/* Current Price */}
      <div className="text-white text-lg font-semibold mb-1">
        ${position.current_price.toFixed(2)}
      </div>
      
      {/* Shares */}
      <div className="text-white text-sm opacity-90 mb-2">
        {position.qty} shares
      </div>
      
      {/* P&L */}
      <div className="text-white font-bold text-lg">
        {isProfit ? '+' : ''}${position.unrealized_pl.toFixed(2)}
      </div>
      
      {/* Percentage */}
      <div className="text-white font-medium text-sm">
        {percentChange >= 0 ? '+' : ''}{percentChange.toFixed(1)}%
      </div>
      
      {/* Market Value */}
      <div className="text-white text-xs opacity-75 mt-2">
        Value: ${position.market_value.toFixed(0)}
      </div>
      
      {/* Click indicator */}
      <div className="absolute top-2 right-2 text-white text-xs opacity-60">
        📊
      </div>
    </div>
  );
};

interface StockDetailModalProps {
  position: Position | null;
  isOpen: boolean;
  onClose: () => void;
  onExecuteTrade: (symbol: string, action: 'buy' | 'sell', quantity: number) => void;
}

const StockDetailModal: React.FC<StockDetailModalProps> = ({ position, isOpen, onClose, onExecuteTrade }) => {
  const [aiAnalysis, setAiAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [tradeQty, setTradeQty] = useState(1);
  const [executing, setExecuting] = useState(false);

  useEffect(() => {
    if (position && isOpen) {
      fetchAIAnalysis();
    }
  }, [position, isOpen]);

  const fetchAIAnalysis = async () => {
    if (!position) return;
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/ai-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: position.symbol,
          context: `Analyze ${position.symbol} current position. I own ${position.qty} shares at $${position.avg_entry_price} avg cost. Current P&L: ${position.unrealized_pl >= 0 ? '+' : ''}$${position.unrealized_pl.toFixed(2)}. What should I do next?`
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setAiAnalysis(data);
      }
    } catch (error) {
      console.error('Failed to fetch AI analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTrade = async (action: 'buy' | 'sell') => {
    if (!position || tradeQty <= 0) return;
    
    setExecuting(true);
    try {
      await onExecuteTrade(position.symbol, action, tradeQty);
      // Log the trade for system learning
      await logTrade(position.symbol, action, tradeQty, position.current_price, aiAnalysis);
    } catch (error) {
      console.error('Trade execution failed:', error);
    } finally {
      setExecuting(false);
    }
  };

  const logTrade = async (symbol: string, action: string, qty: number, price: number, analysis: any) => {
    try {
      await fetch('http://localhost:8000/api/trades/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          action,
          quantity: qty,
          price,
          timestamp: new Date().toISOString(),
          ai_analysis: analysis,
          reasoning: `${action.toUpperCase()} ${qty} shares of ${symbol} at $${price} based on AI analysis`
        })
      });
    } catch (error) {
      console.error('Failed to log trade:', error);
    }
  };

  if (!isOpen || !position) return null;

  const isProfit = position.unrealized_pl >= 0;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className={`p-6 rounded-t-2xl text-white ${isProfit ? 'bg-green-600' : 'bg-red-600'}`}>
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-3xl font-bold">{position.symbol}</h2>
              <div className="text-lg opacity-90">{position.qty} shares @ ${position.avg_entry_price.toFixed(2)}</div>
              <div className="text-2xl font-bold mt-2">
                Current: ${position.current_price.toFixed(2)}
              </div>
            </div>
            <button onClick={onClose} className="text-white text-2xl hover:opacity-75">×</button>
          </div>
          
          <div className="grid grid-cols-3 gap-4 mt-4">
            <div>
              <div className="text-sm opacity-80">Market Value</div>
              <div className="text-xl font-bold">${position.market_value.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-sm opacity-80">Unrealized P&L</div>
              <div className="text-xl font-bold">
                {isProfit ? '+' : ''}${position.unrealized_pl.toFixed(2)}
              </div>
            </div>
            <div>
              <div className="text-sm opacity-80">% Return</div>
              <div className="text-xl font-bold">
                {position.unrealized_plpc >= 0 ? '+' : ''}{position.unrealized_plpc.toFixed(1)}%
              </div>
            </div>
          </div>
        </div>

        {/* AI Analysis Section */}
        <div className="p-6">
          <h3 className="text-xl font-bold mb-4">🤖 AI Analysis & Recommendations</h3>
          
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Analyzing position...</p>
            </div>
          ) : aiAnalysis ? (
            <div className="space-y-4">
              {aiAnalysis.agents?.map((agent: any, index: number) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold">{agent.name}</span>
                      <div className="text-sm text-gray-500">
                        Confidence: {Math.round(agent.confidence * 100)}%
                      </div>
                    </div>
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          agent.confidence >= 0.8 ? 'bg-green-500' : 
                          agent.confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${agent.confidence * 100}%` }}
                      />
                    </div>
                  </div>
                  <p className="text-gray-700">{agent.reasoning}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-500 text-center py-4">
              Failed to load AI analysis
            </div>
          )}
        </div>

        {/* Trading Actions */}
        <div className="p-6 border-t bg-gray-50 rounded-b-2xl">
          <h3 className="text-lg font-bold mb-4">📈 Execute Trades</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Buy More */}
            <div className="border rounded-lg p-4 bg-white">
              <h4 className="font-semibold text-green-600 mb-3">Buy More Shares</h4>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
                  <input
                    type="number"
                    value={tradeQty}
                    onChange={(e) => setTradeQty(parseInt(e.target.value) || 1)}
                    min="1"
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-green-500"
                  />
                </div>
                <div className="text-sm text-gray-600">
                  Cost: ~${(position.current_price * tradeQty).toFixed(2)}
                </div>
                <button
                  onClick={() => handleTrade('buy')}
                  disabled={executing}
                  className="w-full bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 disabled:opacity-50"
                >
                  {executing ? 'Executing...' : `Buy ${tradeQty} Shares`}
                </button>
              </div>
            </div>

            {/* Sell Shares */}
            <div className="border rounded-lg p-4 bg-white">
              <h4 className="font-semibold text-red-600 mb-3">Sell Shares</h4>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
                  <input
                    type="number"
                    value={tradeQty}
                    onChange={(e) => setTradeQty(Math.min(parseInt(e.target.value) || 1, position.qty))}
                    min="1"
                    max={position.qty}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-red-500"
                  />
                </div>
                <div className="text-sm text-gray-600">
                  Proceeds: ~${(position.current_price * tradeQty).toFixed(2)}
                </div>
                <button
                  onClick={() => handleTrade('sell')}
                  disabled={executing || tradeQty > position.qty}
                  className="w-full bg-red-600 text-white py-2 px-4 rounded hover:bg-red-700 disabled:opacity-50"
                >
                  {executing ? 'Executing...' : `Sell ${tradeQty} Shares`}
                </button>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="mt-6 grid grid-cols-3 gap-3">
            <button 
              onClick={() => handleTrade('sell')}
              className="bg-yellow-600 text-white py-2 px-4 rounded hover:bg-yellow-700"
            >
              Take Profits (25%)
            </button>
            <button 
              onClick={() => handleTrade('buy')}
              className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
            >
              Add to Position
            </button>
            <button 
              onClick={() => handleTrade('sell')}
              className="bg-red-600 text-white py-2 px-4 rounded hover:bg-red-700"
            >
              Close Position
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const TileApp: React.FC = () => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [selectedPosition, setSelectedPosition] = useState<Position | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [showAIAnalysis, setShowAIAnalysis] = useState(false);
  const [performance, setPerformance] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshTime, setRefreshTime] = useState<Date>(new Date());

  const fetchPortfolioData = async () => {
    try {
      const [positionsRes, performanceRes] = await Promise.all([
        fetch('http://localhost:8000/api/portfolio/positions'),
        fetch('http://localhost:8000/api/portfolio/performance')
      ]);

      if (positionsRes.ok) {
        const posData = await positionsRes.json();
        setPositions(posData.positions || []);
      }

      if (performanceRes.ok) {
        const perfData = await performanceRes.json();
        setPerformance(perfData);
      }

      setRefreshTime(new Date());
    } catch (error) {
      console.error('Failed to fetch portfolio data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolioData();
    const interval = setInterval(fetchPortfolioData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleTileClick = (position: Position) => {
    setSelectedPosition(position);
    setShowModal(true);
  };

  const handleExecuteTrade = async (symbol: string, action: 'buy' | 'sell', quantity: number) => {
    try {
      const response = await fetch('http://localhost:8000/api/trades/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          qty: quantity,
          side: action,
          type: 'market',
          time_in_force: 'day'
        })
      });

      if (response.ok) {
        // Refresh portfolio data after trade
        await fetchPortfolioData();
        alert(`Trade executed: ${action.toUpperCase()} ${quantity} shares of ${symbol}`);
      } else {
        throw new Error('Trade execution failed');
      }
    } catch (error) {
      console.error('Trade execution error:', error);
      alert('Trade execution failed. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your portfolio...</p>
        </div>
      </div>
    );
  }

  const totalValue = performance?.totalEquity || 0;
  const totalPL = positions.reduce((sum, pos) => sum + pos.unrealized_pl, 0);
  const winners = positions.filter(pos => pos.unrealized_pl > 0);

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header with AI Analysis Button */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">📱 AI Trading Portfolio</h1>
              <p className="text-gray-600">Real-time tile interface with AI analysis</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowAIAnalysis(true)}
                className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors font-medium shadow-lg"
              >
                🤖 Ask AI About Any Stock
              </button>
              <button
                onClick={fetchPortfolioData}
                className="bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors"
              >
                🔄 Refresh
              </button>
              <div className="text-right">
                <div className="text-sm text-gray-500">Last Updated</div>
                <div className="text-sm font-medium">{refreshTime.toLocaleTimeString()}</div>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-5 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">${totalValue.toLocaleString()}</div>
              <div className="text-sm text-gray-500">Total Value</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold ${totalPL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {totalPL >= 0 ? '+' : ''}${totalPL.toFixed(2)}
              </div>
              <div className="text-sm text-gray-500">Total P&L</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{positions.length}</div>
              <div className="text-sm text-gray-500">Positions</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{winners.length}</div>
              <div className="text-sm text-gray-500">Winners</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {Math.round((winners.length / positions.length) * 100)}%
              </div>
              <div className="text-sm text-gray-500">Win Rate</div>
            </div>
          </div>
        </div>

        {/* Stock Tiles Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {positions.map((position) => (
            <StockTile
              key={position.symbol}
              position={position}
              onTileClick={handleTileClick}
            />
          ))}
        </div>

        {/* Add new position tile */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          <div className="p-4 rounded-2xl border-2 border-dashed border-gray-300 cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors flex items-center justify-center h-48">
            <div className="text-center text-gray-500">
              <div className="text-3xl mb-2">+</div>
              <div className="text-sm">Add Position</div>
            </div>
          </div>
        </div>
      </div>

      {/* Stock Detail Modal */}
      <StockDetailModal
        position={selectedPosition}
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onExecuteTrade={handleExecuteTrade}
      />

      {/* AI Analysis Modal for Any Stock */}
      <StockAnalysisModal
        isOpen={showAIAnalysis}
        onClose={() => setShowAIAnalysis(false)}
      />
    </div>
  );
};

export default TileApp;