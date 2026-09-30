from typing import Dict, List, Any, Optional
from app.core.config import settings
from app.core.constants import MatchStatus
from app.ai.extraction.skill_normalizer import skill_normalizer
from app.ai.embeddings.embedding_engine import embedding_engine


class MatchingEngine:
    def __init__(self):
        self.weights = settings.matching_weights_dict

    def match(
        self,
        candidate_profile: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        candidate_skills_list = [s["canonical_name"] for s in candidate_profile.get("skills", [])]
        candidate_evidence_map = {
            s["canonical_name"]: s.get("evidence_context", "")
            for s in candidate_profile.get("skills", [])
        }

        req_skills_spec = job_data.get("required_skills", [])
        req_evidences = []
        req_scores = []

        for req in req_skills_spec:
            req_name = req["canonical_name"] if isinstance(req, dict) else req
            status, matched_skill, score, explanation = skill_normalizer.match_skill_against_candidates(
                req_name,
                candidate_skills_list
            )
            quote = candidate_evidence_map.get(matched_skill, "") if matched_skill else None
            req_scores.append(score)
            req_evidences.append({
                "skill_name": req_name,
                "is_required": True,
                "match_status": status.value,
                "matched_candidate_skill": matched_skill,
                "similarity_score": score,
                "evidence_quote": quote,
                "explanation": explanation
            })

        req_score_avg = (sum(req_scores) / len(req_scores)) if req_scores else 1.0

        pref_skills_spec = job_data.get("preferred_skills", [])
        pref_evidences = []
        pref_scores = []

        for pref in pref_skills_spec:
            pref_name = pref["canonical_name"] if isinstance(pref, dict) else pref
            status, matched_skill, score, explanation = skill_normalizer.match_skill_against_candidates(
                pref_name,
                candidate_skills_list
            )
            quote = candidate_evidence_map.get(matched_skill, "") if matched_skill else None
            pref_scores.append(score)
            pref_evidences.append({
                "skill_name": pref_name,
                "is_required": False,
                "match_status": status.value,
                "matched_candidate_skill": matched_skill,
                "similarity_score": score,
                "evidence_quote": quote,
                "explanation": explanation
            })

        pref_score_avg = (sum(pref_scores) / len(pref_scores)) if pref_scores else 1.0

        candidate_semantic_text = f"{candidate_profile.get('summary', '')} {' '.join(candidate_skills_list)}"
        job_semantic_text = f"{job_data.get('title', '')} {job_data.get('raw_text', '')[:1000]}"

        cand_vec = embedding_engine.encode(candidate_semantic_text)
        job_vec = embedding_engine.encode(job_semantic_text)
        semantic_sim = embedding_engine.cosine_similarity(cand_vec, job_vec)

        cand_years = float(candidate_profile.get("total_years_experience", 0.0))
        job_req_years = float(job_data.get("min_years_experience", 1.0))
        if job_req_years <= 0:
            exp_ratio = 1.0
        else:
            exp_ratio = min(1.0, cand_years / job_req_years)

        cand_educations = candidate_profile.get("educations", [])
        highest_cand_edu = max([e.get("degree_level", 3) for e in cand_educations], default=3)
        job_min_edu = job_data.get("min_education_level", 3)
        edu_score = 1.0 if highest_cand_edu >= job_min_edu else (highest_cand_edu / float(job_min_edu))

        cand_projects = candidate_profile.get("projects", [])
        project_scores = []
        if cand_projects:
            for p in cand_projects:
                p_text = f"{p.get('title', '')} {p.get('description', '')} {' '.join(p.get('technologies_used', []))}"
                p_vec = embedding_engine.encode(p_text)
                sim = embedding_engine.cosine_similarity(p_vec, job_vec)
                project_scores.append(sim)
            project_score_avg = sum(project_scores) / len(project_scores)
        else:
            project_score_avg = 0.50

        overall = (
            self.weights["required_skills"] * req_score_avg +
            self.weights["semantic_similarity"] * semantic_sim +
            self.weights["experience_relevance"] * exp_ratio +
            self.weights["preferred_skills"] * pref_score_avg +
            self.weights["project_relevance"] * project_score_avg +
            self.weights["education_match"] * edu_score
        ) * 100.0

        overall_score = round(max(0.0, min(100.0, overall)), 1)

        all_evidences = req_evidences + pref_evidences
        synthesis = self._build_synthesis_explanation(
            overall_score=overall_score,
            candidate_profile=candidate_profile,
            job_data=job_data,
            evidences=all_evidences,
            cand_years=cand_years,
            req_years=job_req_years
        )

        return {
            "overall_score": overall_score,
            "required_skill_score": round(req_score_avg * 100.0, 1),
            "preferred_skill_score": round(pref_score_avg * 100.0, 1),
            "semantic_score": round(semantic_sim * 100.0, 1),
            "experience_score": round(exp_ratio * 100.0, 1),
            "project_score": round(project_score_avg * 100.0, 1),
            "education_score": round(edu_score * 100.0, 1),
            "scoring_weights": self.weights,
            "evidences": all_evidences,
            "synthesis_explanation": synthesis
        }

    def _build_synthesis_explanation(
        self,
        overall_score: float,
        candidate_profile: Dict[str, Any],
        job_data: Dict[str, Any],
        evidences: List[Dict[str, Any]],
        cand_years: float,
        req_years: float
    ) -> str:
        direct_matches = [e["skill_name"] for e in evidences if e["match_status"] == MatchStatus.DIRECT_MATCH.value]
        transferable = [f"{e['skill_name']} (via {e['matched_candidate_skill']})" for e in evidences if e["match_status"] == MatchStatus.TRANSFERABLE_MATCH.value]
        missing_reqs = [e["skill_name"] for e in evidences if e["is_required"] and e["match_status"] == MatchStatus.MISSING.value]

        narrative_parts = []

        if overall_score >= 80.0:
            rating = "Strong Compatibility"
        elif overall_score >= 65.0:
            rating = "Moderate Compatibility"
        else:
            rating = "Developing Fit"

        narrative_parts.append(
            f"**{rating} ({overall_score}%)** for the **{job_data.get('title', 'Target Role')}** position at **{job_data.get('company', 'Hiring Organization')}**."
        )

        if direct_matches:
            narrative_parts.append(
                f"**Verified Strengths**: Directly verified capability in key technologies including: {', '.join(direct_matches[:6])}."
            )

        if transferable:
            narrative_parts.append(
                f"**Transferable Expertise**: {', '.join(transferable[:4])}. The candidate has demonstrated adjacent competencies that provide a strong foundation."
            )

        if missing_reqs:
            narrative_parts.append(
                f"**Primary Gaps**: Direct evidence was not identified for required qualifications: {', '.join(missing_reqs[:5])}."
            )

        if cand_years < req_years:
            narrative_parts.append(
                f"**Experience Note**: Position targets {req_years:.1f} years; candidate has {cand_years:.1f} years of verified experience."
            )

        return " ".join(narrative_parts)


matching_engine = MatchingEngine()
