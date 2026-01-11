from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass
class Finding:
    pillar: str
    file: str
    severity: str
    message: str
    hint: Optional[str] = None
    line: Optional[int] = None
    context: Optional[str] = None  # The actual line content for context

    def to_dict(self) -> Dict[str, object]:
        payload = asdict(self)
        return {k: v for k, v in payload.items() if v is not None}


def load_config(config_path: Path) -> Dict[str, object]:
    if config_path.exists():
        try:
            return json.loads(config_path.read_text())
        except json.JSONDecodeError:
            print(f"Failed to parse config at {config_path}, using defaults.", file=sys.stderr)
    # Minimal defaults keep the rite usable without config.
    return {
        "allowed_hosts": ["localhost", "127.0.0.1"],
        "ui_liturgy_tokens": ["shared.ui.theme", "ThemeTokens", "apply_visual_liturgy"],
        "config_modules": ["config", "config.config"],
        "pillar_root": "src/pillars",
        "signal_modules": ["shared.navigation_bus", "shared.signal_bus"],
        "ui_contamination_blocklist": ["sqlalchemy", "pandas", "requests", "urllib", "lxml", "bs4", "httpx"],
        "security_secret_keywords": ["API_KEY", "SECRET", "TOKEN"],
        "boundary_markers": ["api", "controller", "handler", "endpoint", "cli", "ui"],
    }


def iter_python_files(paths: List[Path]) -> Iterable[Path]:
    excluded = {".venv", "data", "docs", "wiki", "__pycache__"}
    for base in paths:
        if base.is_file() and base.suffix == ".py":
            yield base
            continue
        for path in base.rglob("*.py"):
            if any(part in excluded for part in path.parts):
                continue
            yield path


def read_lines(path: Path) -> List[str]:
    try:
        return path.read_text().splitlines()
    except Exception:
        return []


def extract_blessed_colors(repo_root: Path) -> set:
    """Extract all blessed hex colors from shared/ui/theme.py.
    
    Includes both:
    - Colors defined in the COLORS dictionary
    - Colors used in QSS stylesheets (gradients, etc.)
    """
    theme_path = repo_root / "src" / "shared" / "ui" / "theme.py"
    if not theme_path.exists():
        return set()
    
    blessed = set()
    content = theme_path.read_text()
    
    # Extract ALL hex colors from theme.py (3-8 digits)
    for match in re.findall(r"#[0-9a-fA-F]{3,8}\b", content):
        blessed.add(match.lower())
    
    return blessed


def detect_cross_pillar_imports(path: Path, content: str, pillar_root: str) -> Optional[Finding]:
    if pillar_root not in str(path):
        return None
    parts = path.parts
    try:
        idx = parts.index(Path(pillar_root).name)
        current = parts[idx + 1]
    except (ValueError, IndexError):
        return None
    matches = re.findall(r"from\s+pillars\.([a-zA-Z0-9_]+)", content)
    matches += re.findall(r"import\s+pillars\.([a-zA-Z0-9_]+)", content)
    for target in matches:
        if target != current:
            return Finding(
                pillar="Signal Bus",
                file=str(path.relative_to(Path.cwd())),
                severity="high",
                message=f"Direct import from pillar '{target}' inside pillar '{current}'.",
                hint="Use the signal bus or shared substrate instead of cross-pillar imports.",
            )
    return None


def detect_ui_contamination(path: Path, lines: List[str], blocklist: List[str], blessed_colors: set) -> List[Finding]:
    if "/ui/" not in str(path).replace("\\", "/"):
        return []
    findings: List[Finding] = []
    content = "\n".join(lines)
    
    # Check for Exemption Tag
    if "@RiteExempt: Visual Liturgy" in content:
        return []
    
    # Check if file imports from theme module
    has_theme_import = bool(re.search(r"from\s+.*shared\.ui\.theme\s+import|import\s+.*shared\.ui\.theme", content))
    
    # Check for forbidden library imports/references
    for i, line in enumerate(lines, start=1):
        for lib in blocklist:
            if re.search(rf"\b{re.escape(lib)}\b", line):
                findings.append(
                    Finding(
                        pillar="Visual Liturgy",
                        file=str(path.relative_to(Path.cwd())),
                        line=i,
                        severity="high",
                        message=f"UI file imports or references '{lib}'.",
                        hint="Move heavy IO/DB logic to services; keep UI pure.",
                        context=line.strip()[:80]
                    )
                )
        
        # Detect hard-coded hex colors (3, 4, 6, or 8 digits)
        # Skip HTML inline styles - they're content formatting, not UI chrome
        hex_pattern = r"#[0-9a-fA-F]{3,8}\b"
        for match in re.finditer(hex_pattern, line):
            color = match.group().lower()
            
            # Skip if it's a blessed color from theme.py
            if color in blessed_colors:
                continue
            
            # Skip if line contains COLORS reference (f-string template)
            if "COLORS[" in line or "{COLORS" in line:
                continue
            
            # Skip if it's HTML inline style (content formatting, not UI chrome)
            # Examples: <div style='color: #xxx'>, <span style='background: #xxx'>
            if re.search(r"<\w+\s+style\s*=\s*['\"].*" + re.escape(color), line, re.IGNORECASE):
                continue
            # Also skip HTML in triple-quoted strings (dialog content)
            if "'''" in line or '"""' in line:
                # Check if this appears to be HTML content
                if any(tag in line.lower() for tag in ['<div', '<span', '<h1', '<h2', '<h3', '<p>']):
                    continue
            
            # Flag the violation
            severity = "medium" if has_theme_import else "high"
            hint = (
                "Use COLORS dict from shared.ui.theme instead of hard-coded hex colors."
                if has_theme_import
                else "Import theme and use COLORS dict instead of hard-coded hex colors."
            )
            
            findings.append(
                Finding(
                    pillar="Visual Liturgy",
                    file=str(path.relative_to(Path.cwd())),
                    line=i,
                    severity=severity,
                    message=f"Hard-coded color '{color}' not in Visual Liturgy theme.",
                    hint=hint,
                    context=line.strip()[:80]
                )
            )
    
    # If no theme import found and file has UI widgets, warn about it
    if not has_theme_import and any(widget in content for widget in ["QWidget", "QMainWindow", "QDialog"]):
        findings.append(
            Finding(
                pillar="Visual Liturgy",
                file=str(path.relative_to(Path.cwd())),
                severity="low",
                message="UI file lacks theme import.",
                hint="Import and use shared.ui.theme for consistent Visual Liturgy adherence."
            )
        )
    
    return findings


def detect_error_handling(lines: List[str], path: Path) -> List[Finding]:
    findings: List[Finding] = []
    is_ui = "/ui/" in str(path).replace("\\", "/")
    
    for i, line in enumerate(lines, start=1):
        if re.search(r"except\s*:|except\s+Exception", line):
            # UI defensive error handling is lower priority than service-layer errors
            severity = "low" if is_ui else "medium"
            findings.append(
                Finding(
                    pillar="Error Handling",
                    file=str(path.relative_to(Path.cwd())),
                    line=i,
                    severity=severity,
                    message="Broad exception handler detected.",
                    hint="Catch specific exceptions and log via pillar errors module.",
                    context=line.strip()[:80]
                )
            )
        if "print(" in line and "Exception" in line:
            findings.append(
                Finding(
                    pillar="Error Handling",
                    file=str(path.relative_to(Path.cwd())),
                    line=i,
                    severity="low",
                    message="Printing exceptions instead of logging.",
                    hint="Route errors through structured logging.",
                    context=line.strip()[:80]
                )
            )
    return findings


def detect_config_leaks(lines: List[str], path: Path, config_modules: List[str]) -> List[Finding]:
    # Whitelist config.py, paths.py, and main.py (bootstrapping)
    if path.name in ("config.py", "paths.py", "main.py"):
        return []
    
    findings: List[Finding] = []
    
    # Map of forbidden path patterns to their centralized alternatives
    forbidden_paths = {
        '"databases"': 'config.paths.databases',
        '"isopgem.db"': 'config.paths.main_db',
        '"lexicons"': 'config.paths.lexicons',
        '"etymology_db"': 'config.paths.etymology_db',
        '"ephemeris"': 'config.paths.ephemeris',
        '"correspondences"': 'config.paths.correspondences',
        '"geometry"': 'config.paths.geometry',
    }
    
    for i, line in enumerate(lines, start=1):
        # 1. Detect direct environment variable access
        if "os.environ" in line or "environ.get" in line:
            findings.append(
                Finding(
                    pillar="Config",
                    file=str(path.relative_to(Path.cwd())),
                    line=i,
                    severity="medium",
                    message="Direct environment access detected outside config module.",
                    hint="Centralize configuration reads in config.py and inject via get_config().",
                    context=line.strip()[:80]
                )
            )
        
        # 2. Detect hardcoded absolute paths (Linux/Unix style)
        if re.search(r'Path\(["\']/(usr|home|opt|var|etc)/', line):
            findings.append(
                Finding(
                    pillar="Config",
                    file=str(path.relative_to(Path.cwd())),
                    line=i,
                    severity="high",
                    message="Hardcoded absolute path detected.",
                    hint="Use config.paths.* for deployment-flexible paths.",
                    context=line.strip()[:80]
                )
            )
        
        # 3. Detect forbidden path construction patterns
        # Pattern: variable / "databases" or get_data_path() / "databases"
        for pattern, suggestion in forbidden_paths.items():
            # Match both direct and variable-based construction
            if f'/ {pattern}' in line:
                # Check if this is a known forbidden pattern
                findings.append(
                    Finding(
                        pillar="Config",
                        file=str(path.relative_to(Path.cwd())),
                        line=i,
                        severity="medium",
                        message=f"Repeated path construction detected: {pattern}",
                        hint=f"Use {suggestion} instead of manual construction.",
                        context=line.strip()[:80]
                    )
                )
                break  # Only report once per line
    
    return findings


def detect_async_issues(lines: List[str], path: Path) -> List[Finding]:
    findings: List[Finding] = []
    is_ui = "/ui/" in str(path).replace("\\", "/")
    for i, line in enumerate(lines, start=1):
        if re.search(r"requests\.(get|post|put|delete|patch)\(", line) and "timeout=" not in line:
            findings.append(
                Finding(
                    pillar="Async",
                    file=str(path.relative_to(Path.cwd())),
                    line=i,
                    severity="medium",
                    message="Network call without timeout.",
                    hint="Add timeouts and consider running off the UI thread if applicable.",
                )
            )
        if is_ui and "time.sleep(" in line:
            findings.append(
                Finding(
                    pillar="Async",
                    file=str(path.relative_to(Path.cwd())),
                    line=i,
                    severity="high",
                    message="Blocking sleep on UI thread.",
                    hint="Offload work to a worker thread or use non-blocking timers.",
                )
            )
    return findings


def detect_validation_gaps(lines: List[str], path: Path, boundary_markers: List[str]) -> Optional[Finding]:
    # Only check files that are TRUE boundaries (handlers, controllers, APIs)
    filename = path.name.lower()
    
    # Check if filename matches boundary patterns
    is_boundary = any(
        filename.endswith(f"_{marker}.py") or filename == f"{marker}.py"
        for marker in boundary_markers
    )
    
    if not is_boundary:
        return None
    
    text = "\n".join(lines)
    if re.search(r"validate|schema|pydantic|attrs|marshmallow", text, re.IGNORECASE):
        return None
    return Finding(
        pillar="Validation",
        file=str(path.relative_to(Path.cwd())),
        severity="low",
        message="Boundary file without visible validation hooks.",
        hint="Add boundary validation (schema/guards) at entry points.",
    )


def detect_observability(lines: List[str], path: Path) -> Optional[Finding]:
    if "except" not in " ".join(lines):
        return None
    if any("logger." in line for line in lines):
        return None
    return Finding(
        pillar="Observability",
        file=str(path.relative_to(Path.cwd())),
        severity="low",
        message="Exception handling present without logger usage.",
        hint="Emit structured logs at entry/error/exit points.",
    )


def detect_dependency_perf(lines: List[str], path: Path) -> List[Finding]:
    findings: List[Finding] = []
    is_ui = "/ui/" in str(path).replace("\\", "/")
    heavy = ["numpy", "pandas", "matplotlib"]
    for i, line in enumerate(lines, start=1):
        if is_ui and any(re.search(rf"\b{lib}\b", line) for lib in heavy):
            findings.append(
                Finding(
                    pillar="Dependency/Perf",
                    file=str(path.relative_to(Path.cwd())),
                    line=i,
                    severity="medium",
                    message="UI file importing heavy dependency.",
                    hint="Keep UI lean; move heavy work to services.",
                )
            )
    return findings


def detect_security(lines: List[str], path: Path, allowed_hosts: List[str], secret_keywords: List[str]) -> List[Finding]:
    findings: List[Finding] = []
    url_pattern = re.compile(r"https?://([^/'\"]+)")
    for i, line in enumerate(lines, start=1):
        for match in url_pattern.findall(line):
            host = match.lower()
            if not any(allowed in host for allowed in allowed_hosts):
                findings.append(
                    Finding(
                        pillar="Security",
                        file=str(path.relative_to(Path.cwd())),
                        line=i,
                        severity="low",
                        message=f"External host '{host}' not in allowlist.",
                        hint="Whitelist intentional hosts or route through approved clients.",
                    )
                )
        for keyword in secret_keywords:
            if keyword in line:
                findings.append(
                    Finding(
                        pillar="Security",
                        file=str(path.relative_to(Path.cwd())),
                        line=i,
                        severity="medium",
                        message=f"Possible secret material referenced: {keyword}.",
                        hint="Keep secrets out of source and logs; use local env/config.",
                    )
                )
    return findings


def detect_signal_usage(path: Path, content: str, signal_modules: List[str]) -> Optional[Finding]:
    if "pillars" not in str(path):
        return None
    
    # Only check service-layer files (where cross-pillar calls would occur)
    path_str = str(path).replace("\\", "/")
    excluded_patterns = ["/models/", "/utils/", "/ui/", "/__init__.py", "/tests/"]
    if any(pattern in path_str for pattern in excluded_patterns):
        return None
    
    # Only flag if in services/ or controllers/ and lacks signal imports
    is_service_layer = "/services/" in path_str or "/controllers/" in path_str or "/handlers/" in path_str
    if not is_service_layer:
        return None
    
    if any(mod in content for mod in signal_modules):
        return None
    if re.search(r"navigation_bus|signal_bus", content):
        return None
    
    return Finding(
        pillar="Signal Bus",
        file=str(path.relative_to(Path.cwd())),
        severity="low",
        message="Service-layer file lacks signal bus references; verify cross-pillar calls are decoupled.",
        hint="Prefer signals/events over direct imports for inter-pillar communication.",
    )


def aggregate(findings: List[Finding]) -> Dict[str, List[Dict[str, object]]]:
    grouped: Dict[str, List[Dict[str, object]]] = {}
    for f in findings:
        grouped.setdefault(f.pillar, []).append(f.to_dict())
    return grouped


def print_text_report(findings: List[Finding]) -> None:
    if not findings:
        print("Rite of Nine: no findings. Architecture holds fast.")
        return
    grouped = aggregate(findings)
    for pillar, items in grouped.items():
        print(f"\n[{pillar}] ({len(items)})")
        for item in items:
            location = item.get("file", "")
            if "line" in item:
                location = f"{location}:{item['line']}"
            print(f"- {item.get('severity','')} :: {location} :: {item.get('message','')}")
            if item.get("hint"):
                print(f"  hint: {item['hint']}")


def run_rite(paths: List[Path], mode: str, config: Dict[str, object], repo_root: Path) -> List[Finding]:
    findings: List[Finding] = []
    
    # Extract blessed colors once for all UI file checks
    blessed_colors = extract_blessed_colors(repo_root)
    
    for path in iter_python_files(paths):
        lines = read_lines(path)
        content = "\n".join(lines)
        pillar_root = str(config.get("pillar_root", "src/pillars"))
        cross = detect_cross_pillar_imports(path, content, pillar_root)
        if cross:
            findings.append(cross)
        findings.extend(detect_ui_contamination(path, lines, config.get("ui_contamination_blocklist", []), blessed_colors))
        findings.extend(detect_error_handling(lines, path))
        findings.extend(detect_config_leaks(lines, path, config.get("config_modules", [])))
        findings.extend(detect_async_issues(lines, path))
        val_gap = detect_validation_gaps(lines, path, config.get("boundary_markers", []))
        if val_gap:
            findings.append(val_gap)
        obs = detect_observability(lines, path)
        if obs:
            findings.append(obs)
        findings.extend(detect_dependency_perf(lines, path))
        findings.extend(detect_security(lines, path, config.get("allowed_hosts", []), config.get("security_secret_keywords", [])))
        sig = detect_signal_usage(path, content, config.get("signal_modules", []))
        if sig:
            findings.append(sig)
        if mode == "focus":
            # Deep mode hook: room for future AST-level checks.
            pass
    return findings


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rite of the Nine Pillars scout")
    parser.add_argument("path", nargs="?", default="src", help="Path to scan (default: src)")
    parser.add_argument("--mode", choices=["fast", "focus"], default="fast", help="Scan mode")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Report format")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    repo_root = Path(__file__).resolve().parent.parent
    target = repo_root / args.path
    paths = [target] if target.exists() else [repo_root / "src"]
    config_path = Path(__file__).with_name("rite_of_nine_config.json")
    config = load_config(config_path)
    findings = run_rite(paths, args.mode, config, repo_root)
    if args.format == "json":
        print(json.dumps({"findings": [f.to_dict() for f in findings]}, indent=2))
    else:
        print_text_report(findings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
