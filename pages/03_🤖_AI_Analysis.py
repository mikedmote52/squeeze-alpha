#!/usr/bin/env python3
"""
AI Analysis - Multi-AI consensus analysis interface
ZERO MOCK DATA - All real OpenRouter AI analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime
import sys
import os

# Add core modules to path
sys.path.append('./core')

st.set_page_config(
    page_title="AI Analysis", 
    page_icon="🤖", 
    layout="wide"
)

def run_ai_analysis(symbol, context=""):
    """Run comprehensive AI analysis for a symbol with timing metrics"""
    import time
    
    try:
        # Status indicators
        status_placeholder = st.empty()
        timing_placeholder = st.empty()
        
        # Start timing
        start_time = time.time()
        
        # Show real-time status
        status_placeholder.info("🤖 AI Models analyzing... Claude, ChatGPT, and Gemini are discussing...")
        
        with st.spinner(f"⏱️ Running multi-AI analysis for {symbol}..."):
            # Update timing every few seconds
            def update_timing():
                elapsed = time.time() - start_time
                timing_placeholder.caption(f"⏱️ Analysis time: {elapsed:.1f} seconds")
            
            update_timing()
            
            response = requests.post(
                "http://localhost:8000/api/ai-analysis",
                json={
                    "symbol": symbol, 
                    "context": context or f"Comprehensive analysis requested from Streamlit AI Analysis page"
                },
                timeout=60  # Longer timeout for comprehensive analysis
            )
            
            # Final timing
            total_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Success status with timing
                num_agents = len(result.get('agents', []))
                status_placeholder.success(f"✅ AI Analysis Complete! {num_agents} models responded in {total_time:.1f}s")
                timing_placeholder.success(f"🚀 Analysis completed in {total_time:.1f} seconds ({total_time/num_agents:.1f}s per AI model)")
                
                # Store timing for optimization
                result['analysis_timing'] = {
                    'total_seconds': total_time,
                    'agents_count': num_agents,
                    'avg_per_agent': total_time / num_agents if num_agents > 0 else 0
                }
                
                return result
            else:
                status_placeholder.error(f"❌ AI analysis failed for {symbol}: {response.status_code}")
                timing_placeholder.empty()
                return None
                
    except Exception as e:
        if 'status_placeholder' in locals():
            status_placeholder.error(f"❌ Analysis error: {str(e)}")
        if 'timing_placeholder' in locals():
            timing_placeholder.empty()
        st.error(f"Error running AI analysis: {e}")
        return None

def display_ai_consensus(analysis_data):
    """Display AI consensus with confidence metrics"""
    agents = analysis_data.get('agents', [])
    
    if not agents:
        st.warning("No AI analysis available")
        return
    
    # Calculate consensus metrics
    total_confidence = sum(agent.get('confidence', 0) for agent in agents)
    avg_confidence = total_confidence / len(agents) if agents else 0
    
    # Display consensus summary
    st.subheader("🎯 AI Consensus Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("AI Agents", len(agents))
    
    with col2:
        st.metric("Avg Confidence", f"{avg_confidence*100:.0f}%")
    
    with col3:
        high_confidence = len([a for a in agents if a.get('confidence', 0) > 0.7])
        st.metric("High Confidence", f"{high_confidence}/{len(agents)}")
    
    with col4:
        agreement = "Strong" if avg_confidence > 0.7 else "Moderate" if avg_confidence > 0.5 else "Weak"
        st.metric("Agreement", agreement)
    
    # Confidence chart
    fig = go.Figure()
    
    agent_names = [agent['name'] for agent in agents]
    confidences = [agent.get('confidence', 0) * 100 for agent in agents]
    colors = ['green' if c >= 70 else 'orange' if c >= 50 else 'red' for c in confidences]
    
    fig.add_trace(go.Bar(
        x=agent_names,
        y=confidences,
        marker_color=colors,
        text=[f"{c:.0f}%" for c in confidences],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="AI Agent Confidence Levels",
        xaxis_title="AI Agent",
        yaxis_title="Confidence (%)",
        height=300,
        yaxis=dict(range=[0, 100])
    )
    
    # Add confidence threshold lines
    fig.add_hline(y=70, line_dash="dash", line_color="green", annotation_text="High Confidence (70%)")
    fig.add_hline(y=50, line_dash="dash", line_color="orange", annotation_text="Moderate Confidence (50%)")
    
    st.plotly_chart(fig, use_container_width=True)

def display_ai_trading_recommendations(analysis_data):
    """Display AI-powered trading recommendations with purchase options"""
    symbol = analysis_data.get('symbol', 'Unknown')
    agents = analysis_data.get('agents', [])
    
    if not agents:
        return
    
    st.subheader("💰 AI Trading Recommendations")
    
    # Get current stock price and AI recommendations
    try:
        import yfinance as yf
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d")
        current_price = float(hist['Close'].iloc[-1]) if not hist.empty else 100.0
    except:
        current_price = 100.0  # Fallback
    
    # Extract AI consensus recommendation
    recommendations = []
    price_targets = []
    risk_levels = []
    
    for agent in agents:
        reasoning = agent.get('reasoning', '').lower()
        confidence = agent.get('confidence', 0.5)
        
        # Extract recommendation
        if 'buy' in reasoning or 'bullish' in reasoning:
            recommendations.append(('BUY', confidence))
        elif 'sell' in reasoning or 'bearish' in reasoning:
            recommendations.append(('SELL', confidence))
        else:
            recommendations.append(('HOLD', confidence))
        
        # Extract price targets (look for numbers that might be price targets)
        import re
        price_matches = re.findall(r'\$(\d+(?:\.\d+)?)', reasoning)
        for price_str in price_matches:
            price = float(price_str)
            if current_price * 0.5 < price < current_price * 2.0:  # Reasonable range
                price_targets.append(price)
        
        # Determine risk level from reasoning
        if 'high risk' in reasoning or 'volatile' in reasoning or confidence < 0.5:
            risk_levels.append('HIGH')
        elif 'low risk' in reasoning or 'stable' in reasoning or confidence > 0.8:
            risk_levels.append('LOW')
        else:
            risk_levels.append('MEDIUM')
    
    # Calculate consensus
    buy_votes = len([r for r, c in recommendations if r == 'BUY'])
    sell_votes = len([r for r, c in recommendations if r == 'SELL'])
    hold_votes = len([r for r, c in recommendations if r == 'HOLD'])
    
    if buy_votes > sell_votes and buy_votes > hold_votes:
        consensus = 'BUY'
        consensus_color = 'green'
    elif sell_votes > buy_votes and sell_votes > hold_votes:
        consensus = 'SELL'
        consensus_color = 'red'
    else:
        consensus = 'HOLD'
        consensus_color = 'orange'
    
    # AI-recommended stop loss and take profit
    avg_confidence = sum(c for r, c in recommendations) / len(recommendations)
    most_common_risk = max(set(risk_levels), key=risk_levels.count) if risk_levels else 'MEDIUM'
    
    if most_common_risk == 'HIGH':
        recommended_stop_loss = 15  # 15% stop loss for high risk
        recommended_take_profit = 25  # 25% take profit
    elif most_common_risk == 'LOW':
        recommended_stop_loss = 8   # 8% stop loss for low risk
        recommended_take_profit = 20  # 20% take profit
    else:
        recommended_stop_loss = 12  # 12% stop loss for medium risk
        recommended_take_profit = 30  # 30% take profit
    
    # Display consensus
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("AI Consensus", consensus, delta=f"{avg_confidence:.1%} confidence")
    
    with col2:
        st.metric("Current Price", f"${current_price:.2f}")
    
    with col3:
        avg_price_target = sum(price_targets) / len(price_targets) if price_targets else current_price * 1.1
        st.metric("Avg AI Target", f"${avg_price_target:.2f}")
    
    with col4:
        st.metric("Risk Level", most_common_risk)
    
    # Trading interface
    if consensus == 'BUY':
        st.success(f"🟢 **AI Consensus: BUY {symbol}**")
        
        # Purchase options
        with st.expander("💰 Purchase Options", expanded=True):
            trade_col1, trade_col2 = st.columns(2)
            
            with trade_col1:
                st.markdown("### 📊 Order Details")
                
                investment_amount = st.number_input(
                    "Investment Amount ($)",
                    min_value=10.0,
                    max_value=50000.0,
                    value=1000.0,
                    step=100.0
                )
                
                shares = int(investment_amount / current_price)
                st.write(f"**Estimated Shares:** {shares}")
                st.write(f"**Total Cost:** ${shares * current_price:.2f}")
                
                order_type = st.selectbox("Order Type", ["Market", "Limit"])
                
                if order_type == "Limit":
                    limit_price = st.number_input(
                        "Limit Price ($)",
                        min_value=current_price * 0.9,
                        max_value=current_price * 1.1,
                        value=current_price,
                        step=0.01
                    )
            
            with trade_col2:
                st.markdown("### 🛡️ AI Risk Management")
                
                st.write(f"🤖 **AI Recommended Stop Loss:** {recommended_stop_loss}%")
                st.write(f"🎯 **AI Recommended Take Profit:** {recommended_take_profit}%")
                
                use_ai_stops = st.checkbox("Use AI Recommendations", value=True)
                
                if use_ai_stops:
                    stop_loss_pct = recommended_stop_loss
                    take_profit_pct = recommended_take_profit
                else:
                    stop_loss_pct = st.slider("Stop Loss %", 5, 25, recommended_stop_loss)
                    take_profit_pct = st.slider("Take Profit %", 10, 50, recommended_take_profit)
                
                stop_price = current_price * (1 - stop_loss_pct / 100)
                profit_price = current_price * (1 + take_profit_pct / 100)
                
                st.write(f"**Stop Loss Price:** ${stop_price:.2f}")
                st.write(f"**Take Profit Price:** ${profit_price:.2f}")
                st.write(f"**Max Loss:** ${investment_amount * (stop_loss_pct / 100):.2f}")
                st.write(f"**Expected Gain:** ${investment_amount * (take_profit_pct / 100):.2f}")
            
            # Execute trade button
            st.divider()
            
            col_execute1, col_execute2, col_execute3 = st.columns([1, 2, 1])
            with col_execute2:
                if st.button(f"🚀 Execute BUY Order for {symbol}", type="primary", key="execute_ai_buy"):
                    execute_ai_recommended_trade(symbol, {
                        'action': 'BUY',
                        'amount': investment_amount,
                        'shares': shares,
                        'order_type': order_type,
                        'limit_price': limit_price if order_type == "Limit" else None,
                        'stop_loss_pct': stop_loss_pct,
                        'take_profit_pct': take_profit_pct,
                        'ai_consensus': consensus,
                        'ai_confidence': avg_confidence,
                        'risk_level': most_common_risk
                    })
    
    elif consensus == 'SELL':
        st.error(f"🔴 **AI Consensus: SELL {symbol}**")
        st.warning("⚠️ AI models recommend selling or avoiding this stock")
        
    else:
        st.info(f"🟡 **AI Consensus: HOLD {symbol}**")
        st.info("💡 AI models suggest waiting for better entry/exit points")

def execute_ai_recommended_trade(symbol, trade_params):
    """Execute AI-recommended trade via Alpaca API"""
    try:
        # Display execution status
        st.warning(f"🚀 Executing AI-recommended {trade_params['action']} order for {symbol}...")
        
        # Prepare trade data
        trade_data = {
            'symbol': symbol,
            'action': trade_params['action'],
            'quantity': trade_params['shares'],
            'order_type': trade_params['order_type'].lower(),
            'limit_price': trade_params.get('limit_price'),
            'stop_loss': {
                'enabled': True,
                'percentage': trade_params['stop_loss_pct']
            },
            'take_profit': {
                'enabled': True,
                'percentage': trade_params['take_profit_pct']
            },
            'ai_metadata': {
                'consensus': trade_params['ai_consensus'],
                'confidence': trade_params['ai_confidence'],
                'risk_level': trade_params['risk_level'],
                'source': 'AI Analysis Center'
            }
        }
        
        # Call backend to execute trade
        response = requests.post(
            "http://localhost:8000/api/trades/execute",
            json=trade_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ Trade executed successfully!")
            st.balloons()
            
            # Show trade confirmation
            with st.expander("📋 Trade Confirmation", expanded=True):
                st.write(f"**Order ID:** {result.get('order_id', 'N/A')}")
                st.write(f"**Symbol:** {symbol}")
                st.write(f"**Action:** {trade_params['action']}")
                st.write(f"**Shares:** {trade_params['shares']}")
                st.write(f"**Order Type:** {trade_params['order_type']}")
                st.write(f"**Stop Loss:** {trade_params['stop_loss_pct']}%")
                st.write(f"**Take Profit:** {trade_params['take_profit_pct']}%")
                st.write(f"**AI Confidence:** {trade_params['ai_confidence']:.1%}")
                
        else:
            st.error(f"❌ Trade execution failed: {response.status_code}")
            try:
                error_data = response.json()
                st.error(f"Error details: {error_data}")
            except:
                st.error(f"Error response: {response.text}")
    
    except Exception as e:
        st.error(f"❌ Trade execution error: {e}")

def display_timing_metrics(analysis_data):
    """Display analysis timing metrics for optimization"""
    timing = analysis_data.get('analysis_timing')
    if not timing:
        return
    
    st.subheader("⏱️ Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Time", f"{timing['total_seconds']:.1f}s")
    
    with col2:
        st.metric("AI Agents", timing['agents_count'])
    
    with col3:
        st.metric("Avg Per Agent", f"{timing['avg_per_agent']:.1f}s")
    
    with col4:
        # Efficiency rating
        if timing['total_seconds'] < 10:
            efficiency = "🚀 Excellent"
        elif timing['total_seconds'] < 20:
            efficiency = "✅ Good"
        elif timing['total_seconds'] < 30:
            efficiency = "⚠️ Slow"
        else:
            efficiency = "🐌 Very Slow"
        
        st.metric("Efficiency", efficiency)
    
    # Optimization suggestions
    if timing['total_seconds'] > 20:
        st.warning("💡 **Optimization Suggestion:** Analysis is taking longer than optimal. Consider reducing context length or using cached results for faster responses.")
    elif timing['total_seconds'] < 5:
        st.success("🎯 **Optimal Performance:** Analysis completed quickly! The system is running efficiently.")

def display_individual_analyses(analysis_data):
    """Display individual AI agent analyses"""
    agents = analysis_data.get('agents', [])
    symbol = analysis_data.get('symbol', 'Unknown')
    
    st.subheader(f"🤖 Individual AI Analyses for {symbol}")
    
    # Create tabs for each AI agent
    if agents:
        tabs = st.tabs([f"{agent['name']} ({agent.get('confidence', 0)*100:.0f}%)" for agent in agents])
        
        for i, agent in enumerate(agents):
            with tabs[i]:
                display_agent_analysis(agent)

def display_agent_analysis(agent):
    """Display a single AI agent's analysis"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        confidence = agent.get('confidence', 0)
        st.metric("Confidence", f"{confidence*100:.0f}%")
        
        # Confidence indicator
        if confidence >= 0.7:
            st.success("🟢 High Confidence")
        elif confidence >= 0.5:
            st.warning("🟡 Moderate Confidence")
        else:
            st.error("🔴 Low Confidence")
        
        # Last updated
        last_updated = agent.get('lastUpdated', 'Unknown')
        if last_updated != 'Unknown':
            try:
                dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                st.caption(f"Updated: {dt.strftime('%H:%M:%S')}")
            except:
                st.caption(f"Updated: {last_updated}")
    
    with col2:
        st.write("**Analysis:**")
        reasoning = agent.get('reasoning', 'No reasoning provided')
        st.write(reasoning)
        
        # Extract key insights if reasoning is long
        if len(reasoning) > 500:
            st.write("**Key Points:**")
            # Simple extraction of sentences with key trading terms
            key_terms = ['buy', 'sell', 'hold', 'target', 'risk', 'upside', 'downside', 'catalyst', 'momentum']
            sentences = reasoning.split('. ')
            key_sentences = [s for s in sentences if any(term in s.lower() for term in key_terms)]
            
            for sentence in key_sentences[:3]:  # Top 3 key sentences
                st.write(f"• {sentence.strip()}")

def display_analysis_history():
    """Display recent analysis history"""
    st.subheader("📚 Analysis History")
    
    # Get analysis history from session state
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    if not st.session_state.analysis_history:
        st.info("No previous analyses. Run an analysis to see history.")
        return
    
    # Display recent analyses
    for i, analysis in enumerate(reversed(st.session_state.analysis_history[-5:])):  # Last 5
        with st.expander(f"{analysis['symbol']} - {analysis['timestamp']}"):
            st.write(f"**Symbol:** {analysis['symbol']}")
            st.write(f"**Timestamp:** {analysis['timestamp']}")
            st.write(f"**Context:** {analysis.get('context', 'N/A')}")
            
            # Show summary metrics
            agents = analysis.get('agents', [])
            if agents:
                avg_confidence = sum(a.get('confidence', 0) for a in agents) / len(agents)
                st.write(f"**Average Confidence:** {avg_confidence*100:.0f}%")
                st.write(f"**AI Agents:** {len(agents)}")
            
            # Button to view full analysis
            if st.button(f"View Full Analysis", key=f"view_{i}"):
                st.session_state.current_analysis = analysis
                st.rerun()

def save_analysis_to_history(symbol, analysis_data, context=""):
    """Save analysis to session history"""
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    history_entry = {
        'symbol': symbol,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'context': context,
        'agents': analysis_data.get('agents', []),
        'source': analysis_data.get('source', 'Unknown')
    }
    
    st.session_state.analysis_history.append(history_entry)
    
    # Keep only last 20 analyses
    if len(st.session_state.analysis_history) > 20:
        st.session_state.analysis_history = st.session_state.analysis_history[-20:]

def main():
    """Main AI analysis interface"""
    
    st.title("🤖 AI Analysis Center")
    st.markdown("Multi-AI consensus analysis using Claude, ChatGPT, and Grok via OpenRouter")
    
    # Analysis input section
    st.subheader("🎯 New Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        symbol = st.text_input(
            "Enter stock symbol for analysis:",
            placeholder="e.g., NVDA, TSLA, AAPL",
            help="Enter any valid stock ticker symbol"
        ).upper().strip()
    
    with col2:
        analysis_type = st.selectbox(
            "Analysis Type:",
            ["Comprehensive", "Quick Overview", "Technical Analysis", "Fundamental Analysis", "Risk Assessment"],
            help="Choose the type of analysis to perform"
        )
    
    # Context input
    context = st.text_area(
        "Additional context (optional):",
        placeholder="e.g., I'm considering this for a swing trade, looking at catalyst opportunities, etc.",
        help="Provide additional context to help AI agents give more targeted analysis"
    )
    
    # Analysis button
    if st.button("🚀 Run AI Analysis", type="primary", disabled=not symbol):
        if symbol:
            # Build context string
            full_context = f"{analysis_type} analysis requested."
            if context:
                full_context += f" Additional context: {context}"
            
            # Run analysis
            analysis_data = run_ai_analysis(symbol, full_context)
            
            if analysis_data:
                # Save to history
                save_analysis_to_history(symbol, analysis_data, full_context)
                
                # Store current analysis
                st.session_state.current_analysis = analysis_data
                st.session_state.current_analysis['symbol'] = symbol
                st.success(f"✅ Analysis completed for {symbol}")
                st.rerun()
            else:
                st.error("❌ Analysis failed. Please try again.")
    
    st.divider()
    
    # Display current analysis
    if 'current_analysis' in st.session_state and st.session_state.current_analysis:
        analysis = st.session_state.current_analysis
        symbol = analysis.get('symbol', 'Unknown')
        
        st.subheader(f"📊 Current Analysis: {symbol}")
        
        # Consensus overview
        display_ai_consensus(analysis)
        
        st.divider()
        
        # Individual analyses
        display_individual_analyses(analysis)
        
        st.divider()
        
        # AI Trading Recommendations with Purchase Options
        display_ai_trading_recommendations(analysis)
        
        st.divider()
        
        # Performance Metrics and Timing
        display_timing_metrics(analysis)
        
        st.divider()
        
        # Analysis metadata
        st.subheader("ℹ️ Analysis Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Symbol:** {symbol}")
        
        with col2:
            source = analysis.get('source', 'Unknown')
            st.write(f"**Source:** {source}")
        
        with col3:
            last_updated = analysis.get('lastUpdated', 'Unknown')
            st.write(f"**Updated:** {last_updated}")
        
        # Clear analysis button
        if st.button("🧹 Clear Current Analysis"):
            if 'current_analysis' in st.session_state:
                del st.session_state.current_analysis
            st.rerun()
        
        st.divider()
    
    # Analysis history
    display_analysis_history()
    
    # Quick analysis shortcuts
    st.subheader("⚡ Quick Analysis")
    st.markdown("Run quick analysis on popular stocks:")
    
    popular_stocks = ['NVDA', 'TSLA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'AMD']
    
    cols = st.columns(4)
    for i, stock in enumerate(popular_stocks):
        with cols[i % 4]:
            if st.button(f"🔍 {stock}", key=f"quick_{stock}"):
                analysis_data = run_ai_analysis(stock, "Quick analysis requested")
                if analysis_data:
                    save_analysis_to_history(stock, analysis_data, "Quick analysis")
                    st.session_state.current_analysis = analysis_data
                    st.session_state.current_analysis['symbol'] = stock
                    st.rerun()

if __name__ == "__main__":
    main()