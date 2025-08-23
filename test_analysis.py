#!/usr/bin/env python3
"""
Test Suite Analysis for tilores_X
Analyzes all test files to determine current vs outdated tests
"""

import os
import ast
from pathlib import Path
from datetime import datetime
import importlib.util

def analyze_test_file(filepath):
    """Analyze a test file for imports and test functions."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            tree = ast.parse(content)
        
        # Extract imports
        imports = []
        test_functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
            elif isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_'):
                    test_functions.append(node.name)
        
        # Check file size and modification time
        stat = os.stat(filepath)
        size = stat.st_size
        mtime = datetime.fromtimestamp(stat.st_mtime)
        
        return {
            'path': filepath,
            'imports': list(set(imports)),
            'test_count': len(test_functions),
            'test_functions': test_functions[:5],  # First 5 for preview
            'size': size,
            'modified': mtime,
            'is_empty': size < 100
        }
    except Exception as e:
        return {
            'path': filepath,
            'error': str(e),
            'is_empty': True
        }

def categorize_tests():
    """Categorize all tests by their type and relevance."""
    categories = {
        'core_functionality': [],
        'virtuous_cycle': [],
        'autonomous_ai': [],
        'integration': [],
        'speed_experiments': [],
        'deprecated': [],
        'utilities': []
    }
    
    test_dirs = ['tests/unit', 'tests/integration', 'tests/speed_experiments']
    
    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            continue
            
        for filepath in Path(test_dir).glob('test_*.py'):
            analysis = analyze_test_file(filepath)
            filename = os.path.basename(filepath)
            
            # Categorize based on filename and imports
            if 'virtuous_cycle' in filename:
                categories['virtuous_cycle'].append(analysis)
            elif 'autonomous' in filename:
                categories['autonomous_ai'].append(analysis)
            elif 'integration' in test_dir:
                categories['integration'].append(analysis)
            elif 'speed_experiments' in test_dir:
                categories['speed_experiments'].append(analysis)
            elif any(core in filename for core in ['core_app', 'main_enhanced', 'redis_cache', 'function_executor']):
                categories['core_functionality'].append(analysis)
            elif any(util in filename for util in ['debug_config', 'context_extraction', 'monitoring']):
                categories['utilities'].append(analysis)
            else:
                # Check if likely deprecated
                if analysis.get('is_empty') or analysis.get('test_count', 0) == 0:
                    categories['deprecated'].append(analysis)
                else:
                    categories['core_functionality'].append(analysis)
    
    return categories

def print_analysis():
    """Print comprehensive test analysis."""
    categories = categorize_tests()
    
    print("=" * 80)
    print("TILORES_X TEST SUITE ANALYSIS")
    print("=" * 80)
    print()
    
    # Summary
    total_tests = sum(len(tests) for tests in categories.values())
    print(f"Total test files found: {total_tests}")
    print()
    
    # Category breakdown
    for category, tests in categories.items():
        if not tests:
            continue
            
        print(f"\n{'='*60}")
        print(f"{category.upper().replace('_', ' ')} ({len(tests)} files)")
        print(f"{'='*60}")
        
        for test in sorted(tests, key=lambda x: x.get('test_count', 0), reverse=True):
            path = test['path']
            rel_path = os.path.relpath(path)
            test_count = test.get('test_count', 0)
            size = test.get('size', 0)
            
            status = "✅" if test_count > 0 and not test.get('error') else "❌"
            
            print(f"\n{status} {rel_path}")
            print(f"   Tests: {test_count}, Size: {size:,} bytes")
            
            if test.get('error'):
                print(f"   ⚠️  Error: {test['error']}")
            elif test_count > 0:
                print(f"   Sample tests: {', '.join(test.get('test_functions', []))}")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    # Identify critical missing tests
    print("\n📌 MISSING TEST COVERAGE:")
    print("   - Rollback functionality (rollback_to_last_good_state)")
    print("   - Dashboard API integration tests")
    print("   - AI change tracking and governance")
    
    print("\n🗑️  TESTS TO DEPRECATE:")
    for test in categories.get('deprecated', []):
        print(f"   - {os.path.relpath(test['path'])}")
    
    print("\n✅ CRITICAL TESTS TO RUN:")
    critical_tests = [
        "tests/unit/test_core_app.py",
        "tests/unit/test_main_enhanced.py", 
        "tests/unit/test_redis_cache.py",
        "tests/integration/test_virtuous_cycle_integration.py",
        "tests/unit/test_function_executor.py"
    ]
    for test in critical_tests:
        if os.path.exists(test):
            print(f"   - {test}")
    
    return categories

if __name__ == "__main__":
    categories = print_analysis()
    
    # Return exit code based on deprecated tests
    deprecated_count = len(categories.get('deprecated', []))
    exit(deprecated_count)  # Non-zero if deprecated tests exist
