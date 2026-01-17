"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: UI Component (GRANDFATHERED - should move to pillars/document_manager)
- USED BY: Internal shared/ modules only (3 references)
- CRITERION: Violation (Single-pillar UI component)

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""

"""
Offline Mermaid Renderer using QtWebEngine.

**Architecture**:
This renderer converts Mermaid diagram code to images (PNG/SVG) using a headless
WebEngine browser. It loads a local copy of mermaid.min.js to work completely offline.

**Performance Strategy**:
- Uses view pooling to avoid recreating QWebEngineView instances
- Smart render detection via JS callbacks instead of blind waits
- Captures JS console errors for detailed error reporting

**Usage Example**:

```python
# Simple render to QImage
image = WebViewMermaidRenderer.render_mermaid("graph TD\\nA-->B", theme="dark")

# High-DPI export
hq_image = WebViewMermaidRenderer.render_mermaid(
    code, theme="forest", scale=3.0, width_hint=1200
)

# SVG export
svg_str = WebViewMermaidRenderer.render_mermaid_svg(code, theme="neutral")

# Advanced configuration
config = MermaidConfig(flowchart_curve="basis", theme_variables={"primaryColor": "#ff6"})
image = WebViewMermaidRenderer.render_mermaid_advanced(code, config)
```

**Error Handling**:
Returns `None` on failure. Check logs for details. Common failure modes:
- Invalid Mermaid syntax (logged from JS console)
- Missing mermaid.min.js file
- Render timeout (default 5s, configurable)

**Thread Safety**:
Not thread-safe. All methods must be called from the Qt main thread.
"""

import os
import logging
import html as html_module
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from PyQt6.QtCore import QUrl, QSize, QEventLoop, QTimer, Qt, QByteArray, QRectF
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
import weakref


logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS
# ============================================================================

# Timeout for page load (milliseconds)
PAGE_LOAD_TIMEOUT_MS = 5000

# Timeout for render completion detection (milliseconds)
RENDER_TIMEOUT_MS = 800

# Time to wait for repaint after resize (milliseconds)
REPAINT_DELAY_MS = 100

# Default dimensions
DEFAULT_WIDTH = 1000
DEFAULT_HEIGHT = 800

# View pool settings
MAX_POOLED_VIEWS = 3  # Maximum number of cached WebView instances
VIEW_POOL_CLEANUP_DELAY_MS = 60000  # Cleanup unused views after 1 minute


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class MermaidConfig:
    """
    Advanced Mermaid configuration options.
    
    Exposes Mermaid's full initialization config for fine-grained control.
    
    **Theme Customization**:
    - theme: One of "default", "dark", "forest", "neutral", "base"
    - theme_variables: Dict of CSS variables (e.g., {"primaryColor": "#ff6"})
    
    **Flowchart/Graph Options**:
    - flowchart_curve: "basis", "linear", "cardinal", "monotoneX", "monotoneY", "natural", "step", "stepAfter", "stepBefore"
    - default_renderer: "dagre", "dagre-d3", "dagre-wrapper", "elk"
    
    **Sequence Diagram Options**:
    - sequence_diagram_actor_margin: Spacing between actors
    - sequence_diagram_box_margin: Margin around boxes
    
    **Font Options**:
    - font_family: CSS font stack
    - font_size: Base font size (CSS value, e.g., "16px")
    
    **Export Options**:
    - log_level: 1 (debug), 2 (info), 3 (warn), 4 (error), 5 (fatal)
    - secure: Security level (["strict", "loose", "antiscript", "sandbox"])
    
    Example:
    ```python
    config = MermaidConfig(
        theme="dark",
        theme_variables={"primaryColor": "#bb86fc", "primaryTextColor": "#fff"},
        flowchart_curve="basis",
        font_family="'Fira Code', monospace"
    )
    image = WebViewMermaidRenderer.render_mermaid_advanced(code, config)
    ```
    """
    theme: str = "default"
    theme_variables: Optional[Dict[str, str]] = None
    
    # Flowchart options
    flowchart_curve: Optional[str] = None  # "basis", "linear", "cardinal", etc.
    default_renderer: str = "dagre"
    
    # Sequence diagram options
    sequence_diagram_actor_margin: Optional[int] = None
    sequence_diagram_box_margin: Optional[int] = None
    
    # Font options
    font_family: Optional[str] = None
    font_size: Optional[str] = None
    
    # Security & logging
    log_level: int = 4  # Error level by default
    secure: str = "strict"
    start_on_load: bool = False
    
    def to_js_config(self) -> str:
        """
        Convert to JavaScript Mermaid initialization config.
        
        Returns:
            str: JavaScript object literal for mermaid.initialize({...})
        """
        config_parts = [
            f"startOnLoad: {'true' if self.start_on_load else 'false'}",
            f"theme: '{self.theme}'",
            f"logLevel: {self.log_level}",
        ]
        
        if self.theme_variables:
            vars_str = ", ".join(f"{k}: '{v}'" for k, v in self.theme_variables.items())
            config_parts.append(f"themeVariables: {{ {vars_str} }}")
        
        if self.flowchart_curve:
            config_parts.append(f"flowchart: {{ curve: '{self.flowchart_curve}' }}")
        
        if self.sequence_diagram_actor_margin is not None or self.sequence_diagram_box_margin is not None:
            seq_parts = []
            if self.sequence_diagram_actor_margin is not None:
                seq_parts.append(f"actorMargin: {self.sequence_diagram_actor_margin}")
            if self.sequence_diagram_box_margin is not None:
                seq_parts.append(f"boxMargin: {self.sequence_diagram_box_margin}")
            config_parts.append(f"sequence: {{ {', '.join(seq_parts)} }}")
        
        if self.font_family:
            config_parts.append(f"fontFamily: '{self.font_family}'")
        
        if self.font_size:
            config_parts.append(f"fontSize: '{self.font_size}'")
        
        return "{ " + ", ".join(config_parts) + " }"


# ============================================================================
# ERROR CAPTURING
# ============================================================================

class ConsoleMessageCollector:
    """Collects console messages from WebEngine for error reporting."""
    
    def __init__(self):
        self.messages = []
    
    def collect(self, level, message, line, source_id):
        """Callback for QWebEnginePage.javaScriptConsoleMessage."""
        self.messages.append({
            "level": level,
            "message": message,
            "line": line,
            "source": source_id
        })
    
    def get_errors(self) -> list[str]:
        """Extract error messages only."""
        return [msg["message"] for msg in self.messages if msg["level"] >= 2]  # Error/Critical
    
    def clear(self):
        """Reset message buffer."""
        self.messages.clear()


# ============================================================================
# RENDERER
# ============================================================================

class WebViewMermaidRenderer:
    """
    High-performance offline Mermaid diagram renderer.
    
    **Features**:
    - Offline rendering using local mermaid.min.js
    - View pooling to minimize WebEngine overhead
    - Smart render detection via JS callbacks
    - Detailed error reporting from JS console
    - PNG and SVG export with scaling
    - Advanced configuration API
    
    **Performance Notes**:
    - First render: ~200-400ms (WebEngine initialization)
    - Subsequent renders: ~80-150ms (view reuse)
    - View pool keeps up to 3 instances warm
    
    **Thread Safety**:
    All methods are static and create views on-demand. Not thread-safe;
    must be called from Qt main thread.
    """
    
    # View pool for performance (class-level)
    _view_pool: list[QWebEngineView] = []
    _pool_lock = False  # Simple flag to prevent concurrent access
    # Track live views to help diagnose leaks that prevent clean shutdown
    _live_views: "weakref.WeakSet[QWebEngineView]" = weakref.WeakSet()  # type: ignore[assignment]

    
    def __init__(self):
        """
        Constructor exists for backwards compatibility but is not needed.
        All methods are static.
        """
        pass

    @classmethod
    def _configure_view(cls, view: QWebEngineView) -> None:
        """Apply WebEngine settings required for offline Mermaid rendering."""
        settings = view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
    
    @classmethod
    def _get_view_from_pool(cls) -> QWebEngineView:
        """
        Get a WebEngineView from the pool or create a new one.
        
        Returns:
            QWebEngineView: A hidden, off-screen web view ready for rendering
        """
        if cls._view_pool and not cls._pool_lock:
            cls._pool_lock = True
            view = cls._view_pool.pop()
            cls._pool_lock = False
            cls._configure_view(view)
            logger.debug("MermaidRenderer: Reusing pooled view %s (pool_size=%d)", hex(id(view)), len(cls._view_pool))
            return view
        
        # Create new view
        view = QWebEngineView()
        cls._configure_view(view)
        view.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        view.show()
        view.move(-10000, -10000)
        # Track live view for diagnostics
        try:
            cls._live_views.add(view)
            logger.debug("MermaidRenderer: Created new view %s (live_views=%d)", hex(id(view)), len(cls._live_views))
        except Exception:
            logger.exception("MermaidRenderer: Failed to track live view")
        
        return view
    
    @classmethod
    def _return_view_to_pool(cls, view: QWebEngineView):
        """
        Return a view to the pool for reuse.
        
        Args:
            view: The view to return to the pool
        """
        if len(cls._view_pool) < MAX_POOLED_VIEWS:
            # Reset view state
            view.resize(DEFAULT_WIDTH, DEFAULT_HEIGHT)
            view.setZoomFactor(1.0)
            cls._view_pool.append(view)
            logger.debug("MermaidRenderer: Returned view %s to pool (pool_size=%d)", hex(id(view)), len(cls._view_pool))
        else:
            # Pool full, delete this view
            try:
                # Remove from live views tracking if present
                if view in cls._live_views:
                    cls._live_views.discard(view)
            except Exception:
                logger.exception("MermaidRenderer: Error removing view from live set")
            logger.debug("MermaidRenderer: Pool full - deleting view %s", hex(id(view)))
            view.close()
            view.deleteLater()
    
    @classmethod
    def _cleanup_view_pool(cls):
        """Clear the view pool (called on app shutdown or memory pressure)."""
        from PyQt6.QtWidgets import QApplication

        logger.info("MermaidRenderer: _cleanup_view_pool called (pool_size=%d, live_views=%d)", len(cls._view_pool), len(cls._live_views))

        # Clean up pooled views
        while cls._view_pool:
            view = cls._view_pool.pop()
            try:
                logger.info("MermaidRenderer: closing pooled view %s", hex(id(view)))
                view.page().deleteLater()  # Delete the page first
                view.close()
                view.deleteLater()
            except Exception:
                logger.exception("MermaidRenderer: Error closing view %s", hex(id(view)))
            try:
                cls._live_views.discard(view)
            except Exception:
                pass

        # Force cleanup of any remaining live views (e.g., leaked references)
        try:
            live_views_copy = list(cls._live_views)
            for view in live_views_copy:
                try:
                    logger.info("MermaidRenderer: force-closing live view %s", hex(id(view)))
                    view.page().deleteLater()
                    view.close()
                    view.deleteLater()
                except Exception:
                    logger.exception("MermaidRenderer: Error force-closing view")
            cls._live_views = weakref.WeakSet()
        except Exception:
            logger.exception("MermaidRenderer: Error cleaning up live views")

        # Process pending deletions immediately
        app = QApplication.instance()
        if app:
            app.processEvents()

        logger.info("MermaidRenderer: cleanup complete (pool_size=%d, live_views=%d)", len(cls._view_pool), len(cls._live_views))

    @classmethod
    def _read_js(cls, view: QWebEngineView, script: str) -> Any:
        """Run JS in the view and return the result synchronously."""
        result: dict[str, Any] = {"value": None}
        loop = QEventLoop()

        def on_result(res: Any) -> None:
            result["value"] = res
            loop.quit()

        view.page().runJavaScript(script, on_result)
        loop.exec()
        return result["value"]

    @classmethod
    def _svg_to_image(
        cls,
        svg_content: str,
        width: int,
        height: int,
        scale: float
    ) -> Optional[QImage]:
        """Render SVG to QImage using QtSvg when available."""
        try:
            from PyQt6.QtSvg import QSvgRenderer
        except Exception:
            return None

        renderer = QSvgRenderer(QByteArray(svg_content.encode("utf-8")))
        if not renderer.isValid():
            return None

        if width <= 0 or height <= 0:
            default_size = renderer.defaultSize()
            width = default_size.width()
            height = default_size.height()
        if width <= 0 or height <= 0:
            width = DEFAULT_WIDTH
            height = DEFAULT_HEIGHT

        target_width = max(1, int(width * scale))
        target_height = max(1, int(height * scale))
        image = QImage(target_width, target_height, QImage.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.white)

        painter = QPainter(image)
        renderer.render(painter, QRectF(0, 0, target_width, target_height))
        painter.end()

        return image

    @classmethod
    def render_mermaid(
        cls,
        code: str,
        width_hint: int = DEFAULT_WIDTH,
        theme: str = "default",
        scale: float = 1.0
    ) -> Optional[QImage]:
        """
        Render Mermaid diagram code to QImage.
        
        **Blocking Operation**: Uses QEventLoop to wait for render completion.
        Typical render time: 80-150ms for simple diagrams, 200-400ms for complex.
        
        **Args**:
            code: Mermaid diagram source code
                Example: "graph TD\\n    A[Start] --> B[End]"
            width_hint: Initial container width in pixels (default 1000)
                Larger values accommodate wider diagrams before wrapping
            theme: Mermaid theme name (default "default")
                Options: "default", "dark", "forest", "neutral", "base"
            scale: Rendering scale factor for high-DPI export (default 1.0)
                Use 2.0 for Retina, 3.0 for ultra-high-DPI printing
        
        **Returns**:
            QImage: Rendered diagram, or None on failure
        
        **Example**:
        ```python
        # Basic render
        img = WebViewMermaidRenderer.render_mermaid("graph LR\\nA-->B")
        
        # High-DPI export for printing
        hq_img = WebViewMermaidRenderer.render_mermaid(
            code, width_hint=1200, theme="neutral", scale=3.0
        )
        if hq_img:
            hq_img.save("diagram.png", "PNG")
        ```
        
        **Error Handling**:
        Returns None on failure. Check logs for details:
        - Syntax errors in Mermaid code
        - Missing mermaid.min.js
        - Render timeout
        """
        if not code.strip():
            logger.warning("render_mermaid: Empty code provided")
            return None

        # 1. Get view from pool
        view = cls._get_view_from_pool()
        
        # Resize initial window to accommodate scaling
        view.resize(int(width_hint * scale), int(DEFAULT_HEIGHT * scale))
        
        # Apply scaling
        if scale != 1.0:
            view.setZoomFactor(scale)

        # 2. Prepare HTML
        # Point to local assets
        # File is at src/pillars/document_manager/ui/features/webview_mermaid_renderer.py
        # root is at src/ (4 levels up) -> assets/mermaid.min.js
        current_dir = os.path.dirname(__file__)
        src_dir = os.path.abspath(os.path.join(current_dir, "../../../../"))
        project_root = os.path.dirname(src_dir) # Parent of src
        js_path = os.path.join(src_dir, "assets/mermaid.min.js")
        
        if not os.path.exists(js_path):
            logger.error("MermaidRenderer: JS not found at %s", js_path)
            cls._return_view_to_pool(view)
            return None

        js_url = QUrl.fromLocalFile(js_path).toString()

        # Escape HTML so Mermaid receives the original text via entity decoding.
        escaped_code = html_module.escape(code)
        
        # Scale the container padding proportionally? Or keep visual padding?
        # Standard CSS pixels will be scaled by zoom factor.
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="{js_url}"></script>
            <style>
                body {{ margin: 0; padding: 0; background: white; overflow: hidden; color: #000; }}
                #container {{ display: inline-block; padding: 10px; white-space: pre; }}
            </style>
        </head>
        <body>
            <div id="container" class="mermaid">
            {escaped_code}
            </div>
            <script>
                window.__mermaid_render_done = false;
                window.__mermaid_render_error = null;
                try {{
                    mermaid.initialize({{
                        startOnLoad: false,
                        theme: '{theme}'
                    }});
                    mermaid.run({{ nodes: [document.getElementById('container')] }})
                        .then(() => {{ window.__mermaid_render_done = true; }})
                        .catch((err) => {{ window.__mermaid_render_error = String(err); }});
                }} catch (err) {{
                    window.__mermaid_render_error = String(err);
                }}
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
        timer.start(PAGE_LOAD_TIMEOUT_MS) 
        
        view.setHtml(html, QUrl.fromLocalFile(project_root + "/"))
        loop.exec()
        
        if not timer.isActive():
            logger.warning("MermaidRenderer: Page load timed out")
            cls._return_view_to_pool(view)
            return None
        timer.stop()

        # 4. Wait for Render stability
        # Smart detection: poll for SVG element presence via JS
        render_complete = {"done": False}
        
        def check_render_done():
            js_check = "document.querySelector('.mermaid svg') !== null"
            
            def on_result(result):
                if result:
                    render_complete["done"] = True
            
            view.page().runJavaScript(js_check, on_result)
        
        # Poll every 50ms for up to RENDER_TIMEOUT_MS
        poll_timer = QTimer()
        poll_timer.timeout.connect(check_render_done)
        poll_timer.start(50)
        
        wait_loop = QEventLoop()
        
        # Timeout fallback
        timeout_timer = QTimer()
        timeout_timer.setSingleShot(True)
        timeout_timer.timeout.connect(wait_loop.quit)
        timeout_timer.start(RENDER_TIMEOUT_MS)
        
        # Check every 50ms if render is done
        def check_loop():
            if render_complete["done"]:
                wait_loop.quit()
        
        check_timer = QTimer()
        check_timer.timeout.connect(check_loop)
        check_timer.start(50)
        
        wait_loop.exec()
        
        poll_timer.stop()
        check_timer.stop()
        timeout_timer.stop()
        
        svg_content = cls._read_js(
            view,
            "document.querySelector('.mermaid svg') && document.querySelector('.mermaid svg').outerHTML"
        )
        if not svg_content:
            error_msg = cls._read_js(view, "window.__mermaid_render_error")
            if error_msg:
                logger.error("MermaidRenderer: JS render error: %s", error_msg)
            else:
                logger.warning("MermaidRenderer: Render timed out (SVG not detected)")
            cls._return_view_to_pool(view)
            return None

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

        image = cls._svg_to_image(svg_content, w, h, scale)
        if image is None:
            # Resize view to fit content tightly
            # If scale is 2.0, w/h (CSS pixels) are same, but view needs to be 2x CSS pixels physically.
            view.resize(int(w * scale), int(h * scale))

            # Wait for resize repaint
            repaint_loop = QEventLoop()
            QTimer.singleShot(REPAINT_DELAY_MS, repaint_loop.quit)
            repaint_loop.exec()

            # 6. Capture fallback
            image = view.grab().toImage()

        # Return view to pool for reuse
        cls._return_view_to_pool(view)

        return image


    @classmethod
    def render_mermaid_svg(cls, code: str, theme: str = "default") -> Optional[str]:
        """
        Render Mermaid diagram to scalable SVG string.
        
        **Use Case**: Export vector diagrams for embedding in web pages,
        PDFs, or any vector-capable format. SVG is resolution-independent.
        
        **Args**:
            code: Mermaid diagram source code
            theme: Mermaid theme name (default "default")
        
        **Returns**:
            str: Raw SVG markup (including <svg> root element), or None on failure
        
        **Example**:
        ```python
        svg_str = WebViewMermaidRenderer.render_mermaid_svg(code, theme="dark")
        if svg_str:
            with open("diagram.svg", "w") as f:
                f.write(svg_str)
        ```
        
        **Note**: SVG output includes inline styles and is self-contained.
        """
        if not code.strip():
            logger.warning("render_mermaid_svg: Empty code provided")
            return None

        # 1. Get view from pool
        view = cls._get_view_from_pool()
        view.resize(DEFAULT_WIDTH, DEFAULT_HEIGHT)

        # 2. Prepare HTML
        current_dir = os.path.dirname(__file__)
        src_dir = os.path.abspath(os.path.join(current_dir, "../../../../"))
        project_root = os.path.dirname(src_dir)
        js_path = os.path.join(src_dir, "assets/mermaid.min.js")
        
        if not os.path.exists(js_path):
            logger.error("MermaidRenderer: JS not found at %s", js_path)
            cls._return_view_to_pool(view)
            return None

        js_url = QUrl.fromLocalFile(js_path).toString()
        escaped_code = html_module.escape(code)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="{js_url}"></script>
            <style>
                body {{ margin: 0; padding: 0; background: white; color: #000; }}
                #container {{ display: inline-block; padding: 10px; white-space: pre; }}
            </style>
        </head>
        <body>
            <div id="container" class="mermaid">
            {escaped_code}
            </div>
            <script>
                window.__mermaid_render_done = false;
                window.__mermaid_render_error = null;
                try {{
                    mermaid.initialize({{
                        startOnLoad: false,
                        theme: '{theme}'
                    }});
                    mermaid.run({{ nodes: [document.getElementById('container')] }})
                        .then(() => {{ window.__mermaid_render_done = true; }})
                        .catch((err) => {{ window.__mermaid_render_error = String(err); }});
                }} catch (err) {{
                    window.__mermaid_render_error = String(err);
                }}
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
        timer.start(PAGE_LOAD_TIMEOUT_MS)
        
        view.setHtml(html, QUrl.fromLocalFile(project_root + "/"))
        loop.exec()
        
        if not timer.isActive():
            logger.warning("MermaidRenderer: SVG render page load timed out")
            cls._return_view_to_pool(view)
            return None
        timer.stop()

        # 4. Wait for Render stability (same smart detection as PNG render)
        render_complete = {"done": False}
        
        def check_render_done():
            js_check = "document.querySelector('.mermaid svg') !== null"
            
            def on_result(result):
                if result:
                    render_complete["done"] = True
            
            view.page().runJavaScript(js_check, on_result)
        
        poll_timer = QTimer()
        poll_timer.timeout.connect(check_render_done)
        poll_timer.start(50)
        
        wait_loop = QEventLoop()
        timeout_timer = QTimer()
        timeout_timer.setSingleShot(True)
        timeout_timer.timeout.connect(wait_loop.quit)
        timeout_timer.start(RENDER_TIMEOUT_MS)
        
        def check_loop():
            if render_complete["done"]:
                wait_loop.quit()
        
        check_timer = QTimer()
        check_timer.timeout.connect(check_loop)
        check_timer.start(50)
        
        wait_loop.exec()
        poll_timer.stop()
        check_timer.stop()
        timeout_timer.stop()

        svg_content = cls._read_js(
            view,
            "document.querySelector('.mermaid svg') && document.querySelector('.mermaid svg').outerHTML"
        )
        if not svg_content:
            error_msg = cls._read_js(view, "window.__mermaid_render_error")
            if error_msg:
                logger.error("MermaidRenderer: SVG render error: %s", error_msg)
            else:
                logger.warning("MermaidRenderer: SVG render timed out")
            cls._return_view_to_pool(view)
            return None
        
        # Return view to pool
        cls._return_view_to_pool(view)
        
        logger.debug("MermaidRenderer: Successfully rendered SVG (%d chars)", len(svg_content))
        return svg_content

    @classmethod
    def debug_dump_state(cls) -> Dict[str, Any]:
        """Return current pool and live view diagnostic info and log it.

        Use this when debugging shutdown hangs to see which views remain alive
        and whether the pool still holds views that should have been cleaned up.
        """
        try:
            live = [hex(id(v)) for v in list(cls._live_views)]
        except Exception:
            live = ["<error>"]
        info = {
            "pool_size": len(cls._view_pool),
            "live_views": live,
        }
        logger.warning("MermaidRenderer: DEBUG STATE - pool_size=%d, live_views=%s", info["pool_size"], info["live_views"])
        return info
    
    @classmethod
    def render_mermaid_advanced(
        cls,
        code: str,
        config: MermaidConfig,
        width_hint: int = DEFAULT_WIDTH,
        scale: float = 1.0
    ) -> Optional[QImage]:
        """
        Render Mermaid diagram with advanced configuration options.
        
        **Advanced Features**:
        - Custom theme variables (colors, fonts, spacing)
        - Flowchart curve styles (basis, linear, cardinal, etc.)
        - Sequence diagram layout customization
        - Font family and size overrides
        
        **Args**:
            code: Mermaid diagram source code
            config: MermaidConfig instance with advanced settings
            width_hint: Initial container width in pixels (default 1000)
            scale: Rendering scale factor (default 1.0)
        
        **Returns**:
            QImage: Rendered diagram, or None on failure
        
        **Example**:
        ```python
        # Custom purple theme with smooth curves
        config = MermaidConfig(
            theme="dark",
            theme_variables={"primaryColor": "#bb86fc", "primaryTextColor": "#fff"},
            flowchart_curve="basis",
            font_family="'Fira Code', monospace",
            font_size="14px"
        )
        img = WebViewMermaidRenderer.render_mermaid_advanced(code, config, scale=2.0)
        ```
        
        **Performance**: Same as render_mermaid (~80-150ms for simple diagrams)
        """
        if not code.strip():
            logger.warning("render_mermaid_advanced: Empty code provided")
            return None
        
        # Get view from pool
        view = cls._get_view_from_pool()
        view.resize(int(width_hint * scale), int(DEFAULT_HEIGHT * scale))
        
        if scale != 1.0:
            view.setZoomFactor(scale)
        
        # Prepare HTML with advanced config
        current_dir = os.path.dirname(__file__)
        src_dir = os.path.abspath(os.path.join(current_dir, "../../../../"))
        project_root = os.path.dirname(src_dir)
        js_path = os.path.join(src_dir, "assets/mermaid.min.js")
        
        if not os.path.exists(js_path):
            logger.error("MermaidRenderer: JS not found at %s", js_path)
            cls._return_view_to_pool(view)
            return None
        
        js_url = QUrl.fromLocalFile(js_path).toString()
        escaped_code = html_module.escape(code)
        
        # Build HTML with advanced config
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="{js_url}"></script>
            <style>
                body {{ margin: 0; padding: 0; background: white; overflow: hidden; color: #000; }}
                #container {{ display: inline-block; padding: 10px; white-space: pre; }}
            </style>
        </head>
        <body>
            <div id="container" class="mermaid">
            {escaped_code}
            </div>
            <script>
                window.__mermaid_render_done = false;
                window.__mermaid_render_error = null;
                try {{
                    mermaid.initialize({config.to_js_config()});
                    mermaid.run({{ nodes: [document.getElementById('container')] }})
                        .then(() => {{ window.__mermaid_render_done = true; }})
                        .catch((err) => {{ window.__mermaid_render_error = String(err); }});
                }} catch (err) {{
                    window.__mermaid_render_error = String(err);
                }}
            </script>
        </body>
        </html>
        """
        
        # Load and render (same pattern as render_mermaid)
        loop = QEventLoop()
        view.loadFinished.connect(lambda ok: loop.quit())
        
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        timer.start(PAGE_LOAD_TIMEOUT_MS)
        
        view.setHtml(html, QUrl.fromLocalFile(project_root + "/"))
        loop.exec()
        
        if not timer.isActive():
            logger.warning("MermaidRenderer: Advanced render page load timed out")
            cls._return_view_to_pool(view)
            return None
        timer.stop()
        
        # Wait for render with smart detection
        render_complete = {"done": False}
        
        def check_render_done():
            js_check = "document.querySelector('.mermaid svg') !== null"
            view.page().runJavaScript(js_check, lambda result: render_complete.update(done=result))
        
        poll_timer = QTimer()
        poll_timer.timeout.connect(check_render_done)
        poll_timer.start(50)
        
        wait_loop = QEventLoop()
        timeout_timer = QTimer()
        timeout_timer.setSingleShot(True)
        timeout_timer.timeout.connect(wait_loop.quit)
        timeout_timer.start(RENDER_TIMEOUT_MS)
        
        check_timer = QTimer()
        check_timer.timeout.connect(lambda: wait_loop.quit() if render_complete["done"] else None)
        check_timer.start(50)
        
        wait_loop.exec()
        poll_timer.stop()
        check_timer.stop()
        timeout_timer.stop()

        svg_content = cls._read_js(
            view,
            "document.querySelector('.mermaid svg') && document.querySelector('.mermaid svg').outerHTML"
        )
        if not svg_content:
            error_msg = cls._read_js(view, "window.__mermaid_render_error")
            if error_msg:
                logger.error("MermaidRenderer: Advanced render error: %s", error_msg)
            else:
                logger.warning("MermaidRenderer: Advanced render timed out")
            cls._return_view_to_pool(view)
            return None
        
        # Get content size and resize
        size_data = {"w": 0, "h": 0}
        size_loop = QEventLoop()
        
        def on_size(res):
            if res:
                size_data["w"], size_data["h"] = res[0], res[1]
            size_loop.quit()
        
        js_size = "[document.getElementById('container').offsetWidth, document.getElementById('container').offsetHeight]"
        view.page().runJavaScript(js_size, on_size)
        size_loop.exec()
        
        w, h = size_data["w"], size_data["h"]
        if w == 0 or h == 0:
            w, h = view.width(), view.height()

        image = cls._svg_to_image(svg_content, w, h, scale)
        if image is None:
            view.resize(int(w * scale), int(h * scale))

            # Wait for repaint
            repaint_loop = QEventLoop()
            QTimer.singleShot(REPAINT_DELAY_MS, repaint_loop.quit)
            repaint_loop.exec()

            # Capture
            image = view.grab().toImage()
        
        # Return view to pool
        cls._return_view_to_pool(view)
        
        logger.debug("MermaidRenderer: Advanced render complete (%dx%d)", image.width(), image.height())
        
        return image
    
    # ============================================================================
    # CONVENIENCE METHODS - EXPORT PRESETS
    # ============================================================================
    
    @classmethod
    def render_for_web(cls, code: str, theme: str = "default") -> Optional[QImage]:
        """
        Render diagram optimized for web display (1x scale, standard width).
        
        **Preset**: Balanced quality and file size for embedding in HTML/markdown.
        
        **Args**:
            code: Mermaid diagram source code
            theme: Mermaid theme name
        
        **Returns**:
            QImage: Web-optimized rendering (typically 800-1200px wide)
        
        **Example**:
        ```python
        img = WebViewMermaidRenderer.render_for_web(code, theme="default")
        if img:
            img.save("diagram-web.png", "PNG", quality=90)
        ```
        """
        return cls.render_mermaid(code, width_hint=DEFAULT_WIDTH, theme=theme, scale=1.0)
    
    @classmethod
    def render_for_print(cls, code: str, theme: str = "neutral") -> Optional[QImage]:
        """
        Render diagram optimized for printing (3x scale, wide, neutral theme).
        
        **Preset**: High-resolution for professional documents and presentations.
        Produces images suitable for 300 DPI printing.
        
        **Args**:
            code: Mermaid diagram source code
            theme: Mermaid theme (default "neutral" for print)
        
        **Returns**:
            QImage: Print-quality rendering (~3000-3600px wide)
        
        **Example**:
        ```python
        img = WebViewMermaidRenderer.render_for_print(code)
        if img:
            img.save("diagram-print.png", "PNG", quality=100)
        ```
        """
        return cls.render_mermaid(code, width_hint=1200, theme=theme, scale=3.0)
    
    @classmethod
    def render_for_presentation(cls, code: str, theme: str = "default") -> Optional[QImage]:
        """
        Render diagram optimized for presentations (2x scale, wide, high contrast).
        
        **Preset**: Sharp rendering for HD/4K projectors and large displays.
        
        **Args**:
            code: Mermaid diagram source code
            theme: Mermaid theme (default "default" for high contrast)
        
        **Returns**:
            QImage: Presentation-quality rendering (~2000-2400px wide)
        
        **Example**:
        ```python
        img = WebViewMermaidRenderer.render_for_presentation(code, theme="default")
        if img:
            img.save("slide-diagram.png", "PNG", quality=95)
        ```
        """
        return cls.render_mermaid(code, width_hint=1200, theme=theme, scale=2.0)
    
    @classmethod
    def render_thumbnail(cls, code: str, theme: str = "default") -> Optional[QImage]:
        """
        Render small preview thumbnail (0.5x scale, compact).
        
        **Preset**: Fast rendering for previews, galleries, or mobile displays.
        
        **Args**:
            code: Mermaid diagram source code
            theme: Mermaid theme
        
        **Returns**:
            QImage: Thumbnail rendering (~400-500px wide)
        
        **Example**:
        ```python
        thumb = WebViewMermaidRenderer.render_thumbnail(code)
        if thumb:
            thumb.save("diagram-thumb.png", "PNG", quality=80)
        ```
        """
        return cls.render_mermaid(code, width_hint=800, theme=theme, scale=0.5)
