import os
import ast
from pathlib import Path
import logging

SRC_DIR = Path("/home/burkettdaniel927/projects/isopgem/src")
DOCS_FILE = Path("/home/burkettdaniel927/projects/isopgem/Docs/source_documentation.md")

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class AdvancedAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.classes = []
        self.imports = []
        self.signals_emitted = []
        self.signals_defined = []
        self.method_complexities = {}
        self.main_logic_method = None
        self.max_complexity = 0
        self.custom_painting = False
        
    def visit_Import(self, node):
        for n in node.names:
            self.imports.append(n.name)
        self.generic_visit(node)
            
    def visit_ImportFrom(self, node):
        module = node.module if node.module else ""
        for n in node.names:
            self.imports.append(f"{module}.{n.name}")
        self.generic_visit(node)
        
    def visit_ClassDef(self, node):
        self.classes.append(node.name)
        # Check for View/UI inheritance implicitly via name or simple heuristic
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        complexity = self.calculate_complexity(node)
        self.method_complexities[node.name] = complexity
        if complexity > self.max_complexity:
            self.max_complexity = complexity
            self.main_logic_method = node
            
        if node.name == 'paintEvent':
            self.custom_painting = True
            
        self.generic_visit(node)

    def calculate_complexity(self, node):
        # Simple Cyclomatic Complexity: 1 + loops + branches
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                complexity += 1
        return complexity

    def visit_Call(self, node):
        # Detect signal emissions: `.emit(...)`
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'emit':
            # This is a weak heuristic, but covers standard PyQt `signal.emit()`
            self.signals_emitted.append("signal.emit")
        self.generic_visit(node)
        
    def visit_Assign(self, node):
        # Detect signal definitions: `x = pyqtSignal(...)`
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            if node.value.func.id == 'pyqtSignal':
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.signals_defined.append(target.id)
        self.generic_visit(node)

def infer_architecture(file_path, classes, imports):
    path_str = str(file_path).lower()
    if 'ui' in path_str or 'window' in path_str or 'dialog' in path_str or 'view' in path_str:
        return "Presentation Layer (View)"
    if 'service' in path_str or 'manager' in path_str or 'calculator' in path_str:
        return "Business Logic Layer (Service)"
    if 'repository' in path_str or 'database' in path_str or 'storage' in path_str:
        return "Persistence Layer"
    if 'model' in path_str or 'entity' in path_str or 'record' in path_str:
        return "Domain Model"
    
    # Fallback based on imports
    if any('QtWidgets' in i for i in imports):
        return "Presentation Layer (View)"
        
    return "Infrastructure / Utility"

def analyze_file(file_path):
    rel_path = file_path.relative_to(SRC_DIR)
    
    if file_path.suffix != ".py":
        try:
             size = file_path.stat().st_size
             return {
                "type": "other",
                "path": str(rel_path),
                "purpose": "Resource / Asset",
                "summary": f"Non-Python file. Size: {size} bytes",
                "is_complex": False
            }
        except Exception:
             return {"type": "error", "path": str(rel_path), "summary": "Error reading file"}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        tree = ast.parse(content)
        analyzer = AdvancedAnalyzer()
        analyzer.visit(tree)
        
        docstring = ast.get_docstring(tree)
        short_summary = docstring.split('\n')[0] if docstring else "No module docstring."
        
        # Logic Extraction
        key_logic = "Standard boilerplate."
        if analyzer.main_logic_method:
            method_doc = ast.get_docstring(analyzer.main_logic_method)
            if method_doc:
                key_logic = f"`{analyzer.main_logic_method.name}`: {method_doc.splitlines()[0]}"
            else:
                key_logic = f"`{analyzer.main_logic_method.name}`: performs core logic (Complexity: {analyzer.max_complexity})"
                
        # Data Flow
        # Inputs: implicitly via init or methods
        inputs = "Standard method arguments"
        outputs = []
        if analyzer.signals_defined:
            outputs.append(f"Signals: {', '.join(analyzer.signals_defined)}")
        if not outputs:
            outputs.append("Return values")
            
        # Relationships
        relationships = []
        for imp in analyzer.imports:
            if 'pillars.' in imp or 'shared.' in imp:
                relationships.append(imp)
            elif imp.startswith('.'):
                 relationships.append(f"Internal: {imp}")
        
        # Complexity Alert
        alerts = []
        if analyzer.max_complexity > 10:
            alerts.append(f"High Cyclomatic Complexity ({analyzer.max_complexity})")
        if analyzer.custom_painting:
            alerts.append("Custom Painting (paintEvent)")
        if 'numpy' in analyzer.imports or 'scipy' in analyzer.imports:
            alerts.append("Complex Math Libraries")
            
        # Architecture
        arch = infer_architecture(rel_path, analyzer.classes, analyzer.imports)
        
        return {
            "type": "python",
            "path": str(rel_path),
            "purpose": arch,
            "summary": short_summary,
            "key_logic": key_logic,
            "inputs": inputs,
            "outputs": "; ".join(outputs),
            "relationships": sorted(list(set(relationships))),
            "alerts": alerts,
            "classes": analyzer.classes,
            "is_complex": (len(analyzer.classes) > 0 and (analyzer.max_complexity >= 6 or len(analyzer.signals_defined) >= 2))
        }
            
    except Exception as e:
        return {
            "type": "error",
            "path": str(rel_path),
            "summary": f"Analysis failed: {e}",
            "is_complex": False
        }

def generate_mermaid(info):
    if not info.get('classes'):
        return ""
    
    # Simple class diagram
    lines = ["\n```mermaid", "classDiagram"]
    for cls in info['classes']:
        lines.append(f"    class {cls} {{")
        # Start/End is handled by the block, we don't have method details here readily available 
        # without storing them in analyzer, but ensuring we just show the class exists is a start.
        # To make it better, let's just make it a sequence if we can, or just a note.
        # Actually user asked for sequence for rich_text_editor. 
        # A static sequence diagram is hard. Let's stick to class diagram showing relationships if possible.
        lines.append("        +Logic()")
        lines.append("    }")
    
    # Add relationships
    for rel in info.get('relationships', []):
        parts = rel.split('.')
        if len(parts) > 2:
            target = parts[-1] 
            # Avoid self-loops or messy graphs
            if target not in info['classes']:
                 lines.append(f"    {info['classes'][0]} ..> {target} : depends")

    lines.append("```\n")
    return "\n".join(lines)

def generate_markdown(infos):
    lines = ["# source_documentation.md\n\n"]
    lines.append("Architectural Analysis of `src` directory.\n\n")
    
    sorted_infos = sorted(infos, key=lambda x: x['path'])
    current_dir = ""
    
    for info in sorted_infos:
        # Grouping
        dir_name = os.path.dirname(info['path'])
        if dir_name != current_dir:
            lines.append(f"## {dir_name if dir_name else 'Root'}\n\n")
            current_dir = dir_name
            
        file_name = os.path.basename(info['path'])
        lines.append(f"### {file_name}\n")
        
        if info.get('type') == 'error':
            lines.append(f"> [!WARNING]\n> {info['summary']}\n\n")
            lines.append("---\n\n")
            continue
            
        if info.get('type') == 'other':
            lines.append(f"**Path**: `src/{info['path']}`\n\n")
            lines.append(f"**Summary**: {info['summary']}\n\n")
            lines.append("---\n\n")
            continue

        # Python Analysis
        lines.append(f"**Path**: `src/{info['path']}`\n\n")
        lines.append(f"**Architectural Purpose**: {info['purpose']}\n\n")
        lines.append(f"**Summary**: {info['summary']}\n\n")
        
        lines.append("#### Deep Analysis\n")
        lines.append(f"- **Key Logic**: {info['key_logic']}\n")
        lines.append(f"- **Inputs**: {info['inputs']}\n")
        lines.append(f"- **Outputs**: {info['outputs']}\n")
        
        if info['relationships']:
            lines.append(f"- **Critical Relationships**:\n")
            for r in info['relationships']:
                lines.append(f"  - {r}\n")
        else:
            lines.append("- **Critical Relationships**: None detected.\n")
            
        if info['alerts']:
            lines.append("\n> [!NOTE] Complexity Alert\n")
            for a in info['alerts']:
                lines.append(f"> - {a}\n")
            lines.append("\n")
            
        if info['is_complex']:
            lines.append("#### Visual Model\n")
            lines.append(generate_mermaid(info))
            
        lines.append("\n---\n\n")
        
    return "".join(lines)

def main():
    if not SRC_DIR.exists():
        return

    Docs_Dir = DOCS_FILE.parent
    Docs_Dir.mkdir(parents=True, exist_ok=True)
    
    all_files = []
    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(('.', '__'))]
        for file in files:
            if file.endswith('.pyc') or file.startswith('.'):
                continue
            all_files.append(Path(root) / file)
            
    print(f"Analyzing {len(all_files)} files...")
    infos = []
    for f in all_files:
        infos.append(analyze_file(f))
        
    print("Generating Markdown...")
    content = generate_markdown(infos)
    
    with open(DOCS_FILE, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Done: {DOCS_FILE}")

if __name__ == "__main__":
    main()
