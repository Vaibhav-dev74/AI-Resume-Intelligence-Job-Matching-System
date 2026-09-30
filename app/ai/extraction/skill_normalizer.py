import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from app.core.config import settings
from app.core.constants import SkillCategory, MatchStatus
from app.core.logging import logger


class CanonicalSkillNode:
    def __init__(self, canonical_name: str, category: SkillCategory, aliases: List[str], description: str = ""):
        self.canonical_name = canonical_name
        self.category = category
        self.aliases = set(a.lower().strip() for a in aliases)
        self.aliases.add(canonical_name.lower().strip())
        self.description = description
        self.related_skills: Dict[str, float] = {}

    def add_relation(self, target_canonical: str, weight: float):
        self.related_skills[target_canonical] = weight


class SkillNormalizer:
    def __init__(self, taxonomy_path: Optional[Path] = None):
        self.taxonomy_path = taxonomy_path or settings.TAXONOMY_PATH
        self.canonical_nodes: Dict[str, CanonicalSkillNode] = {}
        self.alias_to_canonical: Dict[str, str] = {}
        self._load_taxonomy()

    def _load_taxonomy(self):
        if not self.taxonomy_path.exists():
            logger.warning(f"Taxonomy file not found at {self.taxonomy_path}. Initializing empty.")
            return

        with open(self.taxonomy_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data.get("skills", []):
            canonical_name = item["canonical_name"]
            category = SkillCategory(item.get("category", "tool"))
            aliases = item.get("aliases", [])
            desc = item.get("description", "")
            node = CanonicalSkillNode(canonical_name, category, aliases, desc)
            self.canonical_nodes[canonical_name] = node

            for alias in node.aliases:
                self.alias_to_canonical[alias] = canonical_name

        for item in data.get("skills", []):
            src_name = item["canonical_name"]
            for rel in item.get("related_skills", []):
                tgt_name = rel["skill"]
                weight = float(rel.get("transferability", 0.75))
                if src_name in self.canonical_nodes and tgt_name in self.canonical_nodes:
                    self.canonical_nodes[src_name].add_relation(tgt_name, weight)
                    if src_name not in self.canonical_nodes[tgt_name].related_skills:
                        self.canonical_nodes[tgt_name].add_relation(src_name, weight * 0.9)

        logger.info(f"Loaded {len(self.canonical_nodes)} canonical skills and {len(self.alias_to_canonical)} aliases.")

    def normalize(self, raw_skill: str) -> Optional[CanonicalSkillNode]:
        clean = raw_skill.lower().strip()
        if clean in self.alias_to_canonical:
            canonical_name = self.alias_to_canonical[clean]
            return self.canonical_nodes[canonical_name]
        return None

    def match_skill_against_candidates(
        self,
        required_skill_name: str,
        candidate_skills: List[str]
    ) -> Tuple[MatchStatus, Optional[str], float, str]:
        req_node = self.normalize(required_skill_name)
        req_canonical = req_node.canonical_name if req_node else required_skill_name

        candidate_canonical_map: Dict[str, str] = {}
        for c in candidate_skills:
            node = self.normalize(c)
            c_can = node.canonical_name if node else c
            candidate_canonical_map[c_can.lower()] = c

        if req_canonical.lower() in candidate_canonical_map:
            orig = candidate_canonical_map[req_canonical.lower()]
            return (
                MatchStatus.DIRECT_MATCH,
                req_canonical,
                1.0,
                f"Candidate directly possesses '{req_canonical}' (found as '{orig}')."
            )

        if req_node:
            best_transfer_skill = None
            best_weight = 0.0

            for rel_name, weight in req_node.related_skills.items():
                if rel_name.lower() in candidate_canonical_map:
                    if weight > best_weight:
                        best_weight = weight
                        best_transfer_skill = rel_name

            if best_transfer_skill and best_weight >= 0.60:
                penalized_score = round(best_weight * settings.TRANSFERABLE_SKILL_PENALTY, 2)
                return (
                    MatchStatus.TRANSFERABLE_MATCH,
                    best_transfer_skill,
                    penalized_score,
                    f"Candidate has proven '{best_transfer_skill}' experience (transferable skill rating: {int(best_weight*100)}%), which is transferable to '{req_canonical}', though direct '{req_canonical}' experience was not explicitly found."
                )

        return (
            MatchStatus.MISSING,
            None,
            0.0,
            f"No direct evidence or strongly transferable peer skills found for required skill '{req_canonical}'."
        )


skill_normalizer = SkillNormalizer()
