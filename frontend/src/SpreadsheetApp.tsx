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

interface AIRecommendation {
  symbol: string;
  action: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  reasoning: string;
  target_price?: number;
  stop_loss?: number;
  position_size?: number;
  time_horizon?: string;
}

interface PortfolioSummary {
  total_value: number;
  total_pl: number;
  day_pl: number;
  winners: number;
  losers: number;
  win_rate: number;
  ai_score: number;
  recommendations_count: number;
}

interface NewOpportunity {
  symbol: string;
  current_price: number;
  target_price: number;
  confidence: number;
  discovery_reason: string;
  catalyst_type: string;
  expected_upside: number;
  time_horizon: string;
  ai_consensus: string;
}

interface PortfolioSwap {
  new_symbol: string;
  replace_symbol: string;
  new_opportunity: NewOpportunity;
  current_position: Position;
  swap_reasoning: string;
  expected_improvement: number;
  confidence: number;
}

type SortField = 'symbol' | 'qty' | 'market_value' | 'current_price' | 'unrealized_pl' | 'unrealized_plpc' | 'ai_action' | 'ai_confidence';
type FilterType = 'all' | 'winners' | 'losers' | 'buy_recs' | 'sell_recs' | 'hold_recs';

const SpreadsheetApp: React.FC = () => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [recommendations, setRecommendations] = useState<Map<string, AIRecommendation>>(new Map());
  const [portfolioSummary, setPortfolioSummary] = useState<PortfolioSummary | null>(null);
  const [newOpportunities, setNewOpportunities] = useState<NewOpportunity[]>([]);
  const [portfolioSwaps, setPortfolioSwaps] = useState<PortfolioSwap[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingAI, setLoadingAI] = useState(false);
  const [loadingOpportunities, setLoadingOpportunities] = useState(false);
  const [showAIAnalysis, setShowAIAnalysis] = useState(false);
  const [selectedStock, setSelectedStock] = useState<string | null>(null);
  const [sortField, setSortField] = useState<SortField>('unrealized_pl');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [filter, setFilter] = useState<FilterType>('all');
  const [refreshTime, setRefreshTime] = useState<Date>(new Date());
  const [usageStats, setUsageStats] = useState({ today_calls: 0, remaining_calls: 50, today_cost: 0 });

  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      const [positionsRes, performanceRes] = await Promise.all([
        fetch('http://localhost:8000/api/portfolio/positions'),
        fetch('http://localhost:8000/api/portfolio/performance')
      ]);

      if (positionsRes.ok && performanceRes.ok) {
        const posData = await positionsRes.json();
        const perfData = await performanceRes.json();
        
        const positionsList = posData.positions || [];
        setPositions(positionsList);

        // Calculate portfolio summary
        const totalPL = positionsList.reduce((sum: number, pos: Position) => sum + pos.unrealized_pl, 0);
        const winners = positionsList.filter((pos: Position) => pos.unrealized_pl > 0);
        const losers = positionsList.filter((pos: Position) => pos.unrealized_pl < 0);

        setPortfolioSummary({
          total_value: perfData.totalEquity || 0,
          total_pl: totalPL,
          day_pl: perfData.dayPL || 0,
          winners: winners.length,
          losers: losers.length,
          win_rate: positionsList.length > 0 ? (winners.length / positionsList.length) * 100 : 0,
          ai_score: 0, // Will be calculated after AI analysis
          recommendations_count: 0
        });

        setRefreshTime(new Date());
      }
    } catch (error) {
      console.error('Failed to fetch portfolio data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAIRecommendations = async () => {
    if (positions.length === 0) return;
    
    setLoadingAI(true);
    const newRecommendations = new Map<string, AIRecommendation>();

    try {
      // Get AI analysis for each position
      for (const position of positions) {
        try {
          const response = await fetch('http://localhost:8000/api/ai-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              symbol: position.symbol,
              context: `Current position: ${position.qty} shares at $${position.avg_entry_price} avg cost. Current price: $${position.current_price}. P&L: ${position.unrealized_pl >= 0 ? '+' : ''}$${position.unrealized_pl.toFixed(2)} (${position.unrealized_plpc.toFixed(1)}%). Provide specific action recommendation: BUY more, SELL some/all, or HOLD. Include confidence score, reasoning, and specific targets.`
            })
          });

          if (response.ok) {
            const aiData = await response.json();
            if (aiData.agents && aiData.agents.length > 0) {
              // Process AI responses to extract recommendation
              const avgConfidence = aiData.agents.reduce((sum: number, agent: any) => sum + agent.confidence, 0) / aiData.agents.length;
              const combinedReasoning = aiData.agents.map((agent: any) => `${agent.name}: ${agent.reasoning}`).join('\n\n');
              
              // Determine action based on AI analysis
              let action: 'BUY' | 'SELL' | 'HOLD' = 'HOLD';
              if (position.unrealized_plpc > 20 || combinedReasoning.toLowerCase().includes('take profit')) {
                action = 'SELL';
              } else if (position.unrealized_plpc < -10 || combinedReasoning.toLowerCase().includes('buy more')) {
                action = 'BUY';
              }

              newRecommendations.set(position.symbol, {
                symbol: position.symbol,
                action,
                confidence: avgConfidence,
                reasoning: combinedReasoning,
                target_price: position.current_price * (action === 'BUY' ? 1.15 : 1.05),
                stop_loss: position.current_price * 0.9,
                position_size: action === 'BUY' ? Math.min(position.qty * 0.25, 10) : Math.min(position.qty * 0.5, position.qty),
                time_horizon: '2-4 weeks'
              });
            }
          }
        } catch (error) {
          console.error(`Failed to get AI recommendation for ${position.symbol}:`, error);
        }
      }

      setRecommendations(newRecommendations);
      
      // Update portfolio summary with AI data
      if (portfolioSummary) {
        const aiScore = Array.from(newRecommendations.values())
          .reduce((sum, rec) => sum + rec.confidence, 0) / newRecommendations.size * 100;
        
        setPortfolioSummary({
          ...portfolioSummary,
          ai_score: aiScore,
          recommendations_count: newRecommendations.size
        });
      }

    } catch (error) {
      console.error('Failed to fetch AI recommendations:', error);
    } finally {
      setLoadingAI(false);
    }
  };

  const fetchNewOpportunities = async () => {
    setLoadingOpportunities(true);
    try {
      // Get opportunities from catalyst discovery and alpha discovery systems
      const [catalystRes, alphaRes] = await Promise.all([
        fetch('http://localhost:8000/api/catalyst-discovery'),
        fetch('http://localhost:8000/api/alpha-discovery')
      ]);

      const opportunities: NewOpportunity[] = [];

      // Process catalyst opportunities
      if (catalystRes.ok) {
        const catalystData = await catalystRes.json();
        if (catalystData.catalysts) {
          for (const catalyst of catalystData.catalysts) {
            // Skip if we already own this stock
            if (!positions.find(pos => pos.symbol === catalyst.ticker)) {
              // Get current price for the opportunity
              try {
                const stockRes = await fetch(`http://localhost:8000/api/stocks/${catalyst.ticker}`);
                if (stockRes.ok) {
                  const stockData = await stockRes.json();
                  
                  opportunities.push({
                    symbol: catalyst.ticker,
                    current_price: stockData.currentPrice || 0,
                    target_price: stockData.currentPrice * 1.2, // 20% upside estimate
                    confidence: catalyst.aiProbability ? catalyst.aiProbability / 10 : 0.8,
                    discovery_reason: catalyst.description || 'Catalyst opportunity detected',
                    catalyst_type: catalyst.type || 'CATALYST',
                    expected_upside: catalyst.expectedUpside || 20,
                    time_horizon: '2-6 weeks',
                    ai_consensus: `Catalyst-driven opportunity: ${catalyst.type}`
                  });
                }
              } catch (error) {
                console.error(`Failed to get stock data for ${catalyst.ticker}:`, error);
              }
            }
          }
        }
      }

      // Process alpha opportunities
      if (alphaRes.ok) {
        const alphaData = await alphaRes.json();
        if (alphaData.opportunities) {
          for (const alpha of alphaData.opportunities) {
            // Skip if we already own this stock or already added from catalysts
            if (!positions.find(pos => pos.symbol === alpha.ticker) && 
                !opportunities.find(opp => opp.symbol === alpha.ticker)) {
              
              opportunities.push({
                symbol: alpha.ticker,
                current_price: alpha.current_price || 0,
                target_price: alpha.target_price || alpha.current_price * 1.15,
                confidence: alpha.confidence_score || 0.75,
                discovery_reason: alpha.discovery_reason || 'Alpha opportunity detected',
                catalyst_type: alpha.catalyst_type || 'TECHNICAL',
                expected_upside: alpha.target_price ? 
                  ((alpha.target_price - alpha.current_price) / alpha.current_price) * 100 : 15,
                time_horizon: '1-4 weeks',
                ai_consensus: alpha.rationale || 'Technical analysis opportunity'
              });
            }
          }
        }
      }

      // Sort by confidence and expected upside
      opportunities.sort((a, b) => (b.confidence * b.expected_upside) - (a.confidence * a.expected_upside));
      
      setNewOpportunities(opportunities.slice(0, 5)); // Top 5 opportunities

    } catch (error) {
      console.error('Failed to fetch new opportunities:', error);
    } finally {
      setLoadingOpportunities(false);
    }
  };

  const generatePortfolioSwaps = async () => {
    if (newOpportunities.length === 0 || positions.length === 0) return;

    try {
      const swaps: PortfolioSwap[] = [];
      
      // Find weak performers (negative P&L or SELL recommendations)
      const weakPositions = positions.filter(pos => 
        pos.unrealized_pl < 0 || recommendations.get(pos.symbol)?.action === 'SELL'
      );

      // For each new opportunity, see if it makes sense to swap with a weak position
      for (const opportunity of newOpportunities.slice(0, 3)) {
        for (const weakPos of weakPositions.slice(0, 2)) {
          
          // Get AI analysis for the swap recommendation
          try {
            const response = await fetch('http://localhost:8000/api/ai-analysis', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                symbol: opportunity.symbol,
                context: `Compare ${opportunity.symbol} (new opportunity: ${opportunity.discovery_reason}) vs ${weakPos.symbol} (current position: ${weakPos.qty} shares, P&L: ${weakPos.unrealized_pl.toFixed(2)}). Should we swap ${weakPos.symbol} for ${opportunity.symbol}? Consider: 1) ${opportunity.symbol} potential upside: ${opportunity.expected_upside}%, 2) ${weakPos.symbol} current performance: ${weakPos.unrealized_plpc.toFixed(1)}%, 3) Market conditions and timing. Provide swap recommendation with confidence.`
              })
            });

            if (response.ok) {
              const aiData = await response.json();
              const avgConfidence = aiData.agents.reduce((sum: number, agent: any) => sum + agent.confidence, 0) / aiData.agents.length;
              const combinedReasoning = aiData.agents.map((agent: any) => `${agent.name}: ${agent.reasoning}`).join('\n\n');
              
              // Only suggest swap if AI is confident (>70%) and it makes financial sense
              if (avgConfidence > 0.7 && opportunity.expected_upside > Math.abs(weakPos.unrealized_plpc)) {
                
                const expectedImprovement = opportunity.expected_upside + Math.abs(weakPos.unrealized_plpc);
                
                swaps.push({
                  new_symbol: opportunity.symbol,
                  replace_symbol: weakPos.symbol,
                  new_opportunity: opportunity,
                  current_position: weakPos,
                  swap_reasoning: combinedReasoning,
                  expected_improvement: expectedImprovement,
                  confidence: avgConfidence
                });
              }
            }
          } catch (error) {
            console.error(`Failed to analyze swap ${opportunity.symbol} for ${weakPos.symbol}:`, error);
          }
        }
      }

      // Sort swaps by expected improvement and confidence
      swaps.sort((a, b) => (b.expected_improvement * b.confidence) - (a.expected_improvement * a.confidence));
      setPortfolioSwaps(swaps.slice(0, 3)); // Top 3 swap recommendations

    } catch (error) {
      console.error('Failed to generate portfolio swaps:', error);
    }
  };

  const executeSwap = async (swap: PortfolioSwap) => {
    try {
      // First sell the current position
      const sellResponse = await fetch('http://localhost:8000/api/trades/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: swap.replace_symbol,
          qty: swap.current_position.qty,
          side: 'sell',
          type: 'market',
          time_in_force: 'day'
        })
      });

      if (sellResponse.ok) {
        // Calculate how many shares of new stock to buy with proceeds
        const proceeds = swap.current_position.market_value * 0.99; // Account for fees
        const newShares = Math.floor(proceeds / swap.new_opportunity.current_price);

        // Buy the new position
        const buyResponse = await fetch('http://localhost:8000/api/trades/execute', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            symbol: swap.new_symbol,
            qty: newShares,
            side: 'buy',
            type: 'market',
            time_in_force: 'day'
          })
        });

        if (buyResponse.ok) {
          alert(`Swap executed: Sold ${swap.current_position.qty} shares of ${swap.replace_symbol}, bought ${newShares} shares of ${swap.new_symbol}`);
          
          // Log the swap for system learning
          await fetch('http://localhost:8000/api/trades/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              timestamp: new Date().toISOString(),
              action: 'PORTFOLIO_SWAP',
              sell_symbol: swap.replace_symbol,
              sell_quantity: swap.current_position.qty,
              buy_symbol: swap.new_symbol,
              buy_quantity: newShares,
              reasoning: swap.swap_reasoning,
              expected_improvement: swap.expected_improvement,
              confidence: swap.confidence
            })
          });

          // Refresh data after swap
          setTimeout(() => {
            fetchPortfolioData();
          }, 3000);
        } else {
          throw new Error('Failed to buy new position');
        }
      } else {
        throw new Error('Failed to sell current position');
      }
    } catch (error) {
      console.error('Swap execution error:', error);
      alert('Swap execution failed. Please try again.');
    }
  };

  useEffect(() => {
    fetchPortfolioData();
    fetchUsageStats();
  }, []);

  useEffect(() => {
    if (positions.length > 0) {
      fetchAIRecommendations();
      fetchNewOpportunities();
    }
  }, [positions]);

  useEffect(() => {
    if (newOpportunities.length > 0 && recommendations.size > 0) {
      generatePortfolioSwaps();
    }
  }, [newOpportunities, recommendations]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const handleExecuteRecommendation = async (symbol: string, action: 'BUY' | 'SELL', quantity: number) => {
    try {
      const response = await fetch('http://localhost:8000/api/trades/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          qty: quantity,
          side: action.toLowerCase(),
          type: 'market',
          time_in_force: 'day'
        })
      });

      if (response.ok) {
        alert(`${action} order submitted for ${quantity} shares of ${symbol}`);
        // Refresh data after trade
        setTimeout(() => {
          fetchPortfolioData();
        }, 2000);
      } else {
        throw new Error('Trade execution failed');
      }
    } catch (error) {
      console.error('Trade execution error:', error);
      alert('Trade execution failed. Please try again.');
    }
  };

  const fetchUsageStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/usage_stats');
      if (response.ok) {
        const data = await response.json();
        setUsageStats(data.stats || { today_calls: 0, remaining_calls: 50, today_cost: 0 });
      }
    } catch (error) {
      console.log('Usage stats fetch failed (non-critical):', error);
    }
  };

  const handleRefreshStock = async (symbol: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/force_refresh/${symbol}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        const data = await response.json();
        alert(`✅ ${symbol} analysis refreshed successfully`);
        // Refresh the AI recommendations after getting fresh analysis
        fetchAIRecommendations();
        // Update usage stats
        fetchUsageStats();
      } else {
        const errorData = await response.json();
        alert(`❌ Refresh failed: ${errorData.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Refresh error:', error);
      alert('❌ Failed to refresh analysis. Please try again.');
    }
  };

  const handleValidateThesis = async (symbol: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/validate_thesis/${symbol}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        const data = await response.json();
        const statusEmoji: Record<string, string> = {
          'CONFIRMED': '✅',
          'WEAKENED': '⚠️', 
          'INVALIDATED': '❌',
          'UNKNOWN': '❓'
        };
        const emoji = statusEmoji[data.status] || '❓';
        
        alert(`${emoji} ${symbol} thesis: ${data.status}\n\n${data.explanation}`);
        // Update usage stats
        fetchUsageStats();
      } else {
        const errorData = await response.json();
        alert(`❌ Validation failed: ${errorData.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Validation error:', error);
      alert('❌ Failed to validate thesis. Please try again.');
    }
  };

  const getFilteredAndSortedPositions = () => {
    let filtered = [...positions];

    // Apply filters
    switch (filter) {
      case 'winners':
        filtered = filtered.filter(pos => pos.unrealized_pl > 0);
        break;
      case 'losers':
        filtered = filtered.filter(pos => pos.unrealized_pl < 0);
        break;
      case 'buy_recs':
        filtered = filtered.filter(pos => recommendations.get(pos.symbol)?.action === 'BUY');
        break;
      case 'sell_recs':
        filtered = filtered.filter(pos => recommendations.get(pos.symbol)?.action === 'SELL');
        break;
      case 'hold_recs':
        filtered = filtered.filter(pos => recommendations.get(pos.symbol)?.action === 'HOLD');
        break;
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue: any, bValue: any;
      
      switch (sortField) {
        case 'ai_action':
          aValue = recommendations.get(a.symbol)?.action || 'HOLD';
          bValue = recommendations.get(b.symbol)?.action || 'HOLD';
          break;
        case 'ai_confidence':
          aValue = recommendations.get(a.symbol)?.confidence || 0;
          bValue = recommendations.get(b.symbol)?.confidence || 0;
          break;
        default:
          aValue = a[sortField];
          bValue = b[sortField];
      }

      if (typeof aValue === 'string') {
        return sortDirection === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
      }
      
      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
    });

    return filtered;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading portfolio data...</p>
        </div>
      </div>
    );
  }

  const filteredPositions = getFilteredAndSortedPositions();

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">📊 AI Portfolio Management</h1>
              <p className="text-gray-600">Real-time analysis and recommendations</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowAIAnalysis(true)}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
              >
                🤖 Analyze Any Stock
              </button>
              <button
                onClick={() => { fetchPortfolioData(); fetchAIRecommendations(); fetchUsageStats(); }}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                disabled={loadingAI}
              >
                {loadingAI ? 'Updating AI...' : '🔄 Refresh'}
              </button>
              <div className="text-right text-sm">
                <div className="text-gray-500">Last Updated</div>
                <div className="font-medium">{refreshTime.toLocaleTimeString()}</div>
              </div>
              <div className="text-right bg-gray-50 rounded-lg p-3 border">
                <div className="text-sm text-gray-500">API Usage Today</div>
                <div className="text-lg font-bold text-blue-600">{usageStats.today_calls}/50</div>
                <div className="text-xs text-gray-500">${usageStats.today_cost.toFixed(3)} spent</div>
                <div className="text-xs text-green-600">{usageStats.remaining_calls} remaining</div>
              </div>
            </div>
          </div>

          {/* Portfolio Summary */}
          {portfolioSummary && (
            <div className="grid grid-cols-6 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-gray-900">${portfolioSummary.total_value.toLocaleString()}</div>
                <div className="text-sm text-gray-500">Total Value</div>
              </div>
              <div>
                <div className={`text-2xl font-bold ${portfolioSummary.total_pl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {portfolioSummary.total_pl >= 0 ? '+' : ''}${portfolioSummary.total_pl.toFixed(2)}
                </div>
                <div className="text-sm text-gray-500">Total P&L</div>
              </div>
              <div>
                <div className={`text-2xl font-bold ${portfolioSummary.day_pl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {portfolioSummary.day_pl >= 0 ? '+' : ''}${portfolioSummary.day_pl.toFixed(2)}
                </div>
                <div className="text-sm text-gray-500">Today's P&L</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-600">{portfolioSummary.win_rate.toFixed(0)}%</div>
                <div className="text-sm text-gray-500">Win Rate</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-purple-600">{portfolioSummary.ai_score.toFixed(0)}%</div>
                <div className="text-sm text-gray-500">AI Confidence</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-orange-600">{portfolioSummary.recommendations_count}</div>
                <div className="text-sm text-gray-500">AI Recommendations</div>
              </div>
            </div>
          )}
        </div>

        {/* New Opportunities Section */}
        {newOpportunities.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-green-600">🎯 AI-Discovered Opportunities</h2>
              <span className="text-sm text-gray-500">
                {loadingOpportunities ? 'Analyzing market...' : `${newOpportunities.length} opportunities found`}
              </span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {newOpportunities.map((opportunity, index) => (
                <div key={opportunity.symbol} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-bold text-lg text-gray-900">{opportunity.symbol}</h3>
                      <div className="text-sm text-gray-600">{opportunity.catalyst_type}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-500">Confidence</div>
                      <div className="font-bold text-green-600">{(opportunity.confidence * 100).toFixed(0)}%</div>
                    </div>
                  </div>
                  
                  <div className="space-y-2 mb-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Current:</span>
                      <span className="font-medium">${opportunity.current_price.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Target:</span>
                      <span className="font-medium text-green-600">${opportunity.target_price.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Upside:</span>
                      <span className="font-bold text-green-600">+{opportunity.expected_upside.toFixed(1)}%</span>
                    </div>
                  </div>
                  
                  <div className="text-xs text-gray-700 mb-3 line-clamp-3">
                    {opportunity.discovery_reason}
                  </div>
                  
                  <button
                    onClick={() => {
                      setSelectedStock(opportunity.symbol);
                      setShowAIAnalysis(true);
                    }}
                    className="w-full bg-green-600 text-white py-2 px-3 rounded text-sm hover:bg-green-700"
                  >
                    Analyze & Consider
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Portfolio Swap Recommendations */}
        {portfolioSwaps.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-orange-600">🔄 AI Portfolio Swap Recommendations</h2>
              <span className="text-sm text-gray-500">{portfolioSwaps.length} swap opportunities</span>
            </div>
            
            <div className="space-y-4">
              {portfolioSwaps.map((swap, index) => (
                <div key={`${swap.new_symbol}-${swap.replace_symbol}`} 
                     className="border rounded-lg p-4 bg-orange-50">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center space-x-4">
                      <div className="text-center">
                        <div className="font-bold text-red-600">{swap.replace_symbol}</div>
                        <div className="text-xs text-gray-600">SELL</div>
                        <div className="text-sm font-medium">
                          {swap.current_position.qty} shares
                        </div>
                        <div className="text-sm text-red-600">
                          {swap.current_position.unrealized_plpc.toFixed(1)}% P&L
                        </div>
                      </div>
                      
                      <div className="text-2xl text-gray-400">→</div>
                      
                      <div className="text-center">
                        <div className="font-bold text-green-600">{swap.new_symbol}</div>
                        <div className="text-xs text-gray-600">BUY</div>
                        <div className="text-sm font-medium">
                          ${swap.new_opportunity.current_price.toFixed(2)}
                        </div>
                        <div className="text-sm text-green-600">
                          +{swap.new_opportunity.expected_upside.toFixed(1)}% target
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-sm text-gray-600">Expected Improvement</div>
                      <div className="text-lg font-bold text-green-600">
                        +{swap.expected_improvement.toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-600">
                        AI Confidence: {(swap.confidence * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-sm text-gray-700 mb-3">
                    <strong>AI Reasoning:</strong> {swap.swap_reasoning.substring(0, 200)}...
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => executeSwap(swap)}
                      className="bg-orange-600 text-white px-4 py-2 rounded text-sm hover:bg-orange-700"
                    >
                      Execute Swap
                    </button>
                    <button
                      onClick={() => {
                        setSelectedStock(swap.new_symbol);
                        setShowAIAnalysis(true);
                      }}
                      className="bg-gray-600 text-white px-4 py-2 rounded text-sm hover:bg-gray-700"
                    >
                      Full Analysis
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex items-center space-x-4">
            <span className="font-medium text-gray-700">Filter:</span>
            {[
              { key: 'all', label: 'All Positions' },
              { key: 'winners', label: 'Winners' },
              { key: 'losers', label: 'Losers' },
              { key: 'buy_recs', label: 'AI: Buy' },
              { key: 'sell_recs', label: 'AI: Sell' },
              { key: 'hold_recs', label: 'AI: Hold' }
            ].map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setFilter(key as FilterType)}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  filter === key 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Spreadsheet Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  {[
                    { key: 'symbol', label: 'Symbol' },
                    { key: 'qty', label: 'Shares' },
                    { key: 'current_price', label: 'Price' },
                    { key: 'market_value', label: 'Value' },
                    { key: 'unrealized_pl', label: 'P&L ($)' },
                    { key: 'unrealized_plpc', label: 'P&L (%)' },
                    { key: 'ai_action', label: 'AI Action' },
                    { key: 'ai_confidence', label: 'AI Confidence' },
                    { key: 'actions', label: 'Execute' }
                  ].map(({ key, label }) => (
                    <th
                      key={key}
                      onClick={() => key !== 'actions' && handleSort(key as SortField)}
                      className={`px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider ${
                        key !== 'actions' ? 'cursor-pointer hover:bg-gray-100' : ''
                      }`}
                    >
                      <div className="flex items-center space-x-1">
                        <span>{label}</span>
                        {sortField === key && (
                          <span>{sortDirection === 'asc' ? '↑' : '↓'}</span>
                        )}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredPositions.map((position) => {
                  const recommendation = recommendations.get(position.symbol);
                  const isProfit = position.unrealized_pl >= 0;
                  
                  return (
                    <tr
                      key={position.symbol}
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => {
                        setSelectedStock(position.symbol);
                        setShowAIAnalysis(true);
                      }}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-lg font-bold text-gray-900">{position.symbol}</div>
                        <div className="text-sm text-gray-500">Avg: ${position.avg_entry_price.toFixed(2)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {position.qty.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${position.current_price.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${position.market_value.toFixed(2)}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm font-bold ${isProfit ? 'text-green-600' : 'text-red-600'}`}>
                        {isProfit ? '+' : ''}${position.unrealized_pl.toFixed(2)}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm font-bold ${isProfit ? 'text-green-600' : 'text-red-600'}`}>
                        {isProfit ? '+' : ''}{position.unrealized_plpc.toFixed(1)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {recommendation ? (
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            recommendation.action === 'BUY' ? 'bg-green-100 text-green-800' :
                            recommendation.action === 'SELL' ? 'bg-red-100 text-red-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {recommendation.action}
                          </span>
                        ) : (
                          <span className="text-gray-400">Loading...</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {recommendation ? (
                          <div className="flex items-center">
                            <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                              <div
                                className={`h-2 rounded-full ${
                                  recommendation.confidence >= 0.8 ? 'bg-green-500' :
                                  recommendation.confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                                }`}
                                style={{ width: `${recommendation.confidence * 100}%` }}
                              />
                            </div>
                            <span>{(recommendation.confidence * 100).toFixed(0)}%</span>
                          </div>
                        ) : (
                          <span className="text-gray-400">...</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                        {recommendation && (
                          <div className="flex space-x-1">
                            {recommendation.action === 'BUY' && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleExecuteRecommendation(position.symbol, 'BUY', recommendation.position_size || 1);
                                }}
                                className="bg-green-600 text-white px-2 py-1 rounded text-xs hover:bg-green-700"
                              >
                                Buy More
                              </button>
                            )}
                            {recommendation.action === 'SELL' && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleExecuteRecommendation(position.symbol, 'SELL', recommendation.position_size || 1);
                                }}
                                className="bg-red-600 text-white px-2 py-1 rounded text-xs hover:bg-red-700"
                              >
                                Take Profit
                              </button>
                            )}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedStock(position.symbol);
                                setShowAIAnalysis(true);
                              }}
                              className="bg-purple-600 text-white px-2 py-1 rounded text-xs hover:bg-purple-700"
                            >
                              Details
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleRefreshStock(position.symbol);
                              }}
                              className="bg-blue-600 text-white px-2 py-1 rounded text-xs hover:bg-blue-700"
                            >
                              🔄 Refresh
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleValidateThesis(position.symbol);
                              }}
                              className="bg-orange-600 text-white px-2 py-1 rounded text-xs hover:bg-orange-700"
                            >
                              ✓ Validate
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* AI Analysis for specific stock */}
        {selectedStock && (
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold mb-4">🤖 AI Analysis for {selectedStock}</h3>
            {recommendations.get(selectedStock) ? (
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="mb-2">
                  <span className="font-semibold">Recommendation: </span>
                  <span className={`font-bold ${
                    recommendations.get(selectedStock)?.action === 'BUY' ? 'text-green-600' :
                    recommendations.get(selectedStock)?.action === 'SELL' ? 'text-red-600' :
                    'text-gray-600'
                  }`}>
                    {recommendations.get(selectedStock)?.action}
                  </span>
                  <span className="ml-4 text-sm text-gray-600">
                    Confidence: {((recommendations.get(selectedStock)?.confidence || 0) * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="text-sm text-gray-700 whitespace-pre-line">
                  {recommendations.get(selectedStock)?.reasoning}
                </div>
              </div>
            ) : (
              <div className="text-gray-500">Loading AI analysis...</div>
            )}
          </div>
        )}
      </div>

      {/* Stock Analysis Modal */}
      <StockAnalysisModal
        isOpen={showAIAnalysis}
        onClose={() => {
          setShowAIAnalysis(false);
          setSelectedStock(null);
        }}
        selectedStock={selectedStock}
      />
    </div>
  );
};

export default SpreadsheetApp;