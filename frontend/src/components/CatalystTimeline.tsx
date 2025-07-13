// CatalystTimeline Component - Real FDA, SEC, and Earnings data
import React, { useMemo } from 'react';
import { Calendar, Clock, TrendingUp, AlertTriangle, Building, Scale } from 'lucide-react';
import { useCatalystData } from '../hooks/useRealTimeData';

interface CatalystEvent {
  id: string;
  ticker: string;
  name: string;
  date: Date;
  type: 'Earnings' | 'FDA' | 'M&A' | 'Legal' | 'Macro' | 'SEC_FILING';
  aiProbability: number; // 1-10 scale
  expectedUpside: number; // percentage
  source: string;
  sourceUrl?: string;
  description?: string;
}

interface CatalystTimelineProps {
  ticker: string;
  className?: string;
  maxEvents?: number;
}

const CatalystTimeline: React.FC<CatalystTimelineProps> = ({ 
  ticker, 
  className = '', 
  maxEvents = 10 
}) => {
  const { catalysts, loading, error, lastUpdated } = useCatalystData();

  // Filter catalysts for specific ticker and sort by date
  const tickerCatalysts = useMemo(() => {
    return catalysts
      .filter(catalyst => catalyst.ticker === ticker)
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
      .slice(0, maxEvents);
  }, [catalysts, ticker, maxEvents]);

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'Earnings': return <TrendingUp className="w-4 h-4" />;
      case 'FDA': return <AlertTriangle className="w-4 h-4" />;
      case 'M&A': return <Building className="w-4 h-4" />;
      case 'Legal': return <Scale className="w-4 h-4" />;
      case 'SEC_FILING': return <Building className="w-4 h-4" />;
      case 'Macro': return <TrendingUp className="w-4 h-4" />;
      default: return <Calendar className="w-4 h-4" />;
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'Earnings': return 'bg-blue-500';
      case 'FDA': return 'bg-red-500';
      case 'M&A': return 'bg-green-500';
      case 'Legal': return 'bg-yellow-500';
      case 'SEC_FILING': return 'bg-purple-500';
      case 'Macro': return 'bg-gray-500';
      default: return 'bg-gray-400';
    }
  };

  const formatTimeUntil = (date: Date) => {
    const now = new Date();
    const diffTime = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) {
      return `${Math.abs(diffDays)}d ago`;
    } else if (diffDays === 0) {
      return 'Today';
    } else if (diffDays === 1) {
      return 'Tomorrow';
    } else if (diffDays <= 30) {
      return `${diffDays}d`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const getProbabilityColor = (probability: number) => {
    if (probability >= 8) return 'text-green-600 bg-green-50';
    if (probability >= 6) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  if (loading) {
    return (
      <div className={`catalyst-timeline ${className}`}>
        <div className="flex items-center space-x-2 mb-4">
          <Calendar className="w-5 h-5 text-gray-500" />
          <h3 className="text-lg font-semibold text-gray-900">Catalyst Timeline</h3>
        </div>
        <div className="flex space-x-4 animate-pulse">
          {[1, 2, 3].map(i => (
            <div key={i} className="flex-shrink-0 w-64 h-32 bg-gray-200 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`catalyst-timeline ${className}`}>
        <div className="flex items-center space-x-2 mb-4">
          <Calendar className="w-5 h-5 text-gray-500" />
          <h3 className="text-lg font-semibold text-gray-900">Catalyst Timeline</h3>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">Error loading catalysts: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`catalyst-timeline ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Calendar className="w-5 h-5 text-gray-500" />
          <h3 className="text-lg font-semibold text-gray-900">
            Catalyst Timeline - {ticker}
          </h3>
        </div>
        {lastUpdated && (
          <div className="flex items-center space-x-1 text-sm text-gray-500">
            <Clock className="w-4 h-4" />
            <span>Updated {lastUpdated.toLocaleTimeString()}</span>
          </div>
        )}
      </div>

      {tickerCatalysts.length === 0 ? (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
          <Calendar className="w-8 h-8 text-gray-400 mx-auto mb-2" />
          <p className="text-gray-600">No upcoming catalysts found for {ticker}</p>
          <p className="text-sm text-gray-500 mt-1">
            Check back later or try a different ticker
          </p>
        </div>
      ) : (
        <div className="flex space-x-4 overflow-x-auto pb-4 scrollbar-hide">
          {tickerCatalysts.map((catalyst) => (
            <div
              key={catalyst.id}
              className="flex-shrink-0 w-80 bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow duration-200"
            >
              {/* Event Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <div className={`p-2 rounded-lg ${getEventColor(catalyst.type)} text-white`}>
                    {getEventIcon(catalyst.type)}
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 text-sm">
                      {catalyst.name}
                    </h4>
                    <p className="text-xs text-gray-500 capitalize">
                      {catalyst.type.replace('_', ' ')}
                    </p>
                  </div>
                </div>
                <span className="text-xs text-gray-500">
                  {formatTimeUntil(new Date(catalyst.date))}
                </span>
              </div>

              {/* Event Date */}
              <div className="mb-3">
                <div className="flex items-center space-x-2 text-sm">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-600">
                    {new Date(catalyst.date).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric'
                    })}
                  </span>
                </div>
              </div>

              {/* AI Probability & Expected Upside */}
              <div className="grid grid-cols-2 gap-3 mb-3">
                <div>
                  <p className="text-xs text-gray-500 mb-1">AI Probability</p>
                  <div className={`px-2 py-1 rounded text-xs font-medium ${getProbabilityColor(catalyst.aiProbability)}`}>
                    {catalyst.aiProbability}/10
                  </div>
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Expected Upside</p>
                  <div className="text-sm font-semibold text-green-600">
                    +{catalyst.expectedUpside.toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Description */}
              {catalyst.description && (
                <div className="mb-3">
                  <p className="text-xs text-gray-600 line-clamp-3">
                    {catalyst.description}
                  </p>
                </div>
              )}

              {/* Source */}
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>Source: {catalyst.source}</span>
                {catalyst.sourceUrl && (
                  <a
                    href={catalyst.sourceUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:text-blue-600 underline"
                  >
                    Verify
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CatalystTimeline;