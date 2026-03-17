import json
import sys

if len(sys.argv) < 2:
    print("Usage: python3 analyze_risks.py <path_to_risks.json>")
    sys.exit(1)

severity_map = {'critical': 5, 'elevated': 4, 'high': 3, 'medium': 2, 'low': 1}
likelihood_map = {'very-likely': 4, 'likely': 3, 'possible': 2, 'unlikely': 1}
impact_map = {'high': 3, 'medium': 2, 'low': 1}

try:
    with open(sys.argv[1], 'r') as f:
        risks = json.load(f)
except FileNotFoundError:
    print(f"Error: File '{sys.argv[1]}' not found")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: Invalid JSON in '{sys.argv[1]}'")
    sys.exit(1)

for risk in risks:
    sev = severity_map.get(risk['severity'], 0)
    like = likelihood_map.get(risk['exploitation_likelihood'], 0)
    imp = impact_map.get(risk['exploitation_impact'], 0)
    risk['composite_score'] = sev * 100 + like * 10 + imp

risks_sorted = sorted(risks, key=lambda x: x['composite_score'], reverse=True)

print("| Rank | Risk Title | Severity | Category | Asset | Likelihood | Impact | Score |")
print("|------|-----------|----------|----------|-------|------------|--------|-------|")

for i, risk in enumerate(risks_sorted[:5], 1):
    print(f"| {i} | {risk['title']} | {risk['severity']} | {risk['category']} | "
          f"{risk['most_relevant_technical_asset']} | {risk['exploitation_likelihood']} | "
          f"{risk['exploitation_impact']} | {risk['composite_score']} |")
