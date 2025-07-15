#!/usr/bin/env python3
"""
Portfolio Memory - AI Learning and Thesis Validation
ZERO MOCK DATA - All real memory analysis and learning
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import json
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Portfolio Memory",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .memory-card {
        border: 1px solid #00D4AA;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: rgba(0, 212, 170, 0.1);
    }
    
    .challenge-high {
        border-left: 5px solid #ef4444;
        background: rgba(239, 68, 68, 0.1);
    }
    
    .challenge-medium {
        border-left: 5px solid #f59e0b;
        background: rgba(245, 158, 11, 0.1);
    }
    
    .challenge-low {
        border-left: 5px solid #10b981;
        background: rgba(16, 185, 129, 0.1);
    }
    
    .move-buy {
        border-left: 5px solid #10b981;
        background: rgba(16, 185, 129, 0.1);
    }
    
    .move-sell {
        border-left: 5px solid #ef4444;
        background: rgba(239, 68, 68, 0.1);
    }
    
    .move-hold {
        border-left: 5px solid #6b7280;
        background: rgba(107, 114, 128, 0.1);
    }
</style>
""", unsafe_allow_html=True)

def check_backend_connection():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return response.status_code == 200
    except:
        return False

def save_daily_snapshot():
    """Save daily portfolio snapshot"""
    try:
        response = requests.post("http://localhost:8000/api/memory/daily-snapshot", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Backend error: {response.status_code}"}
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}

def get_thesis_challenges():
    """Get AI thesis challenges"""
    try:
        response = requests.get("http://localhost:8000/api/memory/thesis-challenges", timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return {"challenges": [], "error": f"Backend error: {response.status_code}"}
    except Exception as e:
        return {"challenges": [], "error": f"Connection error: {str(e)}"}

def get_portfolio_moves():
    """Get recommended portfolio moves"""
    try:
        response = requests.get("http://localhost:8000/api/memory/next-moves", timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return {"moves": [], "error": f"Backend error: {response.status_code}"}
    except Exception as e:
        return {"moves": [], "error": f"Connection error: {str(e)}"}

def get_memory_summary(days=30):
    """Get portfolio memory summary"""
    try:
        response = requests.get(f"http://localhost:8000/api/memory/summary?days={days}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"memory_summary": {}, "error": f"Backend error: {response.status_code}"}
    except Exception as e:
        return {"memory_summary": {}, "error": f"Connection error: {str(e)}"}

def memory_enhanced_analysis(symbol, context="Portfolio memory analysis"):
    """Run memory-enhanced AI analysis"""
    try:
        payload = {"symbol": symbol, "context": context}
        response = requests.post("http://localhost:8000/api/ai-analysis-with-memory", 
                               json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Backend error: {response.status_code}"}
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}

def display_header():
    """Display page header"""
    st.markdown("# 🧠 Portfolio Memory & Learning")
    
    # Backend status
    backend_online = check_backend_connection()
    if backend_online:
        st.success("✅ Backend connected - Memory system operational")
    else:
        st.error("❌ Backend offline - Start real_ai_backend.py")
        return False
    
    st.markdown("---")
    return True

def display_memory_controls():
    """Display memory system controls"""
    st.subheader("📊 Memory System Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Daily Snapshot", use_container_width=True):
            with st.spinner("Saving daily snapshot..."):
                result = save_daily_snapshot()
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.success(f"✅ {result['message']}")
    
    with col2:
        days_back = st.selectbox("Memory Period", [7, 14, 30, 60, 90], index=2)
    
    with col3:
        st.metric("Analysis Period", f"{days_back} days")
    
    return days_back

def display_thesis_challenges():
    """Display AI thesis challenges"""
    st.subheader("🎯 AI Thesis Challenges")
    
    with st.spinner("Challenging AI thesis for all positions..."):
        challenges_data = get_thesis_challenges()
    
    if "error" in challenges_data:
        st.error(f"Error loading thesis challenges: {challenges_data['error']}")
        return
    
    challenges = challenges_data.get('challenges', [])
    
    if not challenges:
        st.info("No thesis challenges available - Portfolio positions may be new")
        return
    
    # Display challenges
    for challenge in challenges:
        accuracy = challenge['accuracy_score']
        confidence = challenge['confidence']
        
        # Determine challenge level
        if accuracy < 30:
            challenge_class = "challenge-high"
            challenge_level = "🔴 HIGH CHALLENGE"
        elif accuracy < 60:
            challenge_class = "challenge-medium"
            challenge_level = "🟡 MEDIUM CHALLENGE"
        else:
            challenge_class = "challenge-low"
            challenge_level = "🟢 LOW CHALLENGE"
        
        with st.container():
            st.markdown(f"""
            <div class="memory-card {challenge_class}">
                <h4>{challenge['ticker']} - {challenge_level}</h4>
                <p><strong>Accuracy Score:</strong> {accuracy:.1f}%</p>
                <p><strong>Performance Since Thesis:</strong> {challenge['performance_since_thesis']:+.1f}%</p>
                <p><strong>Recommended Action:</strong> {challenge['recommended_action']}</p>
                <p><strong>Challenge Reasoning:</strong> {challenge['challenge_reasoning']}</p>
                <p><strong>Original Thesis:</strong> {challenge['original_thesis'][:100]}...</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add action buttons
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                if st.button(f"🤖 Memory Analysis", key=f"analyze_{challenge['ticker']}"):
                    run_memory_analysis(challenge['ticker'])
            with col2:
                if st.button(f"📊 Deep Dive", key=f"dive_{challenge['ticker']}"):
                    st.session_state[f"show_details_{challenge['ticker']}"] = True
    
    # Summary metrics
    if challenges:
        avg_accuracy = sum(c['accuracy_score'] for c in challenges) / len(challenges)
        high_challenges = len([c for c in challenges if c['accuracy_score'] < 30])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Thesis Accuracy", f"{avg_accuracy:.1f}%")
        with col2:
            st.metric("High Challenge Positions", high_challenges)
        with col3:
            st.metric("Total Positions Analyzed", len(challenges))

def display_portfolio_moves():
    """Display recommended portfolio moves"""
    st.subheader("🎯 Recommended Portfolio Moves")
    
    with st.spinner("Analyzing portfolio for optimal moves..."):
        moves_data = get_portfolio_moves()
    
    if "error" in moves_data:
        st.error(f"Error loading portfolio moves: {moves_data['error']}")
        return
    
    moves = moves_data.get('moves', [])
    
    if not moves:
        st.info("No specific portfolio moves recommended at this time")
        return
    
    # Sort moves by priority and confidence
    moves.sort(key=lambda x: (x['priority'], x['confidence_score']), reverse=True)
    
    for i, move in enumerate(moves[:5]):  # Show top 5 moves
        action_type = move['action_type']
        
        # Determine move styling
        if action_type == "BUY":
            move_class = "move-buy"
            action_emoji = "📈"
        elif action_type == "SELL":
            move_class = "move-sell"
            action_emoji = "📉"
        else:
            move_class = "move-hold"
            action_emoji = "⚖️"
        
        with st.container():
            st.markdown(f"""
            <div class="memory-card {move_class}">
                <h4>{action_emoji} {action_type} {move['ticker']} (Priority {move['priority']})</h4>
                <p><strong>Confidence:</strong> {move['confidence_score']:.1f}%</p>
                <p><strong>Reasoning:</strong> {move['reasoning']}</p>
                <p><strong>Risk Assessment:</strong> {move['risk_assessment']}</p>
                <p><strong>Expected Outcome:</strong> {move['expected_outcome']}</p>
                <p><strong>Historical Evidence:</strong> {'; '.join(move['historical_evidence'])}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Action button
            if st.button(f"Execute {action_type} {move['ticker']}", key=f"execute_{i}"):
                st.warning(f"⚠️ Would execute {action_type} for {move['ticker']} - Manual approval required")

def display_memory_summary(days_back):
    """Display portfolio memory summary"""
    st.subheader(f"📈 Portfolio Memory Summary ({days_back} days)")
    
    with st.spinner("Loading memory summary..."):
        summary_data = get_memory_summary(days_back)
    
    if "error" in summary_data:
        st.error(f"Error loading memory summary: {summary_data['error']}")
        return
    
    memory_summary = summary_data.get('memory_summary', {})
    
    if not memory_summary:
        st.info("No memory data available - System is learning from your portfolio")
        return
    
    # Performance trend chart
    performance_trend = memory_summary.get('performance_trend', [])
    if performance_trend:
        df = pd.DataFrame(performance_trend)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['pl_pct'],
            mode='lines+markers',
            name='Portfolio P&L %',
            line=dict(color='#00D4AA', width=3)
        ))
        
        fig.update_layout(
            title="Portfolio Performance Trend",
            xaxis_title="Date",
            yaxis_title="P&L %",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Snapshots Recorded", memory_summary.get('snapshots_count', 0))
    with col2:
        thesis_challenges = memory_summary.get('thesis_challenges', [])
        st.metric("Thesis Challenges", len(thesis_challenges))
    with col3:
        portfolio_moves = memory_summary.get('portfolio_moves', [])
        st.metric("Portfolio Moves", len(portfolio_moves))
    with col4:
        executed_moves = len([m for m in portfolio_moves if m.get('executed', False)])
        st.metric("Executed Moves", executed_moves)

def run_memory_analysis(symbol):
    """Run memory-enhanced analysis for a symbol"""
    st.subheader(f"🧠 Memory-Enhanced Analysis: {symbol}")
    
    with st.spinner(f"Running memory-enhanced analysis for {symbol}..."):
        analysis_result = memory_enhanced_analysis(symbol)
    
    if "error" in analysis_result:
        st.error(f"Analysis failed: {analysis_result['error']}")
        return
    
    # Display historical context
    if 'historical_context' in analysis_result:
        historical = analysis_result['historical_context']
        
        st.markdown("### 📚 Historical Memory Context")
        
        col1, col2 = st.columns(2)
        
        with col1:
            decision_summary = historical.get('decision_summary', {})
            st.write("**Decision History:**")
            st.write(f"- Total decisions: {decision_summary.get('total_decisions', 0)}")
            st.write(f"- Most recent action: {decision_summary.get('most_recent_action', 'None')}")
            st.write(f"- Average confidence: {decision_summary.get('avg_confidence', 0):.1f}")
        
        with col2:
            performance_summary = historical.get('performance_summary', {})
            st.write("**Performance History:**")
            st.write(f"- Average return: {performance_summary.get('avg_actual_return', 0):.1f}%")
            st.write(f"- Win rate: {performance_summary.get('win_rate', 0):.1f}%")
            st.write(f"- Outcomes tracked: {performance_summary.get('outcomes_tracked', 0)}")
        
        # Key lessons
        key_lessons = historical.get('key_lessons', [])
        if key_lessons:
            st.markdown("### 💡 Key Lessons Learned")
            for lesson in key_lessons:
                st.write(f"• {lesson}")
        
        # Current recommendation
        current_rec = historical.get('current_recommendation', '')
        if current_rec:
            st.markdown("### 🎯 Memory-Based Recommendation")
            st.info(current_rec)
    
    # Display AI agents analysis
    if 'agents' in analysis_result:
        st.markdown("### 🤖 Multi-AI Analysis (Memory Enhanced)")
        
        agents = analysis_result['agents']
        tabs = st.tabs([agent['name'] for agent in agents])
        
        for i, agent in enumerate(agents):
            with tabs[i]:
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    confidence = agent.get('confidence', 0)
                    st.metric("Confidence", f"{confidence*100:.0f}%")
                
                with col2:
                    st.write("**Analysis:**")
                    st.write(agent.get('reasoning', 'No reasoning provided'))

def main():
    """Main memory page"""
    if not display_header():
        return
    
    # Memory controls
    days_back = display_memory_controls()
    
    st.markdown("---")
    
    # Two column layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        display_thesis_challenges()
    
    with col2:
        display_portfolio_moves()
    
    st.markdown("---")
    
    # Memory summary
    display_memory_summary(days_back)
    
    # Handle memory analysis requests
    for key in st.session_state:
        if key.startswith("show_details_"):
            ticker = key.replace("show_details_", "")
            run_memory_analysis(ticker)
            del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()