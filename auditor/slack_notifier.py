import json
import urllib.request
from typing import Dict, Any


def send_cost_alert_slack(webhook_url: str, cost_data: Dict[str, Any], budget_passed: bool):
    if not webhook_url:
        print("No Slack webhook provided. Skipping alert dispatch.")
        return

    status_color = "#2EB886" if budget_passed else "#A30200"
    status_text = "PASSED (Within Budget)" if budget_passed else "FAILED (Cost Overrun Blocked)"

    payload = {
        "attachments": [
            {
                "color": status_color,
                "title": f"GitOps FinOps Audit: {status_text}",
                "fields": [
                    {
                        "title": "Projected Monthly Cost",
                        "value": f"${cost_data.get('projected_monthly_cost_usd')} USD",
                        "short": True,
                    },
                    {
                        "title": "Allocated CPU / Memory",
                        "value": f"{cost_data.get('total_cpu_cores')} Cores | {cost_data.get('total_mem_gb')} GB",
                        "short": True,
                    },
                ],
                "footer": "GitOps Cost Auditor Bot",
            }
        ]
    }

    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as response:
        return response.status
