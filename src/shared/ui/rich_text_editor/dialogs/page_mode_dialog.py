"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: UI Component (GRANDFATHERED - should move to pillars/document_manager)
- USED BY: Internal shared/ modules only (1 references)
- CRITERION: Violation (Single-pillar UI component)

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""

"""Page Mode Dialog for advanced pagination control."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QCheckBox, QSpinBox, QDialogButtonBox, QLabel, QGroupBox
)
from PyQt6.QtCore import Qt


class PageModeDialog(QDialog):
    """

    Advanced settings dialog for CUSTOM page mode.
    
    Provides granular control over pagination options including
    guides, gap fill, enforcement, and visual tuning.
    """
    
    def __init__(self, parent=None, current_options=None):
        super().__init__(parent)
        self.setWindowTitle("Page View Options")
        self.setMinimumWidth(300)
        self.options = current_options
        self._setup_ui()
        if current_options:
            self._load_options(current_options)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Visual group
        visual_group = QGroupBox("Visual Settings")
        visual_layout = QFormLayout(visual_group)
        
        self.chk_guides = QCheckBox()
        self.chk_guides.setToolTip("Show dashed lines at page breaks")
        visual_layout.addRow("Show Page Guides:", self.chk_guides)
        
        self.chk_gap_fill = QCheckBox()
        self.chk_gap_fill.setToolTip("Show shaded gutter between pages")
        visual_layout.addRow("Show Gap Fill:", self.chk_gap_fill)

        self.chk_page_outline = QCheckBox()
        self.chk_page_outline.setToolTip("Show page border outline")
        visual_layout.addRow("Show Page Outline:", self.chk_page_outline)

        self.chk_margin_guides = QCheckBox()
        self.chk_margin_guides.setToolTip("Show margin guides inside pages")
        visual_layout.addRow("Show Margin Guides:", self.chk_margin_guides)
        
        self.spin_gap = QSpinBox()
        self.spin_gap.setRange(5, 100)
        self.spin_gap.setValue(20)
        self.spin_gap.setSuffix(" px")
        self.spin_gap.setToolTip("Gutter size between pages")
        visual_layout.addRow("Page Gap:", self.spin_gap)
        
        layout.addWidget(visual_group)
        
        # Behavior group
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QFormLayout(behavior_group)
        
        self.chk_enforce = QCheckBox()
        self.chk_enforce.setToolTip("Enforce blocks don't straddle page boundaries")
        behavior_layout.addRow("Enforce Pagination:", self.chk_enforce)
        
        self.chk_anchor = QCheckBox()
        self.chk_anchor.setChecked(True)
        self.chk_anchor.setToolTip("Preserve scroll position during layout changes")
        behavior_layout.addRow("Scroll Anchoring:", self.chk_anchor)
        
        self.chk_coupling = QCheckBox()
        self.chk_coupling.setToolTip("Sync guides and enforcement together")
        behavior_layout.addRow("Couple Guides/Enforce:", self.chk_coupling)
        
        layout.addWidget(behavior_group)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _load_options(self, opts):
        """Load values from PageModeOptions."""
        self.chk_guides.setChecked(opts.show_guides)
        self.chk_gap_fill.setChecked(opts.show_gap_fill)
        self.chk_page_outline.setChecked(opts.show_page_outline)
        self.chk_margin_guides.setChecked(opts.show_margin_guides)
        self.chk_enforce.setChecked(opts.enforce_pagination)
        self.chk_anchor.setChecked(opts.scroll_anchor)
        self.chk_coupling.setChecked(opts.couple_guides_and_enforcement)
        if opts.page_gap is not None:
            self.spin_gap.setValue(opts.page_gap)
    
    def get_options(self):
        """Return PageModeOptions from dialog values."""
        # Import here to avoid circular dependency
        from ..editor import PageModeOptions
        return PageModeOptions(
            show_guides=self.chk_guides.isChecked(),
            show_gap_fill=self.chk_gap_fill.isChecked(),
            show_page_outline=self.chk_page_outline.isChecked(),
            show_margin_guides=self.chk_margin_guides.isChecked(),
            enforce_pagination=self.chk_enforce.isChecked(),
            scroll_anchor=self.chk_anchor.isChecked(),
            couple_guides_and_enforcement=self.chk_coupling.isChecked(),
            page_gap=self.spin_gap.value()
        )
