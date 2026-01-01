
import ast
import os
import sys

def check_syntax(directory):
    print(f"🔍 Scanning {directory} for syntax fractures...")
    issues = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        source = f.read()
                    ast.parse(source)
                except SyntaxError as e:
                    print(f"❌ Syntax Fracture in {path}:")
                    print(f"   Line {e.lineno}: {e.msg}")
                    print(f"   {e.text.strip() if e.text else ''}")
                    issues += 1
                except Exception as e:
                    print(f"⚠️  Unknown Error in {path}: {e}")
                    issues += 1
    
    if issues == 0:
        print("✨ No syntax fractures detected.")
    else:
        print(f"💔 Found {issues} fractures.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "src/pillars/correspondences"
    check_syntax(target)
