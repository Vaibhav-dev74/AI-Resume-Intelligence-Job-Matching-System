from typing import Optional, List, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.skill import Skill, SkillRelation


class SkillRepository:
    @classmethod
    async def get_or_create(
        cls,
        db: AsyncSession,
        canonical_name: str,
        category: str,
        aliases: List[str] = None,
        description: str = None
    ) -> Skill:
        query = select(Skill).where(Skill.canonical_name == canonical_name)
        result = await db.execute(query)
        skill = result.scalar_one_or_none()

        if not skill:
            skill = Skill(
                canonical_name=canonical_name,
                category=category,
                aliases=aliases or [],
                description=description
            )
            db.add(skill)
            await db.flush()
        return skill

    @classmethod
    async def list_all(cls, db: AsyncSession) -> List[Skill]:
        query = select(Skill).order_by(Skill.canonical_name)
        result = await db.execute(query)
        return list(result.scalars().all())


skill_repo = SkillRepository()
