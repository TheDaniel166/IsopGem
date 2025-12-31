"""
Math Renderer module using Matplotlib.
Converts LaTeX strings to QImage.
"""
import io
from typing import Optional
from PyQt6.QtGui import QImage

class MathRenderer:
    """Helper to render LaTeX to QImage using Matplotlib."""
    
    @staticmethod
    def render_latex(latex: str, fontsize: int = 14, dpi: int = 120, color: str = 'black') -> Optional[QImage]:
        """
        Render a LaTeX string to a QImage.
        """
        try:
            import matplotlib
            # Use Agg backend (non-interactive) to avoid GUI conflicts
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
        except ImportError:
            # This should not happen if dependencies are correct
            print("Matplotlib not found.")
            return None
            
        try:
            # Ensure math mode
            render_text = latex.strip()
            if not render_text.startswith('$'):
                render_text = f"${render_text}$"
            
            # Setup figure
            # Small initial size, will expand with bbox_inches='tight'
            fig = plt.figure(figsize=(0.01, 0.01))
            
            # Render text
            # We use the text capability of matplotlib
            fig.text(0, 0, render_text, fontsize=fontsize, color=color)
            
            buffer = io.BytesIO()
            fig.savefig(
                buffer, 
                dpi=dpi, 
                format='png', 
                transparent=True, 
                bbox_inches='tight', 
                pad_inches=0.05
            )
            plt.close(fig)
            
            buffer.seek(0)
            image = QImage()
            success = image.loadFromData(buffer.getvalue())
            
            if not success:
                print("Failed to load image from matplotlib buffer")
                return None
                
            return image
            
        except Exception as e:
            print(f"Failed to render LaTeX: {e}")
            return None
