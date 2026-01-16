"""Export service for cymatics images and animations.

Provides functionality to save cymatics patterns as PNG images
and animated GIF files.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Callable, List, Optional

import numpy as np
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QFileDialog, QWidget

from ..models import ColorGradient, SimulationResult
from .cymatics_gradient_service import CymaticsGradientService


class CymaticsExportService:
    """Handles export of cymatics patterns as images and animations.

    Supports:
        - Single frame PNG/JPG export
        - PNG sequence export for video creation
        - Animated GIF export (requires imageio)
    """

    def __init__(self):
        self._gradient_service = CymaticsGradientService()

    def export_image(
        self,
        parent: QWidget,
        result: SimulationResult,
        gradient_type: ColorGradient = ColorGradient.GRAYSCALE,
        path: Optional[Path] = None,
    ) -> Optional[Path]:
        """Export current pattern as image file.

        Args:
            parent: Parent widget for file dialog
            result: Simulation result to export
            gradient_type: Color gradient to apply
            path: Optional explicit path. If None, shows file dialog.

        Returns:
            Path to saved file, or None if cancelled
        """
        if path is None:
            timestamp = int(time.time())
            default_name = f"cymatics_{timestamp}.png"
            path_str, _ = QFileDialog.getSaveFileName(
                parent,
                "Save Cymatics Pattern",
                str(Path.home() / default_name),
                "PNG Image (*.png);;JPEG Image (*.jpg);;BMP Image (*.bmp)",
            )
            if not path_str:
                return None
            path = Path(path_str)

        # Generate colored image
        qimage = self._gradient_service.to_qimage(
            result.normalized, gradient_type
        )

        # Determine format from extension
        ext = path.suffix.lower()
        if ext in (".jpg", ".jpeg"):
            fmt = "JPEG"
        elif ext == ".bmp":
            fmt = "BMP"
        else:
            fmt = "PNG"
            if not path.suffix:
                path = path.with_suffix(".png")

        qimage.save(str(path), fmt)
        return path

    def export_widget_snapshot(
        self,
        widget: QWidget,
        path: Optional[Path] = None,
    ) -> Optional[Path]:
        """Export widget contents as image.

        Args:
            widget: Widget to capture
            path: Optional explicit path. If None, shows file dialog.

        Returns:
            Path to saved file, or None if cancelled
        """
        if path is None:
            timestamp = int(time.time())
            default_name = f"cymatics_snapshot_{timestamp}.png"
            path_str, _ = QFileDialog.getSaveFileName(
                widget,
                "Save Snapshot",
                str(Path.home() / default_name),
                "PNG Image (*.png)",
            )
            if not path_str:
                return None
            path = Path(path_str)

        pixmap = widget.grab()
        pixmap.save(str(path), "PNG")
        return path

    def export_frame_sequence(
        self,
        render_func: Callable[[float], np.ndarray],
        gradient_type: ColorGradient,
        frame_count: int = 60,
        output_dir: Optional[Path] = None,
    ) -> List[Path]:
        """Export animation as sequence of PNG frames.

        Args:
            render_func: Function that takes phase (0 to 2*pi) and returns
                        normalized amplitude array
            gradient_type: Color gradient to apply
            frame_count: Number of frames to generate
            output_dir: Directory for frames. If None, uses temp directory.

        Returns:
            List of paths to generated frame files
        """
        if output_dir is None:
            timestamp = int(time.time())
            output_dir = Path.home() / f"cymatics_frames_{timestamp}"

        output_dir.mkdir(parents=True, exist_ok=True)
        paths: List[Path] = []

        for i in range(frame_count):
            phase = (i / frame_count) * 2 * np.pi
            normalized = render_func(phase)

            qimage = self._gradient_service.to_qimage(normalized, gradient_type)
            frame_path = output_dir / f"frame_{i:04d}.png"
            qimage.save(str(frame_path), "PNG")
            paths.append(frame_path)

        return paths

    def export_gif(
        self,
        parent: QWidget,
        render_func: Callable[[float], np.ndarray],
        gradient_type: ColorGradient,
        frame_count: int = 60,
        fps: int = 30,
        path: Optional[Path] = None,
    ) -> Optional[Path]:
        """Export animation as GIF file.

        Requires imageio library to be installed.

        Args:
            parent: Parent widget for file dialog
            render_func: Function that takes phase and returns normalized array
            gradient_type: Color gradient to apply
            frame_count: Number of frames
            fps: Frames per second
            path: Optional explicit path. If None, shows file dialog.

        Returns:
            Path to saved GIF, or None if cancelled or imageio unavailable

        Raises:
            RuntimeError: If imageio is not installed
        """
        try:
            import imageio.v3 as iio
        except ImportError:
            raise RuntimeError(
                "GIF export requires imageio library. "
                "Install with: pip install imageio"
            )

        if path is None:
            timestamp = int(time.time())
            default_name = f"cymatics_{timestamp}.gif"
            path_str, _ = QFileDialog.getSaveFileName(
                parent,
                "Save Animated GIF",
                str(Path.home() / default_name),
                "GIF Animation (*.gif)",
            )
            if not path_str:
                return None
            path = Path(path_str)

        if not path.suffix:
            path = path.with_suffix(".gif")

        # Generate frames
        frames: List[np.ndarray] = []
        for i in range(frame_count):
            phase = (i / frame_count) * 2 * np.pi
            normalized = render_func(phase)
            rgba = self._gradient_service.apply_gradient(normalized, gradient_type)
            frames.append(rgba)

        # Write GIF
        duration = 1000 // fps  # milliseconds per frame
        iio.imwrite(path, frames, duration=duration, loop=0)

        return path

    def result_to_numpy_rgba(
        self,
        result: SimulationResult,
        gradient_type: ColorGradient,
    ) -> np.ndarray:
        """Convert simulation result to RGBA numpy array.

        Useful for custom export pipelines.

        Args:
            result: Simulation result
            gradient_type: Color gradient to apply

        Returns:
            RGBA array of shape (H, W, 4)
        """
        return self._gradient_service.apply_gradient(
            result.normalized, gradient_type
        )
