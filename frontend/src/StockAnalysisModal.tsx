import React, { useState, useEffect } from 'react';

interface AIAgent {
  name: string;
  confidence: number;
  reasoning: string;
  lastUpdated: string;
}

interface StockAnalysisModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedStock?: string | null;
}

const StockAnalysisModal: React.FC<StockAnalysisModalProps> = ({ isOpen, onClose, selectedStock }) => {
  const [symbol, setSymbol] = useState('');
  const [question, setQuestion] = useState('');
  const [analysis, setAnalysis] = useState<AIAgent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-populate symbol and trigger analysis when selectedStock changes
  useEffect(() => {
    if (selectedStock && isOpen) {
      setSymbol(selectedStock);
      setQuestion(`Detailed analysis of ${selectedStock}: Should I buy, sell, or hold? What's the price target and main catalysts?`);
      // Auto-trigger analysis for clicked stocks
      setLoading(true);
      setError(null);
      setAnalysis([]);
      
      const autoAnalyze = async () => {
        try {
          const response = await fetch('http://localhost:8000/api/ai-analysis', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              symbol: selectedStock,
              context: `Detailed investment analysis of ${selectedStock}: Current position analysis, should I buy more, sell, or hold? What's the price target for next 3-6 months? What are the main catalysts and risks?`
            }),
          });

          if (response.ok) {
            const data = await response.json();
            setAnalysis(data.agents || []);
          } else {
            setError('Failed to get AI analysis');
          }
        } catch (err) {
          setError('Error connecting to AI analysis service');
        } finally {
          setLoading(false);
        }
      };
      
      autoAnalyze();
    }
  }, [selectedStock, isOpen]);

  const getAIAnalysis = async () => {
    if (!symbol.trim()) {
      setError('Please enter a stock symbol');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/ai-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: symbol.toUpperCase(),
          context: question || `Analyze ${symbol} for investment potential`
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setAnalysis(data.agents || []);
      } else {
        setError('Failed to get AI analysis');
      }
    } catch (err) {
      setError('Error connecting to AI analysis service');
    } finally {
      setLoading(false);
    }
  };

  const commonQuestions = [
    "Should I buy this stock now?",
    "What's the price target for next 6 months?",
    "What are the main risks with this investment?",
    "How does this compare to sector peers?",
    "What catalysts could drive the price up?",
    "Is this a good long-term hold?",
    "What's the technical analysis saying?",
    "Should I add more to my position?"
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">🤖 AI Stock Analysis</h2>
            <p className="text-gray-600">Get insights from Claude, ChatGPT, and Grok</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Input Section */}
        <div className="p-6 border-b bg-gray-50">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Stock Symbol
              </label>
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                placeholder="e.g., NVDA, TSLA, AAPL"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent uppercase"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Question (Optional)
              </label>
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask anything about this stock..."
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Quick Questions */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quick Questions
              </label>
              <div className="grid grid-cols-2 gap-2">
                {commonQuestions.map((q, index) => (
                  <button
                    key={index}
                    onClick={() => setQuestion(q)}
                    className="text-left p-2 text-sm bg-white border border-gray-200 rounded hover:bg-blue-50 hover:border-blue-300 transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={getAIAnalysis}
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {loading ? 'Analyzing...' : 'Get AI Analysis'}
            </button>
          </div>
        </div>

        {/* Results Section */}
        <div className="p-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p className="text-red-600">{error}</p>
            </div>
          )}

          {loading && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Getting insights from AI agents...</p>
            </div>
          )}

          {analysis.length > 0 && (
            <div className="space-y-6">
              <div className="flex items-center space-x-2 mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Analysis for {symbol}</h3>
                <span className="text-sm text-gray-500">
                  • {new Date().toLocaleTimeString()}
                </span>
              </div>

              {analysis.map((agent, index) => (
                <div key={index} className="bg-gray-50 rounded-lg p-6 border">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-bold text-sm">
                          {agent.name === 'Claude' ? '🤖' : 
                           agent.name === 'ChatGPT' ? '💬' : '🚀'}
                        </span>
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900">{agent.name}</h4>
                        <div className="flex items-center space-x-2">
                          <div className="text-sm text-gray-500">Confidence:</div>
                          <div className={`text-sm font-medium ${
                            agent.confidence >= 0.8 ? 'text-green-600' :
                            agent.confidence >= 0.6 ? 'text-yellow-600' : 'text-red-600'
                          }`}>
                            {Math.round(agent.confidence * 100)}%
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Confidence Bar */}
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          agent.confidence >= 0.8 ? 'bg-green-500' :
                          agent.confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${agent.confidence * 100}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <p className="text-gray-700 leading-relaxed">{agent.reasoning}</p>
                </div>
              ))}

              {/* Consensus Summary */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h4 className="font-semibold text-blue-900 mb-2">🎯 AI Consensus</h4>
                <div className="text-blue-800">
                  Average Confidence: {Math.round((analysis.reduce((sum, agent) => sum + agent.confidence, 0) / analysis.length) * 100)}%
                </div>
                <div className="text-sm text-blue-600 mt-2">
                  {analysis.length} AI agents analyzed {symbol}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StockAnalysisModal;