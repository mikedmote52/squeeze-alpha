// AlphaReplay Component - Historical trade performance and AI accuracy tracking
import React, { useState, useMemo } from 'react';
import { History, TrendingUp, TrendingDown, Brain, X, Filter, Medal, Target } from 'lucide-react';

interface HistoricalTrade {
  id: string;
  ticker: string;
  companyName: string;
  entryPrice: number;
  exitPrice: number;
  entryDate: Date;
  exitDate: Date;
  pnl: number;
  pnlPercentage: number;
  catalystType: 'Earnings' | 'FDA' | 'M&A' | 'Legal' | 'Macro' | 'SEC_FILING';
  predictedOutcome: string;
  actualOutcome: string;
  mostAccurateAgent: 'Claude' | 'ChatGPT' | 'Grok';
  agentAccuracy: {
    Claude: number;
    ChatGPT: number;
    Grok: number;
  };
  holdingPeriodDays: number;
  maxDrawdown?: number;
  maxGain?: number;
}

interface AlphaReplayProps {
  historicalTrades: HistoricalTrade[];
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

const AlphaReplay: React.FC<AlphaReplayProps> = ({
  historicalTrades,
  isOpen,
  onClose,
  className = ''
}) => {
  const [filterPeriod, setFilterPeriod] = useState<'1M' | '3M' | '6M' | '1Y' | 'ALL'>('3M');
  const [filterCatalyst, setFilterCatalyst] = useState<string>('ALL');
  const [sortBy, setSortBy] = useState<'date' | 'pnl' | 'accuracy'>('date');

  // Filter trades based on selected criteria
  const filteredTrades = useMemo(() => {
    let filtered = [...historicalTrades];

    // Filter by time period
    if (filterPeriod !== 'ALL') {
      const months = filterPeriod === '1M' ? 1 : filterPeriod === '3M' ? 3 : filterPeriod === '6M' ? 6 : 12;
      const cutoffDate = new Date();
      cutoffDate.setMonth(cutoffDate.getMonth() - months);
      filtered = filtered.filter(trade => new Date(trade.exitDate) >= cutoffDate);
    }

    // Filter by catalyst type
    if (filterCatalyst !== 'ALL') {
      filtered = filtered.filter(trade => trade.catalystType === filterCatalyst);
    }

    // Sort trades
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.exitDate).getTime() - new Date(a.exitDate).getTime();
        case 'pnl':
          return b.pnlPercentage - a.pnlPercentage;
        case 'accuracy':
          const aAccuracy = Math.max(...Object.values(a.agentAccuracy));
          const bAccuracy = Math.max(...Object.values(b.agentAccuracy));
          return bAccuracy - aAccuracy;
        default:
          return 0;
      }
    });

    return filtered;
  }, [historicalTrades, filterPeriod, filterCatalyst, sortBy]);

  // Calculate performance metrics
  const performanceMetrics = useMemo(() => {
    if (filteredTrades.length === 0) {
      return {
        totalTrades: 0,
        winRate: 0,
        avgReturn: 0,
        totalReturn: 0,
        bestTrade: 0,
        worstTrade: 0,
        avgHoldingPeriod: 0,
        agentAccuracy: { Claude: 0, ChatGPT: 0, Grok: 0 }
      };
    }

    const winningTrades = filteredTrades.filter(t => t.pnl > 0);
    const totalReturn = filteredTrades.reduce((sum, t) => sum + t.pnl, 0);
    const avgReturn = filteredTrades.reduce((sum, t) => sum + t.pnlPercentage, 0) / filteredTrades.length;
    const bestTrade = Math.max(...filteredTrades.map(t => t.pnlPercentage));
    const worstTrade = Math.min(...filteredTrades.map(t => t.pnlPercentage));
    const avgHoldingPeriod = filteredTrades.reduce((sum, t) => sum + t.holdingPeriodDays, 0) / filteredTrades.length;

    // Calculate agent accuracy
    const agentAccuracy = {
      Claude: filteredTrades.reduce((sum, t) => sum + t.agentAccuracy.Claude, 0) / filteredTrades.length,
      ChatGPT: filteredTrades.reduce((sum, t) => sum + t.agentAccuracy.ChatGPT, 0) / filteredTrades.length,
      Grok: filteredTrades.reduce((sum, t) => sum + t.agentAccuracy.Grok, 0) / filteredTrades.length,
    };

    return {
      totalTrades: filteredTrades.length,
      winRate: (winningTrades.length / filteredTrades.length) * 100,
      avgReturn,
      totalReturn,
      bestTrade,
      worstTrade,
      avgHoldingPeriod,
      agentAccuracy
    };
  }, [filteredTrades]);

  const getCatalystColor = (type: string) => {
    switch (type) {
      case 'Earnings': return 'bg-blue-100 text-blue-800';
      case 'FDA': return 'bg-red-100 text-red-800';
      case 'M&A': return 'bg-green-100 text-green-800';
      case 'Legal': return 'bg-yellow-100 text-yellow-800';
      case 'SEC_FILING': return 'bg-purple-100 text-purple-800';
      case 'Macro': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getAgentColor = (agent: string) => {
    switch (agent) {
      case 'Claude': return 'text-purple-600';
      case 'ChatGPT': return 'text-green-600';
      case 'Grok': return 'text-blue-600';
      default: return 'text-gray-600';
    }
  };

  if (!isOpen) return null;

  return (
    <div className={`fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 ${className}`}>
      <div className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <History className="w-6 h-6 text-blue-600" />
            <h2 className="text-2xl font-bold text-gray-900">Alpha Replay</h2>
            <span className="text-sm text-gray-500">Historical Performance Analysis</span>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Filters */}
        <div className="p-6 border-b border-gray-200 bg-gray-50">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">Filters:</span>
            </div>
            
            <select
              value={filterPeriod}
              onChange={(e) => setFilterPeriod(e.target.value as any)}
              className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
            >
              <option value="1M">Last Month</option>
              <option value="3M">Last 3 Months</option>
              <option value="6M">Last 6 Months</option>
              <option value="1Y">Last Year</option>
              <option value="ALL">All Time</option>
            </select>

            <select
              value={filterCatalyst}
              onChange={(e) => setFilterCatalyst(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
            >
              <option value="ALL">All Catalysts</option>
              <option value="Earnings">Earnings</option>
              <option value="FDA">FDA</option>
              <option value="M&A">M&A</option>
              <option value="Legal">Legal</option>
              <option value="SEC_FILING">SEC Filing</option>
              <option value="Macro">Macro</option>
            </select>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
            >
              <option value="date">Sort by Date</option>
              <option value="pnl">Sort by P&L</option>
              <option value="accuracy">Sort by AI Accuracy</option>
            </select>
          </div>
        </div>

        {/* Performance Summary */}
        <div className="p-6 border-b border-gray-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{performanceMetrics.totalTrades}</p>
              <p className="text-sm text-gray-500">Total Trades</p>
            </div>
            <div className="text-center">
              <p className={`text-2xl font-bold ${performanceMetrics.winRate >= 50 ? 'text-green-600' : 'text-red-600'}`}>
                {performanceMetrics.winRate.toFixed(1)}%
              </p>
              <p className="text-sm text-gray-500">Win Rate</p>
            </div>
            <div className="text-center">
              <p className={`text-2xl font-bold ${performanceMetrics.avgReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {performanceMetrics.avgReturn >= 0 ? '+' : ''}{performanceMetrics.avgReturn.toFixed(1)}%
              </p>
              <p className="text-sm text-gray-500">Avg Return</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{performanceMetrics.avgHoldingPeriod.toFixed(1)}d</p>
              <p className="text-sm text-gray-500">Avg Hold Period</p>
            </div>
          </div>

          {/* AI Agent Performance */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-3">AI Agent Accuracy</h4>
            <div className="grid grid-cols-3 gap-4">
              {Object.entries(performanceMetrics.agentAccuracy).map(([agent, accuracy]) => (
                <div key={agent} className="text-center">
                  <div className="flex items-center justify-center space-x-1 mb-1">
                    <Brain className="w-4 h-4 text-gray-400" />
                    <span className="text-sm font-medium text-gray-900">{agent}</span>
                  </div>
                  <p className={`text-lg font-bold ${getAgentColor(agent)}`}>
                    {(accuracy * 100).toFixed(1)}%
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Trade History */}
        <div className="flex-1 overflow-y-auto max-h-96">
          {filteredTrades.length === 0 ? (
            <div className="p-12 text-center">
              <History className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No trades found for selected filters</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredTrades.map((trade) => (
                <div key={trade.id} className="p-6 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="text-lg font-semibold text-gray-900">{trade.ticker}</h4>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCatalystColor(trade.catalystType)}`}>
                          {trade.catalystType}
                        </span>
                        <div className="flex items-center space-x-1">
                          <Medal className="w-4 h-4 text-gray-400" />
                          <span className={`text-sm font-medium ${getAgentColor(trade.mostAccurateAgent)}`}>
                            {trade.mostAccurateAgent}
                          </span>
                        </div>
                      </div>
                      
                      <p className="text-sm text-gray-600 mb-3">{trade.companyName}</p>
                      
                      <div className="grid grid-cols-4 gap-4 mb-3">
                        <div>
                          <p className="text-xs text-gray-500">Entry</p>
                          <p className="text-sm font-semibold text-gray-900">${trade.entryPrice.toFixed(2)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Exit</p>
                          <p className="text-sm font-semibold text-gray-900">${trade.exitPrice.toFixed(2)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Hold Period</p>
                          <p className="text-sm font-semibold text-gray-900">{trade.holdingPeriodDays}d</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Date</p>
                          <p className="text-sm font-semibold text-gray-900">
                            {new Date(trade.exitDate).toLocaleDateString()}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-xs text-gray-500">Predicted: {trade.predictedOutcome}</p>
                          <p className="text-xs text-gray-500">Actual: {trade.actualOutcome}</p>
                        </div>
                        
                        <div className="flex items-center space-x-4">
                          <div className="text-right">
                            <p className="text-xs text-gray-500">P&L</p>
                            <p className={`text-sm font-bold ${trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              ${trade.pnl.toLocaleString()}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-gray-500">Return</p>
                            <div className={`flex items-center space-x-1 ${trade.pnlPercentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {trade.pnlPercentage >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                              <span className="text-sm font-bold">
                                {trade.pnlPercentage >= 0 ? '+' : ''}{trade.pnlPercentage.toFixed(1)}%
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AlphaReplay;