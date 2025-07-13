// TradeCard Component - Real trade execution with Alpaca integration
import React, { useState } from 'react';
import { TrendingUp, TrendingDown, Target, Shield, Clock, DollarSign, AlertTriangle, CheckCircle } from 'lucide-react';
import { useTradeExecution, useStockData } from '../hooks/useRealTimeData';

interface TradeRecommendation {
  id: string;
  ticker: string;
  companyName: string;
  entryPrice: number;
  currentPrice?: number;
  targetPrice: number;
  stopLoss: number;
  positionSize: number; // percentage of portfolio
  catalystType: 'Earnings' | 'FDA' | 'M&A' | 'Legal' | 'Macro' | 'SEC_FILING';
  whyNow: string;
  aiThesis: string;
  confidence: number; // 0-1 scale
  expectedUpside: number;
  expectedDownside: number;
  timeHorizon: string;
  createdAt: Date;
  expiresAt?: Date;
  riskLevel: 'Low' | 'Medium' | 'High';
}

interface TradeCardProps {
  trade: TradeRecommendation;
  portfolioValue?: number;
  onExecute?: (trade: TradeRecommendation, quantity: number) => void;
  className?: string;
  showExecuteButton?: boolean;
}

const TradeCard: React.FC<TradeCardProps> = ({
  trade,
  portfolioValue = 100000, // Default $100k portfolio
  onExecute,
  className = '',
  showExecuteButton = true
}) => {
  const { executeTrade, loading: executeLoading, error: executeError } = useTradeExecution();
  const { stockData, loading: stockLoading } = useStockData(trade.ticker);
  const [showDetails, setShowDetails] = useState(false);
  const [customQuantity, setCustomQuantity] = useState<number | null>(null);

  // Use real current price from stock data, fallback to trade data
  const currentPrice = stockData?.currentPrice || trade.currentPrice || trade.entryPrice;
  const dailyChange = stockData?.dailyChange || 0;
  const dailyChangePercent = stockData?.dailyChangePercent || 0;

  // Calculate trade metrics
  const calculateQuantity = () => {
    if (customQuantity) return customQuantity;
    const positionValue = portfolioValue * (trade.positionSize / 100);
    return Math.floor(positionValue / currentPrice);
  };

  const positionValue = calculateQuantity() * currentPrice;
  const potentialGain = calculateQuantity() * (trade.targetPrice - currentPrice);
  const potentialLoss = calculateQuantity() * (currentPrice - trade.stopLoss);
  const riskRewardRatio = Math.abs(potentialGain / potentialLoss);

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

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'Low': return 'text-green-600 bg-green-50';
      case 'Medium': return 'text-yellow-600 bg-yellow-50';
      case 'High': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const isExpired = trade.expiresAt ? new Date() > new Date(trade.expiresAt) : false;
  const daysUntilExpiry = trade.expiresAt 
    ? Math.ceil((new Date(trade.expiresAt).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
    : null;

  const handleExecuteTrade = async () => {
    try {
      const quantity = calculateQuantity();
      
      const order = {
        symbol: trade.ticker,
        qty: quantity,
        side: 'buy' as const,
        type: 'limit' as const,
        limit_price: currentPrice * 1.01, // 1% above current price for limit order
        time_in_force: 'day' as const,
      };

      await executeTrade(order);
      
      if (onExecute) {
        onExecute(trade, quantity);
      }
    } catch (error) {
      console.error('Trade execution failed:', error);
    }
  };

  return (
    <div className={`trade-card bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 ${className}`}>
      {/* Header */}
      <div className="p-6 pb-4">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <h3 className="text-xl font-bold text-gray-900">{trade.ticker}</h3>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCatalystColor(trade.catalystType)}`}>
                {trade.catalystType}
              </span>
              {isExpired && (
                <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  Expired
                </span>
              )}
            </div>
            <p className="text-sm text-gray-600 mb-2">{trade.companyName}</p>
            <div className="flex items-center space-x-2">
              <p className="text-sm font-semibold text-blue-600">{trade.whyNow}</p>
            </div>
          </div>
          
          <div className="text-right">
            <div className="flex items-center space-x-1 mb-1">
              <span className="text-2xl font-bold text-gray-900">
                ${currentPrice.toFixed(2)}
              </span>
              {stockLoading && (
                <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
              )}
            </div>
            {dailyChange !== 0 && (
              <div className={`flex items-center space-x-1 text-sm ${dailyChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {dailyChange >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                <span>{dailyChangePercent >= 0 ? '+' : ''}{dailyChangePercent.toFixed(2)}%</span>
              </div>
            )}
          </div>
        </div>

        {/* AI Thesis */}
        <div className="bg-blue-50 rounded-lg p-3 mb-4">
          <p className="text-sm text-blue-900 font-medium mb-1">AI Trading Thesis:</p>
          <p className="text-sm text-blue-800">{trade.aiThesis}</p>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Entry Price</span>
              <span className="text-sm font-semibold text-gray-900">${trade.entryPrice.toFixed(2)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500 flex items-center">
                <Target className="w-4 h-4 mr-1" />
                Target
              </span>
              <span className="text-sm font-semibold text-green-600">${trade.targetPrice.toFixed(2)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500 flex items-center">
                <Shield className="w-4 h-4 mr-1" />
                Stop Loss
              </span>
              <span className="text-sm font-semibold text-red-600">${trade.stopLoss.toFixed(2)}</span>
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Position Size</span>
              <span className="text-sm font-semibold text-gray-900">{trade.positionSize.toFixed(1)}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Confidence</span>
              <span className={`text-sm font-semibold ${getConfidenceColor(trade.confidence)}`}>
                {(trade.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Risk Level</span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskColor(trade.riskLevel)}`}>
                {trade.riskLevel}
              </span>
            </div>
          </div>
        </div>

        {/* Trade Calculator */}
        <div className="bg-gray-50 rounded-lg p-4 mb-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-semibold text-gray-900">Trade Calculator</h4>
            <div className="flex items-center space-x-2">
              <input
                type="number"
                placeholder="Custom qty"
                value={customQuantity || ''}
                onChange={(e) => setCustomQuantity(e.target.value ? parseInt(e.target.value) : null)}
                className="w-20 px-2 py-1 text-xs border border-gray-300 rounded"
              />
              <span className="text-xs text-gray-500">shares</span>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-xs text-gray-500 mb-1">Quantity</p>
              <p className="text-sm font-semibold text-gray-900">{calculateQuantity()} shares</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Position Value</p>
              <p className="text-sm font-semibold text-gray-900">${positionValue.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">R/R Ratio</p>
              <p className="text-sm font-semibold text-gray-900">{riskRewardRatio.toFixed(1)}:1</p>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4 mt-3 pt-3 border-t border-gray-200">
            <div className="text-center">
              <p className="text-xs text-gray-500 mb-1">Potential Gain</p>
              <p className="text-sm font-semibold text-green-600">+${potentialGain.toLocaleString()}</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-500 mb-1">Potential Loss</p>
              <p className="text-sm font-semibold text-red-600">-${potentialLoss.toLocaleString()}</p>
            </div>
          </div>
        </div>

        {/* Expiry Warning */}
        {daysUntilExpiry && daysUntilExpiry <= 3 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-yellow-600" />
              <p className="text-sm text-yellow-800">
                Trade expires in {daysUntilExpiry} day{daysUntilExpiry !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
        )}

        {/* Execute Button */}
        {showExecuteButton && !isExpired && (
          <div className="space-y-3">
            {executeError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 text-red-500" />
                  <p className="text-sm text-red-600">Execution Error: {executeError}</p>
                </div>
              </div>
            )}
            
            <button
              onClick={handleExecuteTrade}
              disabled={executeLoading || isExpired}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
            >
              {executeLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Executing Trade...</span>
                </>
              ) : (
                <>
                  <DollarSign className="w-4 h-4" />
                  <span>Execute Trade - {calculateQuantity()} shares</span>
                </>
              )}
            </button>
          </div>
        )}

        {/* Details Toggle */}
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="w-full mt-3 text-sm text-blue-600 hover:text-blue-700 underline"
        >
          {showDetails ? 'Hide Details' : 'Show Details'}
        </button>

        {/* Expanded Details */}
        {showDetails && (
          <div className="mt-4 pt-4 border-t border-gray-200 space-y-3">
            <div>
              <p className="text-sm font-medium text-gray-900 mb-1">Expected Returns</p>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-500">Upside</p>
                  <p className="text-sm font-semibold text-green-600">+{trade.expectedUpside.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Downside</p>
                  <p className="text-sm font-semibold text-red-600">{trade.expectedDownside.toFixed(1)}%</p>
                </div>
              </div>
            </div>
            
            <div>
              <p className="text-sm font-medium text-gray-900 mb-1">Time Horizon</p>
              <p className="text-sm text-gray-600">{trade.timeHorizon}</p>
            </div>
            
            <div>
              <p className="text-sm font-medium text-gray-900 mb-1">Created</p>
              <p className="text-sm text-gray-600">
                {new Date(trade.createdAt).toLocaleDateString()} at {new Date(trade.createdAt).toLocaleTimeString()}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TradeCard;