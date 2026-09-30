from typing import List, Dict, Any
from fastapi import APIRouter
from app.ai.extraction.skill_normalizer import skill_normalizer

router = APIRouter(prefix="/skills", tags=["Skills Taxonomy"])


@router.get("/canonical", response_model=List[Dict[str, Any]])
async def list_canonical_skills():
    skills = []
    for name, node in skill_normalizer.canonical_nodes.items():
        skills.append({
            "canonical_name": name,
            "category": node.category.value,
            "aliases": list(node.aliases),
            "description": node.description,
            "related_skills": node.related_skills
        })
    return skills
