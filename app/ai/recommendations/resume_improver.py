import re
from typing import Dict, List, Any


class ResumeImprovementEngine:
    PASSIVE_WEAK_VERBS = [
        "worked on", "responsible for", "helped", "helped with", "assisted",
        "assisted with", "participated in", "handled", "involved in", "did"
    ]

    ACTION_VERB_REPLACEMENTS = {
        "worked on": ["Engineered", "Architected", "Developed", "Implemented"],
        "responsible for": ["Led", "Spearheaded", "Directed", "Orchestrated"],
        "helped": ["Collaborated to deliver", "Co-engineered", "Contributed to"],
        "helped with": ["Co-designed", "Implemented components for"],
        "assisted": ["Co-authored", "Co-developed", "Collaborated on"],
        "assisted with": ["Co-developed", "Contributed to building"],
        "participated in": ["Contributed to", "Co-developed"],
        "handled": ["Administered", "Maintained", "Automated", "Managed"],
        "involved in": ["Built modules for", "Architected solutions for"],
        "did": ["Executed", "Implemented", "Delivered"]
    }

    METRIC_PATTERN = re.compile(r"\b(\d+[\d,.]*(?:%|\+|x|k|m|ms|s|gb|tb|users|requests|qps)?)\b", re.IGNORECASE)

    @classmethod
    def improve(cls, candidate_profile: Dict[str, Any]) -> Dict[str, Any]:
        suggestions = []
        formatting_insights = []
        total_bullets_checked = 0
        strong_bullets_count = 0

        experiences = candidate_profile.get("experiences", [])
        projects = candidate_profile.get("projects", [])

        for exp in experiences:
            company = exp.get("company", "Role")
            bullets = exp.get("key_achievements", [])
            for bullet in bullets:
                if not bullet or len(bullet.strip()) < 10:
                    continue

                total_bullets_checked += 1
                item = cls._analyze_bullet(bullet, section=f"Experience at {company}")
                if item:
                    suggestions.append(item)
                else:
                    strong_bullets_count += 1

        for proj in projects:
            title = proj.get("title", "Project")
            desc = proj.get("description", "")
            bullets = [b.strip() for b in desc.split("\n") if b.strip()]
            for bullet in bullets:
                if len(bullet) < 15:
                    continue
                total_bullets_checked += 1
                item = cls._analyze_bullet(bullet, section=f"Project: {title}")
                if item:
                    suggestions.append(item)
                else:
                    strong_bullets_count += 1

        skills = candidate_profile.get("skills", [])
        if len(skills) < 5:
            formatting_insights.append("Skill coverage appears sparse. Ensure relevant frameworks, databases, and core libraries are explicitly declared.")
        if not candidate_profile.get("summary"):
            formatting_insights.append("Consider adding a concise 2-sentence Professional Summary highlighting primary engineering domain and key achievements.")
        if not projects and not experiences:
            formatting_insights.append("Neither work experience nor project sections were cleanly identified. Check section header capitalization.")

        if total_bullets_checked > 0:
            bullet_ratio = strong_bullets_count / float(total_bullets_checked)
            strength_score = round(40.0 + (bullet_ratio * 50.0) + (10.0 if skills else 0.0), 1)
        else:
            strength_score = 65.0

        overall_critique = cls._build_overall_critique(strength_score, len(suggestions))

        return {
            "overall_critique": overall_critique,
            "strength_score": min(100.0, strength_score),
            "suggestions": suggestions[:10],
            "formatting_insights": formatting_insights
        }

    @classmethod
    def _analyze_bullet(cls, bullet: str, section: str) -> Dict[str, Any] | None:
        bullet_lower = bullet.lower()

        weak_verb_found = None
        for wv in cls.PASSIVE_WEAK_VERBS:
            if re.search(rf"\b{re.escape(wv)}\b", bullet_lower):
                weak_verb_found = wv
                break

        has_metrics = bool(cls.METRIC_PATTERN.search(bullet))

        if weak_verb_found:
            replacements = cls.ACTION_VERB_REPLACEMENTS.get(weak_verb_found, ["Engineered"])
            revised = re.sub(
                rf"\b{re.escape(weak_verb_found)}\b",
                replacements[0],
                bullet,
                flags=re.IGNORECASE
            )
            return {
                "section": section,
                "original_text": bullet,
                "critique": f"Contains passive language '{weak_verb_found}', which understates your engineering ownership.",
                "suggested_revision": revised,
                "issue_type": "PASSIVE_VOICE",
                "rationale": "Leading with strong technical action verbs immediately signals initiative and engineering competency.",
                "interactive_prompt": "Can you provide the scale or impact? For example: What was the system's request volume, data size, or performance outcome?"
            }

        elif not has_metrics and len(bullet) > 40:
            return {
                "section": section,
                "original_text": bullet,
                "critique": "Lacks quantifiable metrics or measurable business/engineering outcomes.",
                "suggested_revision": f"{bullet} [Add quantifiable result/scale, e.g. reducing processing time or serving N users].",
                "issue_type": "WEAK_METRIC",
                "rationale": "High-impact engineering resumes quantify scale, latency, accuracy, or efficiency gains rather than solely listing duties.",
                "interactive_prompt": "What measurable metric did this project achieve? (e.g., 'reduced API response time from 350ms to 45ms', 'processed 500k daily records')"
            }

        return None

    @classmethod
    def _build_overall_critique(cls, score: float, suggestions_count: int) -> str:
        if score >= 85:
            return f"Resume demonstrates exceptional technical rigor ({score}/100) with active phrasing and clear accomplishments."
        elif score >= 70:
            return f"Solid engineering baseline ({score}/100). Found {suggestions_count} high-leverage opportunities to replace passive verbs and attach quantifiable outcomes."
        else:
            return f"Foundation established ({score}/100), but significant improvements can be made by replacing generic task descriptions with measurable engineering outcomes."


resume_improver = ResumeImprovementEngine()
