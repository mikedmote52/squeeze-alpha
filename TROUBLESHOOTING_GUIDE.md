# AI Trading System - Troubleshooting Guide

## 🚨 Common Issues & Solutions

### **1. Trade Execution Issues**

#### **Problem**: Trade buttons not working / "Failed to execute" errors
**Symptoms**: 
- Clicking trade buttons shows no response
- Error messages like "Failed to execute SELL for BLNK"
- Trade confirmations don't appear

**Solutions**:
1. **Check Status Code**: Ensure backend returns HTTP 201 (not 200) for successful trades
2. **Verify API Connection**: Confirm Alpaca API credentials are valid
3. **Check Session State**: Ensure `show_trade_{symbol}` is properly set
4. **Restart Services**: Refresh browser or restart backend

**Code Fix**:
```python
# Fix status code check in streamlit_app.py
if response.status_code == 201:  # NOT 200
    result = response.json()
    st.success(f"✅ Trade executed! Order ID: {result.get('orderId', 'N/A')}")
```

#### **Problem**: Inconsistent price targets
**Symptoms**:
- AI Target shows $1.01 but detailed analysis shows $1.25
- Price targets vary between different display areas

**Solutions**:
1. **Unified Data Source**: All price displays should use same AI analysis source
2. **Cache Consistency**: Ensure cached data matches real-time analysis
3. **Model Consensus**: Use averaged price targets from multiple AI models

**Code Fix**:
```python
# In get_real_time_ai_analysis()
if price_targets:
    avg_target = sum(price_targets) / len(price_targets)
    ai_analysis['projected_price'] = avg_target  # Use consistently
```

### **2. AI Analysis Issues**

#### **Problem**: Boring/generic AI analysis
**Symptoms**:
- "Analysis from cached AI baseline - loads instantly"
- Generic placeholder text instead of real insights
- No actionable recommendations

**Solutions**:
1. **Disable Cached Baseline Priority**: Don't show cached data as primary content
2. **Enhance AI Responses**: Add emojis, percentages, clear actions
3. **Real-time Analysis**: Always fetch fresh AI analysis for display

**Code Fix**:
```python
# Replace boring cached baseline with engaging analysis
ai_analysis = {
    'actionable_recommendation': f"🚀 CONSIDER BUYING MORE: {reason}",
    'claude_score': f"🚀 Strong Buy ({confidence*100:.0f}%)",
    'thesis': combined_reasoning  # Real AI discussion
}
```

#### **Problem**: AI analysis not loading / timeout errors
**Symptoms**:
- "AI Models analyzing..." spinner never completes
- Timeout errors after 30 seconds
- "Error getting AI analysis" messages

**Solutions**:
1. **Check OpenRouter API**: Verify API key and credits
2. **Increase Timeouts**: Extend timeout for complex analysis
3. **Fallback Mechanisms**: Provide backup analysis when AI fails
4. **Retry Logic**: Implement automatic retries for failed requests

### **3. Discovery Engine Issues**

#### **Problem**: No opportunities found / generic explanations
**Symptoms**:
- "No opportunities found at this time" without details
- Generic checklist instead of real search results
- No explanation of filtering criteria

**Solutions**:
1. **Add AI Explanations**: Use OpenRouter to analyze why no opportunities found
2. **Show Search Details**: Display candidates found, filters applied
3. **Market Context**: Include current market conditions and timing
4. **Specific Reasoning**: Explain exactly what was searched and why rejected

**Code Fix**:
```python
# Add detailed explanation when no opportunities found
if not opportunities:
    explanation = await get_discovery_explanation("catalyst", raw_candidates)
    # Show: "Scanned 47 biotech catalysts, filtered 32 for market cap >$50B..."
```

#### **Problem**: Discovery engines not finding opportunities
**Symptoms**:
- Always returns empty results
- No catalyst or alpha discoveries
- Discovery engines timing out

**Solutions**:
1. **Check API Quotas**: Verify external API limits (Alpha Vantage, Finnhub)
2. **Adjust Filters**: Lower quality thresholds temporarily
3. **Verify Data Sources**: Ensure FDA/SEC APIs are responding
4. **Debug Logging**: Add detailed logging to discovery engines

### **4. Backend Connection Issues**

#### **Problem**: Backend connection timeouts
**Symptoms**:
- "Backend Connection Error" messages
- HTTPConnectionPool timeout errors
- Portfolio data not loading

**Solutions**:
1. **Check Backend URL**: Ensure BACKEND_URL environment variable is set
2. **Service Health**: Verify backend service is running on port 8000
3. **Network Issues**: Check firewall/proxy settings
4. **Timeout Settings**: Increase timeout values for complex operations

**Code Fix**:
```python
# Add BACKEND_URL configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
response = requests.get(f"{BACKEND_URL}/api/portfolio/positions", timeout=30)
```

#### **Problem**: CORS errors in browser
**Symptoms**:
- "Access to fetch blocked by CORS policy"
- API calls failing from frontend

**Solutions**:
1. **Configure CORS**: Add proper CORS middleware to FastAPI
2. **Same Origin**: Ensure frontend and backend are on same domain
3. **Headers**: Add required headers for cross-origin requests

### **5. Deployment Issues**

#### **Problem**: Render.com deployment failures
**Symptoms**:
- Build fails with Python 3.12 distutils errors
- Services not starting correctly
- Environment variables not loaded

**Solutions**:
1. **Python Version**: Use Python 3.11 in Dockerfile (has distutils)
2. **Environment Variables**: Set all required API keys in Render dashboard
3. **Port Configuration**: Use ${PORT} environment variable for dynamic ports
4. **Startup Script**: Ensure both backend and frontend start correctly

**Code Fix**:
```dockerfile
# Use Python 3.11 (not 3.12)
FROM python:3.11-slim

# Use dynamic PORT
streamlit run streamlit_app.py --server.port=${PORT:-8501}
```

#### **Problem**: Services not accessible after deployment
**Symptoms**:
- URLs return 404 or connection refused
- Backend API endpoints not responding
- Frontend shows raw JSON instead of UI

**Solutions**:
1. **Health Checks**: Verify both services are running
2. **Port Mapping**: Ensure correct port exposure
3. **Startup Order**: Backend must start before frontend
4. **Logs Review**: Check deployment logs for specific errors

### **6. API Integration Issues**

#### **Problem**: OpenRouter API errors
**Symptoms**:
- 401 Unauthorized errors
- Rate limit exceeded
- AI models not responding

**Solutions**:
1. **API Credits**: Check OpenRouter account balance
2. **Rate Limits**: Implement proper rate limiting
3. **Model Availability**: Verify requested models are available
4. **Headers**: Include required HTTP-Referer and X-Title headers

**Code Fix**:
```python
headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://github.com/your-repo/ai-trading-system",
    "X-Title": "AI Trading System"
}
```

#### **Problem**: Alpaca API connection issues
**Symptoms**:
- Portfolio data not loading
- Trade execution failures
- Authentication errors

**Solutions**:
1. **API Keys**: Verify Alpaca API credentials are correct
2. **Paper Trading**: Ensure using paper trading environment
3. **Account Status**: Check account is active and funded
4. **Permissions**: Verify API keys have trading permissions

### **7. Performance Issues**

#### **Problem**: Slow AI analysis responses
**Symptoms**:
- Analysis takes >30 seconds
- UI freezes during AI calls
- Timeout errors

**Solutions**:
1. **Caching**: Implement 30-minute cache for AI analysis
2. **Async Processing**: Use asynchronous API calls
3. **Parallel Requests**: Process multiple analyses simultaneously
4. **Optimize Prompts**: Reduce AI prompt complexity

#### **Problem**: High API costs
**Symptoms**:
- Unexpected API charges
- Cost tracker showing high usage
- Rate limit warnings

**Solutions**:
1. **Cost Monitoring**: Track API usage by endpoint
2. **Caching Strategy**: Increase cache duration for expensive calls
3. **Batch Processing**: Combine multiple requests
4. **Usage Limits**: Set daily/weekly spending limits

## 🔧 Debugging Tools

### **Backend Debugging**
```python
# Add logging to backend
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Log API calls
logger.info(f"API call: {endpoint} - Response: {response.status_code}")
```

### **Frontend Debugging**
```python
# Add debug info to Streamlit
if st.checkbox("Debug Mode"):
    st.json(ai_analysis)  # Show raw data
    st.write(f"Backend URL: {BACKEND_URL}")
    st.write(f"Session State: {st.session_state}")
```

### **API Testing**
```bash
# Test backend endpoints directly
curl -X GET "http://localhost:8000/api/portfolio/positions"
curl -X POST "http://localhost:8000/api/trades/execute" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","qty":"1","side":"buy"}'
```

## 📞 Support Resources

### **Error Tracking**
- Check browser console for JavaScript errors
- Review server logs for API errors
- Monitor external API status pages

### **Documentation**
- Alpaca API docs: https://alpaca.markets/docs/
- OpenRouter API docs: https://openrouter.ai/docs
- Streamlit docs: https://docs.streamlit.io/

### **Community**
- GitHub Issues: Report bugs and feature requests
- Discord: Real-time support and discussions
- Stack Overflow: Technical questions and solutions

---

**Keep this guide updated as new issues are discovered and resolved. Always test fixes in development before deploying to production.**