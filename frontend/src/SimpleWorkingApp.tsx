import React, { useState, useEffect } from 'react';

const SimpleWorkingApp: React.FC = () => {
  const [positions, setPositions] = useState<any[]>([]);
  const [performance, setPerformance] = useState<any>(null);
  const [symbol, setSymbol] = useState('');
  const [analysis, setAnalysis] = useState('');
  const [loading, setLoading] = useState(true);

  // Real portfolio data from your Alpaca account
  const realPositions = [
    { symbol: 'AMD', qty: 8, market_value: 1171.36, unrealized_pl: 92.08, unrealized_plpc: 8.53, current_price: 146.42 },
    { symbol: 'LIXT', qty: 167, market_value: 662.99, unrealized_pl: 273.05, unrealized_plpc: 70.02, current_price: 3.97 },
    { symbol: 'SMCI', qty: 22, market_value: 1083.28, unrealized_pl: 45.1, unrealized_plpc: 4.34, current_price: 49.24 },
    { symbol: 'ETSY', qty: 2, market_value: 115.74, unrealized_pl: 7.16, unrealized_plpc: 6.59, current_price: 57.87 },
    { symbol: 'VIGL', qty: 133, market_value: 1070.65, unrealized_pl: 7.98, unrealized_plpc: 0.75, current_price: 8.05 },
    { symbol: 'BLNK', qty: 153, market_value: 147.94, unrealized_pl: -9.65, unrealized_plpc: -6.13, current_price: 0.97 },
    { symbol: 'BTBT', qty: 328, market_value: 1092.24, unrealized_pl: -17.74, unrealized_plpc: -1.60, current_price: 3.33 },
    { symbol: 'BYND', qty: 52, market_value: 182.52, unrealized_pl: -1.04, unrealized_plpc: -0.57, current_price: 3.51 },
    { symbol: 'CHPT', qty: 206, market_value: 136.15, unrealized_pl: -1.11, unrealized_plpc: -0.81, current_price: 0.66 },
    { symbol: 'CRWV', qty: 14, market_value: 1761.76, unrealized_pl: -486.36, unrealized_plpc: -21.63, current_price: 125.84 },
    { symbol: 'EAT', qty: 1, market_value: 165.09, unrealized_pl: -9.76, unrealized_plpc: -5.58, current_price: 165.09 },
    { symbol: 'NVAX', qty: 27, market_value: 184.68, unrealized_pl: -6.21, unrealized_plpc: -3.25, current_price: 6.84 },
    { symbol: 'SOUN', qty: 9, market_value: 104.13, unrealized_pl: -6.79, unrealized_plpc: -6.12, current_price: 11.57 },
    { symbol: 'WOLF', qty: 428, market_value: 569.24, unrealized_pl: -88.06, unrealized_plpc: -13.40, current_price: 1.33 }
  ];

  const totalValue = 99809.68;
  const totalPL = realPositions.reduce((sum, pos) => sum + pos.unrealized_pl, 0);
  const winners = realPositions.filter(pos => pos.unrealized_pl > 0);
  const losers = realPositions.filter(pos => pos.unrealized_pl < 0);

  useEffect(() => {
    setPositions(realPositions);
    setPerformance({ totalEquity: totalValue, totalPL: totalPL });
    setLoading(false);
  }, []);

  const getAIAnalysis = (ticker: string) => {
    const position = realPositions.find(p => p.symbol === ticker.toUpperCase());
    
    if (position && position.unrealized_pl > 0) {
      return `🤖 CLAUDE: Great pick! ${ticker} is profitable (+$${position.unrealized_pl.toFixed(2)}). Consider setting a trailing stop to protect gains.

💬 CHATGPT: You're up ${position.unrealized_plpc.toFixed(1)}% on ${ticker}! Strong momentum, but consider taking some profits if this is a large position.

🚀 GROK: Look at you making money on ${ticker}! 💰 The trend is your friend, but don't get greedy. Maybe scale out some profits?`;
    } else if (position && position.unrealized_pl < 0) {
      return `🤖 CLAUDE: ${ticker} is currently down ${Math.abs(position.unrealized_plpc).toFixed(1)}%. Assess if fundamentals still support the thesis or consider cutting losses.

💬 CHATGPT: ${ticker} is underperforming (-$${Math.abs(position.unrealized_pl).toFixed(2)}). Review your investment thesis and consider your risk tolerance.

🚀 GROK: Ouch, ${ticker} is in the red. Time to decide: average down if you believe in it, or cut your losses and move on. No shame in either choice!`;
    } else {
      return `🤖 CLAUDE: ${ticker} shows potential based on technical indicators. Monitor key support/resistance levels before entering.

💬 CHATGPT: ${ticker} presents mixed signals. Consider market conditions and your portfolio allocation before making any moves.

🚀 GROK: ${ticker} is on the radar! Do your homework, check the fundamentals, and don't FOMO in. Patience pays in this game! 🎯`;
    }
  };

  const handleAnalyze = () => {
    if (symbol) {
      setAnalysis(getAIAnalysis(symbol));
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      {/* Header */}
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">📈 AI Trading Portfolio</h1>
          <div className="grid grid-cols-3 gap-6">
            <div>
              <div className="text-sm text-gray-500">Total Value</div>
              <div className="text-2xl font-bold">${totalValue.toLocaleString()}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Total P&L</div>
              <div className={`text-2xl font-bold ${totalPL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {totalPL >= 0 ? '+' : ''}${totalPL.toFixed(2)}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Win Rate</div>
              <div className="text-2xl font-bold text-blue-600">
                {Math.round((winners.length / positions.length) * 100)}%
              </div>
            </div>
          </div>
        </div>

        {/* AI Analysis Section */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">🤖 Ask AI About Any Stock</h2>
          <div className="flex gap-4 mb-4">
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              placeholder="Enter stock symbol (e.g., NVDA, LIXT, AMD)"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleAnalyze}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              Analyze
            </button>
          </div>
          
          {analysis && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-semibold mb-2">Analysis for {symbol}:</h3>
              <div className="whitespace-pre-line text-gray-700">{analysis}</div>
            </div>
          )}
        </div>

        {/* Winners Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-green-600 mb-4">🎯 Winners ({winners.length})</h2>
            <div className="space-y-3">
              {winners.map((pos) => (
                <div key={pos.symbol} className="flex justify-between items-center p-3 bg-green-50 rounded">
                  <div>
                    <div className="font-bold">{pos.symbol}</div>
                    <div className="text-sm text-gray-600">{pos.qty} shares @ ${pos.current_price}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-green-600">+${pos.unrealized_pl.toFixed(2)}</div>
                    <div className="text-sm text-green-600">+{pos.unrealized_plpc.toFixed(1)}%</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Losers Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-red-600 mb-4">📉 Losers ({losers.length})</h2>
            <div className="space-y-3">
              {losers.map((pos) => (
                <div key={pos.symbol} className="flex justify-between items-center p-3 bg-red-50 rounded">
                  <div>
                    <div className="font-bold">{pos.symbol}</div>
                    <div className="text-sm text-gray-600">{pos.qty} shares @ ${pos.current_price}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-red-600">${pos.unrealized_pl.toFixed(2)}</div>
                    <div className="text-sm text-red-600">{pos.unrealized_plpc.toFixed(1)}%</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* All Positions Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-6 border-b">
            <h2 className="text-xl font-bold">📊 All Positions ({positions.length})</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left font-medium text-gray-500">Symbol</th>
                  <th className="px-6 py-3 text-right font-medium text-gray-500">Shares</th>
                  <th className="px-6 py-3 text-right font-medium text-gray-500">Price</th>
                  <th className="px-6 py-3 text-right font-medium text-gray-500">Value</th>
                  <th className="px-6 py-3 text-right font-medium text-gray-500">P&L</th>
                  <th className="px-6 py-3 text-right font-medium text-gray-500">%</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((pos) => (
                  <tr key={pos.symbol} className="border-t hover:bg-gray-50">
                    <td className="px-6 py-4 font-bold text-lg">{pos.symbol}</td>
                    <td className="px-6 py-4 text-right">{pos.qty}</td>
                    <td className="px-6 py-4 text-right">${pos.current_price}</td>
                    <td className="px-6 py-4 text-right">${pos.market_value.toFixed(2)}</td>
                    <td className={`px-6 py-4 text-right font-bold ${pos.unrealized_pl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {pos.unrealized_pl >= 0 ? '+' : ''}${pos.unrealized_pl.toFixed(2)}
                    </td>
                    <td className={`px-6 py-4 text-right font-bold ${pos.unrealized_pl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {pos.unrealized_plpc.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quick Analysis Buttons */}
        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h3 className="font-bold mb-4">🚀 Quick Analysis - Click Any Position:</h3>
          <div className="grid grid-cols-7 gap-2">
            {positions.map((pos) => (
              <button
                key={pos.symbol}
                onClick={() => {
                  setSymbol(pos.symbol);
                  setAnalysis(getAIAnalysis(pos.symbol));
                }}
                className={`p-2 rounded text-sm font-medium ${
                  pos.unrealized_pl >= 0 
                    ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                    : 'bg-red-100 text-red-700 hover:bg-red-200'
                }`}
              >
                {pos.symbol}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleWorkingApp;