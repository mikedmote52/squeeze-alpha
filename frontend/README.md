# Catalyst Trading UI - Frontend

A clean, modular React + TypeScript front-end for the catalyst-focused AI trading platform. Built for fast comprehension, strong visual storytelling, and complete transparency into AI agent analysis.

## 🚀 Features

### Core Components

- **CatalystTimeline**: Horizontally scrollable timeline showing FDA, SEC, earnings, and M&A events
- **AIConsensusBar**: Real-time analysis from Claude, ChatGPT, and Grok via OpenRouter
- **TradeCard**: Robinhood-style cards with entry/exit prices, position sizing, and execution
- **AlphaReplay**: Historical performance analysis with AI agent accuracy tracking

### Real-Time Integration

- **Live Portfolio Data**: Direct Alpaca API integration for positions and P&L
- **Real Catalyst Discovery**: FDA.gov, SEC EDGAR, and earnings calendar data
- **WebSocket Updates**: Real-time price and portfolio updates
- **AI Analysis**: OpenRouter integration for multi-agent consensus

## 🏗️ Architecture

```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── CatalystTimeline.tsx
│   │   ├── AIConsensusBar.tsx
│   │   ├── TradeCard.tsx
│   │   └── AlphaReplay.tsx
│   ├── hooks/               # Custom React hooks
│   │   └── useRealTimeData.ts
│   ├── api/                 # API integration layer
│   │   └── client.ts
│   ├── types/               # TypeScript definitions
│   │   └── index.ts
│   └── App.tsx             # Main application
├── package.json
└── tailwind.config.js
```

## 🔧 Installation & Setup

### Prerequisites

1. Node.js 16+ and npm
2. Your Python backend running on `http://localhost:8000`
3. Environment variables configured

### Quick Start

```bash
# Install dependencies
cd frontend
npm install

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Start development server
npm start
```

### Environment Variables

Create a `.env` file in the frontend directory:

```env
# API Configuration
REACT_APP_API_URL=http://localhost:3000
REACT_APP_PYTHON_BACKEND_URL=http://localhost:8000

# Alpaca Configuration
REACT_APP_ALPACA_API_KEY=your_alpaca_key
REACT_APP_ALPACA_SECRET_KEY=your_alpaca_secret
REACT_APP_ALPACA_BASE_URL=https://paper-api.alpaca.markets

# AI Integration
REACT_APP_OPENROUTER_API_KEY=your_openrouter_key

# WebSocket
REACT_APP_WS_URL=ws://localhost:8000/ws
```

## 🔌 Backend Integration

### Required API Endpoints

The frontend expects these endpoints from your Python backend:

```python
# Catalyst Discovery
GET /api/catalyst-discovery
GET /api/fda-catalysts  
GET /api/sec-catalysts

# Portfolio Management
GET /api/portfolio/positions
GET /api/portfolio/performance
POST /api/trades/execute

# Stock Data
GET /api/stocks/{symbol}

# AI Analysis
POST /api/ai-analysis
```

### WebSocket Events

Real-time updates via WebSocket:

```typescript
// Portfolio updates
{
  type: 'portfolio_update',
  data: {
    positions: [...],
    performance: {...}
  }
}

// Catalyst updates
{
  type: 'catalyst_update', 
  data: {
    id: 'catalyst-id',
    ticker: 'NVDA',
    // ... catalyst data
  }
}

// Stock price updates
{
  type: 'stock_update',
  data: {
    symbol: 'NVDA',
    currentPrice: 485.20,
    // ... price data
  }
}
```

## 📱 Component Usage

### CatalystTimeline

```tsx
import CatalystTimeline from './components/CatalystTimeline';

<CatalystTimeline 
  ticker="NVDA"
  maxEvents={10}
  className="my-custom-class"
/>
```

### AIConsensusBar

```tsx
import AIConsensusBar from './components/AIConsensusBar';

<AIConsensusBar
  symbol="NVDA"
  context="Analyze NVDA for upcoming earnings catalyst"
  autoRefresh={true}
  refreshInterval={15} // minutes
/>
```

### TradeCard

```tsx
import TradeCard from './components/TradeCard';

<TradeCard
  trade={tradeRecommendation}
  portfolioValue={100000}
  onExecute={handleTradeExecution}
  showExecuteButton={true}
/>
```

### AlphaReplay

```tsx
import AlphaReplay from './components/AlphaReplay';

<AlphaReplay
  historicalTrades={trades}
  isOpen={showReplay}
  onClose={() => setShowReplay(false)}
/>
```

## 🎨 Styling

### Tailwind CSS Configuration

The app uses a custom Tailwind config with:

- **Inter font** for modern typography
- **Custom colors** matching Robinhood/Public design
- **Responsive breakpoints** optimized for mobile
- **Animation utilities** for smooth interactions

### Custom CSS Classes

```css
/* Trading-specific utilities */
.price-positive { @apply text-green-600; }
.price-negative { @apply text-red-600; }
.trading-card { @apply bg-white rounded-xl shadow-sm hover:shadow-md; }

/* Component-specific styles */
.consensus-bar { @apply relative overflow-hidden bg-gray-200 rounded-lg; }
.catalyst-timeline { @apply space-y-4; }
```

## 🔄 Real-Time Data Flow

### Data Hooks

The app uses custom hooks for real-time data management:

```typescript
// Portfolio data with auto-refresh
const { positions, performance, loading, error, refetch } = usePortfolioData();

// Catalyst discovery with WebSocket updates  
const { catalysts, loading, error, lastUpdated } = useCatalystData();

// AI analysis with OpenRouter integration
const { analysis, loading, error, getAnalysis } = useAIAnalysis(symbol, context);

// Trade execution with Alpaca
const { executeTrade, loading, error, lastTrade } = useTradeExecution();
```

### Auto-Refresh Strategy

- **Portfolio**: Every 30 seconds during market hours
- **Catalysts**: Every 5 minutes  
- **Stock Prices**: Every 5 seconds during market hours
- **AI Analysis**: On-demand with 15-minute cache

## 🚀 Production Deployment

### Build for Production

```bash
npm run build
```

### Deployment Options

1. **Vercel** (Recommended)
   ```bash
   npm install -g vercel
   vercel --prod
   ```

2. **Netlify**
   ```bash
   npm install -g netlify-cli
   netlify deploy --prod --dir=build
   ```

3. **Docker**
   ```dockerfile
   FROM node:16-alpine
   COPY . /app
   WORKDIR /app
   RUN npm ci && npm run build
   EXPOSE 3000
   CMD ["npx", "serve", "-s", "build"]
   ```

### Environment-Specific Config

Production environment variables:

```env
REACT_APP_API_URL=https://api.yourtrading.app
REACT_APP_PYTHON_BACKEND_URL=https://backend.yourtrading.app
REACT_APP_WS_URL=wss://ws.yourtrading.app
```

## 🔐 Security Considerations

### API Key Management

- All API keys stored in environment variables
- Never commit `.env` files to git
- Use different keys for dev/staging/production

### CORS Configuration

Ensure your Python backend allows the frontend domain:

```python
# In your FastAPI backend
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourfrontend.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Performance Monitoring

### Key Metrics to Track

- **Component Render Times**: Use React DevTools Profiler
- **API Response Times**: Monitor with `useRealTimeData` hooks
- **WebSocket Connection Health**: Track connection status
- **Bundle Size**: Monitor with `npm run build --analyze`

### Optimization Tips

- Use `React.memo()` for expensive components
- Implement virtualization for large lists
- Lazy load components with `React.lazy()`
- Optimize images and assets

## 🧪 Testing

### Unit Tests

```bash
npm test
```

### Component Testing

```typescript
import { render, screen } from '@testing-library/react';
import CatalystTimeline from './CatalystTimeline';

test('renders catalyst timeline with events', () => {
  render(<CatalystTimeline ticker="NVDA" />);
  expect(screen.getByText('Catalyst Timeline')).toBeInTheDocument();
});
```

### E2E Testing

```bash
# Install Playwright
npm install @playwright/test

# Run E2E tests
npx playwright test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/awesome-feature`
3. Commit changes: `git commit -m 'Add awesome feature'`
4. Push to branch: `git push origin feature/awesome-feature`
5. Open a Pull Request

## 📚 Additional Resources

- [React Documentation](https://reactjs.org/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Alpaca API Documentation](https://alpaca.markets/docs/)
- [OpenRouter API Documentation](https://openrouter.ai/docs)

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**: Check backend CORS configuration
2. **WebSocket Connection Failed**: Verify WS_URL and backend WebSocket server
3. **API Key Errors**: Ensure all environment variables are set correctly
4. **Build Failures**: Clear node_modules and reinstall dependencies

### Debug Mode

Enable debug logging:

```typescript
// Add to your .env
REACT_APP_DEBUG=true

// In your code
if (process.env.REACT_APP_DEBUG) {
  console.log('Debug info:', data);
}
```

---

**Ready to go live with real catalyst discovery and AI-powered trading!** 🚀