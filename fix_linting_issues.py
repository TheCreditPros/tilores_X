#!/usr / bin / env python3
"""
Automated linting fix script for tilores_X project.
Fixes common linting issues while preserving functionality.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Set


class LintingFixer:
    """Automated fixer for common linting issues."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixed_files: Set[str] = set()
        self.issues_fixed = 0
        
    def fix_f_string_placeholders(self, content: str) -> str:
        """Fix F541: f - string is missing placeholders."""
        # Pattern to match f - strings without placeholders
        pattern = r'"([^"]*)"'
        
        def replace_f_string(match):
            string_content = match.group(1)
            # If no {} placeholders, convert to regular string
            if '{' not in string_content:
                return f'"{string_content}"'
            return match.group(0)
        
        return re.sub(pattern, replace_f_string, content)
    
    def fix_unused_imports(self, content: str) -> str:
        """Fix F401: imported but unused."""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Skip lines that are clearly used (this is a simple heuristic)
            if line.strip().startswith('from ') or line.strip().startswith('import '):
                # For now, keep all imports to avoid breaking functionality
                # A more sophisticated approach would analyze usage
                fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_arithmetic_operators(self, content: str) -> str:
        """Fix E226: missing whitespace around arithmetic operator."""
        # Add spaces around arithmetic operators
        patterns = [
            (r'(\w)(\+)(\w)', r'\1 \2 \3'),
            (r'(\w)(-)(\w)', r'\1 \2 \3'),
            (r'(\w)(\*)(\w)', r'\1 \2 \3'),
            (r'(\w)(/)(\w)', r'\1 \2 \3'),
            (r'(\w)(\*\*)(\w)', r'\1 \2 \3'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def fix_bare_except(self, content: str) -> str:
        """Fix E722: do not use bare 'except'."""
        # Replace bare except with except Exception
        content = re.sub(r'\bexcept:\s*$', 'except Exception:', content, flags=re.MULTILINE)
        return content
    
    def fix_comparison_to_false(self, content: str) -> str:
        """Fix E712: comparison to False should be 'if cond is not False:' or 'if cond:'."""
        # Replace is False with 'is False' and is not False with 'is not False'
        content = re.sub(r'(\w+)\s*==\s * False\b', r'\1 is False', content)
        content = re.sub(r'(\w+)\s*!=\s * False\b', r'\1 is not False', content)
        return content
    
    def fix_ambiguous_variable_names(self, content: str) -> str:
        """Fix E741: ambiguous variable name."""
        # Replace single letter variables in common contexts
        # This is conservative to avoid breaking functionality
        content = re.sub(r'\bfor\s + l\s + in\s+', 'for item in ', content)
        return content
    
    def fix_file(self, file_path: Path) -> bool:
        """Fix linting issues in a single file."""
        try:
            with open(file_path, 'r', encoding='utf - 8') as f:
                original_content = f.read()
            
            content = original_content
            
            # Apply fixes in order of safety
            content = self.fix_f_string_placeholders(content)
            content = self.fix_arithmetic_operators(content)
            content = self.fix_bare_except(content)
            content = self.fix_comparison_to_false(content)
            content = self.fix_ambiguous_variable_names(content)
            
            # Only write if content changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf - 8') as f:
                    f.write(content)
                
                self.fixed_files.add(str(file_path))
                print(f"✅ Fixed: {file_path.relative_to(self.project_root)}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
            return False
    
    def fix_project(self) -> Dict[str, int]:
        """Fix linting issues across the entire project."""
        python_files = list(self.project_root.glob('**/*.py'))
        
        # Exclude certain directories
        excluded_dirs = {'.venv', 'venv', '__pycache__', '.git', 'node_modules'}
        
        filtered_files = []
        for file_path in python_files:
            # Check if any parent directory is in excluded_dirs
            if not any(part in excluded_dirs for part in file_path.parts):
                filtered_files.append(file_path)
        
        print(f"🔧 Fixing linting issues in {len(filtered_files)} Python files...")
        
        fixed_count = 0
        for file_path in filtered_files:
            if self.fix_file(file_path):
                fixed_count += 1
        
        return {
            'total_files': len(filtered_files),
            'fixed_files': fixed_count,
            'fixed_file_list': list(self.fixed_files)
        }


def main():
    """Main function to run the linting fixer."""
    project_root = os.getcwd()
    
    print("🚀 Starting automated linting fixes...")
    print(f"📁 Project root: {project_root}")
    
    fixer = LintingFixer(project_root)
    results = fixer.fix_project()
    
    print("\n📊 LINTING FIX RESULTS:")
    print(f"  📁 Total files processed: {results['total_files']}")
    print(f"  ✅ Files fixed: {results['fixed_files']}")
    
    if results['fixed_files'] > 0:
        print("\n🔧 Fixed files:")
        for file_path in results['fixed_file_list']:
            print(f"  - {file_path}")
        
        print("\n💡 Next steps:")
        print("  1. Run: flake8 . --count --statistics --max - line - length=120")
        print("  2. Test functionality to ensure no regressions")
        print("  3. Commit the linting fixes")
    else:
        print("\n✅ No files needed fixing!")


if __name__ == '__main__':
    main()
