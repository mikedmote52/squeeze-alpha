// AIConsensusBar Component - Real Claude, ChatGPT, Grok analysis via OpenRouter
import React, { useState, useEffect } from 'react';
import { Brain, Zap, MessageCircle, RefreshCw, AlertCircle } from 'lucide-react';
import { useAIAnalysis } from '../hooks/useRealTimeData';

interface AIAgent {
  name: 'Claude' | 'ChatGPT' | 'Grok';
  confidence: number; // 0-1 scale
  reasoning?: string;
  lastUpdated: Date;
  status: 'analyzing' | 'complete' | 'error';
}

interface AIConsensusBarProps {
  symbol: string;
  context: string;
  className?: string;
  autoRefresh?: boolean;
  refreshInterval?: number; // minutes
}

const AIConsensusBar: React.FC<AIConsensusBarProps> = ({
  symbol,
  context,
  className = '',
  autoRefresh = true,
  refreshInterval = 15 // 15 minutes
}) => {
  const { analysis, loading, error, getAnalysis } = useAIAnalysis(symbol, context);
  const [agents, setAgents] = useState<AIAgent[]>([]);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  // Process AI analysis response into agent format
  useEffect(() => {
    if (analysis && analysis.agents) {
      const processedAgents: AIAgent[] = analysis.agents.map((agent: any) => ({
        name: agent.name as 'Claude' | 'ChatGPT' | 'Grok',
        confidence: agent.confidence || 0,
        reasoning: agent.reasoning || '',
        lastUpdated: new Date(agent.lastUpdated || Date.now()),
        status: agent.error ? 'error' : 'complete'
      }));
      
      setAgents(processedAgents);
      setLastRefresh(new Date());
    }
  }, [analysis]);

  // Auto-refresh functionality
  useEffect(() => {
    if (!autoRefresh || !symbol || !context) return;

    const interval = setInterval(() => {
      getAnalysis();
    }, refreshInterval * 60 * 1000);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, symbol, context, getAnalysis]);

  // Initial load
  useEffect(() => {
    if (symbol && context) {
      getAnalysis();
    }
  }, [symbol, context, getAnalysis]);

  const getAgentIcon = (name: string) => {
    switch (name) {
      case 'Claude': return <Brain className="w-4 h-4" />;
      case 'ChatGPT': return <MessageCircle className="w-4 h-4" />;
      case 'Grok': return <Zap className="w-4 h-4" />;
      default: return <Brain className="w-4 h-4" />;
    }
  };

  const getAgentColor = (name: string) => {
    switch (name) {
      case 'Claude': return 'bg-purple-500';
      case 'ChatGPT': return 'bg-green-500';
      case 'Grok': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getConsensusLevel = () => {
    if (agents.length === 0) return 'No Data';
    
    const validAgents = agents.filter(a => a.status === 'complete');
    if (validAgents.length === 0) return 'Analyzing';
    
    const avgConfidence = validAgents.reduce((sum, agent) => sum + agent.confidence, 0) / validAgents.length;
    const variance = validAgents.reduce((sum, agent) => sum + Math.pow(agent.confidence - avgConfidence, 2), 0) / validAgents.length;
    
    if (variance < 0.05) return 'Strong Consensus';
    if (variance < 0.15) return 'Moderate Consensus';
    return 'Mixed Signals';
  };

  const getOverallConfidence = () => {
    const validAgents = agents.filter(a => a.status === 'complete');
    if (validAgents.length === 0) return 0;
    
    return validAgents.reduce((sum, agent) => sum + agent.confidence, 0) / validAgents.length;
  };

  const handleRefresh = () => {
    getAnalysis();
  };

  if (error) {
    return (
      <div className={`ai-consensus-bar ${className}`}>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900">AI Consensus</h3>
          <button
            onClick={handleRefresh}
            className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <p className="text-red-600">Failed to get AI analysis: {error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`ai-consensus-bar ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Brain className="w-5 h-5 text-gray-500" />
          <h3 className="text-lg font-semibold text-gray-900">
            AI Consensus - {symbol}
          </h3>
        </div>
        <div className="flex items-center space-x-2">
          {lastRefresh && (
            <span className="text-xs text-gray-500">
              {lastRefresh.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Consensus Summary */}
      <div className="bg-gray-50 rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-900">
              {getConsensusLevel()}
            </p>
            <p className="text-xs text-gray-500">
              Overall Confidence: {(getOverallConfidence() * 100).toFixed(0)}%
            </p>
          </div>
          <div className="text-right">
            <p className="text-lg font-bold text-gray-900">
              {agents.filter(a => a.status === 'complete').length}/3
            </p>
            <p className="text-xs text-gray-500">Agents Ready</p>
          </div>
        </div>
      </div>

      {/* AI Agents Bar */}
      <div className="space-y-3">
        {loading && agents.length === 0 ? (
          <div className="animate-pulse">
            <div className="flex space-x-2 mb-2">
              {['Claude', 'ChatGPT', 'Grok'].map((name) => (
                <div key={name} className="flex-1 h-12 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
          </div>
        ) : (
          <>
            {/* Visual Consensus Bar */}
            <div className="relative h-12 bg-gray-200 rounded-lg overflow-hidden">
              {agents.map((agent, index) => {
                const width = agent.status === 'complete' ? (agent.confidence * 100) / 3 : 0;
                const left = (100 / 3) * index;
                
                return (
                  <div
                    key={agent.name}
                    className={`absolute top-0 h-full transition-all duration-500 ${getAgentColor(agent.name)} opacity-80`}
                    style={{
                      left: `${left}%`,
                      width: `${width}%`,
                    }}
                  />
                );
              })}
              
              {/* Agent Labels */}
              {['Claude', 'ChatGPT', 'Grok'].map((name, index) => (
                <div
                  key={name}
                  className="absolute top-0 h-full flex items-center justify-center text-white font-medium text-sm"
                  style={{
                    left: `${(100 / 3) * index}%`,
                    width: `${100 / 3}%`,
                  }}
                >
                  <div className="flex items-center space-x-1">
                    {getAgentIcon(name)}
                    <span>{name.charAt(0)}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Individual Agent Details */}
            <div className="grid grid-cols-3 gap-3">
              {['Claude', 'ChatGPT', 'Grok'].map((agentName) => {
                const agent = agents.find(a => a.name === agentName);
                const isLoading = loading && !agent;
                const hasError = agent?.status === 'error';
                
                return (
                  <div
                    key={agentName}
                    className="bg-white border border-gray-200 rounded-lg p-3"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <div className={`p-1 rounded ${getAgentColor(agentName)} text-white`}>
                          {getAgentIcon(agentName)}
                        </div>
                        <span className="text-sm font-medium text-gray-900">
                          {agentName}
                        </span>
                      </div>
                      {isLoading && (
                        <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
                      )}
                    </div>
                    
                    {hasError ? (
                      <div className="text-red-500 text-xs">
                        Analysis failed
                      </div>
                    ) : agent ? (
                      <>
                        <div className="mb-2">
                          <p className="text-lg font-bold text-gray-900">
                            {(agent.confidence * 100).toFixed(0)}%
                          </p>
                          <p className="text-xs text-gray-500">Confidence</p>
                        </div>
                        
                        {agent.reasoning && (
                          <div className="text-xs text-gray-600 line-clamp-3">
                            {agent.reasoning}
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="text-gray-400 text-xs">
                        Waiting for analysis...
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>

      {/* Analysis Context */}
      {context && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-xs text-blue-700">
            <strong>Analysis Context:</strong> {context}
          </p>
        </div>
      )}
    </div>
  );
};

export default AIConsensusBar;