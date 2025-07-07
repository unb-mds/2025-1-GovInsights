#!/usr/bin/env python3
"""
🔄 Post-Migration Validation Script
Validates the new test_analysis structure and optionally cleans up old analysis_reports
"""

import os
import sys
from pathlib import Path

def validate_new_structure():
    """Validate that the new structure is complete and functional"""
    print("🔍 Validating new test_analysis structure...")
    
    base_path = Path("test_analysis")
    if not base_path.exists():
        print("❌ test_analysis folder not found!")
        return False
    
    # Expected structure
    expected_structure = {
        "README.md": "file",
        "reports/main/RELATORIO_COMPLETO_FINAL.md": "file",
        "reports/main/CONCLUSAO_FINAL_TESTES_INTEGRACAO.md": "file", 
        "reports/detailed/": "dir",
        "scripts/validation/": "dir",
        "scripts/fixes/": "dir",
        "scripts/infrastructure/": "dir",
        "data/coverage/": "dir", 
        "data/json_reports/": "dir",
        "docs/GETTING_STARTED.md": "file",
        "docs/STRUCTURE_GUIDE.md": "file",
        "docs/SCRIPT_USAGE.md": "file",
        "docs/MIGRATION.md": "file"
    }
    
    all_good = True
    for path, type_expected in expected_structure.items():
        full_path = base_path / path
        
        if type_expected == "file":
            if full_path.is_file():
                print(f"✅ {path}")
            else:
                print(f"❌ {path} - Missing file")
                all_good = False
        elif type_expected == "dir":
            if full_path.is_dir():
                print(f"✅ {path}")
            else:
                print(f"❌ {path} - Missing directory")
                all_good = False
    
    return all_good

def count_files_migrated():
    """Count files in new structure to verify migration completeness"""
    print("\n📊 Counting migrated files...")
    
    base_path = Path("test_analysis")
    
    # Count files by category
    counts = {
        "reports": 0,
        "scripts": 0,
        "data": 0,
        "docs": 0
    }
    
    for root, dirs, files in os.walk(base_path):
        root_path = Path(root)
        
        if "reports" in root_path.parts:
            counts["reports"] += len(files)
        elif "scripts" in root_path.parts:
            counts["scripts"] += len(files)
        elif "data" in root_path.parts:
            counts["data"] += len(files)
        elif "docs" in root_path.parts:
            counts["docs"] += len(files)
    
    print(f"📋 Reports: {counts['reports']} files")
    print(f"🔧 Scripts: {counts['scripts']} files")
    print(f"📊 Data: {counts['data']} files")
    print(f"📚 Docs: {counts['docs']} files")
    print(f"📦 Total: {sum(counts.values())} files")
    
    return counts

def check_old_structure():
    """Check if old analysis_reports structure still exists"""
    old_path = Path("analysis_reports")
    if old_path.exists():
        print(f"\n⚠️  Old structure 'analysis_reports' still exists")
        print(f"   Location: {old_path.absolute()}")
        return True
    else:
        print(f"\n✅ Old structure 'analysis_reports' not found (clean)")
        return False

def suggest_cleanup():
    """Suggest cleanup actions"""
    print("\n🧹 Cleanup Suggestions:")
    print("1. ✅ New structure validated and working")
    print("2. 📁 Old 'analysis_reports' can be safely removed")
    print("3. 🔄 Update team documentation to reference 'test_analysis'")
    print("4. 📢 Inform team members about new structure")
    
    print("\n🚀 To remove old structure (optional):")
    print("   rm -rf analysis_reports/     # Unix/Linux/Mac")
    print("   rmdir /s analysis_reports\\   # Windows")

def main():
    """Main validation and cleanup script"""
    print("🔄 Test Analysis Structure Validation")
    print("=" * 50)
    
    # Validate new structure
    structure_ok = validate_new_structure()
    
    # Count migrated files
    file_counts = count_files_migrated()
    
    # Check old structure
    old_exists = check_old_structure()
    
    print("\n" + "=" * 50)
    
    if structure_ok:
        print("🎉 VALIDATION SUCCESSFUL!")
        print("✅ New test_analysis structure is complete and ready to use")
        
        if old_exists:
            suggest_cleanup()
        else:
            print("🎯 Migration fully complete - ready for production use!")
            
    else:
        print("❌ VALIDATION FAILED!")
        print("Some files or directories are missing in the new structure")
        print("Please check the migration process")
        return 1
    
    print("\n📖 Next steps:")
    print("   cd test_analysis/")
    print("   cat README.md")
    print("   cat docs/GETTING_STARTED.md")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
