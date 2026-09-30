from typing import Dict, Any, List
from app.ai.providers.base import BaseAIProvider


class LocalModelProvider(BaseAIProvider):
    def synthesize_match_narrative(self, match_data: Dict[str, Any]) -> str:
        score = match_data.get("overall_score", 0.0)
        req_score = match_data.get("required_skill_score", 0.0)
        evidences = match_data.get("evidences", [])

        direct = [e["skill_name"] for e in evidences if e.get("match_status") == "direct_match"]
        trans = [f"{e['skill_name']} via {e.get('matched_candidate_skill')}" for e in evidences if e.get("match_status") == "transferable_match"]
        missing = [e["skill_name"] for e in evidences if e.get("is_required") and e.get("match_status") == "missing"]

        lines = [
            f"Compatibility Assessment: {score:.1f}% overall score with {req_score:.1f}% required skill match.",
        ]
        if direct:
            lines.append(f"Directly verified competency in {', '.join(direct[:5])}.")
        if trans:
            lines.append(f"Transferable experience verified for {', '.join(trans[:3])}.")
        if missing:
            lines.append(f"Gaps identified in required skills: {', '.join(missing[:4])}.")

        return " ".join(lines)

    def generate_career_roadmap(self, missing_skills: List[str], target_role: str) -> List[Dict[str, Any]]:
        steps = []
        for idx, skill in enumerate(missing_skills[:4], start=1):
            steps.append({
                "step": idx,
                "skill": skill,
                "action": f"Acquire practical implementation experience in {skill} tailored for {target_role}.",
                "recommended_project": f"Build and deploy a reference architecture module utilizing {skill}."
            })
        return steps


local_provider = LocalModelProvider()
