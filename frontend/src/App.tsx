// Main App Component - Catalyst Trading Dashboard
import React, { useState, useEffect } from 'react';
import { Activity, BarChart3, History, Settings, RefreshCw, Wifi, WifiOff } from 'lucide-react';
import CatalystTimeline from './components/CatalystTimeline';
import AIConsensusBar from './components/AIConsensusBar';
import TradeCard from './components/TradeCard';
import AlphaReplay from './components/AlphaReplay';
import { 
  useCatalystData, 
  usePortfolioData, 
  useAlphaOpportunities, 
  useWebSocket 
} from './hooks/useRealTimeData';

interface AppState {
  selectedTicker: string;
  selectedTimeframe: '1D' | '1W' | '1M' | '3M' | '1Y';
  showAlphaReplay: boolean;
  darkMode: boolean;
}

const App: React.FC = () => {
  const [appState, setAppState] = useState<AppState>({
    selectedTicker: 'NVDA',
    selectedTimeframe: '1M',
    showAlphaReplay: false,
    darkMode: false,
  });

  // Real-time data hooks
  const { catalysts, loading: catalystsLoading, error: catalystsError, lastUpdated: catalystsUpdated, refetch: refetchCatalysts } = useCatalystData();
  const { positions, performance, loading: portfolioLoading, error: portfolioError, refetch: refetchPortfolio } = usePortfolioData();
  const { opportunities, loading: alphaLoading, error: alphaError, refetch: refetchAlpha } = useAlphaOpportunities();
  const { connected: wsConnected } = useWebSocket();

  // Auto-refresh data every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      refetchCatalysts();
      refetchPortfolio();
      refetchAlpha();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, [refetchCatalysts, refetchPortfolio, refetchAlpha]);

  // Get ticker symbols from portfolio positions
  const portfolioTickers = positions?.map(p => p.symbol) || [];
  const availableTickers = [...new Set([...portfolioTickers, 'NVDA', 'TSLA', 'AAPL', 'GOOGL', 'MSFT'])];

  const handleTickerChange = (ticker: string) => {
    setAppState(prev => ({ ...prev, selectedTicker: ticker }));
  };

  const handleRefreshAll = () => {
    refetchCatalysts();
    refetchPortfolio();
    refetchAlpha();
  };

  const handleTradeExecution = (trade: any, quantity: number) => {
    console.log('Trade executed:', { trade, quantity });
    // Refresh portfolio after trade execution
    setTimeout(() => {
      refetchPortfolio();
    }, 2000);
  };

  // Mock historical trades for Alpha Replay (would come from backend)
  const historicalTrades = [
    {
      id: '1',
      ticker: 'NVDA',
      companyName: 'NVIDIA Corporation',
      entryPrice: 180.00,
      exitPrice: 220.00,
      entryDate: new Date('2024-11-01'),
      exitDate: new Date('2024-11-15'),
      pnl: 4000,
      pnlPercentage: 22.2,
      catalystType: 'Earnings' as const,
      predictedOutcome: 'Beat earnings by 15%',
      actualOutcome: 'Beat earnings by 18%',
      mostAccurateAgent: 'Claude' as const,
      agentAccuracy: { Claude: 0.92, ChatGPT: 0.88, Grok: 0.84 },
      holdingPeriodDays: 14,
      maxDrawdown: -5.2,
      maxGain: 25.1,
    },
    // Add more historical trades...
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo and Title */}
            <div className="flex items-center space-x-3">
              <Activity className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Catalyst Trading</h1>
                <p className="text-xs text-gray-500">AI-Powered Binary Event Discovery</p>
              </div>
            </div>

            {/* Ticker Selector */}
            <div className="flex items-center space-x-4">
              <select
                value={appState.selectedTicker}
                onChange={(e) => handleTickerChange(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Ticker</option>
                {availableTickers.map(ticker => (
                  <option key={ticker} value={ticker}>{ticker}</option>
                ))}
              </select>

              {/* Connection Status */}
              <div className="flex items-center space-x-2">
                {wsConnected ? (
                  <Wifi className="w-4 h-4 text-green-500" />
                ) : (
                  <WifiOff className="w-4 h-4 text-red-500" />
                )}
                <span className="text-xs text-gray-500">
                  {wsConnected ? 'Live' : 'Offline'}
                </span>
              </div>

              {/* Refresh Button */}
              <button
                onClick={handleRefreshAll}
                className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
                title="Refresh all data"
              >
                <RefreshCw className="w-4 h-4" />
              </button>

              {/* Action Buttons */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setAppState(prev => ({ ...prev, showAlphaReplay: true }))}
                  className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  <History className="w-4 h-4" />
                  <span>Alpha Replay</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Portfolio Summary */}
          {performance && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Overview</h2>
              <div className="grid grid-cols-4 gap-6">
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">
                    ${performance.totalEquity?.toLocaleString() || '0'}
                  </p>
                  <p className="text-sm text-gray-500">Total Value</p>
                </div>
                <div className="text-center">
                  <p className={`text-2xl font-bold ${(performance.dayPL || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {(performance.dayPL || 0) >= 0 ? '+' : ''}${(performance.dayPL || 0).toLocaleString()}
                  </p>
                  <p className="text-sm text-gray-500">Day P&L</p>
                </div>
                <div className="text-center">
                  <p className={`text-2xl font-bold ${(performance.totalPL || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {(performance.totalPL || 0) >= 0 ? '+' : ''}${(performance.totalPL || 0).toLocaleString()}
                  </p>
                  <p className="text-sm text-gray-500">Total P&L</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">{positions?.length || 0}</p>
                  <p className="text-sm text-gray-500">Positions</p>
                </div>
              </div>
            </div>
          )}

          {/* Error States */}
          {(catalystsError || portfolioError || alphaError) && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h3 className="text-sm font-medium text-red-800 mb-2">Data Loading Errors:</h3>
              <ul className="text-sm text-red-600 space-y-1">
                {catalystsError && <li>• Catalysts: {catalystsError}</li>}
                {portfolioError && <li>• Portfolio: {portfolioError}</li>}
                {alphaError && <li>• Alpha: {alphaError}</li>}
              </ul>
            </div>
          )}

          {/* Catalyst Timeline */}
          {appState.selectedTicker && (
            <CatalystTimeline 
              ticker={appState.selectedTicker}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
            />
          )}

          {/* AI Consensus */}
          {appState.selectedTicker && (
            <AIConsensusBar
              symbol={appState.selectedTicker}
              context={`Analyze ${appState.selectedTicker} for upcoming catalysts and trading opportunities`}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
            />
          )}

          {/* Trade Recommendations */}
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">Active Trade Recommendations</h2>
            
            {alphaLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3].map(i => (
                  <div key={i} className="animate-pulse">
                    <div className="bg-gray-200 rounded-xl h-96"></div>
                  </div>
                ))}
              </div>
            ) : opportunities && opportunities.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {opportunities.slice(0, 6).map((opportunity: any) => (
                  <TradeCard
                    key={opportunity.id || opportunity.ticker}
                    trade={{
                      id: opportunity.id || `${opportunity.ticker}-${Date.now()}`,
                      ticker: opportunity.ticker,
                      companyName: opportunity.company_name || opportunity.ticker,
                      entryPrice: opportunity.current_price || 0,
                      currentPrice: opportunity.current_price || 0,
                      targetPrice: opportunity.target_price || opportunity.current_price * 1.15,
                      stopLoss: opportunity.stop_loss || opportunity.current_price * 0.9,
                      positionSize: 5, // Default 5% position
                      catalystType: opportunity.catalyst_type || 'Earnings',
                      whyNow: opportunity.discovery_reason || 'Market opportunity',
                      aiThesis: opportunity.rationale || `${opportunity.ticker} shows strong potential based on technical analysis`,
                      confidence: opportunity.confidence_score || 0.7,
                      expectedUpside: 15,
                      expectedDownside: -10,
                      timeHorizon: '2-4 weeks',
                      createdAt: new Date(),
                      riskLevel: 'Medium' as const,
                    }}
                    portfolioValue={performance?.totalEquity || 100000}
                    onExecute={handleTradeExecution}
                  />
                ))}
              </div>
            ) : (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-12 text-center">
                <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No trade recommendations available</p>
                <p className="text-sm text-gray-500 mt-2">
                  Check back later or try refreshing the data
                </p>
              </div>
            )}
          </div>

          {/* Data Status Footer */}
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between text-sm text-gray-500">
              <div className="flex items-center space-x-4">
                <span>Data Sources: Live APIs</span>
                <span>•</span>
                <span>Portfolio: {portfolioLoading ? 'Updating...' : 'Alpaca'}</span>
                <span>•</span>
                <span>Catalysts: {catalystsLoading ? 'Updating...' : 'FDA.gov, SEC EDGAR'}</span>
              </div>
              {catalystsUpdated && (
                <span>Last Updated: {catalystsUpdated.toLocaleTimeString()}</span>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Alpha Replay Modal */}
      <AlphaReplay
        historicalTrades={historicalTrades}
        isOpen={appState.showAlphaReplay}
        onClose={() => setAppState(prev => ({ ...prev, showAlphaReplay: false }))}
      />
    </div>
  );
};

export default App;