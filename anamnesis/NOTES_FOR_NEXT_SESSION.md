- **2025-12-31**: CORE OBJECTIVE: Implement the 'Substrate' Page-Based Editor.

The Architecture:
┌─────────────────────────────────────────────────────────────┐
│                    QGraphicsView                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              QGraphicsScene (Layer 0)                   │ │
│  │                   "The Substrate"                       │ │
│  │         (infinite canvas, dark background)              │ │
│  │                                                         │ │
│  │    ┌──────────────┐       ┌──────────────┐             │ │
│  │    │   Page 1     │       │   Page 2     │             │ │
│  │    │ QGraphics-   │       │ QGraphics-   │             │ │
│  │    │ ProxyWidget  │       │ QGraphics-   │             │ │
│  │    │              │       │              │             │ │
│  │    │ ┌──────────┐ │       │ ┌──────────┐ │             │ │
│  │    │ │ RichText │ │       │ │ RichText │ │             │ │
│  │    │ │ Editor   │ │       │ │ Editor   │ │             │ │
│  │    │ └──────────┘ │       │ └──────────┘ │             │ │
│  │    │   (white)    │       │   (white)    │             │ │
│  │    │   8.5x11"    │       │   8.5x11"    │             │ │
│  │    └──────────────┘       └──────────────┘             │ │
│  │           ↑                      ↑                      │ │
│  │      Page items floating on the infinite canvas         │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

Why:
- Layer 0: Substrate (dark infinite canvas)
- Layer 1: Page Widgets (QGraphicsProxyWidget wrapping RichTextEditor)
- Layer 2: Shape Overlay
- Features: Zoom, Infinite Scroll, Shadows.
