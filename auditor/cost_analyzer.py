from typing import Dict, List, Any


class CostAuditor:
    def __init__(self, hourly_cpu_cost: float = 0.0316, hourly_mem_gb_cost: float = 0.0042):
        self.hourly_cpu_cost = hourly_cpu_cost
        self.hourly_mem_gb_cost = hourly_mem_gb_cost

    def evaluate_manifest_costs(self, manifests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates total declared monthly run rate from deployment resource requests."""
        total_cpu_cores = 0.0
        total_mem_gb = 0.0

        for manifest in manifests:
            if manifest.get("kind") == "Deployment":
                containers = (
                    manifest.get("spec", {})
                    .get("template", {})
                    .get("spec", {})
                    .get("containers", [])
                )
                replicas = manifest.get("spec", {}).get("replicas", 1)

                for container in containers:
                    resources = container.get("resources", {}).get("requests", {})
                    
                    # Parse CPU
                    cpu_str = str(resources.get("cpu", "100m"))
                    if cpu_str.endswith("m"):
                        total_cpu_cores += (float(cpu_str.rstrip("m")) / 1000.0) * replicas
                    else:
                        total_cpu_cores += float(cpu_str) * replicas

                    # Parse Memory
                    mem_str = str(resources.get("memory", "128Mi"))
                    if mem_str.endswith("Mi"):
                        total_mem_gb += (float(mem_str.rstrip("Mi")) / 1024.0) * replicas
                    elif mem_str.endswith("Gi"):
                        total_mem_gb += float(mem_str.rstrip("Gi")) * replicas

        monthly_hours = 730
        cpu_monthly = total_cpu_cores * self.hourly_cpu_cost * monthly_hours
        mem_monthly = total_mem_gb * self.hourly_mem_gb_cost * monthly_hours
        total_monthly = cpu_monthly + mem_monthly

        return {
            "total_cpu_cores": round(total_cpu_cores, 2),
            "total_mem_gb": round(total_mem_gb, 2),
            "projected_monthly_cost_usd": round(total_monthly, 2),
            "cpu_monthly_usd": round(cpu_monthly, 2),
            "mem_monthly_usd": round(mem_monthly, 2),
        }

    def evaluate_cost_budget_gate(self, current_cost: float, max_budget_usd: float) -> bool:
        """Returns True if projected cost is within budget limit, False otherwise."""
        return current_cost <= max_budget_usd
