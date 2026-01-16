# CymaticsExportService API Reference

<!-- Last Verified: 2026-01-16 -->

<cite>
**Referenced Files in This Document**
- [src/pillars/cymatics/services/cymatics_export_service.py](file://src/pillars/cymatics/services/cymatics_export_service.py)
- [__future__](file://__future__)
- [time](file://time)
- [pathlib](file://pathlib)
- [typing](file://typing)
- [numpy](file://numpy)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Class Overview](#class-overview)
3. [Core Methods](#core-methods)
4. [Usage Examples](#usage-examples)
5. [Error Handling](#error-handling)
6. [Dependencies](#dependencies)
7. [Performance Considerations](#performance-considerations)

## Introduction

Handles export of cymatics patterns as images and animations.

Supports:
    - Single frame PNG/JPG export
    - PNG sequence export for video creation
    - Animated GIF export (requires imageio)

**Architectural Role**: [Documentation needed: Define role (Service/Model/View/Repository)]
- **Layer**: [Documentation needed: Which architectural layer]
- **Responsibilities**: - __init__ method
- Export current pattern as image file
- Export widget contents as image
- **Dependencies**: __future__, time, pathlib
- **Consumers**: Unknown

## Class Overview

```python
class CymaticsExportService:
    """Handles export of cymatics patterns as images and animations.

Supports:
    - Single frame PNG/JPG export
    - PNG sequence export for video creation
    - Animated GIF export (requires imageio)"""
```

[Documentation needed: Add class diagram showing relationships]

## Core Methods

### export_image

```python
def export_image(self, parent: QWidget, result: SimulationResult, gradient_type: ColorGradient, path: Optional[Path]) -> Optional[Path]:
```

**Purpose**: Export current pattern as image file.

**Parameters:**
- `self` (None): Handles export of cymatics patterns as images and animations.
- `parent` (QWidget): Handles export of cymatics patterns as images and animations.
- `result` (SimulationResult): Handles export of cymatics patterns as images and animations.
- `gradient_type` (ColorGradient): Handles export of cymatics patterns as images and animations.
- `path` (Optional[Path]): Handles export of cymatics patterns as images and animations.

**Returns**: `Optional[Path]` - Handles export of cymatics patterns as images and animations.

**Example:**
```python
# ```python
self._preset_service = CymaticsPresetService()
        self._export_service = CymaticsExportService()
        self._audio_service = CymaticsAudioService()
```
```

### export_widget_snapshot

```python
def export_widget_snapshot(self, widget: QWidget, path: Optional[Path]) -> Optional[Path]:
```

**Purpose**: Export widget contents as image.

**Parameters:**
- `self` (None): Handles export of cymatics patterns as images and animations.
- `widget` (QWidget): Handles export of cymatics patterns as images and animations.
- `path` (Optional[Path]): Handles export of cymatics patterns as images and animations.

**Returns**: `Optional[Path]` - Handles export of cymatics patterns as images and animations.

**Example:**
```python
# ```python
self._preset_service = CymaticsPresetService()
        self._export_service = CymaticsExportService()
        self._audio_service = CymaticsAudioService()
```
```

### export_frame_sequence

```python
def export_frame_sequence(self, render_func: Callable[[float], np.ndarray], gradient_type: ColorGradient, frame_count: int, output_dir: Optional[Path]) -> List[Path]:
```

**Purpose**: Export animation as sequence of PNG frames.

**Parameters:**
- `self` (None): Handles export of cymatics patterns as images and animations.
- `render_func` (Callable[[float], np.ndarray]): Handles export of cymatics patterns as images and animations.
- `gradient_type` (ColorGradient): Handles export of cymatics patterns as images and animations.
- `frame_count` (int): Handles export of cymatics patterns as images and animations.
- `output_dir` (Optional[Path]): Handles export of cymatics patterns as images and animations.

**Returns**: `List[Path]` - Handles export of cymatics patterns as images and animations.

**Example:**
```python
# ```python
self._preset_service = CymaticsPresetService()
        self._export_service = CymaticsExportService()
        self._audio_service = CymaticsAudioService()
```
```

### export_gif

```python
def export_gif(self, parent: QWidget, render_func: Callable[[float], np.ndarray], gradient_type: ColorGradient, frame_count: int, fps: int, path: Optional[Path]) -> Optional[Path]:
```

**Purpose**: Export animation as GIF file.

**Parameters:**
- `self` (None): Handles export of cymatics patterns as images and animations.
- `parent` (QWidget): Handles export of cymatics patterns as images and animations.
- `render_func` (Callable[[float], np.ndarray]): Handles export of cymatics patterns as images and animations.
- `gradient_type` (ColorGradient): Handles export of cymatics patterns as images and animations.
- `frame_count` (int): Handles export of cymatics patterns as images and animations.
- `fps` (int): Handles export of cymatics patterns as images and animations.
- `path` (Optional[Path]): Handles export of cymatics patterns as images and animations.

**Returns**: `Optional[Path]` - Handles export of cymatics patterns as images and animations.

**Example:**
```python
# ```python
self._preset_service = CymaticsPresetService()
        self._export_service = CymaticsExportService()
        self._audio_service = CymaticsAudioService()
```
```

### result_to_numpy_rgba

```python
def result_to_numpy_rgba(self, result: SimulationResult, gradient_type: ColorGradient) -> np.ndarray:
```

**Purpose**: Convert simulation result to RGBA numpy array.

**Parameters:**
- `self` (None): Handles export of cymatics patterns as images and animations.
- `result` (SimulationResult): Handles export of cymatics patterns as images and animations.
- `gradient_type` (ColorGradient): Handles export of cymatics patterns as images and animations.

**Returns**: `np.ndarray` - Handles export of cymatics patterns as images and animations.

**Example:**
```python
# ```python
self._preset_service = CymaticsPresetService()
        self._export_service = CymaticsExportService()
        self._audio_service = CymaticsAudioService()
```
```

## Usage Examples

```python
self._preset_service = CymaticsPresetService()
        self._export_service = CymaticsExportService()
        self._audio_service = CymaticsAudioService()
```

## Error Handling

[Documentation needed: Document error types and handling strategies]

## Dependencies

```mermaid
graph LR
    CymaticsExportService --> __future__
 --> time
 --> pathlib
 --> typing
 --> numpy
```

## Performance Considerations

[Documentation needed: Add complexity analysis and optimization notes]

---

**See Also:**
- [../REFERENCE.md](../REFERENCE.md) - Pillar reference
- [Documentation needed: Add related documentation links]

**Revision History:**
- 2026-01-16: Initial auto-generated documentation
