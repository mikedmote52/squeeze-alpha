#!/usr/bin/env python3
"""
Growth Maximizer Page - Streamlit interface for the investment growth maximization system
"""

import streamlit as st
import sys
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json

# Add growth system to path  
sys.path.append('../growth_system')

# Configure page
st.set_page_config(
    page_title="Growth Maximizer",
    page_icon="🚀",
    layout="wide"
)

# Safe imports from clean growth_system directory
try:
    sys.path.append('./growth_system')
    from integrated_growth_system import IntegratedGrowthSystem
    system_available = True
except ImportError as e:
    try:
        # Fallback to direct import
        sys.path.append('.')
        from integrated_growth_system import IntegratedGrowthSystem
        system_available = True
    except ImportError:
        system_available = False
        st.error(f"Growth Maximization System not available: {e}")
        st.info("The Growth Maximizer will be available once the system is properly deployed.")

# Page header
st.title("🚀 Growth Maximization System")
st.markdown("**Maximize investment growth over short time periods**")

if system_available:
    # Initialize system
    if 'growth_system' not in st.session_state:
        try:
            st.session_state.growth_system = IntegratedGrowthSystem()
            init_result = st.session_state.growth_system.initialize_system()
            
            if init_result['status'] == 'initialized':
                st.success("✅ Growth Maximization System initialized successfully")
            else:
                st.error(f"❌ System initialization failed: {init_result.get('error', 'Unknown error')}")
                st.stop()
        except Exception as e:
            st.error(f"❌ Error initializing Growth Maximizer: {e}")
            st.info("The Growth Maximizer system will be available once all dependencies are installed.")
            st.stop()
    
    # Main dashboard
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("System Status", "🟢 Active")
        
    with col2:
        st.metric("Goal", "Max Growth")
        
    with col3:
        if st.button("🔄 Run Growth Scan", type="primary"):
            with st.spinner("Scanning for growth opportunities..."):
                result = st.session_state.growth_system.execute_growth_cycle()
                st.session_state.last_scan_result = result
    
    # Display results if available
    if hasattr(st.session_state, 'last_scan_result'):
        result = st.session_state.last_scan_result
        
        if result['status'] == 'success':
            cycle_result = result['cycle_result']
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Opportunities Found",
                    cycle_result['opportunities_found'],
                    delta=None
                )
                
            with col2:
                st.metric(
                    "Trading Signals",
                    len(cycle_result['trading_signals']),
                    delta=None
                )
                
            with col3:
                st.metric(
                    "Expected Growth",
                    f"{cycle_result['expected_growth']:.2%}",
                    delta=None
                )
                
            with col4:
                risk_color = {
                    'low': '🟢',
                    'medium': '🟡',
                    'high': '🔴'
                }
                st.metric(
                    "Portfolio Risk",
                    f"{risk_color.get(cycle_result['risk_assessment'], '🟡')} {cycle_result['risk_assessment'].upper()}",
                    delta=None
                )
            
            # Top opportunities
            st.subheader("🏆 Top Growth Opportunities")
            
            if cycle_result['top_opportunities']:
                opportunities_df = pd.DataFrame(cycle_result['top_opportunities'])
                
                # Create opportunities table
                display_df = opportunities_df[[
                    'symbol', 'growth_score', 'confidence', 'entry_price', 
                    'target_price', 'risk_level', 'timeframe'
                ]].copy()
                
                display_df['growth_score'] = display_df['growth_score'].round(1)
                display_df['confidence'] = (display_df['confidence'] * 100).round(1)
                display_df['entry_price'] = display_df['entry_price'].round(2)
                display_df['target_price'] = display_df['target_price'].round(2)
                display_df['potential_return'] = ((display_df['target_price'] - display_df['entry_price']) / display_df['entry_price'] * 100).round(2)
                
                # Rename columns for display
                display_df.columns = [
                    'Symbol', 'Growth Score', 'Confidence %', 'Entry Price', 
                    'Target Price', 'Risk Level', 'Timeframe', 'Potential Return %'
                ]
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    column_config={
                        'Growth Score': st.column_config.ProgressColumn(
                            'Growth Score',
                            min_value=0,
                            max_value=100,
                            format='%.1f'
                        ),
                        'Confidence %': st.column_config.ProgressColumn(
                            'Confidence %',
                            min_value=0,
                            max_value=100,
                            format='%.1f%%'
                        ),
                        'Potential Return %': st.column_config.NumberColumn(
                            'Potential Return %',
                            format='%.2f%%'
                        )
                    }
                )
                
                # Growth score chart
                fig = px.bar(
                    opportunities_df,
                    x='symbol',
                    y='growth_score',
                    title='Growth Scores by Symbol',
                    color='confidence',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    xaxis_title="Symbol",
                    yaxis_title="Growth Score",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.info("No growth opportunities found in the current market conditions")
            
            # Trading signals
            st.subheader("📊 Trading Signals")
            
            if cycle_result['trading_signals']:
                signals_df = pd.DataFrame(cycle_result['trading_signals'])
                
                # Create signals table
                display_signals = signals_df[[
                    'symbol', 'action', 'quantity', 'signal_strength', 'expected_return'
                ]].copy()
                
                display_signals['quantity'] = display_signals['quantity'].round(2)
                display_signals['expected_return'] = (display_signals['expected_return'] * 100).round(2)
                
                # Rename columns
                display_signals.columns = [
                    'Symbol', 'Action', 'Quantity', 'Signal Strength', 'Expected Return %'
                ]
                
                st.dataframe(
                    display_signals,
                    use_container_width=True,
                    column_config={
                        'Expected Return %': st.column_config.NumberColumn(
                            'Expected Return %',
                            format='%.2f%%'
                        )
                    }
                )
                
                # Signal strength distribution
                strength_counts = signals_df['signal_strength'].value_counts()
                fig = px.pie(
                    values=strength_counts.values,
                    names=strength_counts.index,
                    title='Signal Strength Distribution'
                )
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.info("No trading signals generated")
            
            # Portfolio allocation
            st.subheader("📈 Portfolio Allocation")
            
            if cycle_result['portfolio_allocation']:
                allocation_data = []
                for symbol, shares in cycle_result['portfolio_allocation'].items():
                    # Find the corresponding opportunity
                    opp = next((o for o in cycle_result['top_opportunities'] if o['symbol'] == symbol), None)
                    if opp:
                        allocation_data.append({
                            'symbol': symbol,
                            'shares': shares,
                            'entry_price': opp['entry_price'],
                            'allocation_value': shares * opp['entry_price']
                        })
                
                if allocation_data:
                    allocation_df = pd.DataFrame(allocation_data)
                    
                    # Allocation pie chart
                    fig = px.pie(
                        allocation_df,
                        values='allocation_value',
                        names='symbol',
                        title='Portfolio Allocation by Value'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Allocation table
                    display_allocation = allocation_df.copy()
                    display_allocation['shares'] = display_allocation['shares'].round(2)
                    display_allocation['entry_price'] = display_allocation['entry_price'].round(2)
                    display_allocation['allocation_value'] = display_allocation['allocation_value'].round(2)
                    display_allocation['allocation_percent'] = (display_allocation['allocation_value'] / display_allocation['allocation_value'].sum() * 100).round(2)
                    
                    display_allocation.columns = [
                        'Symbol', 'Shares', 'Entry Price', 'Allocation Value', 'Allocation %'
                    ]
                    
                    st.dataframe(display_allocation, use_container_width=True)
                    
            else:
                st.info("No portfolio allocation available")
                
        else:
            st.error(f"Growth scan failed: {result.get('error', 'Unknown error')}")
    
    # Performance dashboard
    st.subheader("📊 Performance Dashboard")
    
    try:
        dashboard_data = st.session_state.growth_system.get_performance_dashboard()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.json({
                "System Status": dashboard_data['system_status'],
                "Goal": dashboard_data['goal'],
                "Last Scan": dashboard_data['last_scan'],
                "Total Scans": dashboard_data['total_scans']
            })
            
        with col2:
            st.json({
                "Risk Limits": dashboard_data['risk_limits'],
                "Recent Trends": dashboard_data['recent_trends']
            })
            
    except Exception as e:
        st.error(f"Could not load performance dashboard: {e}")
    
    # System information
    with st.expander("ℹ️ System Information"):
        st.markdown("""
        ### Growth Maximization System
        
        **🛡️ ZERO MOCK DATA POLICY ENFORCED**
        
        This system is designed to maximize investment growth over short time periods by:
        
        1. **Scanning** for high-growth opportunities in real-time using REAL market data
        2. **Analyzing** market data using technical indicators from REAL sources
        3. **Optimizing** position sizes for maximum growth potential with REAL portfolio data
        4. **Managing** risk while pursuing aggressive growth targets
        
        #### Key Features:
        - Real-time opportunity discovery (NO MOCK DATA)
        - Technical analysis integration (REAL indicators only)
        - Position size optimization (REAL portfolio values)
        - Risk management controls
        - Performance tracking (REAL results only)
        
        #### Risk Management:
        - Maximum 25% position size per stock
        - Maximum 5% daily loss limit
        - 15% growth target per cycle
        - Diversification across opportunities
        
        #### Data Sources:
        - **Market Data**: Real Alpaca API, Polygon, Alpha Vantage
        - **Portfolio Data**: Real brokerage account values
        - **Technical Indicators**: Calculated from real price data
        - **NO MOCK DATA**: System will show empty results if real data unavailable
        """)
        
else:
    st.error("Growth Maximization System is not available. Please check the system configuration.")
    st.stop()