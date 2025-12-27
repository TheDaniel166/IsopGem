#!/usr/bin/env python3
"""
The Automated Sentinel - Guardian of the Akaschic Record.

This script verifies that the REFERENCE.md files (The Soul) in each Sovereign Pillar
accurately reflect the implementation files (The Body) in the source code.
"""

import os
import re
import sys
from pathlib import Path

# --- Configuration ---
ROOT_DIR = Path("/home/burkettdaniel927/projects/isopgem")
PILLAR_DOCS_DIR = ROOT_DIR / "wiki/02_pillars"
SOURCE_DIR = ROOT_DIR / "src"

# --- Regex Patterns ---
# Matches the start of a file entry: **File:** `path/to/file.py`
FILE_ENTRY_PATTERN = re.compile(r"\*\*File:\*\* `([^`]+)`")
# Matches role: **Role:** `[Muscle]`
ROLE_PATTERN = re.compile(r"\*\*Role:\*\* `\[([^\]]+)\]`")
# Matches dependencies section and captures list items
DEP_SECTION_PATTERN = re.compile(r"\*\*Dependencies \(It Needs\):\*\*\n((?:\* .*\n?)+)", re.MULTILINE)
DEP_ITEM_PATTERN = re.compile(r"\* `([^`]+)`")

class Sentinel:
    def __init__(self):
        self.errors = []
        self.verified_count = 0

    def log_error(self, message: str):
        self.errors.append(message)
        print(f"[ERROR] {message}")

    def log_info(self, message: str):
        print(f"[INFO] {message}")

    def verify_pillar(self, pillar_name: str, ref_file: Path):
        self.log_info(f"Scanning Grimoire: {pillar_name} ({ref_file.name})")
        
        content = ref_file.read_text()
        
        # Find all file blocks
        blocks = content.split("---")
        for block in blocks:
            file_match = FILE_ENTRY_PATTERN.search(block)
            if not file_match:
                continue
            
            rel_path = file_match.group(1)
            abs_path = ROOT_DIR / rel_path
            
            if not abs_path.exists():
                self.log_error(f"Inscribed path does not exist: {rel_path} (Pillar: {pillar_name})")
                continue
            
            self.verified_count += 1
            self.verify_file_integrity(pillar_name, rel_path, abs_path, block)

    def verify_file_integrity(self, pillar, rel_path, abs_path, block_content):
        # 1. Verify Role consistency (Muscle/Bone/Skin vs directory)
        role_match = ROLE_PATTERN.search(block_content)
        if role_match:
            role = role_match.group(1).lower()
            if "service" in rel_path and role != "muscle":
                self.log_error(f"Role mismatch: {rel_path} is in services/ but role is [{role}] (Expected [Muscle])")
            elif "models" in rel_path and role != "bone":
                self.log_error(f"Role mismatch: {rel_path} is in models/ but role is [{role}] (Expected [Bone])")
            elif "ui" in rel_path and role != "skin":
                self.log_error(f"Role mismatch: {rel_path} is in ui/ but role is [{role}] (Expected [Skin])")

        # 2. Verify Dependencies (Basic presence check in code)
        dep_section = DEP_SECTION_PATTERN.search(block_content)
        if dep_section:
            deps = DEP_ITEM_PATTERN.findall(dep_section.group(1))
            if deps:
                code_content = abs_path.read_text()
                for dep in deps:
                    # Skip wildcard or generic dependencies for now
                    if "*" in dep or "Multiple" in dep:
                        continue
                    
                    # Convert dot notation to path-like fragment for searching
                    # e.g. pillars.gematria.models.CalculationRecord -> gematria.models
                    dep_fragment = dep.split('.')[-1] if '.' in dep else dep
                    
                    # Check if the dependency is mentioned in code (very loose check)
                    if dep_fragment not in code_content:
                        self.log_error(f"Stale Record: {rel_path} claims dependency on `{dep}`, but it is not found in code.")

    def run(self):
        self.log_info("Sentinel awakening...")
        
        if not PILLAR_DOCS_DIR.exists():
            print(f"Pillar docs directory not found: {PILLAR_DOCS_DIR}")
            return

        for pillar_dir in PILLAR_DOCS_DIR.iterdir():
            if pillar_dir.is_dir():
                ref_file = pillar_dir / "REFERENCE.md"
                if ref_file.exists():
                    self.verify_pillar(pillar_dir.name, ref_file)
                else:
                    self.log_info(f"Skipping {pillar_dir.name}: No REFERENCE.md found")

        self.summary()

    def summary(self):
        print("\n" + "="*40)
        print(f"Sentinel Scan Detailed Report")
        print(f"Files Verified: {self.verified_count}")
        print(f"Errors Found: {len(self.errors)}")
        print("="*40)
        
        if self.errors:
            sys.exit(1)
        else:
            print("The Temple is stable. The Soul and Body are in harmony.")
            sys.exit(0)

if __name__ == "__main__":
    Sentinel().run()
