#!/usr/bin/env python3
"""
Portfolio Dashboard - Real-time portfolio visualization
ZERO MOCK DATA - All real Alpaca portfolio data
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime, timedelta
import sys
import os

# Add core modules to path
sys.path.append('./core')
sys.path.append('..')

# Import the new integrated tiles
from integrated_portfolio_tiles import display_integrated_portfolio_tiles

# Backend URL configuration - connect to your real backend service
BACKEND_URL = os.getenv('BACKEND_URL', 'https://squeeze-alpha.onrender.com')

st.set_page_config(
    page_title="Portfolio Dashboard", 
    page_icon="🏠", 
    layout="wide"
)

def load_portfolio_data():
    """Load real portfolio data directly from Alpaca API"""
    # Use direct Alpaca API - skip backend entirely
    from direct_alpaca_service import get_real_portfolio_positions
    return get_real_portfolio_positions()

def create_portfolio_pie_chart(positions):
    """Create portfolio allocation pie chart"""
    if not positions:
        return None
    
    # Calculate allocations
    allocations = {}
    for pos in positions:
        allocations[pos['symbol']] = pos['market_value']
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=list(allocations.keys()),
        values=list(allocations.values()),
        hole=0.3,
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        title="Portfolio Allocation",
        showlegend=True,
        height=400,
        font=dict(size=12)
    )
    
    return fig

def create_performance_chart(positions):
    """Create performance bar chart"""
    if not positions:
        return None
    
    # Prepare data
    symbols = [pos['symbol'] for pos in positions]
    pl_amounts = [pos['unrealized_pl'] for pos in positions]
    pl_percentages = [pos['unrealized_plpc'] for pos in positions]
    
    # Create bar chart
    fig = go.Figure()
    
    # Add bars with colors based on performance
    colors = ['green' if pl >= 0 else 'red' for pl in pl_amounts]
    
    fig.add_trace(go.Bar(
        x=symbols,
        y=pl_amounts,
        marker_color=colors,
        text=[f"${pl:,.0f}<br>({pl_pct:.1f}%)" for pl, pl_pct in zip(pl_amounts, pl_percentages)],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>P&L: $%{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Position P&L",
        xaxis_title="Symbol",
        yaxis_title="Unrealized P&L ($)",
        height=400,
        showlegend=False
    )
    
    # Add horizontal line at zero
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    return fig

def display_position_details(positions):
    """Display positions using new integrated tiles with all data inside"""
    # Use the new integrated tiles instead of old display
    portfolio_data = {'positions': positions}
    display_integrated_portfolio_tiles(portfolio_data)
    return

def display_portfolio_optimization_summary(positions):
    """Display AI-powered portfolio optimization recommendations with one-click execution"""
    st.subheader("🧠 AI Portfolio Optimization")
    st.markdown("*AI analysis of your portfolio with recommended optimizations*")
    
    # Get portfolio optimization analysis
    try:
        optimization_response = requests.post(
            f"{BACKEND_URL}/api/portfolio/optimization-analysis",
            json={'positions': positions},
            timeout=10
        )
        
        if optimization_response.status_code == 200:
            optimization_data = optimization_response.json()
            st.success("✅ Portfolio optimization analysis complete!")
            # Display optimization results here
        else:
            st.warning("⚠️ Unable to load optimization analysis")
            
    except Exception as e:
        st.error(f"❌ Error loading optimization: {e}")

def generate_local_optimization_analysis(positions):
    """Generate portfolio optimization analysis using local AI logic"""
    recommendations = []
    total_value = sum(pos['market_value'] for pos in positions)
    
    for pos in positions:
        symbol = pos['symbol']
        pl_pct = pos['unrealized_plpc']
        weight = pos['market_value'] / total_value * 100
        current_price = pos['current_price']
        purchase_price = pos['avg_entry_price']
        
        # AGGRESSIVE 60% MONTHLY TARGETING: Much stricter criteria
        # Cut losses at 5% instead of 10%+ for aggressive reallocation
        if current_price < purchase_price * 0.95:  # Down 5%+
            recommendations.append({
                'action': 'SELL',
                'symbol': symbol,
                'reasoning': f'Position down 5%+, reallocate to explosive winners (bought at ${purchase_price:.2f})',
                'priority': 'high'
            })
            continue
        
        # AGGRESSIVE 60% MONTHLY TARGETING: More sensitive profit/loss management
        if pl_pct < -5:  # Much more aggressive loss cutting
            recommendations.append({
                'action': 'SELL',
                'symbol': symbol,
                'reasoning': f'Cut losses aggressively ({pl_pct:.1f}%) - find explosive winners',
                'priority': 'high'
            })
        elif pl_pct > 25 and weight > 15:  # Take profits faster
            recommendations.append({
                'action': 'REDUCE',
                'symbol': symbol,
                'reasoning': f'Strong gains ({pl_pct:.1f}%) - secure profits, find next explosive play',
                'priority': 'medium'
            })
        elif weight > 25:  # Lower concentration threshold
            recommendations.append({
                'action': 'REDUCE',
                'symbol': symbol,
                'reasoning': f'Over-concentrated ({weight:.1f}%) - diversify into more explosive opportunities',
                'priority': 'high'
            })
        elif pl_pct > 20 and weight < 5:  # Increase winning positions
            recommendations.append({
                'action': 'BUY',
                'symbol': symbol,
                'reasoning': f'Explosive performer ({pl_pct:.1f}%) - increase allocation for 60% monthly target',
                'priority': 'high'
            })
    
    # Sort by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 2))
    
    # Calculate expected improvement
    high_priority_actions = len([r for r in recommendations if r.get('priority') == 'high'])
    expected_improvement = high_priority_actions * 2.5  # Rough estimate
    
    return {
        'recommendations': recommendations,
        'expected_improvement': expected_improvement,
        'risk_level': 'HIGH' if high_priority_actions > 2 else 'MEDIUM' if high_priority_actions > 0 else 'LOW',
        'analysis_timestamp': datetime.now().isoformat()
    }

def execute_portfolio_optimization(optimization_data):
    """Execute the portfolio optimization recommendations via Alpaca API with aggressive memory logging"""
    st.warning("🚀 **Executing Aggressive Portfolio Optimization for 60% Monthly Returns...**")
    
    recommendations = optimization_data.get('recommendations', [])
    
    if not recommendations:
        st.info("✅ No optimizations needed - portfolio is already well-balanced!")
        return
    
    # Import aggressive memory system
    import sys
    sys.path.append('./core')
    from aggressive_portfolio_memory import aggressive_memory
    
    # Execute each recommendation
    executed_trades = []
    
    for rec in recommendations:
        action = rec.get('action')
        symbol = rec.get('symbol')
        
        try:
            # Log decision to aggressive memory for learning
            current_price = rec.get('current_price', 0)
            purchase_price = rec.get('purchase_price', 0)
            
            aggressive_memory.log_position_decision(
                symbol=symbol,
                action=action,
                reasoning=rec.get('reasoning'),
                current_price=current_price,
                purchase_price=purchase_price,
                expected_return=25.0 if action == 'BUY' else -5.0 if action == 'SELL' else 0
            )
            
            # Prepare trade order for Alpaca API
            trade_data = {
                'symbol': symbol,
                'action': action,
                'reasoning': rec.get('reasoning'),
                'priority': rec.get('priority', 'medium')
            }
            
            # Call backend to execute trade
            trade_response = requests.post(
                f"{BACKEND_URL}/api/trades/execute-optimization",
                json=trade_data,
                timeout=10
            )
            
            if trade_response.status_code == 200:
                result = trade_response.json()
                executed_trades.append({
                    'symbol': symbol,
                    'action': action,
                    'status': 'success',
                    'order_id': result.get('order_id', 'N/A')
                })
                st.success(f"✅ {action} order submitted for {symbol}")
            else:
                st.error(f"❌ Failed to execute {action} for {symbol}")
                
        except Exception as e:
            st.error(f"❌ Error executing {action} for {symbol}: {str(e)}")
    
    # Summary
    if executed_trades:
        st.success(f"🎯 **Optimization Complete!** {len(executed_trades)} trades executed successfully.")
        
        # Show trade summary
        with st.expander("📋 Trade Summary", expanded=True):
            for trade in executed_trades:
                st.write(f"• **{trade['action']} {trade['symbol']}** - Order ID: {trade['order_id']}")
    else:
        st.warning("⚠️ No trades were executed. Please check your account settings or try again.")

def display_portfolio_optimization_summary(positions):
    """Display AI-powered portfolio optimization recommendations with one-click execution"""
    st.subheader("🧠 AI Portfolio Optimization")
    st.markdown("*AI analysis of your portfolio with recommended optimizations*")
    
    # Get portfolio optimization analysis
    try:
        optimization_response = requests.post(
            f"{BACKEND_URL}/api/portfolio/optimization-analysis",
            json={'positions': positions},
            timeout=10
        )
        
        if optimization_response.status_code == 200:
            optimization_data = optimization_response.json()
        else:
            # Fallback to local analysis if backend endpoint doesn't exist
            optimization_data = generate_local_optimization_analysis(positions)
    except:
        # Fallback to local analysis
        optimization_data = generate_local_optimization_analysis(positions)
    
    # Display optimization summary
    opt_col1, opt_col2 = st.columns([2, 1])
    
    with opt_col1:
        st.markdown("### 📊 Recommended Changes")
        
        recommendations = optimization_data.get('recommendations', [])
        for i, rec in enumerate(recommendations[:5], 1):  # Show top 5 recommendations
            action_type = rec.get('action', 'HOLD')
            symbol = rec.get('symbol', 'N/A')
            reasoning = rec.get('reasoning', 'No reasoning provided')
            
            # Color code by action type
            if action_type == 'SELL':
                action_color = "🔴"
            elif action_type == 'BUY':
                action_color = "🟢"
            elif action_type == 'REDUCE':
                action_color = "🟡"
            else:
                action_color = "🔵"
            
            st.markdown(f"""
            **{i}. {action_color} {action_type} {symbol}**
            *{reasoning}*
            """)
        
        # Expected portfolio improvement
        expected_gain = optimization_data.get('expected_improvement', 0)
        if expected_gain > 0:
            st.success(f"🎯 **Expected Improvement:** +{expected_gain:.1f}% portfolio performance")
        elif expected_gain < 0:
            st.warning(f"⚠️ **Risk Reduction:** {expected_gain:.1f}% volatility reduction")
        else:
            st.info("📊 **Portfolio Status:** Currently well-optimized")
    
    with opt_col2:
        st.markdown("### ⚡ Quick Execute")
        
        # One-click optimization button
        if st.button("🚀 Execute All Optimizations", type="primary", key="execute_optimization"):
            execute_portfolio_optimization(optimization_data)
        
        # Risk level indicator
        risk_level = optimization_data.get('risk_level', 'MEDIUM')
        if risk_level == 'HIGH':
            st.error("⚠️ High Risk Changes")
        elif risk_level == 'LOW':
            st.success("✅ Low Risk Changes")
        else:
            st.warning("⚖️ Medium Risk Changes")
        
        # Show estimated costs
        estimated_trades = len(optimization_data.get('recommendations', []))
        estimated_fees = estimated_trades * 0.00  # Alpaca is commission-free
        st.info(f"📋 **{estimated_trades} trades** • ${estimated_fees:.2f} fees")

def main():
    """Main portfolio dashboard"""
    
    st.title("🏠 Portfolio Dashboard")
    st.markdown("Real-time view of your Alpaca trading portfolio")
    
    # Load portfolio data
    with st.spinner("Loading real portfolio data..."):
        portfolio_data = load_portfolio_data()
    
    if not portfolio_data:
        st.error("❌ Unable to load portfolio data. Check backend connection.")
        st.info("Make sure the backend is running: `python real_ai_backend.py`")
        return
    
    positions = portfolio_data.get('positions', [])
    performance = portfolio_data.get('performance', {})
    
    if not positions:
        st.warning("📊 No positions found in your portfolio.")
        st.info("Your Alpaca account appears to have no current holdings.")
        return
    
    # Portfolio summary metrics
    st.subheader("💰 Portfolio Summary")
    
    # Calculate totals
    total_value = sum(pos['market_value'] for pos in positions)
    total_pl = sum(pos['unrealized_pl'] for pos in positions)
    total_pl_pct = (total_pl / (total_value - total_pl)) * 100 if total_value > total_pl else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Value",
            f"${total_value:,.2f}",
            delta=f"${total_pl:,.2f}"
        )
    
    with col2:
        st.metric(
            "Day P&L",
            f"${total_pl:,.2f}",
            delta=f"{total_pl_pct:.2f}%"
        )
    
    with col3:
        winners = len([p for p in positions if p['unrealized_pl'] > 0])
        st.metric(
            "Winning Positions",
            f"{winners}",
            delta=f"of {len(positions)} total"
        )
    
    with col4:
        win_rate = (winners / len(positions)) * 100 if positions else 0
        st.metric(
            "Win Rate",
            f"{win_rate:.1f}%"
        )
    
    st.divider()
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        # Portfolio allocation pie chart
        pie_chart = create_portfolio_pie_chart(positions)
        if pie_chart:
            st.plotly_chart(pie_chart, use_container_width=True)
    
    with col2:
        # Performance bar chart
        perf_chart = create_performance_chart(positions)
        if perf_chart:
            st.plotly_chart(perf_chart, use_container_width=True)
    
    st.divider()
    
    # Detailed position table
    display_position_details(positions)
    
    st.divider()
    
    # Portfolio Optimization Summary
    display_portfolio_optimization_summary(positions)
    
    # Data source and refresh info
    st.caption(f"Data source: {portfolio_data.get('source', 'Unknown')} | Last updated: {portfolio_data.get('last_updated', 'Unknown')}")
    
    # Refresh button
    if st.button("🔄 Refresh Portfolio Data", type="primary"):
        st.rerun()

if __name__ == "__main__":
    main()