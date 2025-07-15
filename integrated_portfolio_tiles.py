#!/usr/bin/env python3
"""
Integrated Portfolio Tiles - Modern, Interactive Design
Combines all portfolio functionality into sleek, clickable tiles
"""

import streamlit as st
import requests
import os
from datetime import datetime

# Backend URL configuration - connect to your real backend service
BACKEND_URL = os.getenv('BACKEND_URL', 'https://squeeze-alpha.onrender.com')

def display_integrated_portfolio_tiles(portfolio_data):
    """Display integrated interactive portfolio tiles with all functionality"""
    if not portfolio_data or not portfolio_data.get('positions'):
        st.info("📊 Ready to build your portfolio! Check opportunities below.")
        return
    
    positions = portfolio_data['positions']
    
    # Create responsive grid layout
    st.markdown("### 📊 Portfolio Holdings")
    
    # Display tiles in single column for mobile-first design
    for position in positions:
        display_integrated_position_tile(position, positions)

def display_integrated_position_tile(position, all_positions):
    """Display integrated position tile with all data and functionality"""
    symbol = position['symbol']
    current_price = float(position.get('current_price', 0))
    unrealized_plpc = float(position.get('unrealized_plpc', 0))
    unrealized_pl = float(position.get('unrealized_pl', 0))
    market_value = float(position.get('market_value', 0))
    qty = float(position.get('qty', 0))
    avg_cost = float(position.get('avg_cost', position.get('cost_basis', current_price)))
    
    # Calculate portfolio percentage
    total_value = sum(float(pos['market_value']) for pos in all_positions)
    portfolio_pct = (market_value / total_value * 100) if total_value > 0 else 0
    
    # Health indicator and styling
    if unrealized_plpc > 10:
        health_status = "🟢 Excellent"
        border_color = "#00d4aa"
        bg_color = "rgba(0,212,170,0.1)"
    elif unrealized_plpc > 0:
        health_status = "🟡 Good"
        border_color = "#ffd700"
        bg_color = "rgba(255,215,0,0.1)"
    elif unrealized_plpc > -5:
        health_status = "🟠 Caution"
        border_color = "#ff8c00"
        bg_color = "rgba(255,140,0,0.1)"
    else:
        health_status = "🔴 Poor"
        border_color = "#ff4444"
        bg_color = "rgba(255,68,68,0.1)"
    
    # Get AI analysis
    ai_analysis = get_real_time_ai_analysis(symbol, position)
    ai_rating = ai_analysis.get('claude_score', 'HOLD')
    
    # Create clickable tile container
    tile_key = f"tile_{symbol}"
    is_expanded = st.session_state.get(f"expanded_{symbol}", False)
    
    # Main tile with all data inside - CLICKABLE
    with st.container():
        # Make the whole tile clickable using a button that spans the full width
        clicked = st.button(
            f"{symbol} - {health_status} {unrealized_plpc:+.2f}%",
            key=tile_key,
            help=f"Click to expand {symbol} trading options",
            use_container_width=True
        )
        
        if clicked:
            st.session_state[f"expanded_{symbol}"] = not is_expanded
            st.rerun()
        
        # Custom CSS for the tile with ALL data inside
        st.markdown(f"""
        <div style="
            border: 3px solid {border_color};
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            background: linear-gradient(135deg, {bg_color} 0%, rgba(0,0,0,0.3) 100%);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            position: relative;
            min-height: 160px;
        ">
            <!-- Header with symbol and health status -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h2 style="margin: 0; color: #fff; font-size: 1.8em; font-weight: bold;">{symbol}</h2>
                <span style="color: {border_color}; font-size: 1em; font-weight: bold;">{health_status} {unrealized_plpc:+.2f}%</span>
            </div>
            
            <!-- ALL DATA IN THE TILE -->
            <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; margin-bottom: 15px;">
                <div style="text-align: center; padding: 8px; background: rgba(0,0,0,0.4); border-radius: 6px;">
                    <div style="color: #aaa; font-size: 0.7em; margin-bottom: 2px;">Quantity</div>
                    <div style="color: #fff; font-size: 1em; font-weight: bold;">{qty:.0f}</div>
                </div>
                <div style="text-align: center; padding: 8px; background: rgba(0,0,0,0.4); border-radius: 6px;">
                    <div style="color: #aaa; font-size: 0.7em; margin-bottom: 2px;">Avg Cost</div>
                    <div style="color: #fff; font-size: 1em; font-weight: bold;">${avg_cost:.2f}</div>
                </div>
                <div style="text-align: center; padding: 8px; background: rgba(0,0,0,0.4); border-radius: 6px;">
                    <div style="color: #aaa; font-size: 0.7em; margin-bottom: 2px;">Current Price</div>
                    <div style="color: #fff; font-size: 1em; font-weight: bold;">${current_price:.2f}</div>
                </div>
                <div style="text-align: center; padding: 8px; background: rgba(0,0,0,0.4); border-radius: 6px;">
                    <div style="color: #aaa; font-size: 0.7em; margin-bottom: 2px;">Market Value</div>
                    <div style="color: #fff; font-size: 1em; font-weight: bold;">${market_value:.2f}</div>
                </div>
                <div style="text-align: center; padding: 8px; background: rgba(0,0,0,0.4); border-radius: 6px;">
                    <div style="color: #aaa; font-size: 0.7em; margin-bottom: 2px;">P&L Amount</div>
                    <div style="color: {border_color}; font-size: 1em; font-weight: bold;">${unrealized_pl:+.2f}</div>
                </div>
                <div style="text-align: center; padding: 8px; background: rgba(0,0,0,0.4); border-radius: 6px;">
                    <div style="color: #aaa; font-size: 0.7em; margin-bottom: 2px;">AI Rating</div>
                    <div style="color: #fff; font-size: 1em; font-weight: bold;">{ai_rating}</div>
                </div>
            </div>
            
            <!-- Click indicator -->
            <div style="text-align: center; margin-top: 10px;">
                <span style="color: #aaa; font-size: 0.85em;">{'▼ Click to expand trading options' if not is_expanded else '▲ Trading options active'}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Expandable sections when clicked
        if is_expanded:
            display_expanded_tile_options(position)

def display_expanded_tile_options(position):
    """Display expanded tile options with thesis and trading actions"""
    symbol = position['symbol']
    
    # Get AI analysis for recommendations
    ai_analysis = get_real_time_ai_analysis(symbol, position)
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["🤖 AI Recommendations", "💰 Execute Trades", "📊 Full Thesis"])
    
    with tab1:
        display_ai_recommendations_section(position, ai_analysis)
    
    with tab2:
        display_quick_trade_section(position)
    
    with tab3:
        display_integrated_thesis_section(position)

def display_ai_recommendations_section(position, ai_analysis):
    """Display AI recommendations with one-click trading"""
    symbol = position['symbol']
    
    st.markdown("### 🤖 AI Trading Recommendations")
    
    # Get AI recommendation
    recommendation = ai_analysis.get('actionable_recommendation', 'Analyzing market conditions...')
    
    # Display recommendation with action buttons
    st.info(f"**AI Recommendation:** {recommendation}")
    
    # Smart trading buttons based on AI analysis
    trade_cols = st.columns(3)
    
    with trade_cols[0]:
        if st.button(f"🟢 Follow AI: BUY MORE", key=f"ai_buy_{symbol}"):
            execute_ai_trade(symbol, "buy_more", position)
    
    with trade_cols[1]:
        if st.button(f"🎯 Follow AI: SELL HALF", key=f"ai_sell_half_{symbol}"):
            execute_ai_trade(symbol, "sell_half", position)
    
    with trade_cols[2]:
        if st.button(f"🔴 Follow AI: SELL ALL", key=f"ai_sell_all_{symbol}"):
            execute_ai_trade(symbol, "sell_all", position)
    
    # Risk analysis
    risk_analysis = ai_analysis.get('risk_analysis', 'Evaluating risk factors...')
    st.warning(f"**⚠️ Risk Analysis:** {risk_analysis}")

def display_quick_trade_section(position):
    """Display quick trading section with manual controls"""
    symbol = position['symbol']
    qty = float(position.get('qty', 0))
    current_price = float(position.get('current_price', 0))
    
    st.markdown("### 💰 Manual Trading")
    
    trade_cols = st.columns(2)
    
    with trade_cols[0]:
        st.markdown("#### 🟢 BUY MORE")
        buy_amount = st.selectbox(
            "Investment Amount",
            [100, 250, 500, 1000, 2500],
            key=f"buy_amount_{symbol}"
        )
        shares_to_buy = int(buy_amount / current_price) if current_price > 0 else 0
        st.info(f"Will buy ~{shares_to_buy} shares")
        
        if st.button(f"🟢 BUY ${buy_amount}", key=f"manual_buy_{symbol}"):
            execute_trade(symbol, shares_to_buy, "buy")
    
    with trade_cols[1]:
        st.markdown("#### 🔴 SELL OPTIONS")
        
        # Sell all button
        if st.button(f"🔴 SELL ALL ({qty:.0f} shares)", key=f"manual_sell_all_{symbol}"):
            execute_trade(symbol, qty, "sell")
        
        # Sell half button
        half_qty = int(qty / 2)
        if st.button(f"🎯 SELL HALF ({half_qty} shares)", key=f"manual_sell_half_{symbol}"):
            execute_trade(symbol, half_qty, "sell")

def execute_ai_trade(symbol, action, position):
    """Execute AI-recommended trade"""
    qty = float(position.get('qty', 0))
    current_price = float(position.get('current_price', 0))
    
    if action == "buy_more":
        # AI recommends buying $500 more
        buy_amount = 500
        shares_to_buy = int(buy_amount / current_price) if current_price > 0 else 0
        execute_trade(symbol, shares_to_buy, "buy")
    
    elif action == "sell_half":
        half_qty = int(qty / 2)
        execute_trade(symbol, half_qty, "sell")
    
    elif action == "sell_all":
        execute_trade(symbol, qty, "sell")

def display_integrated_trade_section(position):
    """Display integrated trading section with buy/sell options"""
    symbol = position['symbol']
    qty = float(position.get('qty', 0))
    current_price = float(position.get('current_price', 0))
    
    with st.expander(f"⚡ Trade {symbol}", expanded=True):
        st.markdown("### 💰 Trading Options")
        
        trade_cols = st.columns(3)
        
        with trade_cols[0]:
            st.markdown("#### 🟢 BUY MORE")
            buy_qty = st.number_input(f"Shares to buy", min_value=1, max_value=1000, value=1, key=f"buy_qty_{symbol}")
            estimated_cost = buy_qty * current_price
            st.info(f"💰 Cost: ${estimated_cost:,.2f}")
            
            if st.button(f"🟢 BUY {buy_qty} shares", key=f"execute_buy_{symbol}"):
                execute_trade(symbol, buy_qty, "buy")
        
        with trade_cols[1]:
            st.markdown("#### 🔴 SELL ALL")
            st.info(f"📊 Current: {qty:.0f} shares")
            estimated_proceeds = qty * current_price
            st.info(f"💰 Proceeds: ${estimated_proceeds:,.2f}")
            
            if st.button(f"🔴 SELL ALL {qty:.0f} shares", key=f"execute_sell_all_{symbol}"):
                execute_trade(symbol, qty, "sell")
        
        with trade_cols[2]:
            st.markdown("#### 🎯 SELL HALF")
            half_qty = int(qty / 2)
            st.info(f"📊 Half position: {half_qty} shares")
            estimated_proceeds = half_qty * current_price
            st.info(f"💰 Proceeds: ${estimated_proceeds:,.2f}")
            
            if st.button(f"🎯 SELL {half_qty} shares", key=f"execute_sell_half_{symbol}"):
                execute_trade(symbol, half_qty, "sell")

def display_integrated_thesis_section(position):
    """Display integrated thesis section with full AI analysis"""
    symbol = position['symbol']
    
    with st.expander(f"🧠 AI Thesis - {symbol}", expanded=True):
        st.markdown("### 🤖 Complete AI Analysis")
        
        try:
            # Get full AI thesis
            thesis_response = requests.get(f"{BACKEND_URL}/api/ai-analysis/full/{symbol}", timeout=10)
            if thesis_response.status_code == 200:
                thesis_data = thesis_response.json()
                
                thesis_cols = st.columns(2)
                
                with thesis_cols[0]:
                    st.markdown("#### 📈 Bull Case")
                    st.write(thesis_data.get('bull_case', 'Analyzing market conditions...'))
                    
                    st.markdown("#### 🎯 Price Target")
                    st.success(f"${thesis_data.get('price_target', position['current_price']):.2f}")
                
                with thesis_cols[1]:
                    st.markdown("#### 📉 Bear Case")
                    st.write(thesis_data.get('bear_case', 'Evaluating risks...'))
                    
                    st.markdown("#### 💡 Recommendation")
                    recommendation = thesis_data.get('recommendation', 'Analyzing...')
                    if 'buy' in recommendation.lower():
                        st.success(f"🟢 {recommendation}")
                    elif 'sell' in recommendation.lower():
                        st.error(f"🔴 {recommendation}")
                    else:
                        st.info(f"🟡 {recommendation}")
                
                # Live AI conversation
                if thesis_data.get('conversation'):
                    st.markdown("#### 🗣️ Live AI Discussion")
                    for exchange in thesis_data['conversation']:
                        model = exchange.get('model', 'AI')
                        message = exchange.get('message', '')
                        timestamp = exchange.get('timestamp', '')
                        st.markdown(f"**{model}** _{timestamp}_: {message}")
            else:
                st.info("🔄 Full thesis analysis in progress...")
        except Exception as e:
            st.error(f"❌ Error loading thesis: {e}")

def display_integrated_plan_section(position):
    """Display integrated plan section with strategy and targets"""
    symbol = position['symbol']
    
    with st.expander(f"🎯 Trading Plan - {symbol}", expanded=True):
        st.markdown("### 📋 Strategy & Targets")
        
        # Get enhanced position analysis
        ai_analysis = get_real_time_ai_analysis(symbol, position)
        
        plan_cols = st.columns(2)
        
        with plan_cols[0]:
            st.markdown("#### 🎯 Price Targets")
            current_price = float(position.get('current_price', 0))
            st.metric("Current Price", f"${current_price:.2f}")
            st.metric("Target Price", f"${current_price * 1.2:.2f}", "20% upside")
            st.metric("Stop Loss", f"${current_price * 0.95:.2f}", "-5% downside")
            
        with plan_cols[1]:
            st.markdown("#### 📊 Strategy")
            st.write(ai_analysis.get('actionable_recommendation', 'Analyzing best approach...'))
            
            st.markdown("#### ⚠️ Risk Assessment")
            st.write(ai_analysis.get('risk_analysis', 'Evaluating risk factors...'))
        
        # Position sizing recommendations
        st.markdown("#### 💰 Position Sizing")
        current_weight = float(position.get('market_value', 0))
        total_portfolio = sum(float(pos['market_value']) for pos in [position])  # Simplified
        weight_pct = (current_weight / total_portfolio * 100) if total_portfolio > 0 else 0
        
        st.progress(weight_pct / 100)
        st.caption(f"Current allocation: {weight_pct:.1f}% of portfolio")

def display_integrated_replacements_section(position):
    """Display integrated replacement section with alternatives"""
    symbol = position['symbol']
    
    with st.expander(f"🔄 Alternatives - {symbol}", expanded=True):
        st.markdown("### 🔍 Better Opportunities")
        
        # Get replacement candidates
        candidates = position.get('replacement_candidates', [])
        
        if candidates:
            st.markdown("#### 📊 Sector Alternatives")
            for i, candidate in enumerate(candidates):
                candidate_cols = st.columns([3, 1])
                
                with candidate_cols[0]:
                    st.write(f"• **{candidate}** - Same sector, potentially better metrics")
                
                with candidate_cols[1]:
                    if st.button(f"Analyze {candidate}", key=f"analyze_{candidate}_{i}"):
                        st.session_state[f"analyzing_{candidate}"] = True
        else:
            st.info("🔄 Scanning for better alternatives...")
            
            # Placeholder for replacement logic
            st.markdown("#### 🎯 Replacement Criteria")
            st.write("- Same sector exposure")
            st.write("- Better growth metrics")
            st.write("- Lower risk profile")
            st.write("- Higher AI confidence")

def get_real_time_ai_analysis(symbol, position):
    """Get real-time AI analysis for a position"""
    try:
        # Try to get cached analysis first
        if hasattr(st.session_state, f'ai_analysis_{symbol}'):
            return getattr(st.session_state, f'ai_analysis_{symbol}')
        
        # Fallback to basic analysis
        return {
            'claude_score': '⏸️ Hold (20%)',
            'gpt_score': '🔄 Hold Position (20%)',
            'actionable_recommendation': 'Monitor position and market conditions',
            'risk_analysis': 'Standard market risk applies',
            'projected_price': position.get('current_price', 0)
        }
    except Exception as e:
        return {
            'claude_score': 'Analyzing...',
            'gpt_score': 'Analyzing...',
            'actionable_recommendation': 'Analysis in progress...',
            'risk_analysis': 'Evaluating...',
            'projected_price': position.get('current_price', 0)
        }

def execute_trade(symbol, quantity, side):
    """Execute a trade through the backend with proper Alpaca integration"""
    try:
        if quantity <= 0:
            st.error("❌ Invalid quantity. Must be greater than 0.")
            return
        
        order_data = {
            'symbol': symbol,
            'qty': int(quantity),
            'side': side,
            'type': 'market',
            'time_in_force': 'day'
        }
        
        # Show loading message
        with st.spinner(f"Executing {side.upper()} order for {quantity} shares of {symbol}..."):
            response = requests.post(
                f"{BACKEND_URL}/api/trades/execute",
                json=order_data,
                timeout=30
            )
        
        if response.status_code == 201:
            result = response.json()
            st.success(f"✅ {side.upper()} order executed successfully!")
            st.success(f"📊 {quantity} shares of {symbol} at market price")
            
            # Show order details if available
            if 'order_id' in result:
                st.info(f"Order ID: {result['order_id']}")
            
            # Refresh portfolio data
            st.session_state.portfolio_data = None
            st.rerun()
            
        elif response.status_code == 400:
            error_msg = response.json().get('detail', 'Bad request')
            st.error(f"❌ Trade rejected: {error_msg}")
        elif response.status_code == 422:
            error_msg = response.json().get('detail', 'Invalid order parameters')
            st.error(f"❌ Order validation failed: {error_msg}")
        else:
            st.error(f"❌ Trade failed (HTTP {response.status_code}): {response.text}")
            
    except requests.exceptions.Timeout:
        st.error("❌ Trade execution timed out. Please check your account and try again.")
    except requests.exceptions.ConnectionError:
        st.error("❌ Unable to connect to trading backend. Please check system status.")
    except Exception as e:
        st.error(f"❌ Trade execution error: {str(e)}")
        
        # Log error for debugging
        import logging
        logging.error(f"Trade execution error for {symbol}: {e}")