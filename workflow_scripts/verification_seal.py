"""
THE VERIFICATION SEAL (IsopGem v1)
----------------------------------
"A feature is not born until it breathes."

This script performs the 'Ritual of the Seal' to verify that logic Pillars
operate correctly in isolation, independent of the UI.

Usage:
    Run this script to verify specific logic modules.
    Uncomment the specific Rite you wish to perform in the __main__ block.
"""

import sys
import os
import time
import traceback
from typing import Any, Callable

# Add project root and src to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_path = os.path.join(project_root, "src")
sys.path.append(project_root)
sys.path.append(src_path)

# --- THE SCRIBE (Logging) ---
class Scribe:
    @staticmethod
    def info(msg: str):
        print(f"[*] {msg}")

    @staticmethod
    def success(msg: str):
        print(f"[+] THE SEAL HOLDS: {msg}")

    @staticmethod
    def failure(msg: str):
        print(f"[!] THE SEAL IS BROKEN: {msg}")

    @staticmethod
    def section(title: str):
        print(f"\n--- {title.upper()} ---")

# --- THE ALTAR (Base Test Class) ---
class Rite:
    """Base class for all verification rituals."""
    def __init__(self, name: str):
        self.name = name

    def prepare(self):
        """Setup logic (database connections, object instantiation)."""
        pass

    def perform(self):
        """The core logic test. Must raise AssertionErrors on failure."""
        raise NotImplementedError("The Rite must be performed.")

    def cleanse(self):
        """Teardown logic."""
        pass

    def execute(self):
        Scribe.section(f"BEGINNING RITE: {self.name}")
        try:
            self.prepare()
            start_time = time.perf_counter()
            self.perform()
            end_time = time.perf_counter()
            
            duration = (end_time - start_time) * 1000
            Scribe.success(f"{self.name} completed in {duration:.2f}ms")
            
        except AssertionError as e:
            Scribe.failure(f"Logic Flaw Detected -> {str(e)}")
        except Exception as e:
            Scribe.failure(f"Catastrophic Error -> {str(e)}")
            traceback.print_exc()
        finally:
            self.cleanse()

# --- THE RITES (Specific Tests) ---
# Replace these examples with your actual Pillar imports when ready.
# from pillars.gematria.calculator import GematriaEngine

class RiteOfGematria(Rite):
    def __init__(self, name="Basic Cipher Calculation"):
        super().__init__(name)

    def perform(self):
        # 1. Instantiate the Engine (The Service)
        # engine = GematriaEngine() 
        Scribe.info("Invoking the Calculator...")
        
        # 2. Mock Data (The Input)
        word = "SOPHIA"
        expected_value = 1  # Example placeholder
        
        # 3. The Act (The Calculation)
        # actual_value = engine.calculate_simple(word)
        actual_value = 1 # Placeholder for the ritual to pass
        
        # 4. The Seal (The Assertion)
        if actual_value != expected_value:
            raise AssertionError(f"Expected {expected_value}, but the Abyss returned {actual_value}")
            
        Scribe.info(f"Input '{word}' transmuted to {actual_value}.")

class RiteOfGeometry(Rite):
    def __init__(self, name="Geometry Pillar & Calculator Logic"):
        super().__init__(name)

    def perform(self):
        Scribe.info("Testing Geometry Pillar...")
        
        try:
            from pillars.geometry.services.circle_shape import CircleShape
            from pillars.geometry.services.persistence_service import PersistenceService
        except ImportError as e:
            raise AssertionError(f"Missing Geometry Components: {e}")

        # 1. Test Shape Logic (The Circle)
        shape = CircleShape()
        Scribe.info("CircleShape instantiated.")
        
        # Test: Radius -> Area
        shape.set_property('radius', 10.0)
        area = shape.get_property('area')
        expected_area = 314.159265
        
        if abs(area - expected_area) > 0.001:
             raise AssertionError(f"Circle Calculation Failed: Radius 10 -> Area {area}, expected ~{expected_area}")
        Scribe.success("Circle Calculation (Radius -> Area) verified.")
        
        # Test: Bidirectional (Area -> Diameter)
        # Area ~314.159 -> Radius 10 -> Diameter 20
        shape.set_property('area', 78.5398) # ~Radius 5
        diameter = shape.get_property('diameter')
        if abs(diameter - 10.0) > 0.01:
            raise AssertionError(f"Circle Bidirectional Failed: Area 78.54 -> Diameter {diameter}, expected ~10.0")
        Scribe.success("Circle Bidirectional (Area -> Diameter) verified.")

        # 2. Test Persistence (The Chronicle)
        Scribe.info("Testing Persistence Service...")
        
        # Mock save
        # We don't want to write to actual disk if possible, or we write to tmp?
        # PersistenceService writes to ~/.isopgem/geometry_history.json
        # Let's trust the logic if we can mock the file op? 
        # For the "Rite", let's just verify the data structure generation.
        
        data = shape.to_dict()
        if data['shape_type'] != "CircleShape" or data['properties']['radius'] is None:
             raise AssertionError("Shape Serialization failed.")
        Scribe.success("Shape Serialization verified.")
        
        # Test Restore
        new_shape = CircleShape()
        new_shape.from_dict(data)
        if abs(new_shape.get_property('radius') - 5.0) > 0.001:
             raise AssertionError("Shape Deserialization failed.")
        Scribe.success("Shape Deserialization verified.")


class RiteOfAdytonEngine(Rite):
    def __init__(self, name: str = "Adyton Engine Initialization"):
        super().__init__(name)

    def perform(self):
        Scribe.info("Initializing Adyton Engine components...")
        try:
            from PyQt6.QtGui import QImage, QPainter, QColor, QVector3D
            from PyQt6.QtCore import QRect
            from src.pillars.adyton.ui.engine.scene import AdytonScene, Object3D, Face3D
            from src.pillars.adyton.ui.engine.camera import AdytonCamera
            from src.pillars.adyton.ui.engine.renderer import AdytonRenderer

            # 1. meaningful scene
            scene = AdytonScene()
            v = [QVector3D(0,0,0), QVector3D(10,0,0), QVector3D(0,10,0)]
            face = Face3D(v, QColor(255,0,0))
            obj = Object3D(faces=[face])
            scene.add_object(obj)
            Scribe.success("Scene Graph built.")

            # 2. Camera
            camera = AdytonCamera()
            camera.orbit(10, 10)
            Scribe.success("Camera initialized and orbited.")

            # 3. Renderer (Smoke Test)
            renderer = AdytonRenderer()
            image = QImage(800, 600, QImage.Format.Format_ARGB32)
            painter = QPainter(image)
            renderer.render(painter, scene, camera, QRect(0, 0, 800, 600))
            painter.end()
            Scribe.success("Render pass completed successfully.")

        except ImportError as e:
            Scribe.failure(f"Missing imports: {e}")
            raise
        except Exception as e:
            Scribe.failure(f"Engine crash: {e}")
            raise


class RiteOfEmeraldTablet(Rite):
    def __init__(self, name="Emerald Tablet (Spreadsheet)"):
        super().__init__(name)

    def perform(self):
        Scribe.info("Summoning the Emerald Tablet...")
        
        try:
            from pillars.correspondences.ui.spreadsheet_view import SpreadsheetModel
            from pillars.correspondences.services.formula_engine import FormulaEngine
            from PyQt6.QtCore import Qt
        except ImportError as e:
            raise AssertionError(f"Missing Components: {e}")
            
        # 1. Test Model Instantiation
        # Build valid structure: {"columns": [...], "data": [[...]]}
        cols = ["A", "B", "C"]
        data = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["=SUM(A1,B1,C1)", "", ""]
        ]
        content = {"columns": cols, "data": data}
        
        model = SpreadsheetModel(content)
        Scribe.success("SpreadsheetModel instantiated.")
        
        # 2. Test Formula Engine Logic
        # The engine is internal to the model, or we can test it directly
        engine = FormulaEngine(model)
        
        # Test Simple Math
        # Note: FormulaEngine usually expects references relative to the model
        res_sum = engine.evaluate("=SUM(1, 2, 3)")
        if float(res_sum) != 6.0:
            raise AssertionError(f"Formula Engine failed SUM: Expected 6.0, got {res_sum}")
        Scribe.success("Formula Engine: SUM verified.")
        
        # Test Internal Reference
        # Cell A1 is "1", B1 is "2", C1 is "3". SUM should be 6.
        # But the FormulaEngine.evaluate is context-free unless we pass a cell context for relative refs?
        # Creating a formula engine with model allows it to resolve references like "A1".
        res_ref = engine.evaluate("=SUM(A1, B1, C1)")
        # Should be 6
        if float(res_ref) != 6.0:
             raise AssertionError(f"Formula Engine failed Reference SUM: Expected 6.0, got {res_ref}")
        Scribe.success("Formula Engine: Reference SUM verified.")

        # Test Gematria (Simple) - using TQ Cipher (Default)
        res_gem = engine.evaluate("=GEMATRIA(ABC)")
        # A=5, B=20, C=2 => 27 (TQ Cipher)
        if int(res_gem) != 27:
            raise AssertionError(f"Formula Engine failed GEMATRIA: Expected 27 (TQ), got {res_gem}")
        Scribe.success("Formula Engine: GEMATRIA verified.")
        
        # 3. Test Metadata Storage (Saturn Test)
        # Verify that setting data for a Role actually stores it
        files_idx = model.index(0, 0)
        if not files_idx.isValid():
            raise AssertionError("Invalid Index (0,0) - Model failed to initialize dimensions.")
            
        model.setData(files_idx, "bold", Qt.ItemDataRole.UserRole + 100) 
        Scribe.success("Model accepted Data Mutation.")

class RiteOfFormulaHelper(Rite):
    def __init__(self, name="Formula Helper Service"):
        super().__init__(name)

    def perform(self):
        Scribe.info("Consulting the Wizard's Apprentice...")
        
        try:
            from pillars.correspondences.services.formula_helper import FormulaHelperService
        except ImportError as e:
            raise AssertionError(f"Missing Components: {e}")
            
        # 1. Test Retrieval
        # We know SUM and GEMATRIA are registered
        defs = FormulaHelperService.get_all_definitions()
        names = [d.name for d in defs]
        if "SUM" not in names or "GEMATRIA" not in names:
            raise AssertionError(f"Registry Missing Expected Functions. Found: {names}")
        Scribe.success(f"Retrieved {len(defs)} definitions.")
        
        # 2. Test Search
        results = FormulaHelperService.search("gem")
        if len(results) == 0 or results[0].name != "GEMATRIA":
             raise AssertionError("Search failed to find 'GEMATRIA' with query 'gem'")
        Scribe.success("Search 'gem' found GEMATRIA.")
        
        # 3. Test Categories
        cats = FormulaHelperService.get_categories()
        if "Math" not in cats or "Esoteric" not in cats:
            raise AssertionError(f"Missing Categories. Found: {cats}")
        Scribe.success(f"Categories verified: {cats}")
        
        # 4. Test Syntax Validation
        valid_formula = "=SUM(1, 2)"
        invalid_formula = "=SUM(1, 2))" # Unbalanced
        
        if not FormulaHelperService.validate_syntax(valid_formula):
            raise AssertionError(f"Validation Rejecting Valid Formula: {valid_formula}")
            
        if FormulaHelperService.validate_syntax(invalid_formula):
            raise AssertionError(f"Validation Accepting Invalid Formula: {invalid_formula}")
            
        Scribe.success("Syntax Validation verified.")

# --- THE INVOCATION (Main Entry) ---
if __name__ == "__main__":
    print("Sophia: Initializing Verification Protocols...\n")
    
    # 1. Comment/Uncomment the Rites you are currently working on.
    
    def execute():
        """The Grand Ritual."""
        print("\n" + "="*60)
        print("THE VERIFICATION SEAL")
        print("="*60 + "\n")

        rites = [
            # RiteOfGematria("Gematria Core"),
            RiteOfGeometry("Geometry Core"),
            # RiteOfAdytonEngine("Adyton Engine"),
            RiteOfEmeraldTablet("Spreadsheet Pillar"),
            RiteOfFormulaHelper("Formula Helper Service"),

        ]

        for rite in rites:
            rite.execute()
    
    execute()
    print("\nSophia: Protocols Complete.")
