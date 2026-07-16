"""Route checklist domains to appropriate instructions for ACC to execute."""
from __future__ import annotations
from typing import Any

DOMAIN_INSTRUCTIONS: dict[str, str] = {
    "frontend": "Build user-facing interface. Use semantic HTML, CSS variables for theming, JavaScript for interactions.",
    "theme": "Define color palette, typography, spacing scale. Use CSS custom properties. Apply consistently.",
    "responsive": "Mobile-first layout. Use CSS grid/flexbox. Test at 375px, 768px, 1280px.",
    "accessibility": "Semantic HTML. ARIA labels for interactive elements. Keyboard navigation. Color contrast 4.5:1+.",
    "loading states": "Add skeleton screens or spinners. Never show blank content during async operations.",
    "error states": "Show user-friendly error messages. Provide retry actions. Log errors for debugging.",
    "performance": "Bundle assets. Lazy-load non-critical resources. Target <3s first contentful paint.",
    "backend": "Build API layer. Handle auth, validation, error responses. Return consistent JSON shapes.",
    "db": "Define schema. Use migrations. Index foreign keys and search columns. Never store plaintext secrets.",
    "auth": "Use proven auth library. Store sessions securely. Hash passwords with bcrypt. Implement logout.",
    "payments": "Use Stripe SDK. Store only Stripe customer IDs, never raw card data. Test with test mode keys.",
    "security": "Validate all inputs. Use parameterized queries. Set security headers. Rate-limit auth endpoints.",
    "seo": "Add meta tags. Use semantic headings (h1 once). Sitemap.xml. robots.txt. Structured data.",
    "analytics": "Add page view tracking. Track key user actions. Use privacy-respecting setup (no PII).",
    "deploy": "Containerize or use platform-native deploy. Set env vars from secrets manager. Zero-downtime deploys.",
    "tests": "Write unit tests for business logic. Integration tests for API endpoints. E2E for critical flows.",
    "docs": "Write README with setup, run, and deploy steps. Document API endpoints. Add inline comments for non-obvious logic.",
    "ci": "Add GitHub Actions or equivalent. Run tests on every PR. Block merge on test failure.",
    "platform": "Define target OS and minimum version. Use platform-native UI components where possible.",
    "installer": "Package as installer or binary. Include version info. Test clean install on target OS.",
    "data-pipeline": "Define data source → transform → output. Validate input schema. Handle malformed rows.",
    "game-loop": "Define update/render cycle. Separate game logic from rendering. Handle pause/resume.",
    "error-handling": "Define exit codes. Log errors with context. Return helpful messages to callers.",
    "logging": "Structured logs with timestamp, level, context. Separate debug from production logs.",
}


def route_domains(
    checklist: list[dict[str, Any]],
    product_type: str,
) -> dict[str, Any]:
    domains: list[dict[str, str]] = []
    for item in checklist:
        area = item.get("area", "")
        decision = item.get("decision", "unknown")
        if decision != "include":
            continue
        instructions = DOMAIN_INSTRUCTIONS.get(area, f"Handle {area} for {product_type}.")
        domains.append({
            "area": area,
            "instructions": instructions,
            "product_type": product_type,
        })
    return {"domains": domains, "product_type": product_type, "count": len(domains)}
