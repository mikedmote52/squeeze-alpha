// Real-time data hooks for live trading app
import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient, realtimeSocket } from '../api/client';

// Real-time catalyst data hook
export function useCatalystData() {
  const [catalysts, setCatalysts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchCatalysts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get real catalysts from your backend
      const [catalystData, fdaData, secData] = await Promise.all([
        apiClient.getCatalystOpportunities(),
        apiClient.getFDACatalysts(),
        apiClient.getSECCatalysts(),
      ]);
      
      // Combine and format real data
      const allCatalysts = [
        ...catalystData.catalysts || [],
        ...fdaData.catalysts || [],
        ...secData.catalysts || [],
      ];
      
      setCatalysts(allCatalysts);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch catalysts');
      console.error('Catalyst data error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCatalysts();
    
    // Set up real-time updates
    const handleRealtimeUpdate = (event: CustomEvent) => {
      const { type, data } = event.detail;
      if (type === 'catalyst_update') {
        setCatalysts(prev => {
          const updated = [...prev];
          const index = updated.findIndex(c => c.id === data.id);
          if (index >= 0) {
            updated[index] = { ...updated[index], ...data };
          } else {
            updated.push(data);
          }
          return updated;
        });
        setLastUpdated(new Date());
      }
    };

    window.addEventListener('realtimeUpdate', handleRealtimeUpdate as EventListener);
    
    // Refresh every 5 minutes
    const interval = setInterval(fetchCatalysts, 5 * 60 * 1000);

    return () => {
      window.removeEventListener('realtimeUpdate', handleRealtimeUpdate as EventListener);
      clearInterval(interval);
    };
  }, [fetchCatalysts]);

  return { catalysts, loading, error, lastUpdated, refetch: fetchCatalysts };
}

// Real-time portfolio data hook
export function usePortfolioData() {
  const [positions, setPositions] = useState<any[]>([]);
  const [performance, setPerformance] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPortfolio = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get real Alpaca portfolio data
      const [positionsData, performanceData] = await Promise.all([
        apiClient.getPortfolioPositions(),
        apiClient.getPortfolioPerformance(),
      ]);
      
      setPositions(positionsData.positions || []);
      setPerformance(performanceData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch portfolio');
      console.error('Portfolio data error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPortfolio();
    
    // Real-time portfolio updates
    const handleRealtimeUpdate = (event: CustomEvent) => {
      const { type, data } = event.detail;
      if (type === 'portfolio_update') {
        setPositions(data.positions || []);
        setPerformance(data.performance);
      }
    };

    window.addEventListener('realtimeUpdate', handleRealtimeUpdate as EventListener);
    
    // Refresh every 30 seconds during market hours
    const interval = setInterval(fetchPortfolio, 30 * 1000);

    return () => {
      window.removeEventListener('realtimeUpdate', handleRealtimeUpdate as EventListener);
      clearInterval(interval);
    };
  }, [fetchPortfolio]);

  return { positions, performance, loading, error, refetch: fetchPortfolio };
}

// Real-time stock data hook
export function useStockData(symbol: string) {
  const [stockData, setStockData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchStockData = useCallback(async () => {
    if (!symbol) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const data = await apiClient.getStockData(symbol);
      setStockData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch stock data');
      console.error(`Stock data error for ${symbol}:`, err);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => {
    if (!symbol) return;
    
    fetchStockData();
    
    // Real-time stock updates
    const handleRealtimeUpdate = (event: CustomEvent) => {
      const { type, data } = event.detail;
      if (type === 'stock_update' && data.symbol === symbol) {
        setStockData((prev: any) => ({ ...prev, ...data }));
      }
    };

    window.addEventListener('realtimeUpdate', handleRealtimeUpdate as EventListener);
    
    // More frequent updates during market hours
    const now = new Date();
    const marketHours = now.getHours() >= 9 && now.getHours() < 16;
    const refreshInterval = marketHours ? 5000 : 30000; // 5s vs 30s
    
    intervalRef.current = setInterval(fetchStockData, refreshInterval);

    return () => {
      window.removeEventListener('realtimeUpdate', handleRealtimeUpdate as EventListener);
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [symbol, fetchStockData]);

  return { stockData, loading, error, refetch: fetchStockData };
}

// AI Analysis hook with real OpenRouter integration
export function useAIAnalysis(symbol: string, context: string) {
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getAnalysis = useCallback(async () => {
    if (!symbol || !context) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const data = await apiClient.getAIAnalysis(symbol, context);
      setAnalysis(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get AI analysis');
      console.error('AI analysis error:', err);
    } finally {
      setLoading(false);
    }
  }, [symbol, context]);

  return { analysis, loading, error, getAnalysis };
}

// Alpha opportunities hook
export function useAlphaOpportunities() {
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchOpportunities = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await apiClient.getAlphaOpportunities();
      setOpportunities(data.opportunities || []);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch alpha opportunities');
      console.error('Alpha opportunities error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOpportunities();
    
    // Real-time alpha updates
    const handleRealtimeUpdate = (event: CustomEvent) => {
      const { type, data } = event.detail;
      if (type === 'alpha_update') {
        setOpportunities(data.opportunities || []);
        setLastUpdated(new Date());
      }
    };

    window.addEventListener('realtimeUpdate', handleRealtimeUpdate as EventListener);
    
    // Refresh every 10 minutes
    const interval = setInterval(fetchOpportunities, 10 * 60 * 1000);

    return () => {
      window.removeEventListener('realtimeUpdate', handleRealtimeUpdate as EventListener);
      clearInterval(interval);
    };
  }, [fetchOpportunities]);

  return { opportunities, loading, error, lastUpdated, refetch: fetchOpportunities };
}

// Trading execution hook
export function useTradeExecution() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastTrade, setLastTrade] = useState<any>(null);

  const executeTrade = useCallback(async (order: {
    symbol: string;
    qty: number;
    side: 'buy' | 'sell';
    type: 'market' | 'limit';
    limit_price?: number;
    time_in_force: 'day' | 'gtc';
  }) => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await apiClient.executeTrade(order);
      setLastTrade(result);
      
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to execute trade';
      setError(errorMessage);
      console.error('Trade execution error:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { executeTrade, loading, error, lastTrade };
}

// WebSocket connection hook
export function useWebSocket() {
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const connect = async () => {
      try {
        await realtimeSocket.connect();
        setConnected(true);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'WebSocket connection failed');
        console.error('WebSocket error:', err);
      }
    };

    connect();

    return () => {
      realtimeSocket.disconnect();
      setConnected(false);
    };
  }, []);

  return { connected, error };
}