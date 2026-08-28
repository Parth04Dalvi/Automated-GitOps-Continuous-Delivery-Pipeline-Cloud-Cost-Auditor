import pytest
from auditor.cost_analyzer import CostAuditor


@pytest.fixture
def sample_manifests():
    return [
        {
            "kind": "Deployment",
            "spec": {
                "replicas": 3,
                "template": {
                    "spec": {
                        "containers": [
                            {
                                "name": "web",
                                "resources": {
                                    "requests": {"cpu": "250m", "memory": "512Mi"}
                                },
                            }
                        ]
                    }
                },
            },
        }
    ]


def test_cost_calculation(sample_manifests):
    auditor = CostAuditor(hourly_cpu_cost=0.04, hourly_mem_gb_cost=0.005)
    summary = auditor.evaluate_manifest_costs(sample_manifests)

    # 3 replicas * 0.25 cores = 0.75 cores
    # 3 replicas * 0.5 GB = 1.5 GB
    assert summary["total_cpu_cores"] == 0.75
    assert summary["total_mem_gb"] == 1.5
    assert summary["projected_monthly_cost_usd"] > 0


def test_budget_gate():
    auditor = CostAuditor()
    assert auditor.evaluate_cost_budget_gate(current_cost=120.0, max_budget_usd=150.0) is True
    assert auditor.evaluate_cost_budget_gate(current_cost=200.0, max_budget_usd=150.0) is False
