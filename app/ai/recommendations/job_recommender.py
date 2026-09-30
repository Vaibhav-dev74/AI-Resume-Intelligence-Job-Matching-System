from typing import Dict, List, Any
from app.ai.matching.matcher import matching_engine
from app.core.constants import MatchStatus


class JobRecommender:
    @classmethod
    def recommend_jobs(
        cls,
        candidate_profile: Dict[str, Any],
        jobs_pool: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        if not jobs_pool:
            return []

        recommendations = []

        for job in jobs_pool:
            match_res = matching_engine.match(candidate_profile, job)
            score = match_res["overall_score"]

            evidences = match_res.get("evidences", [])
            matched_skills = [
                e["skill_name"] for e in evidences
                if e["match_status"] == MatchStatus.DIRECT_MATCH.value
            ]
            transferable = [
                f"{e['skill_name']} ({e['matched_candidate_skill']})" for e in evidences
                if e["match_status"] == MatchStatus.TRANSFERABLE_MATCH.value
            ]
            missing = [
                e["skill_name"] for e in evidences
                if e.get("is_required") and e["match_status"] == MatchStatus.MISSING.value
            ]

            recommendations.append({
                "job_id": job.get("id", ""),
                "title": job.get("title", "Role"),
                "company": job.get("company", "Company"),
                "overall_fit_score": score,
                "match_rationale": match_res.get("synthesis_explanation", ""),
                "matched_skills": matched_skills[:5],
                "transferable_skills": transferable[:3],
                "missing_skills": missing[:4],
                "scores_breakdown": {
                    "required_skill_score": match_res["required_skill_score"],
                    "semantic_score": match_res["semantic_score"],
                    "experience_score": match_res["experience_score"]
                }
            })

        recommendations.sort(key=lambda x: x["overall_fit_score"], reverse=True)

        for idx, rec in enumerate(recommendations[:top_k], start=1):
            rec["rank"] = idx

        return recommendations[:top_k]


job_recommender = JobRecommender()
