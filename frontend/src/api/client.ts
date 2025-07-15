// Real API client for production catalyst trading app
// Connects to Python backend and live market data

export interface APIConfig {
  baseURL: string;
  pythonBackendURL: string;
  alpacaApiKey: string;
  alpacaSecretKey: string;
  alpacaBaseURL: string;
  openrouterApiKey: string;
}

class APIClient {
  private config: APIConfig;

  constructor(config: APIConfig) {
    this.config = config;
  }

  // Real Catalyst Discovery Integration
  async getCatalystOpportunities(): Promise<any> {
    try {
      const response = await fetch(`${this.config.pythonBackendURL}/api/catalyst-discovery`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Catalyst API error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.warn('Error fetching catalyst opportunities:', error);
      // Return empty data instead of throwing
      return { catalysts: [], lastUpdated: new Date().toISOString(), source: "API Error" };
    }
  }

  // Real Alpha Discovery Integration
  async getAlphaOpportunities(): Promise<any> {
    try {
      const response = await fetch(`${this.config.pythonBackendURL}/api/alpha-discovery`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Alpha API error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.warn('Error fetching alpha opportunities:', error);
      return { opportunities: [], lastUpdated: new Date().toISOString(), source: "API Error" };
    }
  }

  // Live Alpaca Portfolio Integration
  async getPortfolioPositions(): Promise<any> {
    try {
      const response = await fetch(`${this.config.pythonBackendURL}/api/portfolio/positions`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.alpacaApiKey}`,
        },
      });
      
      if (!response.ok) {
        throw new Error(`Portfolio API error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.warn('Error fetching portfolio positions:', error);
      return { positions: [], lastUpdated: new Date().toISOString() };
    }
  }

  // Real-time Stock Data
  async getStockData(symbol: string): Promise<any> {
    try {
      const response = await fetch(`${this.config.pythonBackendURL}/api/stocks/${symbol}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Stock data API error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`Error fetching stock data for ${symbol}:`, error);
      throw error;
    }
  }

  // AI Analysis Integration (Claude, ChatGPT, Grok via OpenRouter)
  async getAIAnalysis(symbol: string, context: string): Promise<any> {
    try {
      const response = await fetch(`${this.config.pythonBackendURL}/api/ai-analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.openrouterApiKey}`,
        },
        body: JSON.stringify({
          symbol,
          context,
          agents: ['claude', 'chatgpt', 'grok']
        }),
      });
      
      if (!response.ok) {
        throw new Error(`AI Analysis API error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching AI analysis:', error);
      throw error;
    }
  }

  // Real FDA Data from your FDA scraper
  async getFDACatalysts(): Promise<any> {
    try {
      const response = await fetch(`${this.config.pythonBackendURL}/api/fda-catalysts`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`FDA API error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching FDA catalysts:', error);
      throw error;
    }
  }

  // Real SEC Data from your SEC monitor
  async getSECCatalysts(): Promise<any> {
    try {
      const response = await fetch(`${this.config.pythonBackendURL}/api/sec-catalysts`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`SEC API error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching SEC catalysts:', error);
      throw error;
    }
  }

  // Live Portfolio Performance
  async getPortfolioPerformance(): Promise<any> {
    try {
      const response = await fetch(`${this.config.pythonBackendURL}/api/portfolio/performance`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.alpacaApiKey}`,
        },
      });
      
      if (!response.ok) {
        throw new Error(`Portfolio performance API error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching portfolio performance:', error);
      throw error;
    }
  }

  // Execute Real Trades via Alpaca
  async executeTrade(order: {
    symbol: string;
    qty: number;
    side: 'buy' | 'sell';
    type: 'market' | 'limit';
    limit_price?: number;
    time_in_force: 'day' | 'gtc';
  }): Promise<any> {
    try {
      const response = await fetch(`${this.config.pythonBackendURL}/api/trades/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.alpacaApiKey}`,
        },
        body: JSON.stringify(order),
      });
      
      if (!response.ok) {
        throw new Error(`Trade execution API error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error executing trade:', error);
      throw error;
    }
  }
}

// Configuration for production
const productionConfig: APIConfig = {
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:3000',
  pythonBackendURL: process.env.REACT_APP_PYTHON_BACKEND_URL || 'http://localhost:8000',
  alpacaApiKey: process.env.REACT_APP_ALPACA_API_KEY || '',
  alpacaSecretKey: process.env.REACT_APP_ALPACA_SECRET_KEY || '',
  alpacaBaseURL: process.env.REACT_APP_ALPACA_BASE_URL || 'https://paper-api.alpaca.markets',
  openrouterApiKey: process.env.REACT_APP_OPENROUTER_API_KEY || '',
};

// Export singleton instance
export const apiClient = new APIClient(productionConfig);

// WebSocket for real-time updates
export class RealTimeDataSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  connect(url: string = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws'): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(url);
        
        this.ws.onopen = () => {
          console.log('Real-time data connection established');
          this.reconnectAttempts = 0;
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleRealtimeUpdate(data);
          } catch (error) {
            console.error('Error parsing real-time data:', error);
          }
        };
        
        this.ws.onclose = () => {
          console.log('Real-time data connection closed');
          this.attemptReconnect();
        };
        
        this.ws.onerror = (error) => {
          console.error('Real-time data connection error:', error);
          reject(error);
        };
        
      } catch (error) {
        reject(error);
      }
    });
  }

  private handleRealtimeUpdate(data: any) {
    // Dispatch real-time updates to components
    window.dispatchEvent(new CustomEvent('realtimeUpdate', { detail: data }));
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++;
        console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect();
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}

export const realtimeSocket = new RealTimeDataSocket();