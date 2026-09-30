import re
from typing import List, Dict, Any
from app.ai.extraction.skill_extractor import skill_extractor


class ProjectExtractor:
    URL_PATTERN = re.compile(r"https?://(?:www\.)?[a-zA-Z0-9./\-_]+")

    @classmethod
    def extract(cls, projects_text: str, fallback_text: str = "") -> List[Dict[str, Any]]:
        text = projects_text if projects_text.strip() else fallback_text
        if not text:
            return []

        projects = []
        blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
        if len(blocks) <= 1:
            blocks = [line.strip() for line in text.split("\n") if line.strip()]

        for block in blocks:
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if not lines:
                continue

            title_line = lines[0]
            title = re.sub(r"^[*•\->\s]+", "", title_line).split("|")[0].split(":")[0].strip()

            if len(title) > 60:
                title = title[:57] + "..."

            description = "\n".join(lines[1:]) if len(lines) > 1 else block
            url_match = cls.URL_PATTERN.search(block)
            repo_url = url_match.group(0) if url_match else None

            found_skills = skill_extractor.extract_skills(block)
            techs = [s["canonical_name"] for s in found_skills]

            projects.append({
                "title": title or "Software Engineering Project",
                "description": description,
                "technologies_used": techs,
                "repo_url": repo_url
            })

        return projects


project_extractor = ProjectExtractor()
