from typing import Dict, List, Any
from app.core.constants import MatchStatus


class SkillGapAnalyzer:
    DIFFICULTY_LOOKUP = {
        "Python": "EASY", "SQL": "EASY", "Git": "EASY", "REST APIs": "EASY",
        "FastAPI": "MODERATE", "Flask": "MODERATE", "Docker": "MODERATE", "PostgreSQL": "MODERATE",
        "React": "MODERATE", "Pandas": "MODERATE", "Scikit-Learn": "MODERATE",
        "Kubernetes": "ADVANCED", "PyTorch": "ADVANCED", "Deep Learning": "ADVANCED",
        "Large Language Models": "ADVANCED", "RAG": "ADVANCED", "Apache Spark": "ADVANCED",
        "Vector Search": "MODERATE", "MLOps": "ADVANCED"
    }

    @classmethod
    def analyze_gaps(
        cls,
        candidate_skills: List[Dict[str, Any]],
        job_evidences: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        strong = []
        transferable = []
        inferred = []
        missing = []

        total_reqs = 0
        matched_reqs = 0

        for ev in job_evidences:
            name = ev["skill_name"]
            is_req = ev.get("is_required", True)
            status = ev.get("match_status", MatchStatus.MISSING.value)
            sim = ev.get("similarity_score", 0.0)
            matched_with = ev.get("matched_candidate_skill")
            explanation = ev.get("explanation", "")

            difficulty = cls.DIFFICULTY_LOOKUP.get(name, "MODERATE")

            if is_req:
                total_reqs += 1
                if status in (MatchStatus.DIRECT_MATCH.value, MatchStatus.TRANSFERABLE_MATCH.value):
                    matched_reqs += 1

            if is_req and status == MatchStatus.MISSING.value:
                priority = "HIGH"
            elif is_req and status == MatchStatus.TRANSFERABLE_MATCH.value:
                priority = "MEDIUM"
            elif not is_req and status == MatchStatus.MISSING.value:
                priority = "MEDIUM"
            else:
                priority = "LOW"

            item = {
                "skill_name": name,
                "category": ev.get("category", "tool"),
                "is_required": is_req,
                "status": status,
                "matched_transferable_skill": matched_with,
                "similarity_score": sim,
                "importance_weight": 1.0 if is_req else 0.5,
                "priority_level": priority,
                "learning_difficulty": difficulty,
                "rationale": explanation
            }

            if status == MatchStatus.DIRECT_MATCH.value:
                strong.append(item)
            elif status == MatchStatus.TRANSFERABLE_MATCH.value:
                transferable.append(item)
            elif status == MatchStatus.INFERRED.value:
                inferred.append(item)
            else:
                missing.append(item)

        missing.sort(key=lambda x: (0 if x["priority_level"] == "HIGH" else 1, x["skill_name"]))
        coverage = round((matched_reqs / total_reqs * 100.0), 1) if total_reqs > 0 else 100.0
        roadmap = cls._generate_upskilling_roadmap(missing, transferable)

        return {
            "strong_skills": strong,
            "transferable_skills": transferable,
            "inferred_skills": inferred,
            "missing_skills": missing,
            "total_required_skills": total_reqs,
            "matched_required_skills": matched_reqs,
            "coverage_ratio": coverage,
            "upskilling_roadmap": roadmap
        }

    @classmethod
    def _generate_upskilling_roadmap(
        cls,
        missing_skills: List[Dict[str, Any]],
        transferable_skills: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        weeks = []
        high_priority = [m["skill_name"] for m in missing_skills if m["priority_level"] == "HIGH"]
        trans_names = [t["skill_name"] for t in transferable_skills]

        if trans_names:
            target = trans_names[0]
            weeks.append({
                "week": 1,
                "phase": f"Accelerated Bridge: {target}",
                "focus_skills": [target],
                "action_items": [
                    f"Leverage your proven adjacent knowledge to fast-track syntax and idioms of {target}.",
                    f"Implement an end-to-end mini project contrasting your prior experience with {target}.",
                    f"Document the migration patterns and key differences in your technical notes."
                ]
            })

        if high_priority:
            target = high_priority[0]
            weeks.append({
                "week": 2,
                "phase": f"Foundational Mastery: {target}",
                "focus_skills": [target],
                "action_items": [
                    f"Study official architecture documentation and best practice guidelines for {target}.",
                    f"Build a standalone proof-of-concept demonstrating {target} integrated into a modular service.",
                    f"Write automated unit tests verifying error handling and edge cases."
                ]
            })

        if len(high_priority) > 1:
            target = high_priority[1]
            weeks.append({
                "week": 3,
                "phase": f"Applied Implementation: {target}",
                "focus_skills": [target],
                "action_items": [
                    f"Integrate {target} alongside existing pipeline components.",
                    f"Focus on production readiness: configuration, containerization, and monitoring.",
                    f"Publish code to GitHub with detailed README and benchmark metrics."
                ]
            })

        weeks.append({
            "week": 4,
            "phase": "Capstone Integration & Profile Alignment",
            "focus_skills": high_priority[:2] or ["End-to-End System Integration"],
            "action_items": [
                "Combine learned technologies into a unified production-grade capstone project.",
                "Update resume experience bullets citing verifiable project links and quantifiable results.",
                "Conduct mock technical interview sessions explaining architectural trade-offs."
            ]
        })

        return weeks


gap_analyzer = SkillGapAnalyzer()
