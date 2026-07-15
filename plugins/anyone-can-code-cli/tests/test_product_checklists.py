import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import product_intake


def _checklist_areas(product_type: str, request: str = "") -> set[str]:
    intake = product_intake.run_product_intake(request or f"build a {product_type}")
    checklist = product_intake.generate_engineering_checklist(intake)
    return {item["area"] for item in checklist}


def test_website_includes_analytics_seo_ci():
    areas = _checklist_areas("website", "build a public website")
    assert "analytics" in areas
    assert "seo" in areas
    assert "ci" in areas


def test_app_includes_analytics_ci():
    areas = _checklist_areas("app", "build a mobile app")
    assert "analytics" in areas
    assert "ci" in areas


def test_game_checklist_complete():
    areas = _checklist_areas("game", "build a game")
    assert "frontend" in areas
    assert "performance" in areas
    assert "tests" in areas
    assert "ci" in areas


def test_native_app_checklist_includes_platform():
    areas = _checklist_areas("native app", "build a windows desktop app")
    assert "platform" in areas
    assert "installer" in areas
    assert "ci" in areas


def test_data_tool_checklist_complete():
    areas = _checklist_areas("data tool", "build a csv analytics tool")
    assert "data-pipeline" in areas
    assert "performance" in areas
    assert "tests" in areas


def test_api_includes_auth_security_docs():
    areas = _checklist_areas("api", "build a rest api")
    assert "auth" in areas
    assert "security" in areas
    assert "docs" in areas
    assert "ci" in areas


def test_all_types_have_tests_docs_security():
    for pt in ["website", "app", "game", "api", "script", "automation", "plugin", "data tool", "dashboard", "native app"]:
        areas = _checklist_areas(pt)
        assert "tests" in areas, f"{pt} missing tests"
        assert "docs" in areas, f"{pt} missing docs"
        assert "security" in areas, f"{pt} missing security"
