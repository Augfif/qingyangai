from app.services.ai_client import AIService

# Module-level singleton — AsyncOpenAI client is designed for reuse
ai_service = AIService()


async def get_ai_service() -> AIService:
    """FastAPI dependency for injecting the AI service."""
    return ai_service
