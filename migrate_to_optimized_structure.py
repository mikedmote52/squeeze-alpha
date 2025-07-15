#!/usr/bin/env python3
"""
AI Trading System - Structure Migration Script
Reorganizes files into optimized structure while preserving all functionality
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

class SystemMigrator:
    """Migrates the AI trading system to optimized file structure"""
    
    def __init__(self, source_dir: str, target_dir: str):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.migration_log = []
        
        # Define the optimized structure mapping
        self.file_mapping = {
            # Core AI systems
            'core/collaborative_ai_system.py': 'core/ai/collaborative_system.py',
            'core/enhanced_ai_consensus.py': 'core/ai/consensus_engine.py',
            'core/openrouter_ai_debate.py': 'core/ai/openrouter_client.py',
            'core/multi_ai_consensus_engine.py': 'core/ai/multi_agent_system.py',
            
            # Discovery systems
            'core/explosive_catalyst_discovery.py': 'core/discovery/explosive_discovery.py',
            'core/catalyst_discovery_engine.py': 'core/discovery/catalyst_discovery.py',
            'core/stock_discovery_engine.py': 'core/discovery/stock_screener.py',
            'core/real_time_stock_discovery.py': 'core/discovery/market_scanner.py',
            'core/weekend_opportunity_scanner.py': 'core/discovery/weekend_scanner.py',
            
            # Analysis systems
            'core/comprehensive_intelligence_engine.py': 'core/analysis/intelligence_engine.py',
            'core/enhanced_discovery_engine.py': 'core/analysis/enhanced_analysis.py',
            'core/performance_report_engine.py': 'core/analysis/performance_tracker.py',
            
            # Portfolio management
            'core/portfolio_memory_engine.py': 'core/portfolio/memory_system.py',
            'core/three_day_memory_system.py': 'core/portfolio/three_day_memory.py',
            'core/real_time_portfolio_engine.py': 'core/portfolio/portfolio_manager.py',
            'core/live_portfolio_engine.py': 'core/portfolio/live_tracker.py',
            
            # Trading systems
            'core/trade_execution_engine.py': 'core/trading/trade_executor.py',
            'core/trading_safety_validator.py': 'core/trading/safety_validator.py',
            'core/trading_safety_enforcer.py': 'core/trading/safety_enforcer.py',
            
            # Data systems
            'core/polygon_market_engine.py': 'core/data/polygon_client.py',
            'core/ai_baseline_cache_system.py': 'core/data/ai_cache.py',
            'core/data_verification.py': 'core/data/data_validator.py',
            
            # API and backend
            'real_ai_backend.py': 'api/routes/ai_analysis.py',
            'real_portfolio_backend.py': 'api/routes/portfolio.py',
            'api_endpoints.py': 'api/routes/discovery.py',
            
            # Services
            'core/pacific_time_schedule.py': 'services/scheduler.py',
            'core/premarket_ai_analysis.py': 'services/premarket_service.py',
            'core/slack_notification_engine.py': 'services/notification_service.py',
            
            # Configuration
            'core/secrets_manager.py': 'config/secrets_manager.py',
            'config/config.json': 'config/settings.json',
            'streamlit_secrets.toml': 'config/streamlit_secrets.toml',
            
            # Applications
            'streamlit_app.py': 'apps/streamlit_app.py',
            'main.py': 'apps/main.py',
            'web_app.py': 'apps/web_app.py',
            
            # Frontend pages
            'pages/01_🏠_Portfolio_Dashboard.py': 'frontend/streamlit/pages/01_Portfolio_Dashboard.py',
            'pages/02_🔍_Opportunity_Discovery.py': 'frontend/streamlit/pages/02_Opportunity_Discovery.py',
            'pages/03_🤖_AI_Analysis.py': 'frontend/streamlit/pages/03_AI_Analysis.py',
            'pages/04_🧠_Portfolio_Memory.py': 'frontend/streamlit/pages/04_Portfolio_Memory.py',
            
            # Integrations
            'mobile/web_control.py': 'integrations/mobile/web_interface.py',
            
            # Utilities
            'utils/start_autonomous_system.py': 'utils/system_starter.py',
            'utils/test_api_keys.py': 'utils/api_tester.py',
            'make_accessible.py': 'utils/accessibility.py',
            
            # Documentation
            'README.md': 'docs/README.md',
            'REORGANIZE_STRUCTURE.md': 'docs/setup/reorganization_guide.md',
        }
        
        # Directories to create
        self.directories = [
            'core/ai', 'core/discovery', 'core/analysis', 'core/portfolio', 
            'core/trading', 'core/data', 'api/routes', 'api/middleware',
            'services', 'integrations/slack', 'integrations/openrouter', 
            'integrations/alpaca', 'integrations/mobile', 'frontend/streamlit/pages',
            'frontend/streamlit/components', 'config/environments', 'utils',
            'tests/unit', 'tests/integration', 'data/databases', 'data/cache',
            'logs/application', 'logs/trading', 'logs/ai_conversations',
            'docs/api', 'docs/setup', 'docs/usage', 'apps'
        ]
    
    def create_optimized_structure(self):
        """Create the optimized directory structure"""
        print("🏗️ Creating optimized directory structure...")
        
        # Create target directory if it doesn't exist
        self.target_dir.mkdir(exist_ok=True)
        
        # Create all subdirectories
        for directory in self.directories:
            dir_path = self.target_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Created: {directory}")
        
        # Create __init__.py files for Python packages
        python_dirs = [d for d in self.directories if not d.startswith(('docs', 'logs', 'data'))]
        for directory in python_dirs:
            init_file = self.target_dir / directory / '__init__.py'
            if not init_file.exists():
                init_file.write_text('# Auto-generated __init__.py\n')
        
        self.log_action("Created optimized directory structure")
    
    def migrate_files(self):
        """Migrate files to new structure"""
        print("\n📦 Migrating files to optimized structure...")
        
        migrated_count = 0
        
        for source_file, target_file in self.file_mapping.items():
            source_path = self.source_dir / source_file
            target_path = self.target_dir / target_file
            
            if source_path.exists():
                # Ensure target directory exists
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(source_path, target_path)
                print(f"   ✅ {source_file} → {target_file}")
                migrated_count += 1
                
                self.log_action(f"Migrated: {source_file} → {target_file}")
            else:
                print(f"   ⚠️  Source not found: {source_file}")
                self.log_action(f"Missing source: {source_file}")
        
        print(f"\n✅ Migrated {migrated_count} files")
    
    def copy_essential_files(self):
        """Copy essential files that need to be in root"""
        print("\n📋 Copying essential files...")
        
        essential_files = [
            'requirements.txt',
            'requirements-streamlit.txt', 
            'setup.py',
            '.env.template' if (self.source_dir / '.env.template').exists() else None,
            'setup_autonomous_system.sh',
            'com.aitrading.autonomous.plist'
        ]
        
        for file_name in essential_files:
            if file_name is None:
                continue
                
            source_path = self.source_dir / file_name
            target_path = self.target_dir / file_name
            
            if source_path.exists():
                shutil.copy2(source_path, target_path)
                print(f"   ✅ {file_name}")
                self.log_action(f"Copied essential: {file_name}")
    
    def migrate_data_and_logs(self):
        """Migrate data files and logs"""
        print("\n💾 Migrating data and logs...")
        
        # Database files
        db_files = [
            'portfolio_memory_3day.db',
            'ai_baseline_cache.db',
            'api_costs.db',
            'api_usage.db'
        ]
        
        for db_file in db_files:
            source_path = self.source_dir / db_file
            if source_path.exists():
                target_path = self.target_dir / 'data' / 'databases' / db_file
                shutil.copy2(source_path, target_path)
                print(f"   ✅ Database: {db_file}")
        
        # Copy logs directory if it exists
        logs_source = self.source_dir / 'logs'
        if logs_source.exists():
            logs_target = self.target_dir / 'logs'
            shutil.copytree(logs_source, logs_target, dirs_exist_ok=True)
            print(f"   ✅ Logs directory")
        
        # Copy JSON data files
        json_files = [
            'current_portfolio.json',
            'system_status.json',
            'system_evolution_recommendations.json'
        ]
        
        for json_file in json_files:
            source_path = self.source_dir / json_file
            if source_path.exists():
                target_path = self.target_dir / 'data' / json_file
                shutil.copy2(source_path, target_path)
                print(f"   ✅ Data: {json_file}")
    
    def create_updated_import_map(self):
        """Create a mapping file for updated imports"""
        print("\n🔗 Creating import mapping guide...")
        
        import_mapping = {
            # Old imports → New imports
            'from core.collaborative_ai_system import': 'from core.ai.collaborative_system import',
            'from core.explosive_catalyst_discovery import': 'from core.discovery.explosive_discovery import',
            'from core.portfolio_memory_engine import': 'from core.portfolio.memory_system import',
            'from core.pacific_time_schedule import': 'from services.scheduler import',
            'from core.secrets_manager import': 'from config.secrets_manager import',
            'from real_ai_backend import': 'from api.routes.ai_analysis import',
            'sys.path.append(\'./core\')': 'sys.path.append(\'./core\')',  # No change needed
            'sys.path.append(\'core\')': 'sys.path.append(\'core\')',    # No change needed
        }
        
        mapping_file = self.target_dir / 'IMPORT_MAPPING.md'
        with open(mapping_file, 'w') as f:
            f.write("# Import Path Mapping\n\n")
            f.write("## Updated Import Statements\n\n")
            f.write("When updating code to use the new structure, use these import mappings:\n\n")
            
            for old_import, new_import in import_mapping.items():
                f.write(f"**Old:** `{old_import}`\n")
                f.write(f"**New:** `{new_import}`\n\n")
            
            f.write("\n## Key Changes:\n")
            f.write("- AI systems moved to `core/ai/`\n")
            f.write("- Discovery systems moved to `core/discovery/`\n")
            f.write("- API routes moved to `api/routes/`\n")
            f.write("- Services moved to `services/`\n")
            f.write("- Configuration moved to `config/`\n")
        
        print(f"   ✅ Import mapping saved to IMPORT_MAPPING.md")
    
    def create_migration_script(self):
        """Create script to update imports in migrated files"""
        print("\n🔄 Creating import update script...")
        
        script_content = '''#!/usr/bin/env python3
"""
Import Path Updater
Updates import statements in migrated files to use new structure
"""

import os
import re
from pathlib import Path

def update_imports_in_file(file_path):
    """Update import statements in a single file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Define replacement patterns
        replacements = {
            r'from core\.collaborative_ai_system import': 'from core.ai.collaborative_system import',
            r'from core\.explosive_catalyst_discovery import': 'from core.discovery.explosive_discovery import',
            r'from core\.portfolio_memory_engine import': 'from core.portfolio.memory_system import',
            r'from core\.pacific_time_schedule import': 'from services.scheduler import',
            r'from core\.secrets_manager import': 'from config.secrets_manager import',
            r'import core\.collaborative_ai_system': 'import core.ai.collaborative_system',
            r'import core\.explosive_catalyst_discovery': 'import core.discovery.explosive_discovery',
        }
        
        # Apply replacements
        updated_content = content
        changes_made = False
        
        for pattern, replacement in replacements.items():
            if re.search(pattern, updated_content):
                updated_content = re.sub(pattern, replacement, updated_content)
                changes_made = True
        
        # Write back if changes were made
        if changes_made:
            with open(file_path, 'w') as f:
                f.write(updated_content)
            print(f"Updated imports in: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Update imports in all Python files"""
    print("🔄 Updating import statements...")
    
    updated_files = 0
    
    # Update imports in all Python files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                if update_imports_in_file(file_path):
                    updated_files += 1
    
    print(f"✅ Updated imports in {updated_files} files")

if __name__ == "__main__":
    main()
'''
        
        script_file = self.target_dir / 'update_imports.py'
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(script_file, 0o755)
        
        print(f"   ✅ Import update script created: update_imports.py")
    
    def log_action(self, action: str):
        """Log migration action"""
        self.migration_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': action
        })
    
    def save_migration_log(self):
        """Save migration log"""
        log_file = self.target_dir / 'MIGRATION_LOG.json'
        with open(log_file, 'w') as f:
            json.dump({
                'migration_timestamp': datetime.now().isoformat(),
                'source_directory': str(self.source_dir),
                'target_directory': str(self.target_dir),
                'actions': self.migration_log
            }, f, indent=2)
        
        print(f"\n📋 Migration log saved to: MIGRATION_LOG.json")
    
    def create_startup_script(self):
        """Create startup script for optimized structure"""
        print("\n🚀 Creating startup script...")
        
        startup_content = '''#!/usr/bin/env python3
"""
AI Trading System - Optimized Startup
Starts the AI trading system with new optimized structure
"""

import sys
import os
from pathlib import Path

# Add core modules to Python path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'core'))
sys.path.insert(0, str(Path(__file__).parent / 'api'))
sys.path.insert(0, str(Path(__file__).parent / 'services'))

def main():
    """Start the AI trading system"""
    print("🚀 AI TRADING SYSTEM - OPTIMIZED STRUCTURE")
    print("=" * 60)
    
    # Import main application
    try:
        from apps.streamlit_app import main as streamlit_main
        
        print("✅ Optimized structure loaded successfully")
        print("🎯 Starting Streamlit interface...")
        
        # Run Streamlit app
        streamlit_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try running: python update_imports.py")
        return 1
    
    except Exception as e:
        print(f"❌ Startup error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
'''
        
        startup_file = self.target_dir / 'start_optimized_system.py'
        with open(startup_file, 'w') as f:
            f.write(startup_content)
        
        # Make script executable
        os.chmod(startup_file, 0o755)
        
        print(f"   ✅ Startup script created: start_optimized_system.py")
    
    def run_migration(self):
        """Run the complete migration process"""
        print("🎯 AI TRADING SYSTEM - STRUCTURE OPTIMIZATION")
        print("=" * 60)
        print(f"Source: {self.source_dir}")
        print(f"Target: {self.target_dir}")
        print("=" * 60)
        
        # Step 1: Create optimized structure
        self.create_optimized_structure()
        
        # Step 2: Migrate files
        self.migrate_files()
        
        # Step 3: Copy essential files
        self.copy_essential_files()
        
        # Step 4: Migrate data and logs
        self.migrate_data_and_logs()
        
        # Step 5: Create import mapping
        self.create_updated_import_map()
        
        # Step 6: Create import update script
        self.create_migration_script()
        
        # Step 7: Create startup script
        self.create_startup_script()
        
        # Step 8: Save migration log
        self.save_migration_log()
        
        print("\n🎉 MIGRATION COMPLETE!")
        print("=" * 60)
        print("Next steps:")
        print("1. cd ai-trading-system-optimized")
        print("2. python update_imports.py  # Update import paths")
        print("3. python start_optimized_system.py  # Test the system")
        print("4. Review IMPORT_MAPPING.md for manual updates")
        print("\n✅ Original system preserved in current directory")

def main():
    """Run the migration"""
    current_dir = Path(__file__).parent
    target_dir = current_dir.parent / 'ai-trading-system-optimized'
    
    migrator = SystemMigrator(current_dir, target_dir)
    migrator.run_migration()

if __name__ == "__main__":
    main()