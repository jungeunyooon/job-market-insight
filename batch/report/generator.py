"""Automated Markdown report generator for DevPulse analysis results.

Generates a comprehensive report from skill rankings, company profiles,
position comparisons, buzz-vs-hiring gaps, and blog topic trends.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ReportData:
    """Data container for report generation."""

    generated_at: str
    skill_ranking: list[dict] = field(default_factory=list)
    total_postings: int = 0
    company_profiles: list[dict] = field(default_factory=list)
    position_comparison: dict = field(default_factory=dict)
    buzz_vs_hiring: list[dict] = field(default_factory=list)
    blog_topics: dict = field(default_factory=dict)


class ReportGenerator:
    """Generates Markdown reports from analysis data."""

    def generate(self, data: ReportData) -> str:
        """Generate full Markdown report."""
        sections = [
            self._header(data),
            self._skill_ranking_section(data),
            self._company_profile_section(data),
            self._position_comparison_section(data),
            self._buzz_vs_hiring_section(data),
            self._blog_trend_section(data),
            self._footer(data),
        ]
        return "\n\n".join(s for s in sections if s)

    def save(self, data: ReportData, path: Path) -> None:
        """Generate and save report to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        content = self.generate(data)
        path.write_text(content, encoding="utf-8")

    def _header(self, data: ReportData) -> str:
        return (
            f"# DevPulse 분석 리포트\n\n"
            f"> 생성일: {data.generated_at}\n"
            f"> 총 분석 공고 수: {data.total_postings}건"
        )

    def _skill_ranking_section(self, data: ReportData) -> str:
        lines = ["## 1. 스킬 랭킹", ""]
        if not data.skill_ranking:
            lines.append("데이터 없음")
            return "\n".join(lines)

        lines.append("| 순위 | 스킬 | 공고 수 | 비율(%) |")
        lines.append("|------|------|---------|---------|")
        for item in data.skill_ranking:
            lines.append(
                f"| {item['rank']} | {item['skill']} | {item['count']} | {item['percentage']}% |"
            )
        return "\n".join(lines)

    def _company_profile_section(self, data: ReportData) -> str:
        if not data.company_profiles:
            return ""

        lines = ["## 2. 회사별 기술 프로필", ""]
        for profile in data.company_profiles:
            company = profile["company"]
            total = profile.get("total_postings", 0)
            lines.append(f"### {company} ({total}건)")
            lines.append("")
            top_skills = profile.get("top_skills", [])
            if top_skills:
                lines.append("| 스킬 | 언급 수 |")
                lines.append("|------|---------|")
                for s in top_skills:
                    lines.append(f"| {s['skill']} | {s['count']} |")
            lines.append("")
        return "\n".join(lines)

    def _position_comparison_section(self, data: ReportData) -> str:
        if not data.position_comparison:
            return ""

        lines = ["## 3. 포지션별 스킬 비교", ""]

        common = data.position_comparison.get("common", [])
        if common:
            lines.append(f"**공통 스킬**: {', '.join(common)}")
            lines.append("")

        for key, skills in data.position_comparison.items():
            if key == "common":
                continue
            lines.append(f"**{key}**: {', '.join(skills)}")

        return "\n".join(lines)

    def _buzz_vs_hiring_section(self, data: ReportData) -> str:
        if not data.buzz_vs_hiring:
            return ""

        lines = ["## 4. Buzz vs Hiring Gap 분석", ""]

        # Group by classification
        groups: dict[str, list[dict]] = {}
        for item in data.buzz_vs_hiring:
            cls = item["classification"]
            groups.setdefault(cls, []).append(item)

        classification_labels = {
            "OVERHYPED": "OVERHYPED (커뮤니티 관심 높음, 채용 낮음)",
            "ADOPTED": "ADOPTED (관심 + 채용 모두 높음)",
            "ESTABLISHED": "ESTABLISHED (채용 높음, 커뮤니티 관심 낮음)",
            "EMERGING": "EMERGING (둘 다 아직 소수)",
        }

        for cls in ["ADOPTED", "OVERHYPED", "ESTABLISHED", "EMERGING"]:
            items = groups.get(cls, [])
            if not items:
                continue
            label = classification_labels.get(cls, cls)
            lines.append(f"### {label}")
            lines.append("")
            lines.append("| 스킬 | 트렌드 언급 | 채용 공고 |")
            lines.append("|------|-----------|----------|")
            for item in items:
                lines.append(
                    f"| {item['skill']} | {item['trend_mentions']} | {item['job_postings']} |"
                )
            lines.append("")

        return "\n".join(lines)

    def _blog_trend_section(self, data: ReportData) -> str:
        if not data.blog_topics:
            return ""

        lines = ["## 5. 블로그 토픽 트렌드", ""]

        yearly = data.blog_topics.get("yearly_trend", {})
        if yearly:
            for year in sorted(yearly.keys()):
                skills = yearly[year]
                lines.append(f"### {year}년")
                lines.append("")
                lines.append("| 스킬 | 게시글 수 |")
                lines.append("|------|----------|")
                for s in skills:
                    lines.append(f"| {s['skill']} | {s['count']} |")
                lines.append("")

        return "\n".join(lines)

    def _footer(self, data: ReportData) -> str:
        return (
            "---\n\n"
            "*이 리포트는 DevPulse에 의해 자동 생성되었습니다.*"
        )
