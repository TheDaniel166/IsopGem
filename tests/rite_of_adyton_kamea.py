import sys
import os
import unittest

# Add project root/src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.append(os.path.join(project_root, "src"))

from pillars.adyton.services.kamea_loader_service import KameaLoaderService

class RiteOfAdytonKamea(unittest.TestCase):
    
    def setUp(self):
        self.loader = KameaLoaderService(project_root)
        self.grid = self.loader.load_grid()

    def test_grid_size(self):
        # 27x27 = 729 cells
        # CSV has rows 13 to -13 (27 rows)
        # Cols -13 to 13 (27 cols)
        # However, grid might filter empty cells
        self.assertEqual(len(self.grid), 729, "Grid should have 729 cells")

    def test_singularity(self):
        # Center should be 000000
        center = self.grid.get((0,0))
        self.assertIsNotNone(center)
        self.assertEqual(center.ditrune, "000000")
        self.assertEqual(center.octant_id, 0)
        self.assertEqual(center.tablet_id, "Spirit")

    def test_octant_logic(self):
        # Test Octant 1: x=2, y=1 (East-North, lower part of upper right)
        # Wait, my logic was: x>0, y>0. if x>y return 1 else 2.
        # So (2,1): x>y -> 1.
        c1 = self.grid.get((2, 1))
        self.assertEqual(c1.octant_id, 1)
        self.assertEqual(c1.tablet_id, "Air")
        
        # Test Octant 5: x=-2, y=-1.
        # x<0, y<0. if abs(x) > abs(y) -> 5 else 6.
        # |-2| > |-1| -> 2 > 1 -> 5.
        c5 = self.grid.get((-2, -1))
        self.assertEqual(c5.octant_id, 5)
        self.assertEqual(c5.tablet_id, "Air") # 1+5 fused

    def test_tablet_size(self):
        # Count cells in Air Tablet (Octants 1 + 5)
        air_cells = [c for c in self.grid.values() if c.tablet_id == "Air"]
        # radius 13.
        # Triangle count per octant: n(n+1)/2 ?
        # No, let's just count.
        # Should be exactly 78 per octant?
        # 78 * 8 = 624. 
        # 729 total. 105 others (Axes).
        
        # Let's verify if our logic yields 78 per octant.
        # Octant 1: 0 < y < x <= 13.
        # For x=1, y ranges empty.
        # For x=2, y=1 (1 cell).
        # For x=3, y=1,2 (2 cells).
        # ...
        # For x=13, y=1..12 (12 cells).
        # Sum 1 to 12 = 12*13/2 = 78.
        # Correct!
        octant_1_count = len([c for c in self.grid.values() if c.octant_id == 1])
        self.assertEqual(octant_1_count, 78, "Octant 1 should have 78 cells")
        
        air_count = len(air_cells)
        self.assertEqual(air_count, 156, "Air Tablet should have 156 cells (78+78)")

if __name__ == '__main__':
    unittest.main()
