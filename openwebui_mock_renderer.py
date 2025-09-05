#!/usr/bin/env python3
"""
OpenWebUI Mock Renderer - Test formatting locally without deployment
Simulates how OpenWebUI processes and renders markdown content
"""

import re
import html
from typing import Dict, Any

class OpenWebUIMockRenderer:
    """Mock renderer that simulates OpenWebUI's markdown processing"""
    
    def __init__(self):
        self.debug = True
    
    def render_message(self, content: str) -> Dict[str, Any]:
        """
        Simulate OpenWebUI's message rendering pipeline
        Returns both HTML and debug info
        """
        if self.debug:
            print("🔍 INPUT CONTENT:")
            print(repr(content))
            print("\n📝 PROCESSING STEPS:")
        
        # Step 1: Preprocess content (simulate OpenWebUI's preprocessing)
        processed = self._preprocess_content(content)
        
        # Step 2: Parse markdown (simulate markdown-it processing)
        html_content = self._parse_markdown(processed)
        
        # Step 3: Apply OpenWebUI-specific rendering rules
        final_html = self._apply_openwebui_rendering(html_content)
        
        # Step 4: Generate visual representation
        visual = self._generate_visual_representation(final_html)
        
        return {
            'original': content,
            'processed': processed,
            'html': final_html,
            'visual': visual,
            'debug_info': self._get_debug_info(content, processed, html_content, final_html)
        }
    
    def _preprocess_content(self, content: str) -> str:
        """Simulate OpenWebUI's content preprocessing"""
        if self.debug:
            print("  1. Preprocessing content...")
        
        # OpenWebUI often normalizes whitespace
        processed = content.strip()
        
        # Handle consecutive newlines (OpenWebUI behavior)
        processed = re.sub(r'\n{3,}', '\n\n', processed)
        
        if self.debug:
            print(f"     Normalized whitespace: {len(content)} -> {len(processed)} chars")
        
        return processed
    
    def _parse_markdown(self, content: str) -> str:
        """Simulate markdown-it parsing (used by OpenWebUI)"""
        if self.debug:
            print("  2. Parsing markdown...")
        
        html = content
        
        # Bold text
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        
        # Italic text
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Headers (if any)
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        
        # Process bullet points - this is where OpenWebUI often has issues
        html = self._process_bullet_points(html)
        
        # Line breaks - critical for OpenWebUI
        html = self._process_line_breaks(html)
        
        if self.debug:
            print("     Processed markdown elements")
        
        return html
    
    def _process_bullet_points(self, content: str) -> str:
        """Process bullet points - simulate OpenWebUI's list handling"""
        if self.debug:
            print("  3. Processing bullet points...")
        
        lines = content.split('\n')
        processed_lines = []
        in_list = False
        
        for line in lines:
            stripped = line.strip()
            
            # Check if this is a bullet point
            if re.match(r'^[-*+]\s+', stripped):
                if not in_list:
                    processed_lines.append('<ul>')
                    in_list = True
                
                # Extract bullet content
                bullet_content = re.sub(r'^[-*+]\s+', '', stripped)
                processed_lines.append(f'<li>{bullet_content}</li>')
                
            else:
                if in_list:
                    processed_lines.append('</ul>')
                    in_list = False
                
                if stripped:  # Non-empty line
                    processed_lines.append(line)
                else:  # Empty line
                    processed_lines.append('')
        
        # Close list if still open
        if in_list:
            processed_lines.append('</ul>')
        
        result = '\n'.join(processed_lines)
        
        if self.debug:
            bullet_count = len(re.findall(r'<li>', result))
            print(f"     Found {bullet_count} bullet points")
        
        return result
    
    def _process_line_breaks(self, content: str) -> str:
        """Process line breaks - simulate OpenWebUI's line break handling"""
        if self.debug:
            print("  4. Processing line breaks...")
        
        # Two spaces + newline should become <br>
        content = re.sub(r'  \n', '<br>\n', content)
        
        # Double newlines should become paragraph breaks
        content = re.sub(r'\n\n+', '</p><p>', content)
        
        # Wrap in paragraph tags
        if not content.startswith('<p>'):
            content = '<p>' + content
        if not content.endswith('</p>'):
            content = content + '</p>'
        
        # Clean up empty paragraphs
        content = re.sub(r'<p>\s*</p>', '', content)
        
        if self.debug:
            br_count = len(re.findall(r'<br>', content))
            p_count = len(re.findall(r'<p>', content))
            print(f"     Added {br_count} line breaks, {p_count} paragraphs")
        
        return content
    
    def _apply_openwebui_rendering(self, html: str) -> str:
        """Apply OpenWebUI-specific rendering rules"""
        if self.debug:
            print("  5. Applying OpenWebUI rendering rules...")
        
        # OpenWebUI sometimes strips certain whitespace
        html = re.sub(r'>\s+<', '><', html)
        
        # Handle nested elements
        html = re.sub(r'<p><ul>', '<ul>', html)
        html = re.sub(r'</ul></p>', '</ul>', html)
        
        return html
    
    def _generate_visual_representation(self, html: str) -> str:
        """Generate a visual representation of how it would appear in OpenWebUI"""
        if self.debug:
            print("  6. Generating visual representation...")
        
        # Convert HTML back to visual text
        visual = html
        
        # Convert HTML elements to visual equivalents
        visual = re.sub(r'<strong>(.*?)</strong>', r'**\1**', visual)
        visual = re.sub(r'<em>(.*?)</em>', r'*\1*', visual)
        visual = re.sub(r'<h3>(.*?)</h3>', r'\n### \1\n', visual)
        visual = re.sub(r'<h2>(.*?)</h2>', r'\n## \1\n', visual)
        
        # Convert lists
        visual = re.sub(r'<ul>', '\n', visual)
        visual = re.sub(r'</ul>', '\n', visual)
        visual = re.sub(r'<li>(.*?)</li>', r'• \1', visual)
        
        # Convert paragraphs and line breaks
        visual = re.sub(r'<p>', '', visual)
        visual = re.sub(r'</p>', '\n\n', visual)
        visual = re.sub(r'<br>', '\n', visual)
        
        # Clean up
        visual = re.sub(r'\n{3,}', '\n\n', visual)
        visual = visual.strip()
        
        return visual
    
    def _get_debug_info(self, original: str, processed: str, html: str, final: str) -> Dict[str, Any]:
        """Generate debug information"""
        return {
            'original_length': len(original),
            'processed_length': len(processed),
            'html_length': len(html),
            'final_length': len(final),
            'newline_count': original.count('\n'),
            'double_space_newlines': original.count('  \n'),
            'bullet_points': len(re.findall(r'^[-*+]\s+', original, re.MULTILINE)),
            'bold_elements': len(re.findall(r'\*\*(.*?)\*\*', original)),
        }

def test_formatting_with_mock():
    """Test current formatting with the mock renderer"""
    
    # Import our API
    import sys
    sys.path.append('.')
    from direct_credit_api_fixed import MultiProviderCreditAPI
    
    api = MultiProviderCreditAPI()
    renderer = OpenWebUIMockRenderer()
    
    # Test response
    test_response = '''Hey Esteban! 🌟 I'm excited to help you understand your credit report better! ### Credit Scores: • TransUnion: 627 • Experian: 689 • Equifax: 635 ### Account Overview: • Credit Limits: $300.00 • $751.00 • $600.00 • $1,250.00 • $3,000.00 • $500.00 • $200.00 • Credit Balances: • $285 • $331 • $0 • $210 • Account Types: • Revolving • Installment ### Payment History: • Late Payments: • 30-day: Several instances noted, with recent trends showing improvement! 🎉 ### Key Insights: • Your TransUnion score is currently at 627, which is a great starting point.'''
    
    print("🧪 TESTING CURRENT FORMATTING WITH OPENWEBUI MOCK")
    print("=" * 60)
    
    # Format with our current system
    formatted = api._enhance_response_formatting(test_response)
    
    # Render with mock
    result = renderer.render_message(formatted)
    
    print("\n🎨 VISUAL RESULT (How it appears in OpenWebUI):")
    print("-" * 50)
    print(result['visual'])
    print("-" * 50)
    
    print(f"\n📊 DEBUG INFO:")
    for key, value in result['debug_info'].items():
        print(f"  {key}: {value}")
    
    print(f"\n🔍 ANALYSIS:")
    debug = result['debug_info']
    
    if debug['double_space_newlines'] > 0:
        print(f"  ✅ Found {debug['double_space_newlines']} two-space line breaks")
    else:
        print(f"  ❌ No two-space line breaks found")
    
    if debug['bullet_points'] > 0:
        print(f"  ✅ Found {debug['bullet_points']} bullet points")
    else:
        print(f"  ❌ No proper bullet points found")
    
    if debug['bold_elements'] > 0:
        print(f"  ✅ Found {debug['bold_elements']} bold elements")
    else:
        print(f"  ❌ No bold elements found")
    
    return result

if __name__ == "__main__":
    test_formatting_with_mock()
