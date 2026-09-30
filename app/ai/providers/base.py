from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseAIProvider(ABC):
    @abstractmethod
    def synthesize_match_narrative(self, match_data: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def generate_career_roadmap(self, missing_skills: List[str], target_role: str) -> List[Dict[str, Any]]:
        pass
