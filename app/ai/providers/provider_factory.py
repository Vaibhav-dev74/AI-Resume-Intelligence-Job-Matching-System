from app.core.config import settings
from app.ai.providers.base import BaseAIProvider
from app.ai.providers.local_provider import local_provider


class AIProviderFactory:
    @classmethod
    def get_provider(cls) -> BaseAIProvider:
        return local_provider


ai_provider = AIProviderFactory.get_provider()
