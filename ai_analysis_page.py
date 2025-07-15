#!/usr/bin/env python3
"""
AI Analysis Page - Comprehensive AI conversations, decisions, and portfolio thesis
"""

import streamlit as st
import requests
import json
import glob
import os
from datetime import datetime
from integrated_portfolio_tiles import get_real_time_ai_analysis

# Backend URL configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

def display_ai_analysis_page():
    """Display comprehensive AI Analysis page with conversations, decisions, and portfolio thesis"""
    st.title("🤖 AI Analysis Center")
    st.markdown("Complete AI conversations, decision points, and portfolio thesis analysis")
    
    # Main tabs for different analysis views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Portfolio Thesis", "🗣️ AI Conversations", "🎯 Decision Points", "📈 Individual Stocks"])
    
    with tab1:
        display_overall_portfolio_thesis()
    
    with tab2:
        display_ai_conversations()
    
    with tab3:
        display_decision_points()
    
    with tab4:
        display_individual_stock_analysis()

def display_overall_portfolio_thesis():
    """Display overall portfolio thesis and AI recommendations"""
    st.markdown("### 🎯 Overall Portfolio Thesis")
    
    # Get portfolio data
    portfolio_data = st.session_state.portfolio_data
    
    if not portfolio_data or not portfolio_data.get('positions'):
        st.info("📊 No portfolio data available. Please check your dashboard.")
        return
    
    # Portfolio overview
    positions = portfolio_data['positions']
    total_value = sum(pos['market_value'] for pos in positions)
    total_pl = sum(pos['unrealized_pl'] for pos in positions)
    total_pl_pct = (total_pl / (total_value - total_pl)) * 100 if (total_value - total_pl) != 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Portfolio Value", f"${total_value:,.2f}")
    with col2:
        st.metric("Total P&L", f"${total_pl:+,.2f}", f"{total_pl_pct:+.2f}%")
    with col3:
        st.metric("Positions", len(positions))
    
    st.divider()
    
    # AI Portfolio Analysis
    st.markdown("#### 🤖 AI Portfolio Assessment")
    
    # Get AI analysis for overall portfolio
    try:
        # Call backend for overall portfolio analysis
        response = requests.get(f"{BACKEND_URL}/api/portfolio/ai-thesis", timeout=10)
        if response.status_code == 200:
            portfolio_thesis = response.json()
            
            thesis_col1, thesis_col2 = st.columns(2)
            
            with thesis_col1:
                st.markdown("##### 📈 Portfolio Strengths")
                st.write(portfolio_thesis.get('strengths', 'Analyzing portfolio composition...'))
                
                st.markdown("##### 🎯 Recommendations")
                st.write(portfolio_thesis.get('recommendations', 'Generating strategic recommendations...'))
            
            with thesis_col2:
                st.markdown("##### ⚠️ Risk Areas")
                st.write(portfolio_thesis.get('risks', 'Evaluating risk factors...'))
                
                st.markdown("##### 🔄 Rebalancing")
                st.write(portfolio_thesis.get('rebalancing', 'Assessing portfolio balance...'))
        else:
            st.info("🔄 Generating comprehensive portfolio analysis...")
    except Exception as e:
        st.warning("⚠️ Unable to load portfolio thesis. Backend connection issue.")
    
    # Top performers and underperformers
    st.divider()
    
    performer_col1, performer_col2 = st.columns(2)
    
    with performer_col1:
        st.markdown("#### 🏆 Top Performers")
        top_performers = sorted(positions, key=lambda x: x['unrealized_plpc'], reverse=True)[:3]
        for pos in top_performers:
            st.success(f"**{pos['symbol']}**: +{pos['unrealized_plpc']:.1f}% (${pos['unrealized_pl']:+,.0f})")
    
    with performer_col2:
        st.markdown("#### 📉 Underperformers")
        underperformers = sorted(positions, key=lambda x: x['unrealized_plpc'])[:3]
        for pos in underperformers:
            st.error(f"**{pos['symbol']}**: {pos['unrealized_plpc']:+.1f}% (${pos['unrealized_pl']:+,.0f})")

def display_ai_conversations():
    """Display AI conversations and model discussions"""
    st.markdown("### 🗣️ AI Model Conversations")
    
    # Get AI conversation history
    conversation_files = []
    try:
        conversation_files = glob.glob("ai_collaborative_analysis_*.json")
        conversation_files.sort(reverse=True)  # Most recent first
    except:
        pass
    
    if conversation_files:
        # Show recent conversations
        st.markdown("#### 📝 Recent AI Discussions")
        
        for i, file in enumerate(conversation_files[:5]):  # Show last 5
            try:
                with open(file, 'r') as f:
                    conversation = json.load(f)
                
                # Extract timestamp from filename
                timestamp = file.split('_')[-1].replace('.json', '')
                formatted_time = datetime.strptime(timestamp, '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
                
                with st.expander(f"🤖 AI Discussion - {formatted_time}"):
                    if 'conversation' in conversation:
                        for exchange in conversation['conversation']:
                            model = exchange.get('model', 'AI')
                            message = exchange.get('message', '')
                            
                            if model == 'Claude':
                                st.markdown(f"**🟦 Claude:** {message}")
                            elif model == 'GPT':
                                st.markdown(f"**🟩 GPT-4:** {message}")
                            elif model == 'Grok':
                                st.markdown(f"**🟪 Grok:** {message}")
                            else:
                                st.markdown(f"**🤖 {model}:** {message}")
                    else:
                        st.write("No conversation data available")
            except Exception as e:
                st.error(f"Error loading conversation: {e}")
    else:
        st.info("🔄 No AI conversation history found. Start some analyses to see discussions here.")
    
    # Live conversation starter
    st.divider()
    st.markdown("#### 🚀 Start New AI Discussion")
    
    discussion_topic = st.selectbox(
        "Choose discussion topic:",
        [
            "Portfolio Strategy Review",
            "Risk Assessment",
            "Rebalancing Recommendations", 
            "Individual Stock Analysis",
            "Market Outlook",
            "Custom Topic"
        ]
    )
    
    if discussion_topic == "Custom Topic":
        custom_topic = st.text_input("Enter your topic:")
        if st.button("Start Discussion") and custom_topic:
            start_ai_discussion(custom_topic)
    else:
        if st.button("Start Discussion"):
            start_ai_discussion(discussion_topic)

def display_decision_points():
    """Display AI decision points and recommendations"""
    st.markdown("### 🎯 AI Decision Points & Recommendations")
    
    # Get portfolio data for decision analysis
    portfolio_data = st.session_state.portfolio_data
    
    if not portfolio_data or not portfolio_data.get('positions'):
        st.info("📊 No portfolio data for decision analysis")
        return
    
    positions = portfolio_data['positions']
    
    # Decision analysis for each position
    st.markdown("#### 📊 Per-Stock Decision Analysis")
    
    for position in positions:
        symbol = position['symbol']
        unrealized_plpc = position['unrealized_plpc']
        
        with st.expander(f"🎯 {symbol} - Decision Analysis"):
            # Get AI analysis for this position
            ai_analysis = get_real_time_ai_analysis(symbol, position)
            
            decision_col1, decision_col2 = st.columns(2)
            
            with decision_col1:
                st.markdown("##### 🤖 AI Recommendation")
                recommendation = ai_analysis.get('actionable_recommendation', 'Analyzing...')
                
                if 'buy' in recommendation.lower():
                    st.success(f"🟢 **BUY MORE**: {recommendation}")
                elif 'sell' in recommendation.lower():
                    st.error(f"🔴 **SELL**: {recommendation}")
                else:
                    st.info(f"🟡 **HOLD**: {recommendation}")
                
                st.markdown("##### 📊 Key Metrics")
                st.write(f"Current P&L: **{unrealized_plpc:+.1f}%**")
                st.write(f"Position Size: **${position['market_value']:,.2f}**")
                st.write(f"Shares: **{position['qty']:.0f}**")
            
            with decision_col2:
                st.markdown("##### ⚠️ Risk Factors")
                risk_analysis = ai_analysis.get('risk_analysis', 'Evaluating risks...')
                st.write(risk_analysis)
                
                st.markdown("##### 🎯 Decision Rationale")
                # Generate decision reasoning
                if unrealized_plpc > 10:
                    st.write("✅ Strong performer - Consider taking profits or adding to winner")
                elif unrealized_plpc > 0:
                    st.write("📈 Positive momentum - Monitor for breakout or reversal")
                elif unrealized_plpc > -10:
                    st.write("⚠️ Underperforming - Evaluate thesis and consider exit")
                else:
                    st.write("🔴 Significant loss - Review stop-loss and exit strategy")
    
    # Portfolio-level decisions
    st.divider()
    st.markdown("#### 🎯 Portfolio-Level Decisions")
    
    # Calculate portfolio metrics for decisions
    total_positions = len(positions)
    winning_positions = sum(1 for pos in positions if pos['unrealized_plpc'] > 0)
    losing_positions = total_positions - winning_positions
    
    decision_metrics_col1, decision_metrics_col2, decision_metrics_col3 = st.columns(3)
    
    with decision_metrics_col1:
        st.metric("Win Rate", f"{(winning_positions/total_positions)*100:.1f}%")
    with decision_metrics_col2:
        st.metric("Winners", winning_positions)
    with decision_metrics_col3:
        st.metric("Losers", losing_positions)
    
    # Portfolio decision recommendations
    if winning_positions / total_positions > 0.6:
        st.success("🏆 **Portfolio Decision**: Strong performance - Consider scaling up successful strategies")
    elif winning_positions / total_positions < 0.4:
        st.error("⚠️ **Portfolio Decision**: Underperforming - Review and rebalance positions")
    else:
        st.info("📊 **Portfolio Decision**: Balanced performance - Continue monitoring")

def display_individual_stock_analysis():
    """Display detailed individual stock analysis"""
    st.markdown("### 📈 Individual Stock Analysis")
    
    # Get portfolio data
    portfolio_data = st.session_state.portfolio_data
    
    if not portfolio_data or not portfolio_data.get('positions'):
        st.info("📊 No portfolio positions to analyze")
        return
    
    positions = portfolio_data['positions']
    
    # Stock selector
    symbols = [pos['symbol'] for pos in positions]
    selected_symbol = st.selectbox("Select stock for detailed analysis:", symbols)
    
    if selected_symbol:
        # Find the position
        selected_position = next((pos for pos in positions if pos['symbol'] == selected_symbol), None)
        
        if selected_position:
            # Display detailed analysis
            st.markdown(f"#### 📊 {selected_symbol} - Complete Analysis")
            
            # Key metrics
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                st.metric("Current Price", f"${selected_position['current_price']:.2f}")
            with metric_col2:
                st.metric("P&L", f"{selected_position['unrealized_plpc']:+.1f}%")
            with metric_col3:
                st.metric("Shares", f"{selected_position['qty']:.0f}")
            with metric_col4:
                st.metric("Value", f"${selected_position['market_value']:,.2f}")
            
            # AI Analysis
            st.divider()
            ai_analysis = get_real_time_ai_analysis(selected_symbol, selected_position)
            
            analysis_col1, analysis_col2 = st.columns(2)
            
            with analysis_col1:
                st.markdown("##### 🤖 AI Models Analysis")
                st.write(f"**Claude**: {ai_analysis.get('claude_score', 'Analyzing...')}")
                st.write(f"**GPT-4**: {ai_analysis.get('gpt_score', 'Analyzing...')}")
                
                st.markdown("##### 💡 Recommendation")
                st.info(ai_analysis.get('actionable_recommendation', 'Generating recommendation...'))
            
            with analysis_col2:
                st.markdown("##### ⚠️ Risk Assessment")
                st.write(ai_analysis.get('risk_analysis', 'Evaluating risks...'))
                
                st.markdown("##### 🎯 Price Target")
                target_price = ai_analysis.get('projected_price', selected_position['current_price'])
                current_price = selected_position['current_price']
                upside = ((target_price - current_price) / current_price) * 100
                st.write(f"Target: **${target_price:.2f}** ({upside:+.1f}% upside)")
            
            # Get full thesis if available
            try:
                thesis_response = requests.get(f"{BACKEND_URL}/api/ai-analysis/full/{selected_symbol}", timeout=10)
                if thesis_response.status_code == 200:
                    thesis_data = thesis_response.json()
                    
                    st.divider()
                    st.markdown("##### 📋 Complete Thesis")
                    
                    thesis_tab1, thesis_tab2 = st.tabs(["📈 Bull Case", "📉 Bear Case"])
                    
                    with thesis_tab1:
                        st.write(thesis_data.get('bull_case', 'Analyzing bull case...'))
                    
                    with thesis_tab2:
                        st.write(thesis_data.get('bear_case', 'Analyzing bear case...'))
                    
                    # Live conversation
                    if thesis_data.get('conversation'):
                        st.markdown("##### 🗣️ Live AI Discussion")
                        for exchange in thesis_data['conversation']:
                            model = exchange.get('model', 'AI')
                            message = exchange.get('message', '')
                            timestamp = exchange.get('timestamp', '')
                            
                            if model == 'Claude':
                                st.markdown(f"**🟦 Claude** _{timestamp}_: {message}")
                            elif model == 'GPT':
                                st.markdown(f"**🟩 GPT-4** _{timestamp}_: {message}")
                            else:
                                st.markdown(f"**🤖 {model}** _{timestamp}_: {message}")
                else:
                    st.info("🔄 Loading complete thesis analysis...")
            except Exception as e:
                st.warning("⚠️ Unable to load complete thesis")

def start_ai_discussion(topic):
    """Start a new AI discussion on the given topic"""
    st.success(f"🚀 Starting AI discussion on: {topic}")
    st.info("🔄 AI models are analyzing and will begin discussion shortly...")
    
    # Here you would typically call your backend to start the discussion
    # For now, we'll just show a placeholder
    try:
        # Call backend to start discussion
        response = requests.post(f"{BACKEND_URL}/api/ai-discussion/start", 
                               json={"topic": topic}, timeout=10)
        if response.status_code == 200:
            st.success("✅ AI discussion started successfully!")
        else:
            st.warning("⚠️ Unable to start discussion. Please try again.")
    except Exception as e:
        st.error(f"❌ Error starting discussion: {e}")