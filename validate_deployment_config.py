#!/usr/bin/env python3
"""
Railway Deployment Configuration Validator
Ensures Procfile and nixpacks.toml are synchronized
"""

import os
import re
import sys
from pathlib import Path

def extract_procfile_entry_point():
    """Extract entry point from Procfile"""
    procfile_path = Path("Procfile")
    if not procfile_path.exists():
        return None, "Procfile not found"
    
    with open(procfile_path, 'r') as f:
        content = f.read().strip()
    
    # Match: web: python -m uvicorn <module>:<app> --host 0.0.0.0 --port $PORT
    match = re.search(r'web:\s*python\s+-m\s+uvicorn\s+([^:]+):(\w+)', content)
    if match:
        return f"{match.group(1)}:{match.group(2)}", None
    return None, f"Could not parse Procfile entry point from: {content}"

def extract_nixpacks_entry_point():
    """Extract entry point from nixpacks.toml"""
    nixpacks_path = Path("nixpacks.toml")
    if not nixpacks_path.exists():
        return None, "nixpacks.toml not found"
    
    with open(nixpacks_path, 'r') as f:
        content = f.read()
    
    # Match: cmd = "python -m uvicorn <module>:<app> --host 0.0.0.0 --port $PORT"
    match = re.search(r'cmd\s*=\s*"python\s+-m\s+uvicorn\s+([^:]+):(\w+)', content)
    if match:
        return f"{match.group(1)}:{match.group(2)}", None
    return None, f"Could not parse nixpacks.toml entry point"

def validate_entry_points():
    """Main validation function"""
    print("🔍 Railway Deployment Configuration Validator")
    print("=" * 50)
    
    # Check Procfile
    procfile_entry, procfile_error = extract_procfile_entry_point()
    if procfile_error:
        print(f"❌ Procfile: {procfile_error}")
        return False
    print(f"✅ Procfile: {procfile_entry}")
    
    # Check nixpacks.toml
    nixpacks_entry, nixpacks_error = extract_nixpacks_entry_point()
    if nixpacks_error:
        print(f"❌ nixpacks.toml: {nixpacks_error}")
        return False
    print(f"✅ nixpacks.toml: {nixpacks_entry}")
    
    # Compare
    if procfile_entry == nixpacks_entry:
        print(f"\n🎯 CONFIGURATION VALID: Both files point to {procfile_entry}")
        print("✅ Ready for Railway deployment")
        return True
    else:
        print(f"\n❌ CONFIGURATION MISMATCH:")
        print(f"   Procfile:      {procfile_entry}")
        print(f"   nixpacks.toml: {nixpacks_entry}")
        print("\n⚠️  Railway will use Procfile - nixpacks.toml will be ignored!")
        print("🔧 Fix: Update nixpacks.toml to match Procfile")
        return False

if __name__ == "__main__":
    success = validate_entry_points()
    sys.exit(0 if success else 1)
