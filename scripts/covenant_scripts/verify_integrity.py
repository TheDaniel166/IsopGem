
import ast
import argparse
import sys
import os
import builtins

def check_structure(filepath):
    """
    Check for SyntaxErrors and undefined names.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as e:
        print(f"❌ SYNTAX ERROR: {filepath}:{e.lineno}:{e.offset} - {e.msg}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Could not parse {filepath} - {e}")
        return False

    # Check for NameErrors (undefined variables)
    undefined_names = []
    
    # Builtins + common globals
    known_globals = set(dir(builtins)) | {'__file__', '__name__', '__doc__', '__path__', 'self'}

    # Walk the tree
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id not in known_globals:
                # Naive check: does not account for scope.
                # To do this properly requires a ScopeVisitor.
                # For now, let's rely on pyflakes if available, or just syntax check.
                pass
    
    # If we want a simple internal checker without deps, it's hard to do name resolution perfectly.
    # So we'll trust 'pyflakes' if installed, otherwise just Syntax.
    
    try:
        import pyflakes.api
        from pyflakes.reporter import Reporter
        
        # Capture output
        from io import StringIO
        stdout = StringIO()
        stderr = StringIO()
        reporter = Reporter(stdout, stderr)
        
        count = pyflakes.api.checkPath(filepath, reporter)
        if count > 0:
            print(f"❌ INTEGRITY FAILURE ({count} issues):")
            print(stdout.getvalue())
            print(stderr.getvalue())
            return False
            
    except ImportError:
        print("⚠️  Pyflakes not installed. Only checking Syntax.")
        # Syntax passed earlier
    
    print(f"✅ INTEGRITY PASSED: {filepath}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify code integrity (Syntax + Lint).")
    parser.add_argument("files", nargs="+", help="Files to check")
    args = parser.parse_args()
    
    success = True
    for f in args.files:
        if not os.path.exists(f):
            print(f"❌ File not found: {f}")
            success = False
            continue
            
        if not check_structure(f):
            success = False
            
    sys.exit(0 if success else 1)
