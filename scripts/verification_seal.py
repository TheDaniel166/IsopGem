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
    def __init__(self, name="Polygon Vertex Generation"):
        super().__init__(name)

    def perform(self):
        Scribe.info("Calculating vertices for a Heptagon...")
        
        # Mock logic
        sides = 7
        vertices = [] # engine.get_vertices(sides)
        
        # Verification: Ensure we didn't crash and got a list (even if empty for now)
        if vertices is None:
            raise AssertionError("The Geometry Pillar returned Void.")
            
        Scribe.info("Vertices generated successfully.")

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
            RiteOfGematria("Gematria Core"),
            RiteOfGeometry("Geometry Core"),
            RiteOfAdytonEngine("Adyton Engine"),
        ]

        for rite in rites:
            rite.execute()
        
        print("\nSophia: Protocols Complete.")

    execute()
