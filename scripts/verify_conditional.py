
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

from pillars.correspondences.services.conditional_formatting import ConditionalManager, ConditionalRule

def verify_conditional():
    manager = ConditionalManager()
    
    # Rule 1: Greater Than 10 -> Red
    rule1 = ConditionalRule(
        rule_type="GT",
        value=10,
        format_style={"bg": "#FF0000"},
        ranges=[(0, 0, 10, 10)] # Apply to A1:K11
    )
    manager.add_rule(rule1)
    
    # Rule 2: Contains "Error" -> Yellow
    rule2 = ConditionalRule(
        rule_type="CONTAINS",
        value="Error",
        format_style={"bg": "#FFFF00"},
        ranges=[(0, 0, 100, 100)]
    )
    manager.add_rule(rule2)
    
    print("Testing GT 10...")
    style = manager.get_style(0, 0, 15)
    if style and style.get("bg") == "#FF0000":
        print("PASS: 15 > 10 trigger")
    else:
        print(f"FAIL: 15 > 10 val. Got {style}")

    style = manager.get_style(0, 0, 5)
    if style is None:
        print("PASS: 5 < 10 no trigger")
    else:
        print(f"FAIL: 5 < 10 trigger. Got {style}")
        
    print("Testing CONTAINS 'Error'...")
    style = manager.get_style(5, 5, "System Error")
    if style and style.get("bg") == "#FFFF00":
        print("PASS: 'System Error' contains 'Error'")
    else:
        print(f"FAIL: 'System Error'. Got {style}")
        
    print("Testing Range Boundaries...")
    # Row 20 is outside Rule 1 range
    style = manager.get_style(20, 0, 15) 
    if style is None:
        print("PASS: Outside range no trigger")
    else:
        print(f"FAIL: Outside range trigger. Got {style}")

if __name__ == "__main__":
    verify_conditional()
