#!/usr/bin/env python3
"""
Pre-Market AI Analysis System
Uses collaborative AI to analyze explosive opportunities for the day
"""

import asyncio
import requests
from datetime import datetime
from typing import List, Dict, Any
import sys
import os

# Add core to path
sys.path.append('./core')

async def run_premarket_collaborative_analysis() -> Dict[str, Any]:
    """Run pre-market analysis using collaborative AI system"""
    
    from collaborative_ai_system import CollaborativeAISystem
    from explosive_catalyst_discovery import ExplosiveCatalystDiscovery
    
    print("🌅 STARTING PRE-MARKET COLLABORATIVE AI ANALYSIS")
    print("=" * 60)
    
    # Initialize systems
    collaborative_ai = CollaborativeAISystem()
    catalyst_discovery = ExplosiveCatalystDiscovery()
    
    # Step 1: Discover explosive opportunities
    print("🔍 Step 1: Discovering explosive catalyst opportunities...")
    explosive_opportunities = await catalyst_discovery.discover_explosive_opportunities()
    
    if not explosive_opportunities:
        return {
            "analysis_complete": True,
            "opportunities_found": 0,
            "message": "No explosive opportunities found in pre-market scan",
            "timestamp": datetime.now().isoformat()
        }
    
    print(f"✅ Found {len(explosive_opportunities)} explosive opportunities")
    
    # Step 2: Run collaborative analysis on top opportunities
    detailed_analyses = []
    
    # Analyze top 3 opportunities in detail
    top_opportunities = explosive_opportunities[:3]
    
    for i, opp in enumerate(top_opportunities, 1):
        ticker = opp['ticker']
        catalyst_type = opp['catalyst_type']
        
        print(f"🤖 Step {i+1}: Collaborative AI analysis for {ticker} ({catalyst_type})")
        
        context = f"""Pre-market analysis for explosive {catalyst_type} opportunity.
        
Market Cap: ${opp['market_cap']:,.0f}
Current Price: ${opp['current_price']:.2f}
Opportunity Score: {opp['opportunity_score']:.0f}%
Catalyst Type: {catalyst_type}

Focus on explosive potential for today's trading session."""
        
        # Run collaborative analysis
        conversation_result = await collaborative_ai.run_collaborative_analysis(ticker, context)
        
        detailed_analyses.append({
            "ticker": ticker,
            "opportunity_data": opp,
            "collaborative_analysis": conversation_result,
            "recommendation": conversation_result['final_recommendation']
        })
    
    # Step 3: Generate pre-market summary
    premarket_summary = generate_premarket_summary(detailed_analyses)
    
    # Save complete analysis
    analysis_result = {
        "analysis_complete": True,
        "analysis_timestamp": datetime.now().isoformat(),
        "opportunities_discovered": len(explosive_opportunities),
        "detailed_analyses": len(detailed_analyses),
        "top_opportunities": detailed_analyses,
        "all_opportunities": explosive_opportunities,
        "premarket_summary": premarket_summary,
        "source": "Pre-Market Collaborative AI Analysis"
    }
    
    # Save to file for morning review
    save_premarket_analysis(analysis_result)
    
    return analysis_result

def generate_premarket_summary(detailed_analyses: List[Dict[str, Any]]) -> str:
    """Generate human-readable pre-market summary"""
    
    if not detailed_analyses:
        return "No explosive opportunities identified for today's session."
    
    summary_parts = []
    summary_parts.append("🚀 PRE-MARKET AI CONSENSUS ANALYSIS")
    summary_parts.append("=" * 50)
    
    for i, analysis in enumerate(detailed_analyses, 1):
        ticker = analysis['ticker']
        opp_data = analysis['opportunity_data']
        catalyst_type = opp_data['catalyst_type']
        opportunity_score = opp_data['opportunity_score']
        current_price = opp_data['current_price']
        
        # Extract consensus from final recommendation
        final_rec = analysis['collaborative_analysis']['final_recommendation']
        confidence = final_rec.get('confidence', 0.5)
        
        summary_parts.append(f"\n{i}. {ticker} - {catalyst_type}")
        summary_parts.append(f"   💰 Price: ${current_price:.2f}")
        summary_parts.append(f"   🎯 Opportunity Score: {opportunity_score:.0f}%")
        summary_parts.append(f"   🤖 AI Confidence: {confidence*100:.0f}%")
        
        # Extract key insights from reasoning
        reasoning = final_rec.get('reasoning', '')
        if 'BUY' in reasoning.upper() or 'APPROVED' in reasoning.upper():
            summary_parts.append(f"   ✅ AI CONSENSUS: APPROVED")
        elif 'AVOID' in reasoning.upper() or 'REJECT' in reasoning.upper():
            summary_parts.append(f"   ❌ AI CONSENSUS: REJECTED")
        else:
            summary_parts.append(f"   ⚠️ AI CONSENSUS: NEEDS REVIEW")
    
    summary_parts.append(f"\n📊 TOTAL EXPLOSIVE OPPORTUNITIES ANALYZED: {len(detailed_analyses)}")
    summary_parts.append(f"⏰ ANALYSIS COMPLETED: {datetime.now().strftime('%I:%M %p PT')}")
    
    return "\n".join(summary_parts)

def save_premarket_analysis(analysis_result: Dict[str, Any]):
    """Save pre-market analysis to file"""
    
    import json
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"premarket_ai_analysis_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(analysis_result, f, indent=2, default=str)
    
    print(f"💾 Pre-market analysis saved to: {filename}")
    
    # Also save human-readable summary
    summary_filename = f"premarket_summary_{timestamp}.txt"
    with open(summary_filename, 'w') as f:
        f.write(analysis_result['premarket_summary'])
    
    print(f"📄 Pre-market summary saved to: {summary_filename}")

async def send_premarket_slack_notification(analysis_result: Dict[str, Any]):
    """Send pre-market analysis to Slack"""
    
    webhook_url = "https://hooks.slack.com/services/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"
    
    opportunities_count = analysis_result['opportunities_discovered']
    detailed_count = analysis_result['detailed_analyses']
    
    slack_message = f"""🌅 **PRE-MARKET AI ANALYSIS COMPLETE**
**{datetime.now().strftime('%I:%M %p PT')}**

🔍 **Discovery Results:**
• {opportunities_count} explosive opportunities identified
• {detailed_count} opportunities analyzed in detail by AI team
• Collaborative analysis by Claude, ChatGPT, and Grok

🤖 **AI Team Consensus:**
{analysis_result['premarket_summary']}

📊 **Ready for market open with explosive opportunities identified!**
**NO LARGE-CAP SAFE STOCKS** - Focus on catalyst-driven explosive plays only."""
    
    payload = {
        "text": slack_message,
        "username": "Pre-Market AI Analysis",
        "icon_emoji": ":sunrise:"
    }
    
    try:
        import urllib.request
        import ssl
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, context=ssl_context) as response:
            success = response.getcode() == 200
            
        if success:
            print("✅ Pre-market analysis sent to Slack")
        else:
            print("⚠️ Failed to send Slack notification")
            
        return success
        
    except Exception as e:
        print(f"❌ Slack notification error: {e}")
        return False

async def main():
    """Run pre-market analysis"""
    print("🌅 STARTING PRE-MARKET AI ANALYSIS SYSTEM")
    print("=" * 60)
    
    # Run collaborative pre-market analysis
    analysis_result = await run_premarket_collaborative_analysis()
    
    # Send to Slack
    await send_premarket_slack_notification(analysis_result)
    
    print("\n✅ PRE-MARKET ANALYSIS COMPLETE")
    print(f"📊 {analysis_result['opportunities_discovered']} opportunities discovered")
    print(f"🤖 {analysis_result['detailed_analyses']} detailed AI analyses completed")

if __name__ == "__main__":
    asyncio.run(main())