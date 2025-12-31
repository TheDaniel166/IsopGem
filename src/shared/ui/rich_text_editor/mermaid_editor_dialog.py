"""
Mermaid Editor Dialog.
A dedicated dialog for creating and editing Mermaid diagrams with live preview.
The Ultimate Mermaid Editor - Phases 1-4: Core Excellence + Intelligent Editing + Advanced Features
"""
import os
import json
import qtawesome as qta
from PyQt6.QtCore import Qt, QTimer, QUrl, QByteArray, QSettings, QPropertyAnimation, QEasingCurve, QObject, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QImage, QClipboard, QGuiApplication, QShortcut, QKeySequence, QCursor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QPlainTextEdit,
    QLabel, QComboBox, QPushButton, QWidget, QFrame, QGraphicsDropShadowEffect,
    QFileDialog, QToolButton, QButtonGroup, QMessageBox, QLineEdit, QMenu,
    QListWidget, QListWidgetItem, QGraphicsOpacityEffect, QApplication,
    QColorDialog, QInputDialog
)
from shared.ui.theme import COLORS
from .code_editor_widget import CodeEditorWidget
from .mermaid_highlighter import MermaidSyntaxHighlighter
from .mermaid_linter import MermaidLinter, LintSeverity
from .er_generator import ERDiagramGenerator
from .webview_mermaid_renderer import WebViewMermaidRenderer



# Mermaid themes
MERMAID_THEMES = {
    "Default": "default",
    "Dark": "dark", 
    "Forest": "forest",
    "Neutral": "neutral",
    "Base": "base",
}

# Diagram templates
MERMAID_TEMPLATES = {
    "Flowchart (TD)": "graph TD\n    A[Start] --> B{Decision}\n    B -->|Yes| C[Action 1]\n    B -->|No| D[Action 2]\n    C --> E[End]\n    D --> E",
    "Flowchart (LR)": "graph LR\n    A[Start] --> B{Decision}\n    B -->|Yes| C[Action 1]\n    B -->|No| D[Action 2]",
    "Sequence Diagram": "sequenceDiagram\n    participant A as Alice\n    participant B as Bob\n    A->>B: Hello Bob!\n    B->>A: Hi Alice!",
    "ER Diagram": "erDiagram\n    CUSTOMER ||--o{ ORDER : places\n    ORDER ||--|{ LINE-ITEM : contains\n    PRODUCT ||--o{ LINE-ITEM : includes",
    "Class Diagram": "classDiagram\n    class Animal {\n        +String name\n        +makeSound()\n    }\n    class Dog {\n        +bark()\n    }\n    Animal <|-- Dog",
    "State Diagram": "stateDiagram-v2\n    [*] --> Idle\n    Idle --> Processing : start\n    Processing --> Done : complete\n    Done --> [*]",
    "Pie Chart": "pie title Distribution\n    \"Slice A\" : 40\n    \"Slice B\" : 35\n    \"Slice C\" : 25",
    "Gantt Chart": "gantt\n    title Project Timeline\n    dateFormat YYYY-MM-DD\n    section Phase 1\n    Task 1 :a1, 2024-01-01, 30d\n    Task 2 :after a1, 20d",
    "Mindmap": "mindmap\n    root((Central Idea))\n        Topic A\n            Subtopic 1\n            Subtopic 2\n        Topic B\n            Subtopic 3",
    "Git Graph": "gitGraph\n    commit\n    branch develop\n    commit\n    checkout main\n    merge develop\n    commit",
}

# Code snippets for quick insertion
MERMAID_SNIPPETS = {
    "Subgraph": "    subgraph Title\n        A --> B\n    end",
    "Styled Node": "    A[Label]:::className\n    classDef className fill:#f9f,stroke:#333",
    "Link with Text": "    A -->|text| B",
    "Note (Sequence)": "    Note over A,B: This is a note",
    "Loop (Sequence)": "    loop Every minute\n        A->>B: Request\n    end",
    "Alt Block (Sequence)": "    alt Condition\n        A->>B: Yes\n    else Other\n        A->>B: No\n    end",
    "Click Action": "    click A callback \"Tooltip\"",
    "Direction Change": "    direction LR",
    "Section (Gantt)": "    section Section Name\n    Task :a1, 2024-01-01, 30d",
    "Entity (ER)": "    ENTITY {\n        string id PK\n        string name\n    }",
}

# Pro-quality diagram gallery
MERMAID_GALLERY = {
    "🏗️ Software Architecture": """graph TB
    subgraph Client
        UI[Web UI]
        Mobile[Mobile App]
    end
    subgraph Backend
        API[API Gateway]
        Auth[Auth Service]
        Core[Core Service]
        DB[(Database)]
    end
    subgraph External
        Email[Email Provider]
        Payment[Payment Gateway]
    end
    UI --> API
    Mobile --> API
    API --> Auth
    API --> Core
    Core --> DB
    Core --> Email
    Core --> Payment
    classDef client fill:#dbeafe,stroke:#3b82f6
    classDef backend fill:#dcfce7,stroke:#22c55e
    classDef external fill:#fef3c7,stroke:#f59e0b
    class UI,Mobile client
    class API,Auth,Core,DB backend
    class Email,Payment external""",
    
    "🔄 CI/CD Pipeline": """graph LR
    A[📝 Code Push] --> B[🔍 Lint & Test]
    B --> C{✅ Pass?}
    C -->|Yes| D[📦 Build]
    C -->|No| E[❌ Notify Dev]
    D --> F[🧪 Integration]
    F --> G{✅ Pass?}
    G -->|Yes| H[🚀 Deploy Staging]
    G -->|No| E
    H --> I[🧑‍💻 QA Review]
    I --> J{✅ Approved?}
    J -->|Yes| K[🎉 Deploy Prod]
    J -->|No| E
    style A fill:#e0e7ff
    style K fill:#dcfce7""",
    
    "👤 User Authentication Flow": """sequenceDiagram
    actor User
    participant Client
    participant Auth as Auth Server
    participant DB as Database
    
    User->>Client: Enter credentials
    Client->>Auth: POST /login
    Auth->>DB: Verify user
    DB-->>Auth: User found
    Auth->>Auth: Generate JWT
    Auth-->>Client: 200 + Token
    Client->>Client: Store token
    Client-->>User: Redirect to dashboard
    
    Note over User,DB: Token expires in 24h""",
    
    "📊 E-Commerce Database": """erDiagram
    CUSTOMER ||--o{ ORDER : places
    CUSTOMER {
        int id PK
        string email UK
        string name
        datetime created_at
    }
    ORDER ||--|{ ORDER_ITEM : contains
    ORDER {
        int id PK
        int customer_id FK
        decimal total
        string status
        datetime ordered_at
    }
    ORDER_ITEM }|--|| PRODUCT : includes
    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal price
    }
    PRODUCT {
        int id PK
        string sku UK
        string name
        decimal price
        int stock
    }""",
    
    "📈 Project Timeline": """gantt
    title IsopGem Development Roadmap
    dateFormat YYYY-MM-DD
    
    section Foundation
    Core Architecture    :done, a1, 2024-01-01, 30d
    Database Design      :done, a2, after a1, 14d
    
    section Features
    Gematria Engine      :active, b1, 2024-02-15, 21d
    Document Manager     :b2, after b1, 28d
    Astrology Module     :b3, after b2, 35d
    
    section Polish
    UI Refinement        :c1, after b3, 14d
    Testing & QA         :c2, after c1, 21d
    Launch               :milestone, m1, after c2, 0d""",
    
    "🧠 Decision Tree": """graph TD
    A{Need a diagram?}
    A -->|Yes| B{What type?}
    A -->|No| C[Use text]
    B -->|Flow| D[Flowchart]
    B -->|Sequence| E[Sequence Diagram]
    B -->|Data| F{Structured?}
    B -->|Time| G[Gantt/Timeline]
    F -->|Yes| H[ER Diagram]
    F -->|No| I[Pie/Mindmap]
    
    style A fill:#fef3c7
    style D fill:#dbeafe
    style E fill:#dcfce7
    style H fill:#fce7f3
    style G fill:#e0e7ff""",
}


class MermaidEditorDialog(QDialog):
    """
    The Ultimate Mermaid Editor Dialog.
    Features: Live preview, themes, zoom controls, export options.
    """
    
    def __init__(self, parent=None, initial_code: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Mermaid Diagram Editor")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        self._current_theme = "default"
        self._zoom_level = 100
        self._last_rendered_image: QImage | None = None
        
        # Debounce timer for live preview
        self._render_timer = QTimer(self)
        self._render_timer.setSingleShot(True)
        self._render_timer.setInterval(600)  # 600ms debounce
        self._render_timer.timeout.connect(self._render_preview)
        
        self._setup_ui()
        self._apply_styles()
        

        
        # Set initial code
        if initial_code:
            self.set_code(initial_code)

    def set_code(self, code: str):
        """Set the code in the editor and render."""
        self.code_editor.setPlainText(code)
        self._render_preview()
        
    def reject(self):
        """Hide instead of close when Cancel is clicked."""
        self.hide()
        
    def closeEvent(self, event):
        """Hide instead of close when X is clicked."""
        self.hide()
        event.ignore() 
        # Crucial: ignore the close event so Qt doesn't destroy the widget
        # The dialog remains alive but hidden, preserving the WebEngine process.
    
    def _setup_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # === TOP TOOLBAR ===
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)
        
        # Template dropdown
        template_label = QLabel("Template:")
        self.template_combo = QComboBox()
        self.template_combo.addItem("-- Select --")
        self.template_combo.addItems(MERMAID_TEMPLATES.keys())
        self.template_combo.currentTextChanged.connect(self._on_template_selected)
        self.template_combo.setMinimumWidth(150)
        
        # Theme dropdown
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(MERMAID_THEMES.keys())
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        self.theme_combo.setMinimumWidth(100)
        
        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet(f"color: {COLORS['border']};")
        
        # Zoom controls
        zoom_label = QLabel("Zoom:")
        self.zoom_out_btn = QPushButton(qta.icon("fa5s.search-minus", color=COLORS["stone"]), "")
        self.zoom_out_btn.setFixedSize(32, 32)
        self.zoom_out_btn.clicked.connect(self._zoom_out)
        
        self.zoom_level_label = QLabel("100%")
        self.zoom_level_label.setMinimumWidth(50)
        self.zoom_level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.zoom_in_btn = QPushButton(qta.icon("fa5s.search-plus", color=COLORS["stone"]), "")
        self.zoom_in_btn.setFixedSize(32, 32)
        self.zoom_in_btn.clicked.connect(self._zoom_in)
        
        self.zoom_fit_btn = QPushButton(qta.icon("fa5s.expand", color=COLORS["stone"]), "")
        self.zoom_fit_btn.setFixedSize(32, 32)
        self.zoom_fit_btn.setToolTip("Fit to view")
        self.zoom_fit_btn.clicked.connect(self._zoom_fit)
        
        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.VLine)
        sep2.setStyleSheet(f"color: {COLORS['border']};")
        
        # Export buttons
        self.copy_btn = QPushButton(qta.icon("fa5s.clipboard", color=COLORS["scribe"]), "")
        self.copy_btn.setFixedSize(32, 32)
        self.copy_btn.setToolTip("Copy to clipboard")
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        
        self.save_png_btn = QPushButton(qta.icon("fa5s.image", color=COLORS["seeker"]), "")
        self.save_png_btn.setFixedSize(32, 32)
        self.save_png_btn.setToolTip("Save as PNG")
        self.save_png_btn.clicked.connect(self._save_as_png)
        
        self.save_svg_btn = QPushButton(qta.icon("fa5s.vector-square", color=COLORS["magus"]), "")
        self.save_svg_btn.setFixedSize(32, 32)
        self.save_svg_btn.setToolTip("Save as SVG")
        self.save_svg_btn.clicked.connect(self._save_as_svg)
        
        # Refresh button
        self.render_btn = QPushButton(qta.icon("fa5s.sync-alt", color=COLORS["accent"]), "")
        self.render_btn.setFixedSize(32, 32)
        self.render_btn.setToolTip("Refresh (Ctrl+Enter)")
        self.render_btn.clicked.connect(self._render_preview)
        
        # Snippets button with dropdown menu
        self.snippet_btn = QPushButton(qta.icon("fa5s.code", color=COLORS["stone"]), "")
        self.snippet_btn.setFixedSize(32, 32)
        self.snippet_btn.setToolTip("Snippets")
        self._setup_snippet_menu()
        
        # Gallery button with dropdown menu
        self.gallery_btn = QPushButton(qta.icon("fa5s.images", color=COLORS["magus"]), "")
        self.gallery_btn.setFixedSize(32, 32)
        self.gallery_btn.setToolTip("Gallery")
        self._setup_gallery_menu()
        
        # ER Generator button
        self.er_gen_btn = QPushButton(qta.icon("fa5s.database", color=COLORS["seeker"]), "")
        self.er_gen_btn.setFixedSize(32, 32)
        self.er_gen_btn.setToolTip("ER Generator")
        self.er_gen_btn.clicked.connect(self._generate_er_diagram)
        
        # Assemble toolbar
        toolbar.addWidget(template_label)
        toolbar.addWidget(self.template_combo)
        toolbar.addWidget(theme_label)
        toolbar.addWidget(self.theme_combo)
        toolbar.addWidget(sep1)
        toolbar.addWidget(self.snippet_btn)
        toolbar.addWidget(self.gallery_btn)
        toolbar.addWidget(self.er_gen_btn)
        toolbar.addWidget(sep2)
        toolbar.addWidget(zoom_label)
        toolbar.addWidget(self.zoom_out_btn)
        toolbar.addWidget(self.zoom_level_label)
        toolbar.addWidget(self.zoom_in_btn)
        toolbar.addWidget(self.zoom_fit_btn)
        
        # Separator
        sep3 = QFrame()
        sep3.setFrameShape(QFrame.Shape.VLine)
        sep3.setStyleSheet(f"color: {COLORS['border']};")
        
        toolbar.addWidget(sep3)
        toolbar.addWidget(self.copy_btn)
        toolbar.addWidget(self.save_png_btn)
        toolbar.addWidget(self.save_svg_btn)
        
        # Separator
        sep4 = QFrame()
        sep4.setFrameShape(QFrame.Shape.VLine)
        sep4.setStyleSheet(f"color: {COLORS['border']};")
        
        # Recent diagrams button
        self.recent_btn = QPushButton(qta.icon("fa5s.history", color=COLORS["stone"]), "")
        self.recent_btn.setFixedSize(32, 32)
        self.recent_btn.setToolTip("Recent diagrams")
        self._setup_recent_menu()
        
        # Maximize button
        self.maximize_btn = QPushButton(qta.icon("fa5s.expand-arrows-alt", color=COLORS["stone"]), "")
        self.maximize_btn.setFixedSize(32, 32)
        self.maximize_btn.setToolTip("Toggle maximized window")
        self.maximize_btn.clicked.connect(self._toggle_maximize)
        
        toolbar.addWidget(sep4)
        toolbar.addWidget(self.recent_btn)
        toolbar.addWidget(self.maximize_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.render_btn)
        
        layout.addLayout(toolbar)
        
        # === FIND/REPLACE BAR ===
        self.find_bar = QFrame()
        self.find_bar.setObjectName("findBar")
        find_layout = QHBoxLayout(self.find_bar)
        find_layout.setContentsMargins(8, 4, 8, 4)
        find_layout.setSpacing(8)
        
        find_layout.addWidget(QLabel("Find:"))
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Search...")
        self.find_input.returnPressed.connect(self._find_next)
        find_layout.addWidget(self.find_input)
        
        self.find_next_btn = QPushButton("Next")
        self.find_next_btn.clicked.connect(self._find_next)
        find_layout.addWidget(self.find_next_btn)
        
        self.find_prev_btn = QPushButton("Prev")
        self.find_prev_btn.clicked.connect(self._find_prev)
        find_layout.addWidget(self.find_prev_btn)
        
        find_layout.addWidget(QLabel("Replace:"))
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Replace with...")
        find_layout.addWidget(self.replace_input)
        
        self.replace_btn = QPushButton("Replace")
        self.replace_btn.clicked.connect(self._replace_current)
        find_layout.addWidget(self.replace_btn)
        
        self.replace_all_btn = QPushButton("All")
        self.replace_all_btn.clicked.connect(self._replace_all)
        find_layout.addWidget(self.replace_all_btn)
        
        close_find_btn = QPushButton(qta.icon("fa5s.times", color=COLORS["stone"]), "")
        close_find_btn.setFixedSize(24, 24)
        close_find_btn.clicked.connect(lambda: self.find_bar.hide())
        find_layout.addWidget(close_find_btn)
        
        self.find_bar.hide()  # Hidden by default, shown with Ctrl+F
        layout.addWidget(self.find_bar)
        
        # === MAIN SPLIT PANE ===
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Code Editor
        editor_frame = QFrame()
        editor_frame.setObjectName("editorFrame")
        editor_layout = QVBoxLayout(editor_frame)
        editor_layout.setContentsMargins(8, 8, 8, 8)
        
        editor_header = QLabel("📝 Code")
        editor_header.setObjectName("paneHeader")
        
        # Use custom CodeEditorWidget with line numbers
        self.code_editor = CodeEditorWidget()
        self.code_editor.setPlaceholderText("Enter Mermaid diagram code here...\n\nTry selecting a template from the dropdown above.")
        self.code_editor.textChanged.connect(self._on_text_changed)
        
        # Attach syntax highlighter
        self._highlighter = MermaidSyntaxHighlighter(self.code_editor.document())
        
        editor_layout.addWidget(editor_header)
        editor_layout.addWidget(self.code_editor)
        
        # Right: Preview Pane (Static Image)
        preview_frame = QFrame()
        preview_frame.setObjectName("previewFrame")
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(8, 8, 8, 8)
        
        preview_header = QLabel("🖼️ Preview")
        preview_header.setObjectName("paneHeader")
        
        # Static Preview Label
        self.preview_view = QLabel("Preview will appear here...")
        self.preview_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_view.setStyleSheet("background-color: white; border-radius: 4px;")
        
        # Scroll area for the preview
        from PyQt6.QtWidgets import QScrollArea
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidget(self.preview_view)
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        preview_layout.addWidget(preview_header)
        preview_layout.addWidget(self.preview_scroll, 1)
        
        splitter.addWidget(editor_frame)
        splitter.addWidget(preview_frame)
        splitter.setSizes([450, 550])
        
        layout.addWidget(splitter, 1)
        
        # === ERROR DISPLAY ===
        self.error_label = QLabel()
        self.error_label.setObjectName("errorLabel")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        layout.addWidget(self.error_label)
        
        # === LINT ISSUES PANEL ===
        self.issues_frame = QFrame()
        self.issues_frame.setObjectName("issuesFrame")
        issues_layout = QVBoxLayout(self.issues_frame)
        issues_layout.setContentsMargins(8, 4, 8, 4)
        issues_layout.setSpacing(4)
        
        issues_header = QLabel("🔍 Syntax Issues")
        issues_header.setStyleSheet(f"font-weight: bold; color: {COLORS['text_secondary']};")
        issues_layout.addWidget(issues_header)
        
        self.issues_list = QListWidget()
        self.issues_list.setMaximumHeight(100)
        self.issues_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['background']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                font-size: 10pt;
            }}
            QListWidget::item {{
                padding: 4px;
            }}
        """)
        self.issues_list.itemDoubleClicked.connect(self._on_issue_clicked)
        issues_layout.addWidget(self.issues_list)
        
        self.issues_frame.hide()  # Hidden until issues are found
        layout.addWidget(self.issues_frame)
        
        # === BOTTOM BUTTONS ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.ok_btn = QPushButton(qta.icon("fa5s.check", color="white"), "Insert Diagram")
        self.ok_btn.setObjectName("primaryButton")
        self.ok_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
    
    def _apply_styles(self):
        """Apply the Visual Liturgy (v2.2) styling."""
        
        # Add levitation shadow to the dialog
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(Qt.GlobalColor.black)
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet(f"""
            /* === THE SUBSTRATE === */
            QDialog {{
                background-color: {COLORS["surface"]};
                border-radius: 12px;
            }}
            
            /* === THE TABLETS (Panels) === */
            QLabel#paneHeader {{
                font-weight: bold;
                font-size: 12pt;
                padding: 8px 12px;
                color: {COLORS["text_primary"]};
                background-color: {COLORS["surface"]};
                border-radius: 8px 8px 0 0;
            }}
            QFrame#editorFrame, QFrame#previewFrame {{
                background-color: {COLORS["marble"]};
                border-radius: 12px;
                border: 1px solid {COLORS["ash"]};
            }}
            QFrame#issuesFrame {{
                background-color: {COLORS["surface"]};
                border-radius: 8px;
                border: 1px solid {COLORS["ash"]};
            }}
            QFrame#findBar {{
                background-color: {COLORS["surface"]};
                border-radius: 8px;
                border: 1px solid {COLORS["border"]};
            }}
            
            /* === THE VESSELS (Inputs) === */
            QPlainTextEdit, QLineEdit {{
                background-color: {COLORS["light"]};
                color: {COLORS["void"]};
                border: 1px solid {COLORS["ash"]};
                border-radius: 6px;
                padding: 8px;
                font-family: 'Fira Code', 'Consolas', monospace;
                min-height: 36px;
            }}
            QPlainTextEdit:focus, QLineEdit:focus {{
                border: 2px solid {COLORS["focus"]};
            }}
            QComboBox {{
                padding: 8px 12px;
                border-radius: 6px;
                background-color: {COLORS["light"]};
                border: 1px solid {COLORS["ash"]};
                min-height: 36px;
            }}
            QComboBox:focus {{
                border: 2px solid {COLORS["focus"]};
            }}
            
            /* === THE CATALYSTS (Buttons) === */
            /* Navigator archetype (default) */
            QPushButton {{
                padding: 8px 14px;
                border-radius: 6px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS["navigator"]}, stop:1 #4b5563);
                color: white;
                border: 1px solid {COLORS["ash"]};
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS["navigator_hover"]}, stop:1 #6b7280);
            }}
            QPushButton:pressed {{
                background: {COLORS["stone"]};
            }}
            
            /* Magus archetype (Primary Action) */
            QPushButton#primaryButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS["magus"]}, stop:1 #5b21b6);
                color: white;
                padding: 10px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
                border: none;
            }}
            QPushButton#primaryButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS["magus_hover"]}, stop:1 #6d28d9);
            }}
            
            /* Destroyer archetype (Delete/Close) */
            QPushButton#destroyerButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS["destroyer"]}, stop:1 #b91c1c);
                color: white;
            }}
            
            /* === ERROR/STATUS DISPLAY === */
            QLabel#errorLabel {{
                color: {COLORS["error"]};
                padding: 10px 14px;
                background-color: rgba(239, 68, 68, 0.15);
                border-radius: 8px;
                border-left: 4px solid {COLORS["error"]};
            }}
            
            /* === THE NAVIGATION (Lists) === */
            QListWidget {{
                background-color: {COLORS["light"]};
                border: 1px solid {COLORS["ash"]};
                border-radius: 6px;
            }}
            QListWidget::item {{
                padding: 6px 8px;
                border-radius: 4px;
            }}
            QListWidget::item:hover {{
                background-color: {COLORS["cloud"]};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS["focus"]};
                color: white;
            }}
            
            /* === HIDE DROPDOWN ARROWS === */
            QPushButton::menu-indicator {{
                image: none;
                width: 0;
                height: 0;
            }}
            
            /* === THE HORIZON (Scrollbars) === */
            QScrollBar:vertical {{
                width: 12px;
                background: transparent;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS["stone"]};
                border-radius: 6px;
                min-height: 40px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)
    
    # === CALLBACKS ===
    
    def _on_template_selected(self, template_name: str):
        """Insert a template into the code editor."""
        if template_name in MERMAID_TEMPLATES:
            self.code_editor.setPlainText(MERMAID_TEMPLATES[template_name])
            self._render_preview()
    
    def _on_theme_changed(self, theme_name: str):
        """Change the Mermaid render theme."""
        if theme_name in MERMAID_THEMES:
            self._current_theme = MERMAID_THEMES[theme_name]
            self._render_preview()
    
    def _on_text_changed(self):
        """Start debounce timer for live preview."""
        self._render_timer.start()
    
    # === ZOOM ===
    
    def _zoom_in(self):
        self._zoom_level = min(200, self._zoom_level + 25)
        self._update_zoom()
    
    def _zoom_out(self):
        self._zoom_level = max(25, self._zoom_level - 25)
        self._update_zoom()
    
    def _zoom_fit(self):
        self._zoom_level = 100
        self._update_zoom()
    
    def _update_zoom(self):
        self.zoom_level_label.setText(f"{self._zoom_level}%")
        self._apply_zoom_to_preview()
    
    def _apply_zoom_to_preview(self):
        """Apply zoom to the preview pane."""
        if not self._last_rendered_image:
            return
            
        pixmap = QPixmap.fromImage(self._last_rendered_image)
        if pixmap.isNull():
            return
            
        factor = self._zoom_level / 100.0
        new_size = pixmap.size() * factor
        
        scaled = pixmap.scaled(
            new_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.preview_view.setPixmap(scaled)
        self.zoom_level_label.setText(f"{self._zoom_level}%")
    
    # === RENDERING ===
    
    def _render_preview(self):
        """Render the current code via WebEngine."""
        code = self.code_editor.toPlainText().strip()
        
        # Run linter
        self._run_lint(code)
        
        if not code:
            self.preview_view.clear()
            self.preview_view.setText("Preview will appear here...")
            self.error_label.hide()
            return
        
        # Render using headless renderer
        try:
             # Use a scale factor for high-resolution render, then scale down for display
             image = WebViewMermaidRenderer.render_mermaid(code, theme=self._current_theme, scale=2.0)
             if image:
                 self._last_rendered_image = image
                 self._apply_zoom_to_preview()
                 self.error_label.hide()
                 self._animate_preview_fade_in()
             else:
                 self.error_label.setText("Failed to render diagram.")
                 self.error_label.show()
        except Exception as e:
            self.error_label.setText(f"Render Error: {str(e)}")
            self.error_label.show()
    
    # === LINTING ===
    
    def _run_lint(self, code: str):
        """Run the linter and update the issues panel."""
        self.issues_list.clear()
        
        if not code:
            self.issues_frame.hide()
            return
        
        issues = MermaidLinter.lint(code)
        
        if not issues:
            self.issues_frame.hide()
            return
        
        # Populate issues list
        for issue in issues:
            # Create icon based on severity
            if issue.severity == LintSeverity.ERROR:
                icon = "❌"
                color = COLORS["error"]
            elif issue.severity == LintSeverity.WARNING:
                icon = "⚠️"
                color = COLORS["warning"]
            else:
                icon = "ℹ️"
                color = COLORS["info"]
            
            text = f"{icon} Line {issue.line}: {issue.message}"
            if issue.suggestion:
                text += f"\n    💡 {issue.suggestion}"
            
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, issue.line)
            self.issues_list.addItem(item)
        
        self.issues_frame.show()
    
    def _on_issue_clicked(self, item: QListWidgetItem):
        """Jump to the line of the clicked issue."""
        line = item.data(Qt.ItemDataRole.UserRole)
        if line:
            cursor = self.code_editor.textCursor()
            block = self.code_editor.document().findBlockByLineNumber(line - 1)
            cursor.setPosition(block.position())
            self.code_editor.setTextCursor(cursor)
            self.code_editor.setFocus()
    
    # === EXPORT ===
    
    def _copy_to_clipboard(self):
        """Copy the rendered diagram to clipboard."""
        if self._last_rendered_image:
            clipboard = QGuiApplication.clipboard()
            clipboard.setImage(self._last_rendered_image)
            QMessageBox.information(self, "Inscribed", "The diagram has been etched to the sacred clipboard.")
        else:
            QMessageBox.warning(self, "The Void", "Manifest a diagram before attempting to preserve it.")
    
    def _save_as_png(self):
        """Save the diagram as high-resolution PNG."""
        code = self.get_code()
        if not code:
            QMessageBox.warning(self, "The Void", "Manifest a diagram before attempting to preserve it.")
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Save as PNG", "diagram.png", "PNG Images (*.png)"
        )
        if path:
            # Perform high-quality render
            # self.preview_label.setText("🔮 Weaving high-resolution spell...") 
            QApplication.processEvents() # Update UI
            
            try:
                # 3.0x scale for Retina-like quality
                hq_image = WebViewMermaidRenderer.render_mermaid(code, theme=self._current_theme, scale=3.0)
                
                if hq_image:
                    hq_image.save(path, "PNG")
                    QMessageBox.information(self, "Inscribed", f"High-resolution diagram saved to:\n{path}")
                else:
                    QMessageBox.warning(self, "Failed", "The symbols crumbled during formation.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to render PNG:\n{str(e)}")
            finally:
                # Restore preview text if needed, or just let it stay until next render
                self._render_preview()
    
    def _save_as_svg(self):
        """Save the diagram as scalable SVG."""
        code = self.get_code()
        if not code:
            QMessageBox.warning(self, "The Void", "Manifest a diagram before attempting to preserve it.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save as SVG", "diagram.svg", "SVG Files (*.svg)"
        )
        if not path:
            return

        # Render SVG
        try:
            svg_content = WebViewMermaidRenderer.render_mermaid_svg(code, self._current_theme)
            
            if svg_content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(svg_content)
                QMessageBox.information(self, "Inscribed", f"The vector sigil has been etched to:\n{path}")
            else:
                QMessageBox.warning(self, "Failed", "The symbols crumbled during formation. Check your syntax.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save SVG:\n{str(e)}")
    
    # === API ===
    
    def get_code(self) -> str:
        """Return the current Mermaid code."""
        return self.code_editor.toPlainText().strip()
    
    # === SNIPPETS ===
    
    def _setup_snippet_menu(self):
        """Create the snippets dropdown menu."""
        menu = QMenu(self)
        for name, code in MERMAID_SNIPPETS.items():
            action = menu.addAction(name)
            action.triggered.connect(lambda checked, c=code: self._insert_snippet(c))
        self.snippet_btn.setMenu(menu)
    
    def _insert_snippet(self, code: str):
        """Insert a snippet at the cursor position."""
        cursor = self.code_editor.textCursor()
        cursor.insertText(code)
        self.code_editor.setFocus()
    
    # === GALLERY ===
    
    def _setup_gallery_menu(self):
        """Create the gallery dropdown menu."""
        menu = QMenu(self)
        for name, code in MERMAID_GALLERY.items():
            action = menu.addAction(name)
            action.triggered.connect(lambda checked, c=code: self._load_gallery_example(c))
        self.gallery_btn.setMenu(menu)
    
    def _load_gallery_example(self, code: str):
        """Load a gallery example into the editor (replaces current content)."""
        self.code_editor.setPlainText(code)
        self._render_preview()
        self.code_editor.setFocus()
    
    # === ER GENERATOR ===
    
    def _generate_er_diagram(self):
        """
        Generate an ER diagram from SQLAlchemy models.
        For now, loads an example since we don't have direct model access.
        In a real implementation, this would introspect the app's models.
        """
        # Try to find SQLAlchemy models in the app
        models = self._discover_sqlalchemy_models()
        
        if models:
            code = ERDiagramGenerator.from_sqlalchemy_models(models)
        else:
            # Use example
            code = ERDiagramGenerator.generate_example()
            QMessageBox.information(
                self, "ER Generator",
                "No SQLAlchemy models detected.\n\n"
                "Loading an example ER diagram instead.\n"
                "To generate from your models, import them and pass to ERDiagramGenerator."
            )
        
        self.code_editor.setPlainText(code)
        self._render_preview()
        self.code_editor.setFocus()
    
    def _discover_sqlalchemy_models(self) -> list[type]:
        """
        Attempt to discover SQLAlchemy models from the application.
        Returns an empty list if none found.
        """
        models = []
        
        try:
            # Try to import from common IsopGem locations
            from pillars.astrology.models import Base as AstrologyBase
            if hasattr(AstrologyBase, 'registry'):
                for mapper in AstrologyBase.registry.mappers:
                    models.append(mapper.class_)
        except ImportError:
            pass
        
        try:
            from pillars.document_manager.models import Base as DocBase
            if hasattr(DocBase, 'registry'):
                for mapper in DocBase.registry.mappers:
                    models.append(mapper.class_)
        except ImportError:
            pass
        
        return models
    
    # === FIND/REPLACE ===
    
    def _find_next(self):
        """Find next occurrence of search text."""
        search_text = self.find_input.text()
        if not search_text:
            return
        
        # Search forward from cursor
        cursor = self.code_editor.textCursor()
        doc = self.code_editor.document()
        found_cursor = doc.find(search_text, cursor)
        
        if found_cursor.isNull():
            # Wrap around
            found_cursor = doc.find(search_text)
        
        if not found_cursor.isNull():
            self.code_editor.setTextCursor(found_cursor)
            self.code_editor.setFocus()
    
    def _find_prev(self):
        """Find previous occurrence of search text."""
        from PyQt6.QtGui import QTextDocument
        search_text = self.find_input.text()
        if not search_text:
            return
        
        cursor = self.code_editor.textCursor()
        doc = self.code_editor.document()
        found_cursor = doc.find(search_text, cursor, QTextDocument.FindFlag.FindBackward)
        
        if found_cursor.isNull():
            # Wrap around to end
            end_cursor = self.code_editor.textCursor()
            end_cursor.movePosition(end_cursor.MoveOperation.End)
            found_cursor = doc.find(search_text, end_cursor, QTextDocument.FindFlag.FindBackward)
        
        if not found_cursor.isNull():
            self.code_editor.setTextCursor(found_cursor)
            self.code_editor.setFocus()
    
    def _replace_current(self):
        """Replace current selection if it matches search text."""
        search_text = self.find_input.text()
        replace_text = self.replace_input.text()
        
        cursor = self.code_editor.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == search_text:
            cursor.insertText(replace_text)
            self._find_next()  # Move to next occurrence
    
    def _replace_all(self):
        """Replace all occurrences of search text."""
        search_text = self.find_input.text()
        replace_text = self.replace_input.text()
        
        if not search_text:
            return
        
        text = self.code_editor.toPlainText()
        count = text.count(search_text)
        new_text = text.replace(search_text, replace_text)
        self.code_editor.setPlainText(new_text)
        
        if count > 0:
            QMessageBox.information(self, "Replace All", f"Replaced {count} occurrence(s).")
    
    # === KEYBOARD SHORTCUTS ===
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        # Ctrl+Enter: Render preview
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Return:
            self._render_preview()
            return
        
        # Ctrl+S: Accept/Insert diagram
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_S:
            self.accept()
            return
        
        # Ctrl+F: Show find bar
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_F:
            self.find_bar.show()
            self.find_input.setFocus()
            return
        
        # Escape: Hide find bar or close dialog
        if event.key() == Qt.Key.Key_Escape:
            if self.find_bar.isVisible():
                self.find_bar.hide()
                self.code_editor.setFocus()
                return
        
        super().keyPressEvent(event)
    
    # === PHASE 5: POLISH ===
    
    def _toggle_maximize(self):
        """Toggle between normal and maximized window."""
        if self.isMaximized():
            self.showNormal()
            self.maximize_btn.setIcon(qta.icon("fa5s.expand-arrows-alt", color=COLORS["stone"]))
        else:
            self.showMaximized()
            self.maximize_btn.setIcon(qta.icon("fa5s.compress-arrows-alt", color=COLORS["accent"]))
    
    def _setup_recent_menu(self):
        """Create the recent diagrams dropdown menu."""
        menu = QMenu(self)
        recents = self._load_recent_diagrams()
        
        if not recents:
            action = menu.addAction("No recent diagrams")
            action.setEnabled(False)
        else:
            for i, (name, code) in enumerate(recents[:10]):  # Max 10 recent
                action = menu.addAction(f"{i+1}. {name}")
                action.triggered.connect(lambda checked, c=code: self._load_recent(c))
            
            menu.addSeparator()
            clear_action = menu.addAction("Clear Recent")
            clear_action.triggered.connect(self._clear_recent_diagrams)
        
        self.recent_btn.setMenu(menu)
    
    def _load_recent(self, code: str):
        """Load a recent diagram."""
        self.code_editor.setPlainText(code)
        self._render_preview()
        self.code_editor.setFocus()
    
    def _save_to_recent(self):
        """Save current diagram to recent list."""
        code = self.code_editor.toPlainText().strip()
        if not code:
            return
        
        # Generate a name from the first line
        first_line = code.split('\n')[0].strip()
        name = first_line[:30] + "..." if len(first_line) > 30 else first_line
        
        recents = self._load_recent_diagrams()
        
        # Remove if already exists
        recents = [(n, c) for n, c in recents if c != code]
        
        # Add to front
        recents.insert(0, (name, code))
        
        # Keep only last 20
        recents = recents[:20]
        
        # Save
        settings = QSettings("IsopGem", "MermaidEditor")
        settings.setValue("recent_diagrams", json.dumps(recents))
    
    def _load_recent_diagrams(self) -> list[tuple[str, str]]:
        """Load recent diagrams from settings."""
        settings = QSettings("IsopGem", "MermaidEditor")
        data = settings.value("recent_diagrams", "[]")
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return []
    



    def _clear_recent_diagrams(self):
        """Clear the recent diagrams list."""
        settings = QSettings("IsopGem", "MermaidEditor")
        settings.setValue("recent_diagrams", "[]")
        self._setup_recent_menu()
    
    def accept(self):
        """Override accept to save to recent before hiding."""
        self._save_to_recent()
        self.hide() # Hide instead of calling super().accept() which might close
        # We manually set result to Accepted so exec() returns True
        self.setResult(QDialog.DialogCode.Accepted)
    
    def _animate_preview_fade(self):
        """Animate a fade effect on the preview for smooth transitions."""
        if not hasattr(self, '_preview_opacity_effect'):
            self._preview_opacity_effect = QGraphicsOpacityEffect(self.preview_view)
            self.preview_view.setGraphicsEffect(self._preview_opacity_effect)
        
        # Fade out
        anim = QPropertyAnimation(self._preview_opacity_effect, b"opacity")
        anim.setDuration(150)
        anim.setStartValue(1.0)
        anim.setEndValue(0.5)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.start()
        
        # Store for later fade in
        self._fade_anim = anim
    
    def _animate_preview_fade_in(self):
        """Fade the preview back in after rendering."""
        if hasattr(self, '_preview_opacity_effect'):
            anim = QPropertyAnimation(self._preview_opacity_effect, b"opacity")
            anim.setDuration(200)
            anim.setStartValue(0.5)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
            anim.start()
            self._fade_anim = anim
    
    def get_image(self):
        """Return the last rendered image."""
        return self._last_rendered_image


