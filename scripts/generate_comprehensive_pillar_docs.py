#!/usr/bin/env python3
"""
Generate COMPREHENSIVE pillar documentation (API + Architecture + Features + UI).

Extends generate_pillar_docs.py with:
- Architecture pattern documentation (data flow, design patterns)
- Feature specification documentation (user-facing features)
- UI component documentation (windows, widgets, views)

Usage:
    python scripts/generate_comprehensive_pillar_docs.py geometry
    python scripts/generate_comprehensive_pillar_docs.py geometry --sections architecture,features
    python scripts/generate_comprehensive_pillar_docs.py astrology --force
"""

import ast
import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime


@dataclass
class UIComponentInfo:
    """Information about a UI component (window/widget)."""
    name: str
    file_path: str
    base_classes: List[str]
    signals: List[str]
    slots: List[str]
    widgets: List[str]
    docstring: Optional[str]
    has_3d: bool
    has_opengl: bool


@dataclass
class FeatureInfo:
    """Information about a user-facing feature."""
    name: str
    entry_points: List[str]  # Windows/functions that implement the feature
    purpose: str
    ui_files: List[str]
    service_files: List[str]


@dataclass
class ArchitecturePattern:
    """Information about an architectural pattern."""
    name: str
    pattern_type: str  # "strategy", "observer", "adapter", etc.
    related_files: List[str]
    description: str


class ComprehensiveAnalyzer:
    """Analyzes pillar code for ALL documentation types."""
    
    def __init__(self, pillar_path: Path):
        self.pillar_path = pillar_path
        self.project_root = pillar_path.parent.parent.parent
    
    def find_ui_components(self) -> List[UIComponentInfo]:
        """Find all UI components (windows, widgets, views)."""
        ui_dir = self.pillar_path / "ui"
        if not ui_dir.exists():
            return []
        
        components = []
        for py_file in ui_dir.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
            
            component = self._analyze_ui_file(py_file)
            if component:
                components.append(component)
        
        return components
    
    def _analyze_ui_file(self, file_path: Path) -> Optional[UIComponentInfo]:
        """Analyze a single UI file for component info."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            # Find QWidget/QWindow classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    bases = [self._get_base_name(b) for b in node.bases]
                    
                    # Check if it's a UI component
                    ui_bases = {'QWidget', 'QDialog', 'QMainWindow', 'QWindow', 'QFrame'}
                    if any(base in ui_bases for base in bases):
                        return UIComponentInfo(
                            name=node.name,
                            file_path=str(file_path.relative_to(self.project_root)),
                            base_classes=bases,
                            signals=self._find_signals(node),
                            slots=self._find_slots(node),
                            widgets=self._find_widget_usage(source),
                            docstring=ast.get_docstring(node),
                            has_3d="3d" in file_path.stem.lower() or "scene" in file_path.stem.lower(),
                            has_opengl="opengl" in source.lower() or "QOpenGL" in source
                        )
            
            return None
        except Exception as e:
            print(f"  Warning: Could not analyze {file_path}: {e}")
            return None
    
    def _find_signals(self, class_node: ast.ClassDef) -> List[str]:
        """Find PyQt signals in a class."""
        signals = []
        for node in ast.walk(class_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if isinstance(node.value, ast.Call):
                            func = node.value.func
                            if isinstance(func, ast.Name) and 'signal' in func.id.lower():
                                signals.append(target.id)
        return signals
    
    def _find_slots(self, class_node: ast.ClassDef) -> List[str]:
        """Find slot methods in a class."""
        slots = []
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                # Slots often start with 'on_' or have @Slot decorator
                if item.name.startswith('on_') or item.name.startswith('_on_'):
                    slots.append(item.name)
                for dec in item.decorator_list:
                    if isinstance(dec, ast.Name) and dec.id == 'Slot':
                        slots.append(item.name)
        return slots
    
    def _find_widget_usage(self, source: str) -> List[str]:
        """Find PyQt widgets used in source code."""
        widgets = set()
        qt_widgets = [
            'QPushButton', 'QLabel', 'QLineEdit', 'QTextEdit', 'QComboBox',
            'QSpinBox', 'QCheckBox', 'QRadioButton', 'QSlider', 'QListWidget',
            'QTreeWidget', 'QTableWidget', 'QScrollArea', 'QGroupBox', 'QTabWidget'
        ]
        
        for widget in qt_widgets:
            if widget in source:
                widgets.add(widget)
        
        return sorted(list(widgets))
    
    def _get_base_name(self, base: ast.expr) -> str:
        """Get base class name."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return ast.unparse(base)
        return "Unknown"
    
    def identify_features(self) -> List[FeatureInfo]:
        """Identify user-facing features by analyzing UI and services."""
        features = []
        ui_dir = self.pillar_path / "ui"
        
        if not ui_dir.exists():
            return []
        
        # Group by feature (based on file naming patterns)
        feature_groups = {}
        
        for py_file in ui_dir.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
            
            # Extract feature name from filename
            stem = py_file.stem
            
            # Common patterns: calculator_window, esoteric_wisdom_window, base_figurate_window
            if stem.endswith("_window"):
                feature_name = stem.replace("_window", "").replace("_", " ").title()
            elif stem.endswith("_widget"):
                feature_name = stem.replace("_widget", "").replace("_", " ").title()
            elif stem.endswith("_view"):
                feature_name = stem.replace("_view", "").replace("_", " ").title()
            elif stem == f"{self.pillar_path.name}_hub":
                feature_name = f"{self.pillar_path.name.title()} Hub"
            else:
                feature_name = stem.replace("_", " ").title()
            
            if feature_name not in feature_groups:
                feature_groups[feature_name] = []
            
            feature_groups[feature_name].append(str(py_file.relative_to(self.project_root)))
        
        # Convert to FeatureInfo objects
        for feature_name, ui_files in feature_groups.items():
            features.append(FeatureInfo(
                name=feature_name,
                entry_points=ui_files,
                purpose="",  # Will be filled by AI
                ui_files=ui_files,
                service_files=[]  # Will be enhanced by AI
            ))
        
        return features
    
    def identify_architecture_patterns(self) -> List[ArchitecturePattern]:
        """Identify architectural patterns in the pillar."""
        patterns = []
        
        # Look for common patterns
        services_dir = self.pillar_path / "services"
        models_dir = self.pillar_path / "models"
        ui_dir = self.pillar_path / "ui"
        
        # Strategy pattern (multiple *_calculator.py or *_service.py files)
        if services_dir.exists():
            service_files = list(services_dir.glob("*_service.py"))
            calculator_files = list(services_dir.glob("*_calculator.py"))
            
            if len(calculator_files) > 3:
                patterns.append(ArchitecturePattern(
                    name="Calculator Strategy Pattern",
                    pattern_type="strategy",
                    related_files=[str(f.relative_to(self.project_root)) for f in calculator_files[:5]],
                    description="Multiple calculator implementations following a common interface"
                ))
            
            if len(service_files) > 2:
                patterns.append(ArchitecturePattern(
                    name="Service Layer",
                    pattern_type="layer",
                    related_files=[str(f.relative_to(self.project_root)) for f in service_files[:5]],
                    description="Business logic services separating UI from data"
                ))
        
        # Model-View separation
        if models_dir.exists() and ui_dir.exists():
            patterns.append(ArchitecturePattern(
                name="Model-View Separation",
                pattern_type="mvc",
                related_files=[],
                description="Clear separation between data models and UI components"
            ))
        
        # Adapter/Scene pattern (for 3D rendering)
        if ui_dir.exists():
            scene_files = list(ui_dir.rglob("*scene*.py"))
            adapter_files = list(ui_dir.rglob("*adapter*.py"))
            
            if scene_files or adapter_files:
                patterns.append(ArchitecturePattern(
                    name="Scene Adapter Pattern",
                    pattern_type="adapter",
                    related_files=[
                        str(f.relative_to(self.project_root))
                        for f in (scene_files + adapter_files)[:5]
                    ],
                    description="Adapts 3D scene data for rendering in different views"
                ))
        
        return patterns


class ComprehensiveDocGenerator:
    """Generates ALL types of pillar documentation."""
    
    def __init__(self, pillar_name: str, output_dir: Path):
        self.pillar_name = pillar_name
        self.output_dir = output_dir
        self.today = datetime.now().strftime("%Y-%m-%d")
    
    def generate_architecture_doc(self, pattern: ArchitecturePattern) -> str:
        """Generate architecture pattern documentation."""
        
        safe_name = pattern.name.lower().replace(" ", "_").replace("-", "_")
        
        doc = f"""# {pattern.name}

<!-- Last Verified: {self.today} -->

<cite>
**Referenced Files in This Document**
"""
        
        for file_path in pattern.related_files[:10]:
            doc += f"- [{file_path}](file://{file_path})\n"
        
        doc += """</cite>

## Table of Contents
1. [Pattern Overview](#pattern-overview)
2. [Architectural Diagram](#architectural-diagram)
3. [Key Components](#key-components)
4. [Data Flow](#data-flow)
5. [Implementation Details](#implementation-details)
6. [Trade-offs & Rationale](#trade-offs--rationale)
7. [Evolution & History](#evolution--history)

## Pattern Overview

"""
        
        doc += f"**Pattern Type**: {pattern.pattern_type.title()}\n\n"
        doc += f"{pattern.description}\n\n"
        doc += "<!-- AI_ENHANCE: Expand pattern description with:\n"
        doc += "- What problem does this pattern solve?\n"
        doc += "- Why was this pattern chosen?\n"
        doc += "- What are the key benefits?\n"
        doc += "-->\n\n"
        
        doc += "## Architectural Diagram\n\n"
        doc += "```mermaid\n"
        doc += "<!-- AI_ENHANCE: Add architecture diagram showing:\n"
        
        if pattern.pattern_type == "strategy":
            doc += "- Strategy interface/abstract base\n"
            doc += "- Concrete strategy implementations\n"
            doc += "- Context that uses strategies\n"
            doc += "- Client code\n"
        elif pattern.pattern_type == "adapter":
            doc += "- Target interface\n"
            doc += "- Adaptee (thing being adapted)\n"
            doc += "- Adapter implementation\n"
            doc += "- Client usage\n"
        elif pattern.pattern_type == "layer":
            doc += "- UI Layer\n"
            doc += "- Service Layer\n"
            doc += "- Data Layer\n"
            doc += "- Dependencies flow\n"
        else:
            doc += "- Key classes and their relationships\n"
            doc += "- Data flow direction\n"
            doc += "- Dependency arrows\n"
        
        doc += "-->\n"
        doc += "```\n\n"
        
        doc += "## Key Components\n\n"
        doc += "### Core Classes\n\n"
        
        for file_path in pattern.related_files[:5]:
            file_name = Path(file_path).stem
            class_name = "".join(word.title() for word in file_name.split("_"))
            doc += f"#### `{class_name}`\n\n"
            doc += f"**Location**: `{file_path}`\n\n"
            doc += "<!-- AI_ENHANCE: Add:\n"
            doc += "- Class responsibility\n"
            doc += "- Key methods\n"
            doc += "- Usage example\n"
            doc += "-->\n\n"
        
        doc += "## Data Flow\n\n"
        doc += "```mermaid\n"
        doc += "sequenceDiagram\n"
        doc += "    <!-- AI_ENHANCE: Add sequence diagram showing:\n"
        doc += "    - Step-by-step data flow\n"
        doc += "    - Method calls between components\n"
        doc += "    - Data transformations\n"
        doc += "    -->\n"
        doc += "```\n\n"
        
        doc += "## Implementation Details\n\n"
        doc += "### Pattern Application\n\n"
        doc += "<!-- AI_ENHANCE: Explain how the pattern is implemented:\n"
        doc += "- How are components instantiated?\n"
        doc += "- How do components communicate?\n"
        doc += "- What are the extension points?\n"
        doc += "-->\n\n"
        
        doc += "### Code Example\n\n"
        doc += "```python\n"
        doc += "# AI_ENHANCE: Add real usage example from the codebase\n"
        doc += "```\n\n"
        
        doc += "## Trade-offs & Rationale\n\n"
        doc += "### Advantages\n\n"
        doc += "<!-- AI_ENHANCE: List specific advantages in this pillar -->\n\n"
        doc += "### Disadvantages\n\n"
        doc += "<!-- AI_ENHANCE: List any downsides or complexity costs -->\n\n"
        doc += "### Alternative Approaches Considered\n\n"
        doc += "<!-- AI_ENHANCE: What other patterns were considered and why rejected? -->\n\n"
        
        doc += "## Evolution & History\n\n"
        doc += "<!-- AI_ENHANCE: Add:\n"
        doc += "- When was this pattern introduced?\n"
        doc += "- Has it changed over time?\n"
        doc += "- Are there plans to refactor?\n"
        doc += "-->\n\n"
        
        doc += "---\n\n"
        doc += "**Last Updated**: " + self.today + "\n"
        doc += "**Status**: Auto-generated skeleton (needs AI enhancement)\n\n"
        doc += "**Navigation:**\n"
        doc += f"- [← Architecture Index](./README.md)\n"
        doc += f"- [↑ {self.pillar_name.title()} Index](../INDEX.md)\n"
        
        return doc
    
    def generate_feature_doc(self, feature: FeatureInfo) -> str:
        """Generate feature specification documentation."""
        
        safe_name = feature.name.lower().replace(" ", "_").replace("-", "_")
        
        doc = f"""# {feature.name}

<!-- Last Verified: {self.today} -->

<cite>
**Referenced Files in This Document**
"""
        
        for file_path in feature.ui_files[:5]:
            doc += f"- [{file_path}](file://{file_path})\n"
        
        doc += """</cite>

## Table of Contents
1. [Feature Overview](#feature-overview)
2. [User Workflows](#user-workflows)
3. [UI Components](#ui-components)
4. [Business Logic](#business-logic)
5. [Data Model](#data-model)
6. [Integration Points](#integration-points)
7. [Future Enhancements](#future-enhancements)

## Feature Overview

### Purpose

<!-- AI_ENHANCE: Describe the feature's purpose:
- What user need does it address?
- What value does it provide?
- Who is the target user?
-->

### Key Capabilities

<!-- AI_ENHANCE: List the main things users can do:
- Primary action 1
- Primary action 2
- Primary action 3
-->

### Access Points

"""
        
        for entry in feature.entry_points:
            file_name = Path(entry).stem
            doc += f"- **{file_name}**: `{entry}`\n"
        
        doc += "\n## User Workflows\n\n"
        doc += "### Primary Workflow\n\n"
        doc += "```mermaid\n"
        doc += "flowchart TD\n"
        doc += "    <!-- AI_ENHANCE: Add user flow diagram:\n"
        doc += "    Start --> Action1\n"
        doc += "    Action1 --> Decision\n"
        doc += "    Decision -->|Yes| Action2\n"
        doc += "    Decision -->|No| Action3\n"
        doc += "    Action2 --> End\n"
        doc += "    Action3 --> End\n"
        doc += "    -->\n"
        doc += "```\n\n"
        
        doc += "### Step-by-Step Instructions\n\n"
        doc += "1. <!-- AI_ENHANCE: Add step 1 -->\n"
        doc += "2. <!-- AI_ENHANCE: Add step 2 -->\n"
        doc += "3. <!-- AI_ENHANCE: Add step 3 -->\n\n"
        
        doc += "### Alternative Workflows\n\n"
        doc += "<!-- AI_ENHANCE: Describe alternative paths or advanced usage -->\n\n"
        
        doc += "## UI Components\n\n"
        doc += "### Main Window/Widget\n\n"
        
        if feature.ui_files:
            main_file = feature.ui_files[0]
            doc += f"**Implementation**: `{main_file}`\n\n"
        
        doc += "```\n"
        doc += "<!-- AI_ENHANCE: Add ASCII UI mockup:\n"
        doc += "┌─────────────────────────────────┐\n"
        doc += "│ Feature Title                   │\n"
        doc += "├─────────────────────────────────┤\n"
        doc += "│ [Main content area]             │\n"
        doc += "│                                 │\n"
        doc += "│ [Buttons] [Controls]            │\n"
        doc += "└─────────────────────────────────┘\n"
        doc += "-->\n"
        doc += "```\n\n"
        
        doc += "### UI Elements\n\n"
        doc += "<!-- AI_ENHANCE: List key UI elements:\n"
        doc += "- Input fields\n"
        doc += "- Buttons\n"
        doc += "- Display areas\n"
        doc += "- Menus/toolbars\n"
        doc += "-->\n\n"
        
        doc += "### User Interactions\n\n"
        doc += "<!-- AI_ENHANCE: Describe how users interact:\n"
        doc += "- Click actions\n"
        doc += "- Keyboard shortcuts\n"
        doc += "- Drag-and-drop\n"
        doc += "- Context menus\n"
        doc += "-->\n\n"
        
        doc += "## Business Logic\n\n"
        doc += "### Core Services\n\n"
        doc += "<!-- AI_ENHANCE: List services used by this feature:\n"
        doc += "- ServiceName: responsibility\n"
        doc += "- ServiceName: responsibility\n"
        doc += "-->\n\n"
        
        doc += "### Calculation/Processing\n\n"
        doc += "<!-- AI_ENHANCE: Explain the core algorithms or processing:\n"
        doc += "- What calculations are performed?\n"
        doc += "- What transformations happen?\n"
        doc += "- What validations occur?\n"
        doc += "-->\n\n"
        
        doc += "### Business Rules\n\n"
        doc += "<!-- AI_ENHANCE: List key business rules:\n"
        doc += "- Rule 1\n"
        doc += "- Rule 2\n"
        doc += "- Rule 3\n"
        doc += "-->\n\n"
        
        doc += "## Data Model\n\n"
        doc += "### Input Data\n\n"
        doc += "<!-- AI_ENHANCE: What data does the feature accept? -->\n\n"
        doc += "### Output Data\n\n"
        doc += "<!-- AI_ENHANCE: What data does the feature produce? -->\n\n"
        doc += "### Persistence\n\n"
        doc += "<!-- AI_ENHANCE: Is data saved? Where? In what format? -->\n\n"
        
        doc += "## Integration Points\n\n"
        doc += "### Dependencies\n\n"
        doc += "<!-- AI_ENHANCE: What other pillars/features does this depend on? -->\n\n"
        doc += "### Signals & Events\n\n"
        doc += "<!-- AI_ENHANCE: What signals does it emit? What signals does it listen to? -->\n\n"
        doc += "### External APIs\n\n"
        doc += "<!-- AI_ENHANCE: Does it use external libraries or APIs? -->\n\n"
        
        doc += "## Future Enhancements\n\n"
        doc += "### Planned Features\n\n"
        doc += "<!-- AI_ENHANCE: List planned improvements -->\n\n"
        doc += "### Known Limitations\n\n"
        doc += "<!-- AI_ENHANCE: List current limitations -->\n\n"
        doc += "### User Requests\n\n"
        doc += "<!-- AI_ENHANCE: List common user requests -->\n\n"
        
        doc += "---\n\n"
        doc += "**Last Updated**: " + self.today + "\n"
        doc += "**Status**: Auto-generated skeleton (needs AI enhancement)\n\n"
        doc += "**Navigation:**\n"
        doc += f"- [← Features Index](./README.md)\n"
        doc += f"- [↑ {self.pillar_name.title()} Index](../INDEX.md)\n"
        
        return doc
    
    def generate_ui_component_doc(self, component: UIComponentInfo) -> str:
        """Generate UI component documentation."""
        
        doc = f"""# {component.name}

<!-- Last Verified: {self.today} -->

<cite>
**Referenced Files in This Document**
- [{component.file_path}](file://{component.file_path})
</cite>

## Table of Contents
1. [Component Overview](#component-overview)
2. [UI Layout](#ui-layout)
3. [Signals & Slots](#signals--slots)
4. [State Management](#state-management)
5. [User Interactions](#user-interactions)
6. [Integration](#integration)
7. [Implementation Details](#implementation-details)

## Component Overview

### Purpose

"""
        
        if component.docstring:
            doc += f"{component.docstring}\n\n"
        else:
            doc += "<!-- AI_ENHANCE: Describe the component's purpose -->\n\n"
        
        doc += "### Component Type\n\n"
        doc += f"**Base Classes**: {', '.join(component.base_classes)}\n\n"
        
        if component.has_3d:
            doc += "**Rendering**: This component includes 3D visualization\n\n"
        if component.has_opengl:
            doc += "**Technology**: Uses OpenGL for hardware-accelerated rendering\n\n"
        
        doc += "### Key Responsibilities\n\n"
        doc += "<!-- AI_ENHANCE: List the component's key responsibilities:\n"
        doc += "- Responsibility 1\n"
        doc += "- Responsibility 2\n"
        doc += "- Responsibility 3\n"
        doc += "-->\n\n"
        
        doc += "## UI Layout\n\n"
        doc += "### Visual Structure\n\n"
        doc += "```\n"
        doc += "<!-- AI_ENHANCE: Add ASCII UI layout:\n"
        doc += "┌────────────────────────────────────────┐\n"
        doc += "│ Window Title                           │\n"
        doc += "├────────────────────────────────────────┤\n"
        doc += "│ ┌────────────┐  ┌──────────────────┐  │\n"
        doc += "│ │  Sidebar   │  │  Main Area       │  │\n"
        doc += "│ │            │  │                  │  │\n"
        doc += "│ │  [Button]  │  │  [Content]       │  │\n"
        doc += "│ │  [Button]  │  │                  │  │\n"
        doc += "│ └────────────┘  └──────────────────┘  │\n"
        doc += "├────────────────────────────────────────┤\n"
        doc += "│ [Status Bar]                           │\n"
        doc += "└────────────────────────────────────────┘\n"
        doc += "-->\n"
        doc += "```\n\n"
        
        doc += "### Widget Hierarchy\n\n"
        
        if component.widgets:
            doc += "**Widgets Used**:\n"
            for widget in component.widgets:
                doc += f"- `{widget}`\n"
            doc += "\n"
        
        doc += "```mermaid\n"
        doc += "graph TD\n"
        doc += f"    A[{component.name}]\n"
        doc += "    <!-- AI_ENHANCE: Add widget hierarchy:\n"
        doc += "    A --> B[MainLayout]\n"
        doc += "    B --> C[Widget1]\n"
        doc += "    B --> D[Widget2]\n"
        doc += "    D --> E[SubWidget]\n"
        doc += "    -->\n"
        doc += "```\n\n"
        
        doc += "### Layout Code Pattern\n\n"
        doc += "```python\n"
        doc += "# AI_ENHANCE: Add actual layout code snippet from the file\n"
        doc += "```\n\n"
        
        doc += "## Signals & Slots\n\n"
        
        if component.signals:
            doc += "### Signals Emitted\n\n"
            for signal in component.signals:
                doc += f"#### `{signal}`\n\n"
                doc += "<!-- AI_ENHANCE: Describe when this signal is emitted and what it means -->\n\n"
        else:
            doc += "### Signals Emitted\n\n"
            doc += "<!-- AI_ENHANCE: List signals this component emits -->\n\n"
        
        if component.slots:
            doc += "### Slots (Event Handlers)\n\n"
            for slot in component.slots:
                doc += f"#### `{slot}()`\n\n"
                doc += "<!-- AI_ENHANCE: Describe what this slot does -->\n\n"
        else:
            doc += "### Slots (Event Handlers)\n\n"
            doc += "<!-- AI_ENHANCE: List key event handlers -->\n\n"
        
        doc += "### Signal Flow Diagram\n\n"
        doc += "```mermaid\n"
        doc += "sequenceDiagram\n"
        doc += "    <!-- AI_ENHANCE: Show signal flow:\n"
        doc += "    User->>Component: User Action\n"
        doc += "    Component->>Component: Process\n"
        doc += "    Component->>Parent: Signal\n"
        doc += "    Parent->>Service: Method Call\n"
        doc += "    -->\n"
        doc += "```\n\n"
        
        doc += "## State Management\n\n"
        doc += "### Component State\n\n"
        doc += "<!-- AI_ENHANCE: Describe the component's internal state:\n"
        doc += "- What data does it track?\n"
        doc += "- How is state initialized?\n"
        doc += "- How does state change?\n"
        doc += "-->\n\n"
        
        doc += "### State Transitions\n\n"
        doc += "```mermaid\n"
        doc += "stateDiagram-v2\n"
        doc += "    <!-- AI_ENHANCE: Add state diagram:\n"
        doc += "    [*] --> Idle\n"
        doc += "    Idle --> Active: User Input\n"
        doc += "    Active --> Processing: Submit\n"
        doc += "    Processing --> Complete: Success\n"
        doc += "    Processing --> Error: Failure\n"
        doc += "    Complete --> Idle: Reset\n"
        doc += "    Error --> Idle: Reset\n"
        doc += "    -->\n"
        doc += "```\n\n"
        
        doc += "## User Interactions\n\n"
        doc += "### Supported Actions\n\n"
        doc += "<!-- AI_ENHANCE: List user actions:\n"
        doc += "- Click button X → Does Y\n"
        doc += "- Enter text in Z → Does W\n"
        doc += "- Drag object → Does V\n"
        doc += "-->\n\n"
        
        doc += "### Keyboard Shortcuts\n\n"
        doc += "<!-- AI_ENHANCE: List keyboard shortcuts:\n"
        doc += "- Ctrl+N: New\n"
        doc += "- Ctrl+S: Save\n"
        doc += "- Ctrl+Q: Quit\n"
        doc += "-->\n\n"
        
        doc += "### Context Menus\n\n"
        doc += "<!-- AI_ENHANCE: Describe context menus if any -->\n\n"
        
        doc += "## Integration\n\n"
        doc += "### Parent/Owner\n\n"
        doc += "<!-- AI_ENHANCE: What creates this component? Where is it used? -->\n\n"
        doc += "### Services Used\n\n"
        doc += "<!-- AI_ENHANCE: What services does this component depend on? -->\n\n"
        doc += "### Communication Pattern\n\n"
        doc += "<!-- AI_ENHANCE: How does it communicate with other components? -->\n\n"
        
        doc += "## Implementation Details\n\n"
        doc += "### Initialization\n\n"
        doc += "```python\n"
        doc += "# AI_ENHANCE: Add __init__ method code\n"
        doc += "```\n\n"
        
        doc += "### Key Methods\n\n"
        doc += "<!-- AI_ENHANCE: List and describe key methods:\n"
        doc += "- method_name(): description\n"
        doc += "-->\n\n"
        
        if component.has_3d:
            doc += "### 3D Rendering\n\n"
            doc += "<!-- AI_ENHANCE: Explain 3D rendering specifics:\n"
            doc += "- How is the scene set up?\n"
            doc += "- What rendering backend is used?\n"
            doc += "- How is the camera controlled?\n"
            doc += "-->\n\n"
        
        if component.has_opengl:
            doc += "### OpenGL Implementation\n\n"
            doc += "<!-- AI_ENHANCE: Explain OpenGL usage:\n"
            doc += "- Shaders used\n"
            doc += "- Buffer management\n"
            doc += "- Performance considerations\n"
            doc += "-->\n\n"
        
        doc += "### Styling & Theming\n\n"
        doc += "<!-- AI_ENHANCE: How is the component styled?\n"
        doc += "- QSS stylesheets?\n"
        doc += "- Dynamic styling?\n"
        doc += "- Theme integration?\n"
        doc += "-->\n\n"
        
        doc += "---\n\n"
        doc += "**Last Updated**: " + self.today + "\n"
        doc += "**Status**: Auto-generated skeleton (needs AI enhancement)\n\n"
        doc += "**Navigation:**\n"
        doc += f"- [← UI Components Index](./README.md)\n"
        doc += f"- [↑ {self.pillar_name.title()} Index](../INDEX.md)\n"
        
        return doc


def main():
    parser = argparse.ArgumentParser(
        description="Generate comprehensive pillar documentation"
    )
    parser.add_argument("pillar", help="Pillar name (e.g., geometry, gematria)")
    parser.add_argument(
        "--sections",
        default="all",
        help="Comma-separated: api,architecture,features,ui_components (default: all)"
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--output", help="Output directory (default: wiki/02_pillars/PILLAR)")
    
    args = parser.parse_args()
    
    # Parse sections
    if args.sections == "all":
        sections = {"api", "architecture", "features", "ui_components"}
    else:
        sections = set(args.sections.split(","))
    
    # Setup paths
    project_root = Path.cwd()
    pillar_src = project_root / "src" / "pillars" / args.pillar
    
    if not pillar_src.exists():
        print(f"❌ Error: Pillar source not found: {pillar_src}")
        sys.exit(1)
    
    output_dir = (
        Path(args.output) if args.output 
        else project_root / "wiki" / "02_pillars" / args.pillar
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🔮 Generating comprehensive documentation for {args.pillar} pillar...")
    print(f"   Source: {pillar_src}")
    print(f"   Output: {output_dir}")
    print(f"   Sections: {', '.join(sections)}")
    
    # Create subdirectories
    for section in ["api", "architecture", "features", "ui_components"]:
        (output_dir / section).mkdir(exist_ok=True)
    
    # Initialize analyzers
    analyzer = ComprehensiveAnalyzer(pillar_src)
    generator = ComprehensiveDocGenerator(args.pillar, output_dir)
    
    # Generate architecture docs
    if "architecture" in sections:
        print("\n📐 Analyzing architectural patterns...")
        patterns = analyzer.identify_architecture_patterns()
        
        for pattern in patterns:
            safe_name = pattern.name.lower().replace(" ", "_").replace("-", "_")
            output_file = output_dir / "architecture" / f"{safe_name}.md"
            
            if output_file.exists() and not args.force:
                print(f"  ⊘ Skipping {output_file.name} (exists)")
            else:
                doc_content = generator.generate_architecture_doc(pattern)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(doc_content)
                print(f"  ✓ Generated {output_file.name}")
    
    # Generate feature docs
    if "features" in sections:
        print("\n✨ Analyzing user-facing features...")
        features = analyzer.identify_features()
        
        for feature in features:
            safe_name = feature.name.lower().replace(" ", "_").replace("-", "_")
            output_file = output_dir / "features" / f"{safe_name}.md"
            
            if output_file.exists() and not args.force:
                print(f"  ⊘ Skipping {output_file.name} (exists)")
            else:
                doc_content = generator.generate_feature_doc(feature)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(doc_content)
                print(f"  ✓ Generated {output_file.name}")
    
    # Generate UI component docs
    if "ui_components" in sections:
        print("\n🎨 Analyzing UI components...")
        components = analyzer.find_ui_components()
        
        for component in components:
            safe_name = component.name.lower().replace(" ", "_")
            output_file = output_dir / "ui_components" / f"{safe_name}.md"
            
            if output_file.exists() and not args.force:
                print(f"  ⊘ Skipping {output_file.name} (exists)")
            else:
                doc_content = generator.generate_ui_component_doc(component)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(doc_content)
                print(f"  ✓ Generated {output_file.name}")
    
    # API docs (use original script)
    if "api" in sections:
        print("\n⚙️  For API docs, also run: scripts/generate_pillar_docs.py")
    
    print(f"\n✅ Comprehensive documentation generation complete!")
    print(f"\nGenerated files in:")
    if "architecture" in sections:
        arch_count = len(list((output_dir / "architecture").glob("*.md")))
        print(f"  • architecture/ - {arch_count} docs")
    if "features" in sections:
        feat_count = len(list((output_dir / "features").glob("*.md")))
        print(f"  • features/ - {feat_count} docs")
    if "ui_components" in sections:
        ui_count = len(list((output_dir / "ui_components").glob("*.md")))
        print(f"  • ui_components/ - {ui_count} docs")
    
    print(f"\nNext steps:")
    print(f"1. Review generated files in {output_dir}")
    print(f"2. Search for '<!-- AI_ENHANCE:' markers")
    print(f"3. Use AI assistant to fill in detailed sections")
    print(f"4. Add Mermaid diagrams where indicated")
    print(f"5. Add code examples and ASCII UI mockups")


if __name__ == "__main__":
    main()
