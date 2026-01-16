"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: UI Component (GRANDFATHERED - should move to pillars/document_manager)
- USED BY: Internal shared/ modules only (1 references)
- CRITERION: Violation (Single-pillar UI component)

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""

"""
Editor constants and page settings for the Rich Text Editor.
Centralizes configuration that was previously hardcoded.
"""

from PyQt6.QtGui import QPageSize, QTextListFormat


class PageSettings:
    """
    Centralized page configuration for the document editor.
    Page dimensions are calculated based on page size and margins.
    """
    
    # DPI for screen rendering (standard screen DPI)
    SCREEN_DPI = 96
    
    # Page sizes with their dimensions in inches (width, height)
    PAGE_DIMENSIONS = {
        "letter": (8.5, 11.0),
        "legal": (8.5, 14.0),
        "a4": (8.27, 11.69),
        "a3": (11.69, 16.54),
        "a5": (5.83, 8.27),
        "tabloid": (11.0, 17.0),
    }
    
    # Default margins in inches (top, right, bottom, left)
    DEFAULT_MARGINS = (1.0, 1.0, 1.0, 1.0)
    
    def __init__(
        self,
        page_size: str = "letter",
        margins: tuple = None,
        custom_dimensions: tuple = None,
        screen_dpi: float | None = None,
        screen_dpi_x: float | None = None,
        screen_dpi_y: float | None = None,
    ):
        """
        Initialize page settings.
        
        Args:
            page_size: One of 'letter', 'legal', 'a4', 'a3', 'a5', 'tabloid'
            margins: Tuple of (top, right, bottom, left) in inches
            custom_dimensions: Optional (width_in, height_in) to override named sizes
        """
        self._custom_dimensions = custom_dimensions
        self._margins = margins or self.DEFAULT_MARGINS
        if screen_dpi is not None:
            self._screen_dpi_x = float(screen_dpi)
            self._screen_dpi_y = float(screen_dpi)
        else:
            self._screen_dpi_x = float(screen_dpi_x) if screen_dpi_x else float(self.SCREEN_DPI)
            self._screen_dpi_y = float(screen_dpi_y) if screen_dpi_y else float(self.SCREEN_DPI)
        if self._custom_dimensions:
            self._page_size = "custom"
        else:
            self._page_size = page_size.lower()
            if self._page_size not in self.PAGE_DIMENSIONS:
                self._page_size = "letter"

    def set_screen_dpi(self, dpi_x: float, dpi_y: float | None = None) -> None:
        """Update the screen DPI used for pixel conversions."""
        if dpi_y is None:
            dpi_y = dpi_x
        if dpi_x and dpi_x > 0:
            self._screen_dpi_x = float(dpi_x)
        if dpi_y and dpi_y > 0:
            self._screen_dpi_y = float(dpi_y)

    @property
    def screen_dpi_x(self) -> float:
        """Screen DPI used for width calculations."""
        return self._screen_dpi_x

    @property
    def screen_dpi_y(self) -> float:
        """Screen DPI used for height calculations."""
        return self._screen_dpi_y
    
    @property
    def page_width_inches(self) -> float:
        """Page width in inches."""
        if self._custom_dimensions:
            return self._custom_dimensions[0]
        return self.PAGE_DIMENSIONS[self._page_size][0]
    
    @property
    def page_height_inches(self) -> float:
        """Page height in inches."""
        if self._custom_dimensions:
            return self._custom_dimensions[1]
        return self.PAGE_DIMENSIONS[self._page_size][1]
    
    @property
    def content_height_inches(self) -> float:
        """Content height (page height minus top and bottom margins)."""
        return self.page_height_inches - self._margins[0] - self._margins[2]
    
    @property
    def content_width_inches(self) -> float:
        """Content width (page width minus left and right margins)."""
        return self.page_width_inches - self._margins[1] - self._margins[3]
    
    @property
    def page_height_pixels(self) -> int:
        """Page height in pixels at screen DPI."""
        return int(self.page_height_inches * self._screen_dpi_y)

    @property
    def page_width_pixels(self) -> int:
        """Page width in pixels at screen DPI."""
        return int(self.page_width_inches * self._screen_dpi_x)
    
    @property
    def content_height_pixels(self) -> int:
        """Content area height in pixels (for page break calculations)."""
        return int(self.content_height_inches * self._screen_dpi_y)
    
    @property 
    def content_width_pixels(self) -> int:
        """Content area width in pixels."""
        return int(self.content_width_inches * self._screen_dpi_x)

    @property
    def margins_inches(self) -> tuple:
        """Return margins in inches (top, right, bottom, left)."""
        return self._margins


# Default page settings instance (Letter size with 1" margins)
# Content height: 11" - 2" = 9" = 864 pixels at 96 DPI
DEFAULT_PAGE_SETTINGS = PageSettings("letter")

# Common constants for quick access
PAGE_HEIGHT_LETTER = DEFAULT_PAGE_SETTINGS.content_height_pixels  # 864
PAGE_HEIGHT_LEGAL = PageSettings("legal").content_height_pixels   # 1152
PAGE_HEIGHT_A4 = PageSettings("a4").content_height_pixels         # 929


# === List Style Constants ===
# Used by the ribbon UI to build list style menus
# The actual list feature logic remains in the ListFeature class

LIST_STYLES = {
    # Bullet styles
    "Disc (●)": QTextListFormat.Style.ListDisc,
    "Circle (○)": QTextListFormat.Style.ListCircle,
    "Square (■)": QTextListFormat.Style.ListSquare,
    # Number styles
    "Decimal (1, 2, 3)": QTextListFormat.Style.ListDecimal,
    "Lower Alpha (a, b, c)": QTextListFormat.Style.ListLowerAlpha,
    "Upper Alpha (A, B, C)": QTextListFormat.Style.ListUpperAlpha,
    "Lower Roman (i, ii, iii)": QTextListFormat.Style.ListLowerRoman,
    "Upper Roman (I, II, III)": QTextListFormat.Style.ListUpperRoman,
}

# Quick access groups for ribbon menus
BULLET_STYLES = ["Disc (●)", "Circle (○)", "Square (■)"]
NUMBER_STYLES = ["Decimal (1, 2, 3)", "Lower Alpha (a, b, c)", "Upper Alpha (A, B, C)", 
                 "Lower Roman (i, ii, iii)", "Upper Roman (I, II, III)"]
