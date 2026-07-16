import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import domain_router


def test_website_routes_all_ux_domains():
    checklist = [
        {"area": "frontend", "decision": "include"},
        {"area": "theme", "decision": "include"},
        {"area": "responsive", "decision": "include"},
        {"area": "accessibility", "decision": "include"},
        {"area": "loading states", "decision": "include"},
        {"area": "error states", "decision": "include"},
        {"area": "backend", "decision": "include"},
        {"area": "auth", "decision": "include"},
        {"area": "deploy", "decision": "include"},
    ]
    routes = domain_router.route_domains(checklist, "website")
    areas = {r["area"] for r in routes["domains"]}
    assert "frontend" in areas
    assert "theme" in areas
    assert "responsive" in areas
    assert "accessibility" in areas
    assert "auth" in areas
    assert "deploy" in areas


def test_each_domain_has_instructions():
    checklist = [{"area": "auth", "decision": "include"}]
    routes = domain_router.route_domains(checklist, "app")
    auth_domain = next(d for d in routes["domains"] if d["area"] == "auth")
    assert auth_domain["instructions"]
    assert len(auth_domain["instructions"]) > 20


def test_skip_domains_are_excluded():
    checklist = [
        {"area": "seo", "decision": "skip"},
        {"area": "frontend", "decision": "include"},
    ]
    routes = domain_router.route_domains(checklist, "api")
    areas = {r["area"] for r in routes["domains"]}
    assert "seo" not in areas
    assert "frontend" in areas


def test_count_matches_included_domains():
    checklist = [
        {"area": "frontend", "decision": "include"},
        {"area": "backend", "decision": "include"},
        {"area": "seo", "decision": "skip"},
    ]
    routes = domain_router.route_domains(checklist, "website")
    assert routes["count"] == 2
    assert len(routes["domains"]) == 2


def test_product_type_preserved_in_output():
    checklist = [{"area": "backend", "decision": "include"}]
    routes = domain_router.route_domains(checklist, "api")
    assert routes["product_type"] == "api"
    assert routes["domains"][0]["product_type"] == "api"


def test_unknown_domain_gets_fallback_instruction():
    checklist = [{"area": "custom-thing", "decision": "include"}]
    routes = domain_router.route_domains(checklist, "tool")
    domain = routes["domains"][0]
    assert domain["instructions"]
    assert "custom-thing" in domain["instructions"] or "tool" in domain["instructions"]


def test_defer_decision_excluded():
    checklist = [
        {"area": "payments", "decision": "defer"},
        {"area": "tests", "decision": "include"},
    ]
    routes = domain_router.route_domains(checklist, "website")
    areas = {r["area"] for r in routes["domains"]}
    assert "payments" not in areas
    assert "tests" in areas


def test_empty_checklist_returns_zero_domains():
    routes = domain_router.route_domains([], "website")
    assert routes["count"] == 0
    assert routes["domains"] == []
