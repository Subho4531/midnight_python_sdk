#!/usr/bin/env python3
"""
Validation script for CLI test suite.
Checks test coverage and structure without running actual tests.
"""

import ast
import re
from pathlib import Path


def analyze_test_file(file_path):
    """Analyze test file structure and coverage"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse AST to find test methods
    tree = ast.parse(content)
    
    test_methods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            test_methods.append(node.name)
    
    return test_methods


def analyze_cli_reference(ref_path):
    """Extract commands from CLI reference documentation"""
    
    with open(ref_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract command patterns
    commands = set()
    
    # Find command examples in markdown
    command_patterns = [
        r'midnight (\w+)(?: (\w+))?',  # Basic commands
        r'`midnight (\w+)(?: (\w+))?`',  # Inline code commands
    ]
    
    for pattern in command_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if isinstance(match, tuple):
                cmd = ' '.join(filter(None, match))
                commands.add(cmd.replace(' ', '_'))
            else:
                commands.add(match)
    
    return commands


def validate_coverage():
    """Validate test coverage against CLI reference"""
    
    print("🔍 Validating CLI Test Coverage")
    print("=" * 50)
    
    # Analyze test file
    test_file = Path("test_complete_cli_routes.py")
    if not test_file.exists():
        print("❌ Test file not found!")
        return False
    
    test_methods = analyze_test_file(test_file)
    print(f"📊 Found {len(test_methods)} test methods")
    
    # Analyze CLI reference
    ref_file = Path("docs/cli/COMPLETE_CLI_REFERENCE.md")
    if not ref_file.exists():
        print("⚠️  CLI reference not found, skipping command coverage check")
        documented_commands = set()
    else:
        documented_commands = analyze_cli_reference(ref_file)
        print(f"📚 Found {len(documented_commands)} documented commands")
    
    # Check test structure
    print("\n🏗️  Test Structure Analysis")
    print("-" * 30)
    
    categories = {
        'wallet': 0,
        'config': 0,
        'contract': 0,
        'transfer': 0,
        'balance': 0,
        'proof': 0,
        'ai': 0,
        'explorer': 0,
        'system': 0,
        'node': 0,
        'events': 0,
        'console': 0,
        'tx': 0
    }
    
    for method in test_methods:
        for category in categories:
            if category in method:
                categories[category] += 1
                break
    
    for category, count in categories.items():
        status = "✅" if count > 0 else "❌"
        print(f"{status} {category.capitalize()}: {count} tests")
    
    # Check for essential test patterns
    print("\n🔧 Essential Test Patterns")
    print("-" * 30)
    
    essential_patterns = [
        ('test_version_option', 'Version command'),
        ('test_help_option', 'Help command'),
        ('test_wallet_new', 'Wallet creation'),
        ('test_config_init', 'Config initialization'),
        ('test_system_status', 'System status'),
        ('test_invalid_command', 'Error handling'),
        ('test_wallet_workflow', 'Integration test'),
    ]
    
    for pattern, description in essential_patterns:
        found = any(pattern in method for method in test_methods)
        status = "✅" if found else "❌"
        print(f"{status} {description}")
    
    # Summary
    print(f"\n📈 Coverage Summary")
    print("-" * 20)
    print(f"Total test methods: {len(test_methods)}")
    print(f"Categories covered: {sum(1 for count in categories.values() if count > 0)}/{len(categories)}")
    
    covered_categories = sum(1 for count in categories.values() if count > 0)
    coverage_percentage = (covered_categories / len(categories)) * 100
    
    if coverage_percentage >= 90:
        print(f"✅ Excellent coverage: {coverage_percentage:.1f}%")
    elif coverage_percentage >= 70:
        print(f"⚠️  Good coverage: {coverage_percentage:.1f}%")
    else:
        print(f"❌ Insufficient coverage: {coverage_percentage:.1f}%")
    
    return coverage_percentage >= 70


def check_test_syntax():
    """Check test file syntax and imports"""
    
    print("\n🔍 Syntax Validation")
    print("-" * 20)
    
    try:
        with open("test_complete_cli_routes.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check syntax
        ast.parse(content)
        print("✅ Syntax is valid")
        
        # Check imports
        required_imports = ['pytest', 'subprocess', 'json', 'tempfile', 'os']
        for imp in required_imports:
            if f"import {imp}" in content or f"from {imp}" in content:
                print(f"✅ {imp} imported")
            else:
                print(f"❌ {imp} missing")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main validation function"""
    
    print("🧪 Midnight CLI Test Suite Validation")
    print("=" * 40)
    
    syntax_ok = check_test_syntax()
    coverage_ok = validate_coverage()
    
    print(f"\n🎯 Final Result")
    print("-" * 15)
    
    if syntax_ok and coverage_ok:
        print("✅ Test suite validation PASSED")
        print("🚀 Ready to run comprehensive CLI tests!")
        return 0
    else:
        print("❌ Test suite validation FAILED")
        if not syntax_ok:
            print("   - Fix syntax errors")
        if not coverage_ok:
            print("   - Improve test coverage")
        return 1


if __name__ == "__main__":
    exit(main())