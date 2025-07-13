// Core data types for the catalyst trading app

export type CatalystType = 'Earnings' | 'FDA' | 'M&A' | 'Legal' | 'Macro';

export type AIAgent = 'Claude' | 'ChatGPT' | 'Grok';

export interface CatalystEvent {
  id: string;
  name: string;
  date: Date;
  type: CatalystType;
  aiProbability: number; // 1-10 scale
  expectedUpside: number; // percentage
  description?: string;
  source?: string;
}

export interface AIConsensus {
  agent: AIAgent;
  confidence: number; // 0-1 scale
  reasoning?: string;
  lastUpdated: Date;
}

export interface TradeRecommendation {
  id: string;
  ticker: string;
  companyName: string;
  entryPrice: number;
  targetPrice: number;
  stopLoss: number;
  positionSize: number; // percentage of portfolio
  catalystType: CatalystType;
  whyNow: string;
  aiThesis: string;
  confidence: number; // 0-1 scale
  createdAt: Date;
  expiresAt?: Date;
}

export interface HistoricalTrade {
  id: string;
  ticker: string;
  companyName: string;
  entryPrice: number;
  exitPrice: number;
  pnl: number;
  pnlPercentage: number;
  catalystType: CatalystType;
  predictedOutcome: string;
  actualOutcome: string;
  mostAccurateAgent: AIAgent;
  executedAt: Date;
  closedAt: Date;
}

export interface StockData {
  ticker: string;
  companyName: string;
  currentPrice: number;
  dailyChange: number;
  dailyChangePercent: number;
  volume: number;
  marketCap: number;
  catalysts: CatalystEvent[];
  aiConsensus: AIConsensus[];
  lastUpdated: Date;
}

// UI State types
export interface AppState {
  selectedTicker?: string;
  selectedTimeframe: '1D' | '1W' | '1M' | '3M' | '1Y';
  showAlphaReplay: boolean;
  darkMode: boolean;
}

// Component Props types
export interface CatalystTimelineProps {
  catalysts: CatalystEvent[];
  ticker: string;
  className?: string;
}

export interface AIConsensusBarProps {
  consensus: AIConsensus[];
  className?: string;
}

export interface TradeCardProps {
  trade: TradeRecommendation;
  onSelect?: (trade: TradeRecommendation) => void;
  className?: string;
}

export interface AlphaReplayProps {
  historicalTrades: HistoricalTrade[];
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}