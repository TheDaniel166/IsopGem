"""
Offline Mermaid Renderer using QtWebEngine.
Renders Mermaid diagrams using a local JS library and a hidden WebEngineView.
"""
import os
import logging
from PyQt6.QtCore import QUrl, QSize, QEventLoop, QTimer, Qt
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings

logger = logging.getLogger(__name__)

class WebViewMermaidRenderer:
    """
    Renders Mermaid code to QImage using a hidden QWebEngineView 
    and local mermaid.min.js.
    """
    
    def __init__(self):
        # We don't keep the view alive permanently to save memory, 
        # or we could keep one instance? 
        # For simplicity/performance trade-off, let's create one per request for now 
        # or one static one if we want to optimize. 
        # Given it's a desktop app, creating a generic hidden view is fine.
        pass

    @staticmethod
    def render_mermaid(code: str, width_hint: int = 1000, theme: str = "default", scale: float = 1.0) -> QImage:
        """
        Render mermaid code to QImage synchronously (blocking via EventLoop).
        
        Args:
            code: Mermaid diagram code
            width_hint: Initial width for the render container
            theme: Mermaid theme (default, dark, forest, neutral, base)
            scale: Scaling factor for high-DPI exports (e.g. 2.0, 3.0)
        """
        if not code.strip():
            return None

        # 1. Setup View
        view = QWebEngineView()
        view.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        # Resize initial window to accommodate scaling
        view.resize(int(width_hint * scale), int(800 * scale)) 
        view.show() 
        view.move(-10000, -10000)
        
        # Apply scaling
        if scale != 1.0:
            view.setZoomFactor(scale)

        # 2. Prepare HTML
        # Point to local assets
        # File is at src/shared/ui/rich_text_editor/webview_mermaid_renderer.py
        # root is at src/ (3 levels up) -> assets/mermaid.min.js
        current_dir = os.path.dirname(__file__)
        src_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
        project_root = os.path.dirname(src_dir) # Parent of src
        js_path = os.path.join(src_dir, "assets/mermaid.min.js")
        
        if not os.path.exists(js_path):
            logger.error("MermaidRenderer: JS not found at %s", js_path)
            return None

        js_url = QUrl.fromLocalFile(js_path).toString()
        
        # Escape code for safe HTML embedding
        escaped_code = code.replace("<", "&lt;").replace(">", "&gt;")
        
        # Scale the container padding proportionally? Or keep visual padding?
        # Standard CSS pixels will be scaled by zoom factor.
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="{js_url}"></script>
            <style>
                body {{ margin: 0; padding: 0; background: white; overflow: hidden; }}
                #container {{ display: inline-block; padding: 10px; }}
            </style>
        </head>
        <body>
            <div id="container" class="mermaid">
            {escaped_code}
            </div>
            <script>
                mermaid.initialize({{ 
                    startOnLoad: true,
                    theme: '{theme}'
                }});
            </script>
        </body>
        </html>
        """
        
        # 3. Load Page
        loop = QEventLoop()
        view.loadFinished.connect(lambda ok: loop.quit())
        
        # Timeout safety
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        timer.start(5000) 
        
        view.setHtml(html, QUrl.fromLocalFile(project_root + "/"))
        loop.exec()
        
        if not timer.isActive():
            logger.warning("MermaidRenderer: load timed out")
            view.deleteLater()
            return None
        timer.stop()

        # 4. Wait for Render stability
        # We'll poll JS until the svg is present
        # TODO: A smarter way is to use a specific JS Done signal.
        # But for now, simple sleep is reliable enough for v1.
        
        wait_loop = QEventLoop()
        QTimer.singleShot(800, wait_loop.quit)
        wait_loop.exec()

        # 5. Get Content Size
        size_data = {"w": 0, "h": 0}
        
        size_loop = QEventLoop()
        def on_size(res):
            if res:
                size_data["w"] = res[0]
                size_data["h"] = res[1]
            size_loop.quit()

        js_size = """
        [
            document.getElementById('container').offsetWidth,
            document.getElementById('container').offsetHeight
        ]
        """
        view.page().runJavaScript(js_size, on_size)
        size_loop.exec()
        
        w, h = size_data["w"], size_data["h"]
        if w == 0 or h == 0:
             # Fallback
             w, h = view.width(), view.height()
        
        # Resize view to fit content tightly
        # If scale is 2.0, w/h (CSS pixels) are same, but view needs to be 2x CSS pixels physically?
        # QtWebEngine setZoomFactor: "The zoom factor by which the view contents are scaled."
        # If I have a 100px div, at zoom 2.0 it renders as 200px visually.
        # offsetWidth returns 100 (CSS pixels).
        # So we need to resize view to (w * scale, h * scale).
        
        view.resize(int(w * scale), int(h * scale))
        
        # Wait for resize repaint
        repaint_loop = QEventLoop()
        QTimer.singleShot(100, repaint_loop.quit)
        repaint_loop.exec()
        
        # 6. Capture
        image = view.grab().toImage()
        
        # Cleanup
        view.deleteLater()
        
        return image


    @staticmethod
    def render_mermaid_svg(code: str, theme: str = "default") -> str | None:
        """
        Render mermaid code to SVG string synchronously.
        
        Args:
            code: Mermaid diagram code
            theme: Mermaid theme
            
        Returns:
            str: Raw SVG string or None if failed
        """
        if not code.strip():
            return None

        # 1. Setup View
        view = QWebEngineView()
        view.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        view.resize(1000, 800) 
        view.show() 
        view.move(-10000, -10000)

        # 2. Prepare HTML
        current_dir = os.path.dirname(__file__)
        src_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
        project_root = os.path.dirname(src_dir)
        js_path = os.path.join(src_dir, "assets/mermaid.min.js")
        
        if not os.path.exists(js_path):
            logger.error("MermaidRenderer: JS not found at %s", js_path)
            return None

        js_url = QUrl.fromLocalFile(js_path).toString()
        escaped_code = code.replace("<", "&lt;").replace(">", "&gt;")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="{js_url}"></script>
            <style>
                body {{ margin: 0; padding: 0; background: white; }}
                #container {{ display: inline-block; padding: 10px; }}
            </style>
        </head>
        <body>
            <div id="container" class="mermaid">
            {escaped_code}
            </div>
            <script>
                mermaid.initialize({{ 
                    startOnLoad: true,
                    theme: '{theme}'
                }});
            </script>
        </body>
        </html>
        """
        
        # 3. Load Page
        loop = QEventLoop()
        view.loadFinished.connect(lambda ok: loop.quit())
        
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        timer.start(5000) 
        
        view.setHtml(html, QUrl.fromLocalFile(project_root + "/"))
        loop.exec()
        
        if not timer.isActive():
            logger.warning("MermaidRenderer: load timed out")
            view.deleteLater()
            return None
        timer.stop()

        # 4. Wait for Render stability
        wait_loop = QEventLoop()
        QTimer.singleShot(800, wait_loop.quit)
        wait_loop.exec()

        # 5. Extract SVG
        svg_data = {"content": None}
        
        js_extract = "document.querySelector('.mermaid svg').outerHTML"
        
        js_loop = QEventLoop()
        def on_result(res):
            svg_data["content"] = res
            js_loop.quit()

        view.page().runJavaScript(js_extract, on_result)
        js_loop.exec()
        
        # Cleanup
        view.deleteLater()
        
        return svg_data["content"]
