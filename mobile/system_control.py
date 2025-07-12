#!/usr/bin/env python3
"""
Squeeze Alpha System Control Panel
Easy commands to start, stop, update, and interact with your AI trading system
"""

import os
import sys
import json
import subprocess
import signal
import time
from datetime import datetime

class SqueezeAlphaControl:
    """Main control interface for the trading system"""
    
    def __init__(self):
        self.system_dir = "/Users/michaelmote/Desktop/ai-trading-system-complete"
        self.status_file = os.path.join(self.system_dir, "system_status.json")
        self.pid_file = os.path.join(self.system_dir, "system.pid")
        
    def show_menu(self):
        """Show main control menu"""
        print("🤖 SQUEEZE ALPHA SYSTEM CONTROL")
        print("=" * 40)
        print("1. 🚀 Start Autonomous System")
        print("2. 🛑 Stop System")
        print("3. 📊 Check System Status")
        print("4. 🧠 Run Hedge Fund Analysis Now")
        print("5. 📱 Test Slack Notifications")
        print("6. 🔄 Update/Restart System")
        print("7. 📋 View Recent Performance")
        print("8. ⚙️  System Settings")
        print("9. 📚 Help & Documentation")
        print("0. 🚪 Exit")
        print()
    
    def start_system(self):
        """Start the autonomous trading system"""
        print("🚀 Starting Squeeze Alpha Autonomous System...")
        
        try:
            # Check if already running
            if self.is_system_running():
                print("⚠️  System is already running!")
                return
            
            # Start the Pacific Time system in background
            process = subprocess.Popen([
                sys.executable, 
                os.path.join(self.system_dir, "pacific_time_schedule.py")
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Update status
            status = {
                "system": "squeeze_alpha",
                "status": "running",
                "started": datetime.now().isoformat(),
                "pid": process.pid,
                "schedule": "pacific_time_autonomous"
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
            
            print("✅ Autonomous system started!")
            print(f"   PID: {process.pid}")
            print("   Schedule: Pacific Time (4 AM, 5:30 AM, 6:30 AM, 9 AM, 12 PM, 1 PM, 3 PM)")
            print("   Notifications: Active via Slack")
            print("   Learning: Continuous evolution enabled")
            
        except Exception as e:
            print(f"❌ Error starting system: {e}")
    
    def stop_system(self):
        """Stop the autonomous trading system"""
        print("🛑 Stopping Squeeze Alpha System...")
        
        try:
            if not self.is_system_running():
                print("⚠️  System is not running")
                return
            
            # Get PID and terminate
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            os.kill(pid, signal.SIGTERM)
            time.sleep(2)
            
            # Clean up files
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
            
            # Update status
            status = {
                "system": "squeeze_alpha",
                "status": "stopped",
                "stopped": datetime.now().isoformat()
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
            
            print("✅ System stopped successfully")
            
        except ProcessLookupError:
            print("⚠️  System process not found (may have already stopped)")
            self.cleanup_files()
        except Exception as e:
            print(f"❌ Error stopping system: {e}")
    
    def check_status(self):
        """Check current system status"""
        print("📊 SYSTEM STATUS CHECK")
        print("=" * 30)
        
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r') as f:
                    status = json.load(f)
                
                print(f"Status: {status.get('status', 'unknown').upper()}")
                if status.get('status') == 'running':
                    print(f"Started: {status.get('started', 'unknown')}")
                    print(f"PID: {status.get('pid', 'unknown')}")
                    print(f"Schedule: {status.get('schedule', 'unknown')}")
                    
                    # Check if process is actually running
                    if self.is_system_running():
                        print("✅ Process confirmed running")
                    else:
                        print("❌ Process not found (may have crashed)")
                else:
                    print(f"Stopped: {status.get('stopped', 'unknown')}")
            else:
                print("❌ No status file found - system not initialized")
            
            # Check recent logs
            print(f"\n📋 Recent Activity:")
            log_dir = os.path.join(self.system_dir, "logs")
            if os.path.exists(log_dir):
                print(f"   Log directory: {len(os.listdir(log_dir))} log categories")
            else:
                print("   No logs found")
                
        except Exception as e:
            print(f"❌ Error checking status: {e}")
    
    def run_analysis_now(self):
        """Run hedge fund consensus analysis immediately"""
        print("🧠 Running Hedge Fund Analysis...")
        
        try:
            result = subprocess.run([
                sys.executable,
                os.path.join(self.system_dir, "multi_ai_consensus_engine.py")
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✅ Analysis complete - Check Slack for results!")
            else:
                print(f"❌ Analysis failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("⏰ Analysis timed out (taking longer than 2 minutes)")
        except Exception as e:
            print(f"❌ Error running analysis: {e}")
    
    def test_slack(self):
        """Test Slack notifications"""
        print("📱 Testing Slack Notifications...")
        
        try:
            result = subprocess.run([
                sys.executable,
                os.path.join(self.system_dir, "test_slack_simple.py")
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Slack test complete - Check your channel!")
            else:
                print(f"❌ Slack test failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error testing Slack: {e}")
    
    def update_system(self):
        """Update and restart the system"""
        print("🔄 Updating System...")
        
        # Stop current system
        if self.is_system_running():
            print("Stopping current system...")
            self.stop_system()
            time.sleep(3)
        
        # Could add git pull or update logic here
        print("System files are up to date")
        
        # Restart
        print("Restarting system...")
        self.start_system()
    
    def view_performance(self):
        """View recent trading performance"""
        print("📋 RECENT PERFORMANCE")
        print("=" * 25)
        
        try:
            # Look for recent portfolio analysis
            analysis_file = os.path.join(self.system_dir, "portfolio_optimization_summary.md")
            if os.path.exists(analysis_file):
                print("📊 Latest Portfolio Optimization:")
                with open(analysis_file, 'r') as f:
                    content = f.read()
                    # Show summary section
                    if "## Executive Summary" in content:
                        summary = content.split("## Executive Summary")[1].split("##")[0]
                        print(summary[:500] + "...")
                    else:
                        print(content[:500] + "...")
            
            # Look for recent ML training data
            ml_dir = os.path.join(self.system_dir, "logs", "ml_training")
            if os.path.exists(ml_dir):
                files = [f for f in os.listdir(ml_dir) if f.endswith('.json')]
                if files:
                    latest_file = max(files)
                    print(f"\n🧠 Latest Learning Data: {latest_file}")
            
        except Exception as e:
            print(f"❌ Error viewing performance: {e}")
    
    def system_settings(self):
        """Show system settings and configuration"""
        print("⚙️  SYSTEM SETTINGS")
        print("=" * 20)
        
        print("📁 System Directory:", self.system_dir)
        print("🔧 Configuration File: .env")
        print("📊 Status File:", self.status_file)
        print("🚀 Main Scripts:")
        print("   - pacific_time_schedule.py (Autonomous system)")
        print("   - multi_ai_consensus_engine.py (Hedge fund analysis)")
        print("   - portfolio_analysis.py (Portfolio review)")
        
        print(f"\n📅 Schedule (Pacific Time):")
        print("   4:00 AM - Early pre-market scan")
        print("   5:30 AM - Full pre-market analysis")
        print("   6:30 AM - Market open analysis")
        print("   9:00 AM - Mid-morning scan") 
        print("  12:00 PM - Midday analysis")
        print("   1:00 PM - Market close summary")
        print("   3:00 PM - After-hours evolution")
    
    def show_help(self):
        """Show help and documentation"""
        print("📚 HELP & DOCUMENTATION")
        print("=" * 30)
        
        print("🤖 SYSTEM OVERVIEW:")
        print("This is your autonomous AI trading system that:")
        print("• Runs 24/7 monitoring for squeeze opportunities")
        print("• Uses two AI hedge fund managers (Claude & ChatGPT)")
        print("• Sends 7 daily updates to Slack")
        print("• Learns and evolves from every trade")
        
        print(f"\n📱 DAILY WORKFLOW:")
        print("1. System wakes up at 4:00 AM PT with pre-market analysis")
        print("2. Sends you Slack updates throughout trading day")
        print("3. You review recommendations and execute trades")
        print("4. System learns from results and evolves")
        
        print(f"\n🛠️  MAINTENANCE:")
        print("• Use this control panel to start/stop system")
        print("• System automatically learns and updates")
        print("• Check logs in logs/ directory for detailed analysis")
        print("• Slack notifications keep you informed")
        
        print(f"\n📞 QUICK COMMANDS:")
        print("python3 system_control.py - This control panel")
        print("python3 multi_ai_consensus_engine.py - Run analysis now")
        print("python3 portfolio_analysis.py - Portfolio review")
        print("python3 test_slack_simple.py - Test Slack")
    
    def is_system_running(self):
        """Check if system is currently running"""
        try:
            if not os.path.exists(self.pid_file):
                return False
            
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            os.kill(pid, 0)  # Signal 0 just checks if process exists
            return True
            
        except (OSError, ProcessLookupError, ValueError):
            return False
    
    def cleanup_files(self):
        """Clean up status files"""
        for file in [self.pid_file]:
            if os.path.exists(file):
                os.remove(file)

def main():
    """Main control interface"""
    control = SqueezeAlphaControl()
    
    while True:
        control.show_menu()
        
        try:
            choice = input("Select option (0-9): ").strip()
            
            if choice == "1":
                control.start_system()
            elif choice == "2":
                control.stop_system()
            elif choice == "3":
                control.check_status()
            elif choice == "4":
                control.run_analysis_now()
            elif choice == "5":
                control.test_slack()
            elif choice == "6":
                control.update_system()
            elif choice == "7":
                control.view_performance()
            elif choice == "8":
                control.system_settings()
            elif choice == "9":
                control.show_help()
            elif choice == "0":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please choose 0-9.")
            
            print("\nPress Enter to continue...")
            input()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()