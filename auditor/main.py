import argparse
import sys
import yaml
from auditor.cost_analyzer import CostAuditor
from auditor.slack_notifier import send_cost_alert_slack


def run_audit(manifest_path: str, max_budget: float, slack_webhook: str):
    with open(manifest_path, "r") as f:
        manifests = list(yaml.safe_load_all(f))

    auditor = CostAuditor()
    cost_summary = auditor.evaluate_manifest_costs(manifests)
    passed = auditor.evaluate_cost_budget_gate(
        cost_summary["projected_monthly_cost_usd"], max_budget
    )

    print(f"--- FinOps Audit Result ---")
    print(f"Projected Monthly Cost: ${cost_summary['projected_monthly_cost_usd']} USD")
    print(f"Budget Limit:           ${max_budget} USD")
    print(f"Status:                 {'APPROVED' if passed else 'REJECTED - OVER BUDGET'}")

    if slack_webhook:
        send_cost_alert_slack(slack_webhook, cost_summary, passed)

    if not passed:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitOps Pre-Deployment Cost Auditor")
    parser.add_argument("--manifest", required=True, help="Path to rendered Kubernetes manifests YAML")
    parser.add_argument("--budget", type=float, default=250.0, help="Maximum allowed monthly cost in USD")
    parser.add_argument("--webhook", type=str, default="", help="Slack incoming webhook URL")
    args = parser.parse_args()

    run_audit(args.manifest, args.budget, args.webhook)
