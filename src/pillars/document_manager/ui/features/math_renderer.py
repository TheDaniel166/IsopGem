"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: UI Component (GRANDFATHERED - should move to pillars/document_manager)
- USED BY: Geometry (4 references)
- CRITERION: Violation (Single-pillar UI component)

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""

"""
Math Renderer module using Matplotlib.
Converts LaTeX strings to QImage with high-quality rendering.
"""

import io
import logging
from typing import Optional
from PyQt6.QtGui import QImage

logger = logging.getLogger(__name__)

class MathRenderer:
    """Helper to render LaTeX to QImage using Matplotlib with enhanced quality."""
    
    @staticmethod
    def render_latex(
        latex: str, 
        fontsize: int = 14, 
        dpi: int = 120, 
        color: str = 'black',
        use_high_quality: bool = True
    ) -> Optional[QImage]:
        """
        Render a LaTeX string to a QImage with high-quality settings.
        
        Args:
            latex: LaTeX string to render
            fontsize: Font size in points
            dpi: Resolution in dots per inch (higher = sharper)
            color: Text color (name or hex)
            use_high_quality: Enable enhanced rendering quality
            
        Returns:
            QImage containing rendered formula, or None on failure
            
        Quality Enhancements (when use_high_quality=True):
            - Anti-aliased text rendering
            - Proper figure sizing for crisp edges
            - Optimized matplotlib rcParams
            - High-quality font rendering
        """
        try:
            import matplotlib
            # Use Agg backend (non-interactive) to avoid GUI conflicts
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from matplotlib import rcParams
        except ImportError:
            # This should not happen if dependencies are correct
            logger.warning("MathRenderer: matplotlib not available")
            return None
            
        try:
            # Ensure math mode
            render_text = latex.strip()
            if not render_text.startswith('$'):
                render_text = f"${render_text}$"
            
            # Configure high-quality rendering
            if use_high_quality:
                # Save original settings
                original_settings = {
                    'text.antialiased': rcParams.get('text.antialiased', True),
                    'path.snap': rcParams.get('path.snap', True),
                    'figure.dpi': rcParams.get('figure.dpi', 100),
                }
                
                # Apply high-quality settings
                rcParams['text.antialiased'] = True
                rcParams['path.snap'] = False  # Better for high-DPI
                rcParams['figure.dpi'] = dpi
                # Use better font rendering
                rcParams['mathtext.fontset'] = 'cm'  # Computer Modern (LaTeX default)
                rcParams['mathtext.default'] = 'regular'
            
            # Setup figure with proper size
            # Use reasonable initial size (will be cropped to content)
            fig = plt.figure(figsize=(2, 1), dpi=dpi)
            fig.patch.set_alpha(0.0)  # Transparent background
            
            # Render text
            # Position at center, will be cropped with bbox_inches='tight'
            fig.text(
                0.5, 0.5, 
                render_text, 
                fontsize=fontsize, 
                color=color,
                ha='center',
                va='center',
                antialiased=True
            )
            
            buffer = io.BytesIO()
            fig.savefig(
                buffer, 
                dpi=dpi, 
                format='png', 
                transparent=True, 
                bbox_inches='tight', 
                pad_inches=0.1,  # Small padding for clean edges
                facecolor='none',
                edgecolor='none'
            )
            plt.close(fig)
            
            # Restore original settings
            if use_high_quality:
                for key, value in original_settings.items():
                    rcParams[key] = value
            
            buffer.seek(0)
            image = QImage()
            success = image.loadFromData(buffer.getvalue())
            
            if not success:
                logger.warning("MathRenderer: failed to load image from buffer")
                return None
                
            return image
            
        except Exception as e:
            logger.debug("MathRenderer: failed to render LaTeX (%s): %s", type(e).__name__, e)
            return None