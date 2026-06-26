"""
courses.py — a small curated catalog of courses and certifications.

Hand-curated so the demo shows real prices and durations (not scraped — the
2026 closing-web makes live course-platform scraping a trap). Each entry maps
a skill to a concrete, credible learning option. Extend freely.
"""

COURSE_CATALOG = [
    {"skill": "kubernetes", "name": "Certified Kubernetes Administrator (CKA)",
     "provider": "CNCF / Linux Foundation", "cost_eur": 395, "weeks": 6,
     "kind": "certification"},
    {"skill": "aws", "name": "AWS Solutions Architect Associate",
     "provider": "Amazon Web Services", "cost_eur": 135, "weeks": 6,
     "kind": "certification"},
    {"skill": "docker", "name": "Docker Mastery",
     "provider": "Udemy", "cost_eur": 20, "weeks": 3, "kind": "course"},
    {"skill": "terraform", "name": "HashiCorp Certified: Terraform Associate",
     "provider": "HashiCorp", "cost_eur": 65, "weeks": 4, "kind": "certification"},
    {"skill": "typescript", "name": "Understanding TypeScript",
     "provider": "Udemy", "cost_eur": 20, "weeks": 4, "kind": "course"},
    {"skill": "react", "name": "Meta Front-End Developer (React)",
     "provider": "Coursera / Meta", "cost_eur": 49, "weeks": 8, "kind": "course"},
    {"skill": "product management", "name": "Google Project Management Certificate",
     "provider": "Coursera / Google", "cost_eur": 49, "weeks": 8, "kind": "certification"},
    {"skill": "machine learning", "name": "Machine Learning Specialization",
     "provider": "Coursera / DeepLearning.AI", "cost_eur": 49, "weeks": 10,
     "kind": "course"},
    {"skill": "llm", "name": "LangChain & LLM App Development",
     "provider": "DeepLearning.AI", "cost_eur": 0, "weeks": 2, "kind": "course"},
    {"skill": "sql", "name": "SQL for Data Analysis",
     "provider": "Udemy", "cost_eur": 20, "weeks": 3, "kind": "course"},
    {"skill": "data analysis", "name": "Google Data Analytics Certificate",
     "provider": "Coursera / Google", "cost_eur": 49, "weeks": 12, "kind": "certification"},
    {"skill": "go", "name": "Learn Go Programming",
     "provider": "Udemy", "cost_eur": 20, "weeks": 4, "kind": "course"},
    {"skill": "ci/cd", "name": "GitHub Actions: CI/CD",
     "provider": "Udemy", "cost_eur": 20, "weeks": 2, "kind": "course"},
    {"skill": "system design", "name": "Grokking the System Design Interview",
     "provider": "Educative", "cost_eur": 70, "weeks": 6, "kind": "course"},
]


def courses_for_skill(skill: str) -> list[dict]:
    s = skill.lower().strip()
    return [c for c in COURSE_CATALOG if c["skill"] == s]


def best_course_for_skill(skill: str) -> dict | None:
    matches = courses_for_skill(skill)
    if not matches:
        return None
    # Prefer the lowest cost-per-week as a simple efficiency heuristic.
    return min(matches, key=lambda c: (c["cost_eur"] / max(c["weeks"], 1)))
