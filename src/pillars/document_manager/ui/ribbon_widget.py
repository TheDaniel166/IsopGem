from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtGui import QAction, QIcon, QColor
from PyQt6.QtCore import Qt, QSize
from pyqtribbon import RibbonBar, RibbonCategoryStyle

class RibbonWidget(RibbonBar):
    """
    A unified 'Ribbon' style navigation widget using pyqtribbon.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(125) # Force a reasonable height for widget usage
        
        # Apply comprehensive Office-like styling with vibrant IsopGem colors
        # We use generic selectors (QTabBar, QToolButton) scoped to RibbonBar to ensure application.
        # UPDATED: Using distinct colors to ensure visibility.
        self.setStyleSheet("""
            /* Main Ribbon Bar Background (The Tab Strip Area) */
            RibbonBar {
                background-color: #dbeafe; /* Blue 100 - Clearly Blue */
                border: none;
                border-bottom: 2px solid #3b82f6; /* Blue 500 border */
            }
            
            /* Force background on the main styling container if exists */
            RibbonBar > QWidget {
                background-color: transparent;
            }

            /* The Tab Bar Area */
            RibbonBar QTabBar {
                background: transparent;
                margin-left: 5px;
            }

            /* Individual Tabs */
            RibbonBar QTabBar::tab {
                color: #334155; /* Slate 700 */
                border: none;
                background: transparent;
                padding: 6px 16px;
                margin-right: 4px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 10pt;
                font-weight: 600;
                min-width: 60px;
            }

            RibbonBar QTabBar::tab:selected {
                color: #2563eb; /* Primary Blue */
                background: #eff6ff; /* Match content area */
                border: 1px solid #93c5fd; /* Blue 300 */
                border-bottom: 1px solid #eff6ff; /* Blend with content */
                border-top: 3px solid #2563eb; /* Top Accent Line */
                font-weight: 700;
            }

            RibbonBar QTabBar::tab:hover:!selected {
                color: #1d4ed8;
                background: rgba(255, 255, 255, 0.5);
            }

            /* The Content Area for Tabs (Where buttons live) */
            RibbonStackedWidget {
                background-color: #eff6ff; /* Blue 50 - Clearly Tinted */
                border: 1px solid #93c5fd; /* Blue 300 */
                border-top: none; /* Connect with tab */
            }

            /* Buttons inside the ribbon - Scoped to RibbonBar */
            RibbonBar QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                color: #1e293b; /* Slate 800 */
            }

            RibbonBar QToolButton:hover {
                background-color: #bfdbfe; /* Blue 200 - Strongly visible hover */
                border: 1px solid #3b82f6; /* Blue 500 */
                color: #172554; /* Blue 950 */
            }

            RibbonBar QToolButton:pressed {
                background-color: #60a5fa; /* Blue 400 */
                color: white;
                border: 1px solid #2563eb;
            }
            
            /* Large button text alignment fix */
            RibbonBar QToolButton[popupMode="1"] {
                padding-right: 10px;
            }
        """)

    def add_ribbon_tab(self, title: str) -> 'RibbonTabWrapper':
        """Create and add a new category (tab) to the ribbon."""
        content = self.addCategory(title)
        return RibbonTabWrapper(content)

    def add_context_category(self, title: str, color=Qt.GlobalColor.blue) -> 'RibbonTabWrapper':
        """
        Add a context category (hidden by default).
        color can be QColor or Qt.GlobalColor
        """
        # pyqtribbon expects QColor for context categories
        if isinstance(color, Qt.GlobalColor):
            color = QColor(color)
            
        content = self.addContextCategory(title, color)
        return RibbonTabWrapper(content)

    def show_context_category(self, tab: 'RibbonTabWrapper'):
        """Show a context category (only if not already visible)."""
        if not getattr(tab, '_is_visible', False):
            self.showContextCategory(tab.category)
            tab._is_visible = True

    def hide_context_category(self, tab: 'RibbonTabWrapper'):
        """Hide a context category."""
        if getattr(tab, '_is_visible', False):
            self.hideContextCategory(tab.category)
            tab._is_visible = False

    def add_file_menu(self):
        """Add the file menu to the application button."""
        return self.addFileMenu()
        
    def add_quick_access_button(self, action: QAction):
        """Add an action to the Quick Access Toolbar."""
        self.quickAccessToolBar().addAction(action)


class RibbonTabWrapper:
    """Wrapper around pyqtribbon Category to match old RibbonTab API."""
    def __init__(self, category):
        self.category = category

    def add_group(self, title: str) -> 'RibbonGroupWrapper':
        """Add a labeled group (panel) of actions to this tab."""
        panel = self.category.addPanel(title)
        return RibbonGroupWrapper(panel)


class RibbonGroupWrapper:
    """Wrapper around pyqtribbon Panel to match old RibbonGroup API."""
    def __init__(self, panel):
        self.panel = panel
        
        # Hide the option button (dialog launcher arrow) by default as it is currently unused
        try:
            # Inspection showed 'panelOptionButton' attribute exists
            if hasattr(self.panel, 'panelOptionButton'):
                btn = self.panel.panelOptionButton
                # It might be a property or method
                if callable(btn):
                    btn = btn()
                
                if btn:
                    btn.setVisible(False)
        except Exception:
            pass

    def add_widget(self, widget: QWidget):
        """Add a custom widget to the group."""
        self.panel.addWidget(widget)
        
    def add_action(self, action: QAction, tool_button_style=Qt.ToolButtonStyle.ToolButtonTextUnderIcon):
        """
        Add an action as a button.
        """
        if tool_button_style == Qt.ToolButtonStyle.ToolButtonTextUnderIcon:
            text = action.text()
            icon = action.icon() if not action.icon().isNull() else None
            btn = self.panel.addLargeButton(text, icon)
            btn.setDefaultAction(action)
            return btn
        else:
            btn = self.panel.addSmallButton(action.text(), action.icon())
            btn.setDefaultAction(action)
            return btn
        
    def add_separator(self):
        """Add a separator."""
        self.panel.addSeparator()

    def add_gallery(self, min_width=200):
        """Add a gallery to the panel."""
        # Note: API might vary, docs say panel.addGallery(...)
        gallery = self.panel.addGallery()
        gallery.setMinimumWidth(min_width)
        return RibbonGalleryWrapper(gallery)


class RibbonGalleryWrapper:
    """Wrapper for RibbonGallery."""
    def __init__(self, gallery):
        self.gallery = gallery
    
    def add_item(self, text, icon, callback=None):
        """Add a button to the gallery."""
        result = self.gallery.addToggleButton(text, icon)
        
        # pyqtribbon might return (button, action) or just button depending on version/method
        btn = result
        if isinstance(result, tuple):
            btn = result[0]
            
        if callback:
             # Ensure btn has clicked signal
             if hasattr(btn, 'clicked'):
                 btn.clicked.connect(callback)
             elif hasattr(btn, 'triggered'):
                 btn.triggered.connect(callback)
        return btn
        
    def add_group(self, title):
        """Add a grouping (if supported) or just return self."""
        # pyqtribbon gallery simple usage is direct items
        return self

