# PyQt6 Import Reference Guide 💫

## Core Modules Overview

### 1. QtWidgets
Primary module for UI elements and widgets.

```python
from PyQt6.QtWidgets import (
    # Windows and Frames
    QMainWindow, QWidget, QDialog, QFrame,
    
    # Layouts
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    
    # Basic Widgets
    QLabel, QPushButton, QLineEdit, QTextEdit,
    
    # Container Widgets
    QTabWidget, QStackedWidget, QScrollArea,
    
    # Item Views
    QListWidget, QTreeWidget, QTableWidget,
    QListWidgetItem, QTreeWidgetItem, QTableWidgetItem,
    
    # Docking
    QDockWidget,
    
    # Menus and Toolbars
    QMenuBar, QMenu, QToolBar, QStatusBar,
    
    # Dialogs
    QFileDialog, QColorDialog, QFontDialog, QMessageBox,
    QInputDialog,
    
    # Advanced Widgets
    QComboBox, QSpinBox, QSlider, QProgressBar,
)
```

### 2. QtCore
Fundamental non-GUI functionality.

```python
from PyQt6.QtCore import (
    # Core Features
    Qt, QObject, QThread,
    
    # Signals and Slots
    pyqtSignal, pyqtSlot,
    
    # Geometry
    QPoint, QPointF, QSize, QSizeF, QRect, QRectF,
    
    # Animation
    QPropertyAnimation, QEasingCurve,
    
    # Data Management
    QSettings, QByteArray, QBuffer,
    
    # Date and Time
    QDate, QTime, QDateTime, QTimer,
    
    # Model/View
    QAbstractItemModel, QModelIndex,
)
```

### 3. QtGui
Window system integration, event handling, and painting.

```python
from PyQt6.QtGui import (
    # Painting
    QPainter, QPen, QBrush, QColor, QFont,
    QPainterPath, QGradient, QLinearGradient,
    
    # Images and Icons
    QImage, QPixmap, QIcon, QPicture,
    
    # Events
    QMouseEvent, QKeyEvent, QPaintEvent,
    
    # Window System
    QWindow, QScreen,
    
    # Text and Font
    QTextDocument, QTextCursor, QTextFormat,
    
    # Graphics Items
    QPalette, QTransform,
)
```

## Common Import Patterns

### 1. Window Creation
```python
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application")
        self.setWindowIcon(QIcon("icon.png"))
```

### 2. Panel System
```python
from PyQt6.QtWidgets import QDockWidget, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPalette, QColor

class CustomPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(200, 200))
```

### 3. Theme Management
```python
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import QObject, pyqtSignal

class ThemeManager(QObject):
    theme_changed = pyqtSignal()
```

## Special Use Cases

### 1. Graphics and Animation
```python
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView
from PyQt6.QtGui import QPainter, QPainterPath
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
```

### 2. Model/View Framework
```python
from PyQt6.QtCore import QAbstractItemModel, QModelIndex
from PyQt6.QtWidgets import QTreeView, QListView, QTableView
```

### 3. Multimedia
```python
from PyQt6.QtMultimedia import (
    QMediaPlayer, QAudioOutput,
    QMediaContent
)
```

### 4. Network Operations
```python
from PyQt6.QtNetwork import (
    QNetworkAccessManager,
    QNetworkRequest,
    QNetworkReply
)
```

## Best Practices

### 1. Import Organization
```python
# Standard library imports
import sys
import os

# Third-party imports
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Local imports
from .widgets import CustomWidget
from .utils import helpers
```

### 2. Wildcard Imports
❌ **Avoid**:
```python
from PyQt6.QtWidgets import *  # Bad practice
```

✅ **Prefer**:
```python
from PyQt6.QtWidgets import (  # Good practice
    QMainWindow,
    QWidget,
)
```

### 3. Module Aliases
```python
# For complex applications
import PyQt6.QtWidgets as QtW
import PyQt6.QtCore as QtC
import PyQt6.QtGui as QtG
```

## Future Imports

### 1. Qt6 3D
```python
from PyQt6.Qt3DCore import (
    Qt3DCore,
    QEntity,
    QTransform
)
from PyQt6.Qt3DRender import (
    Qt3DRender,
    QCamera,
    QMaterial
)
```

### 2. Qt6 Charts
```python
from PyQt6.QtCharts import (
    QChart,
    QChartView,
    QLineSeries,
    QPieSeries
)
```

### 3. Qt6 WebEngine
```python
from PyQt6.QtWebEngineWidgets import (
    QWebEngineView,
    QWebEnginePage
)
from PyQt6.QtWebEngineCore import (
    QWebEngineProfile,
    QWebEngineSettings
)
```

## Troubleshooting

### 1. Import Errors
- Check PyQt6 installation
- Verify Python version compatibility
- Ensure all required modules are installed

### 2. Version Compatibility
- Use `PyQt6>=6.4.0` for latest features
- Check release notes for breaking changes
- Test with specific versions

### 3. Module Dependencies
- Install required Qt modules separately
- Use pip for additional components
- Check system dependencies
