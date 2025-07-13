#!/usr/bin/env python3
"""
AI Trading System - Streamlit Mobile App
Beautiful mobile interface with native app feel
"""

import streamlit as st
import asyncio
import sys
import os
from datetime import datetime
import time

# Add core directory to path
sys.path.append('core')

# Configure page
st.set_page_config(
    page_title="🚀 AI Trading System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile-optimized design
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        text-align: center;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 15px;
        height: 80px;
        font-size: 18px;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        margin: 5px 0;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    .discovery-result {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8em;
        }
        .stButton > button {
            height: 70px;
            font-size: 16px;
        }
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI Trading System</h1>
        <p>Professional Binary Catalyst Discovery</p>
        <small>📱 Mobile-Optimized Trading Dashboard</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📊</h3>
            <p>Alpha Engine</p>
            <small>Momentum & Volume</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯</h3>
            <p>Catalyst Engine</p>
            <small>Binary Events</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🏆</h3>
            <p>Performance</p>
            <small>System Tracking</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main action buttons
    st.markdown("### 🎯 **Discovery Systems**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Alpha Discovery", key="alpha_btn"):
            with st.spinner("🔍 Running Alpha Discovery..."):
                result = run_alpha_discovery()
                st.session_state.last_result = result
                st.session_state.result_type = "Alpha Discovery"
    
    with col2:
        if st.button("🎯 Catalyst Discovery", key="catalyst_btn"):
            with st.spinner("🔍 Scanning Binary Events..."):
                result = run_catalyst_discovery()
                st.session_state.last_result = result
                st.session_state.result_type = "Catalyst Discovery"
    
    # Performance tracking button (full width)
    if st.button("🏆 System Performance Comparison", key="performance_btn"):
        with st.spinner("📊 Analyzing System Performance..."):
            result = run_system_performance()
            st.session_state.last_result = result
            st.session_state.result_type = "System Performance"
    
    st.markdown("---")
    
    # Portfolio and market tools
    st.markdown("### 💰 **Portfolio & Market Tools**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💰 Live Portfolio", key="portfolio_btn"):
            with st.spinner("💰 Loading Live Holdings..."):
                result = run_live_portfolio()
                st.session_state.last_result = result
                st.session_state.result_type = "Live Portfolio"
    
    with col2:
        if st.button("🔍 Market Check", key="market_btn"):
            with st.spinner("📈 Checking Markets..."):
                result = run_market_check()
                st.session_state.last_result = result
                st.session_state.result_type = "Market Check"
    
    # Display results
    if hasattr(st.session_state, 'last_result') and st.session_state.last_result:
        st.markdown("---")
        st.markdown(f"### 📋 **{st.session_state.result_type} Results**")
        
        st.markdown(f"""
        <div class="discovery-result">
            <pre style="white-space: pre-wrap; font-family: monospace; font-size: 14px;">
{st.session_state.last_result}
            </pre>
        </div>
        """, unsafe_allow_html=True)
        
        # Download button for results
        st.download_button(
            label="📥 Download Results",
            data=st.session_state.last_result,
            file_name=f"{st.session_state.result_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; opacity: 0.7; padding: 20px;">
        🚀 AI Trading System v2.0 | 📱 Mobile Optimized<br>
        <small>Professional Binary Catalyst Discovery Platform</small>
    </div>
    """, unsafe_allow_html=True)

# Import and run functions
@st.cache_data(ttl=300)  # Cache for 5 minutes
def run_alpha_discovery():
    """Run alpha discovery with caching"""
    try:
        from main import run_stock_discovery
        return run_stock_discovery()
    except Exception as e:
        return f"❌ Alpha discovery failed: {str(e)}"

@st.cache_data(ttl=300)
def run_catalyst_discovery():
    """Run catalyst discovery with caching"""
    try:
        from main import run_catalyst_discovery
        return run_catalyst_discovery()
    except Exception as e:
        return f"❌ Catalyst discovery failed: {str(e)}"

@st.cache_data(ttl=60)  # Cache performance for 1 minute
def run_system_performance():
    """Run system performance analysis"""
    try:
        from main import run_system_performance
        return run_system_performance()
    except Exception as e:
        return f"❌ System performance analysis failed: {str(e)}"

@st.cache_data(ttl=60)  # Cache for 1 minute for live data
def run_live_portfolio():
    """Run live portfolio tracking"""
    try:
        import asyncio
        from live_portfolio_integration import get_live_portfolio_for_mobile
        return asyncio.run(get_live_portfolio_for_mobile())
    except Exception as e:
        return f"❌ Live portfolio failed: {str(e)}"

@st.cache_data(ttl=300)
def run_portfolio_analysis():
    """Run portfolio analysis"""
    try:
        from main import run_portfolio_analysis
        return run_portfolio_analysis()
    except Exception as e:
        return f"❌ Portfolio analysis failed: {str(e)}"

def run_market_check():
    """Quick market check"""
    try:
        import yfinance as yf
        from datetime import datetime
        
        symbols = ['SPY', 'QQQ', 'IWM', '^VIX']
        result = "📈 **QUICK MARKET CHECK**\n"
        result += "=" * 40 + "\n\n"
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                
                if len(hist) >= 2:
                    current = hist['Close'].iloc[-1]
                    previous = hist['Close'].iloc[-2]
                    change_pct = ((current - previous) / previous) * 100
                    
                    emoji = "🟢" if change_pct > 0 else "🔴" if change_pct < 0 else "⚪"
                    result += f"{emoji} **{symbol}**: ${current:.2f} ({change_pct:+.1f}%)\n"
                else:
                    result += f"⚪ **{symbol}**: Data unavailable\n"
            except:
                result += f"⚪ **{symbol}**: Error fetching data\n"
        
        result += f"\n⏰ Market data as of {datetime.now().strftime('%H:%M %Z')}"
        return result
        
    except Exception as e:
        return f"❌ Market check failed: {str(e)}"

if __name__ == "__main__":
    main()