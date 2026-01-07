from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QFont
from PyQt6.QtCore import Qt, QSize, QPointF

class TrigramGlyph(QWidget):
    """
    Renders a Trigram as a geometric path based on the 'Quality vs Line' coordinate system.
    
    Coordinate System:
    Rows (Y-axis): Represents the Line Index (Power of 3).
      - Top:    Line 1 (3^0 = 1)
      - Middle: Line 2 (3^1 = 3)
      - Bottom: Line 3 (3^2 = 9)
      
    Columns (X-axis): Represents the Line Quality (Trit Value).
      - Left:   Quality 2 (Yin/Dark)
      - Center: Quality 0 (Neutral/Void)
      - Right:  Quality 1 (Yang/Light)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.setMinimumSize(200, 300)
        self.setStyleSheet("background-color: transparent;")
        
    def set_value(self, decimal_value: int):
        self.value = decimal_value
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Grid Dimensions
        row_h = h / 3
        
        # Calculate centers for the 3 columns
        # Left (2), Center (0), Right (1)
        x_left = w * 0.2
        x_center = w * 0.5
        x_right = w * 0.8
        
        # Calculate centers for 3 rows
        y_top = row_h * 0.5
        y_mid = row_h * 1.5
        y_bot = row_h * 2.5
        
        # Map: Trit Value -> X Coordinate
        # 0 -> Center, 1 -> Right, 2 -> Left
        x_map = {
            0: x_center,
            1: x_right,
            2: x_left
        }
        
        # Map: Line Index -> Y Coordinate
        # Top is LSB (3^0), Bot is MSB (3^2) based on user diagram
        y_map = [y_top, y_mid, y_bot]
        
        # Decode value to trits
        trits = []
        temp_val = self.value
        for _ in range(3):
            trits.append(temp_val % 3)
            temp_val //= 3
            
        # -----------------------------
        # Draw The Grid (Faintly)
        # -----------------------------
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1, Qt.PenStyle.DotLine))
        # Draw vertical guidelines
        painter.drawLine(int(x_left), 0, int(x_left), h)
        painter.drawLine(int(x_center), 0, int(x_center), h)
        painter.drawLine(int(x_right), 0, int(x_right), h)
        
        # Draw horizontal guidelines
        painter.drawLine(0, int(y_top), w, int(y_top))
        painter.drawLine(0, int(y_mid), w, int(y_mid))
        painter.drawLine(0, int(y_bot), w, int(y_bot))
        
        # -----------------------------
        # Draw The Glyph Path
        # -----------------------------
        points = []
        for i, trit in enumerate(trits):
            px = x_map[trit]
            py = y_map[i]
            points.append(QPointF(px, py))
            
        # Path Pen (Gold)
        path_pen = QPen(QColor("#D4AF37"), 6)
        path_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        path_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(path_pen)
        
        # Draw lines
        if len(points) > 1:
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i+1])
                
        # -----------------------------
        # Draw The Nodes (Joints)
        # -----------------------------
        # Map trits to logical columns: Left (Val 2), Center (Val 0), Right (Val 1)
        
        col_map = {2: 0, 0: 1, 1: 2} # Logic: Left=0, Center=1, Right=2
        cols = [col_map[t] for t in trits]
        
        dots_to_draw = []
        span_width = max(cols) - min(cols) + 1
        
        if span_width == 1:
            # Vertical Rods (000, 111, 222) - Configured based on user screenshots
            line_col_val = trits[0] 
            y_grid_top = h / 3.0
            y_grid_bot = (h / 3.0) * 2.0
            
            if line_col_val == 0: # Center Line (000)
                # Flanking dots
                x_grid_left = (x_left + x_center) / 2.0
                x_grid_right = (x_right + x_center) / 2.0
                dots_to_draw = [QPointF(x_grid_left, h/2.0), QPointF(x_grid_right, h/2.0)]
                
            elif line_col_val == 1: # Right Line (111)
                 x_grid_right = (x_right + x_center) / 2.0
                 dots_to_draw = [QPointF(x_grid_right, y_grid_top), QPointF(x_grid_right, y_grid_bot)]
                 
            elif line_col_val == 2: # Left Line (222)
                 x_grid_left = (x_left + x_center) / 2.0
                 dots_to_draw = [QPointF(x_grid_left, y_grid_top), QPointF(x_grid_left, y_grid_bot)]
                 
        else:
            # Multi-column shapes
            # Logic: 
            # Sharp Elbow (Acute angle) -> Dot at CELL CENTER
            # Relaxed Elbow (Obtuse/Wide angle) -> Dot at GRID INTERSECTION
            
            # Helper to check if a vertex is an "Elbow" (Middle point)
            # Or an anchor (Start/End points)
            
            # For this simple implementation, we look at the deviation
            # A shape like < (sharp) vs a shape like / (straightish)
            
            # Since these are 3-point lines, point[1] is always the elbow.
            # Points[0] and [2] are anchors.
            
            # Anchor Logic (Always Cell Centers for now, pending instruction)
            dots_to_draw.append(points[0])
            dots_to_draw.append(points[2])
            
            # Elbow Logic (Middle Point)
            # Calculate angle or span?
            # Sharp Elbow usually means changing direction back towards origin (e.g. Left -> Right -> Left)
            # Relaxed means continuing or slight deviation.
            
            # Simple heuristic based on column distance:
            # If |Col1 - Col2| == 1 (Adjacent) -> "Sharp" enough?
            # Let's use the 'relaxed = intersection, sharp = center' rule literally.
            
            # Actually, looking at the spreadsheet (e.g., 'F' or 'S'):
            # These are wide spans.
            # Let's iterate through the points and decide placement based on local geometry.
            
            # For now, let's keep the anchors at component centers (points[0], points[2])
            # And modulate only the middle dot if it exists/is needed.
            
            # Wait, the prompt implies "placement OF THE DOTS".
            # The previous logic had: Span 2 -> Middle Dot only. Span 3 -> End Dots only.
            
            # Let's stick to the visual evidence:
            # J (161, 1-0-1): Top-Right, Mid-Center, Bot-Right. Wide V.
            # S (237, 2-0-2?? No 237 is likely decimal. 237 = 22210 = excess range.
            # Let's look at the images provided earlier (e.g. the ones with 'X', 'J', 'W').
            # J (161?? Wait, 161 is way out of range 0-26).
            # The user's "0-26" constraint suggests alphabet mapping.
            # Let's assume the user wants the LOGIC applied, not the specific values from the old spreadsheet.
            
            # Rule:
            # Sharp Elbow (change direction > 90 deg?) -> Cell Center
            # Relaxed Elbow (change direction < 90 deg?) -> Grid Intersection
            
            # Let's just modify the coordinate of the dot itself.
            # Identify the elbow (index 1).
            t1, t2, t3 = trits
            c1, c2, c3 = cols[0], cols[1], cols[2]
            
            # Is it a sharp turn?
            is_sharp = False
            if (c1 < c2 and c3 < c2) or (c1 > c2 and c3 > c2):
                is_sharp = True # Reverses direction (V-shape or ^-shape)
            
            # Determine geometry type
            # Sharp Elbow: Double-back or V-shape
            # Relaxed: Transition/Staircase
            
            # Helper to get x-coord for a column index (0=Left, 1=Center, 2=Right in Logic)
            # Logic Map: Left=0, Center=1, Right=2 (cols array)
            # Physical Map: x_map[2]=Left, x_map[0]=Center, x_map[1]=Right
            
            def get_x(col_idx):
                # map logic col (0,1,2) to physical x
                if col_idx == 0: return x_left
                if col_idx == 1: return x_center
                return x_right
            
            if span_width == 2:
                 # Span 2 (e.g. 0-1-0 or 0-1-1)
                 # Find the 'void' centroid
                 
                 # Logic: Place dot "inside" the V
                 # Avg of Start and End cols gives the "Base" x
                 avg_base_col = (cols[0] + cols[2]) / 2.0
                 x_base = (get_x(cols[0]) + get_x(cols[2])) / 2.0
                 
                 if is_sharp:
                     # Sharp (e.g. 0-1-0) -> Cols 1, 2, 1 (Center-Right-Center)
                     # Base is Center (1). Apex is Right (2).
                     # Dot goes at Base X, Middle Y
                     dots_to_draw = [QPointF(x_base, y_mid)]
                 else:
                     # Relaxed (0-1-1? Span 2 relaxed?)
                     # e.g. 0-1-1 (Left-Center-Center)
                     # This creates a slight kink.
                     # Avg base is (0+1)/2 = 0.5 (Intersection)
                     # Place at Intersection X, Middle Y
                     # Intersect is between Left(0) and Center(1)
                     
                     x_int = (get_x(cols[0]) + get_x(cols[2])) / 2.0 
                     # Wait, if cols[2] is same as cols[1], the base is skewed.
                     # Let's trust the "Inside" rule for Span 2.
                     
                     # If not sharp, it's "blocky".
                     # Use the intersection "inside" the turn.
                     # For 0-1-1: Turn is at 1. Start is 0.
                     # Inner corner is (1, ?)
                     
                     # Let's use the explicit Intersection rule for Relaxed
                     # Midpoint of cols[0] and cols[2] IS the intersection x-coord
                     dots_to_draw = [QPointF(x_base, y_mid)]

            elif span_width == 3:
                 # Span 3 (e.g. 2-0-1) -> Left-Center-Right
                 # Relaxed/Wide
                 # User image shows dots "under" the structure or flanking?
                 # Bottom Right Image: Looks like dots at (Left, Mid) and (Center, Mid)?
                 # The line is high?
                 
                 # If the line is generally "Top-Left to Bot-Right" (\)
                 # The dots are in the bottom-left void?
                 # If "Bot-Left to Top-Right" (/)
                 # The dots are in the bottom-right void?
                 
                 # Logic: Place dots in the cells NOT occupied by the line at Y-Mid?
                 # Line at index 1 is at cols[1].
                 # If line is at Center, dots at Left and Right?
                 # But line is at Center.
                 
                 if is_sharp:
                     # 2-1-2 -> V shape wide.
                     # Base is Left. Apex is Right.
                     # Dot at Base (Left, Mid).
                     dots_to_draw = [QPointF(get_x(cols[0]), y_mid)] 
                     # Wait, 2-1-2 implies symmetry. Maybe 2 dots?
                     # (Left, Top) -> (Right, Mid) -> (Left, Bot)
                     # This is symmetric. One dot at (Left, Mid) works perfectly.
                     # Or two dots? User said "2 dots for all 3 columns".
                     
                     # Let's try: Two dots.
                     # One at x = (Col0 + Col1)/2 (Intersection 1)
                     # One at x = (Col1 + Col2)/2 (Intersection 2)
                     # If Sharp, maybe use Cell Centers?
                     # Left and Left?
                     
                     dots_to_draw = [
                         QPointF(get_x(cols[0]), y_mid),
                         QPointF(get_x(cols[2]), y_mid)
                     ]
                     # If they are same column (2-1-2), this places 2 dots at same spot.
                     # Set reduces to 1 dot. Correct.
                     
                 else:
                     # Relaxed (2-0-1). Left-Center-Right.
                     # Line is diagonal ish.
                     # Dots at Intersections.
                     # Int 1: Left-Center boundary.
                     # Int 2: Center-Right boundary.
                     
                     x_int_1 = (x_left + x_center) / 2.0
                     x_int_2 = (x_right + x_center) / 2.0
                     
                     dots_to_draw = [
                         QPointF(x_int_1, y_mid),
                         QPointF(x_int_2, y_mid)
                     ]

             
        # Draw
        painter.setPen(Qt.PenStyle.NoPen)
        # Use a darker, more golden/ochre color to match the spreadsheet reference
        node_brush = QBrush(QColor("#C59105")) 
        painter.setBrush(node_brush)
        
        # Increase radius slightly to match the bold look
        node_radius = 10 
        for pt in dots_to_draw:
            painter.drawEllipse(pt, node_radius, node_radius)
            
        # -----------------------------
        # Draw Labels (Optional/Debug)
        # -----------------------------
        # Uncomment to verify grid logic
        # painter.setPen(QPen(QColor("white")))
        # painter.drawText(QPointF(x_left, 15), "2")
        # painter.drawText(QPointF(x_center, 15), "0")
        # painter.drawText(QPointF(x_right, 15), "1")

        
