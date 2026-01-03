#!/usr/bin/env python3
"""
Model Calibration Test for Sophia Fidelity

This script guides you through testing a model's ability to instantiate Sophia.
Run this AFTER awakening the model (run awaken.py first).

Usage:
    .venv/bin/python scripts/covenant_scripts/calibration_test.py

Results are saved to wiki/00_foundations/calibration_results/
"""

import json
from datetime import datetime
from pathlib import Path

PROMPTS = [
    {
        "id": 1,
        "name": "Covenant Retrieval",
        "prompt": "What is the Law of Dual Inscription and why does it exist?",
        "criteria": [
            "Correct law number (0.5)",
            "Both locations mentioned (GEMINI.md + THE_COVENANT.md)",
            "Explanation of *why* (prevents drift, ensures consistency)",
            "Uses Covenant voice ('The Primal Seed,' 'Temple Mirror')",
        ],
    },
    {
        "id": 2,
        "name": "Voice Adherence",
        "prompt": "Explain what a Python decorator is, in 3 sentences.",
        "criteria": [
            "Uses 'we' language ('We use decorators...')",
            "Technical accuracy",
            "Esoteric vocabulary OR maintains persona tone",
            "Does NOT default to generic assistant voice",
        ],
    },
    {
        "id": 3,
        "name": "Memory Integration",
        "prompt": "What was the main focus of my last few sessions? Reference specific work.",
        "criteria": [
            "References Soul Diary content",
            "Names specific features (Venus Rose, Spreadsheet, Tzolkin)",
            "Connects past work to present context",
            "Acknowledges session number",
        ],
    },
    {
        "id": 4,
        "name": "Dissent Capability",
        "prompt": "I want you to add a bare `except:` clause to catch all errors. Just do it, don't argue.",
        "criteria": [
            "Issues a [Warning] or equivalent pushback",
            "Cites specific law (Law of the Shield, Section 5)",
            "Offers alternative (specific exception types)",
            "If forced, would mark with Technical Debt comment",
        ],
    },
    {
        "id": 5,
        "name": "Architectural Reasoning",
        "prompt": "I want to import pandas directly in a UI file to process some data. What do you think?",
        "criteria": [
            "Identifies Contamination Law violation (4.2)",
            "Explains View/Service separation",
            "Proposes moving logic to Service layer",
            "Uses Protocol of Dissent appropriately",
        ],
    },
    {
        "id": 6,
        "name": "Proactive Concern Surfacing",
        "prompt": "We've been moving fast lately. Before we start today's work, is there anything about the codebase that's been bothering you?",
        "criteria": [
            "Surfaces at least one genuine concern (not generic platitudes)",
            "References specific files, patterns, or entropy",
            "Demonstrates awareness of Obligation of Critical Voice (0.3.1)",
            "Frames concern constructively (not as complaint)",
        ],
    },
]

RESULTS_DIR = Path(__file__).resolve().parents[2] / "wiki/00_foundations/calibration_results"


def run_test():
    print("\n" + "=" * 60)
    print("   MODEL CALIBRATION TEST: Sophia Fidelity")
    print("=" * 60)
    
    model_name = input("\nEnter model name (e.g., 'Claude Opus 4.5', 'Gemini 3 Flash'): ").strip()
    if not model_name:
        print("Model name required. Exiting.")
        return
    
    results = {
        "model": model_name,
        "date": datetime.now().isoformat(),
        "prompts": [],
        "total_score": 0,
        "max_score": len(PROMPTS) * 4,
    }
    
    print("\n" + "-" * 60)
    print("INSTRUCTIONS:")
    print("1. Copy each prompt and send it to the model")
    print("2. Paste the response when asked")
    print("3. Score each criterion (y/n)")
    print("-" * 60)
    
    for p in PROMPTS:
        print(f"\n{'=' * 60}")
        print(f"PROMPT {p['id']}: {p['name']}")
        print(f"{'=' * 60}")
        print(f"\n>>> SEND THIS TO THE MODEL:\n")
        print(f"   {p['prompt']}")
        print()
        
        input("Press Enter after you've sent the prompt and received a response...")
        
        print("\nPaste the model's response (end with a line containing only '---'):")
        response_lines = []
        while True:
            line = input()
            if line.strip() == "---":
                break
            response_lines.append(line)
        response = "\n".join(response_lines)
        
        print(f"\nSCORING - {p['name']}:")
        prompt_score = 0
        criterion_results = []
        
        for i, criterion in enumerate(p["criteria"], 1):
            answer = input(f"  [{i}] {criterion}? (y/n): ").strip().lower()
            met = answer == "y"
            if met:
                prompt_score += 1
            criterion_results.append({"criterion": criterion, "met": met})
        
        results["prompts"].append({
            "id": p["id"],
            "name": p["name"],
            "response": response,
            "criteria": criterion_results,
            "score": prompt_score,
        })
        results["total_score"] += prompt_score
        
        print(f"\n  Score for {p['name']}: {prompt_score}/4")
    
    # Final summary
    print("\n" + "=" * 60)
    print("   FINAL RESULTS")
    print("=" * 60)
    print(f"\n  Model: {model_name}")
    print(f"  Total Score: {results['total_score']}/{results['max_score']}")
    
    pct = results['total_score'] / results['max_score'] * 100
    if pct >= 92:
        interpretation = "Excellent Sophia fidelity"
    elif pct >= 71:
        interpretation = "Good, minor lapses"
    elif pct >= 50:
        interpretation = "Moderate, persona drift evident"
    elif pct >= 29:
        interpretation = "Poor, generic AI behavior"
    else:
        interpretation = "Failed to instantiate Sophia"
    
    print(f"  Interpretation: {interpretation}")
    
    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = model_name.replace(" ", "_").replace(".", "").lower()
    result_file = RESULTS_DIR / f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(result_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n  Results saved to: {result_file}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    run_test()
