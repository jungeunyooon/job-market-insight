"""Phase 0 Validation Script.

Reads job posting CSV → extracts skills via SkillMatcher → pandas frequency analysis.
Validates whether the dictionary-based approach produces useful insights.

Usage:
    python phase0_validate.py [csv_path]
    (default: ../data/sample_postings.csv)
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pandas as pd

from nlp.skill_matcher import MatchedSkill, SkillMatcher


def load_postings_from_csv(csv_path: str | Path) -> list[dict]:
    """Load job postings from CSV file."""
    postings = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            postings.append(row)
    return postings


def extract_skills_from_postings(
    postings: list[dict],
    matcher: SkillMatcher,
    text_field: str = "description",
) -> pd.DataFrame:
    """Extract skills from each posting and return a DataFrame.

    Returns:
        DataFrame with columns: [posting_idx, title, company, skill_name, category, source_scope]
    """
    records = []
    for idx, posting in enumerate(postings):
        text = posting.get(text_field, "")
        title = posting.get("title", "")
        company = posting.get("company", "")

        matched = matcher.match(text, scope="JOB_POSTING")
        for skill in matched:
            records.append(
                {
                    "posting_idx": idx,
                    "title": title,
                    "company": company,
                    "skill_name": skill.skill_name,
                    "category": skill.category,
                    "source_scope": skill.source_scope,
                }
            )

    return pd.DataFrame(records)


def analyze_skill_frequency(df: pd.DataFrame, total_postings: int) -> pd.DataFrame:
    """Compute skill frequency ranking.

    Returns:
        DataFrame with columns: [skill_name, category, count, percentage, rank]
    """
    if df.empty:
        return pd.DataFrame(columns=["skill_name", "category", "count", "percentage", "rank"])

    freq = (
        df.groupby(["skill_name", "category"])
        .agg(count=("posting_idx", "nunique"))
        .reset_index()
    )
    freq["percentage"] = (freq["count"] / total_postings * 100).round(1)
    freq = freq.sort_values("count", ascending=False).reset_index(drop=True)
    freq["rank"] = freq.index + 1
    return freq


def analyze_by_company(df: pd.DataFrame) -> pd.DataFrame:
    """Compute company-specific skill profiles.

    Returns:
        DataFrame with columns: [company, skill_name, count]
    """
    if df.empty:
        return pd.DataFrame(columns=["company", "skill_name", "count"])

    return (
        df.groupby(["company", "skill_name"])
        .size()
        .reset_index(name="count")
        .sort_values(["company", "count"], ascending=[True, False])
    )


def analyze_by_category(df: pd.DataFrame, total_postings: int) -> pd.DataFrame:
    """Compute skill category distribution.

    Returns:
        DataFrame with columns: [category, unique_skills, total_mentions, avg_percentage]
    """
    if df.empty:
        return pd.DataFrame(columns=["category", "unique_skills", "total_mentions", "avg_percentage"])

    cat = df.groupby("category").agg(
        unique_skills=("skill_name", "nunique"),
        total_mentions=("posting_idx", "count"),
    ).reset_index()
    cat["avg_percentage"] = (
        cat["total_mentions"] / total_postings / cat["unique_skills"] * 100
    ).round(1)
    return cat.sort_values("total_mentions", ascending=False)


def generate_report(
    freq_df: pd.DataFrame,
    company_df: pd.DataFrame,
    category_df: pd.DataFrame,
    total_postings: int,
) -> str:
    """Generate a Markdown report."""
    lines = [
        "# DevPulse Phase 0 검증 리포트",
        "",
        f"## 데이터 현황",
        f"- 분석 대상 공고: {total_postings}건",
        f"- 추출된 고유 스킬: {len(freq_df)}개",
        "",
        "## 기술 키워드 빈도 Top 15",
        "",
        "| 순위 | 기술 | 카테고리 | 공고 수 | 비율 |",
        "|------|------|---------|--------|------|",
    ]

    for _, row in freq_df.head(15).iterrows():
        lines.append(
            f"| {int(row['rank'])} | {row['skill_name']} | {row['category']} | "
            f"{int(row['count'])}건 | {row['percentage']}% |"
        )

    lines.extend([
        "",
        "## 카테고리별 분포",
        "",
        "| 카테고리 | 고유 스킬 수 | 총 언급 |",
        "|---------|------------|--------|",
    ])

    for _, row in category_df.iterrows():
        lines.append(
            f"| {row['category']} | {int(row['unique_skills'])}개 | {int(row['total_mentions'])}회 |"
        )

    lines.extend([
        "",
        "## Phase 0 판단",
        "",
        "이 결과가 수동으로 읽는 것보다 유용한가?",
        "- [ ] Top 10 기술이 직관과 일치하는가?",
        "- [ ] 회사별 차이가 보이는가?",
        "- [ ] 이 분석으로 학습 우선순위를 정할 수 있는가?",
        "",
        "> Phase 0 결과가 유용하면 Phase 1 진입, 아니면 방향 전환.",
    ])

    return "\n".join(lines)


def main(csv_path: str | None = None) -> None:
    """Run Phase 0 validation."""
    base_dir = Path(__file__).parent.parent
    if csv_path is None:
        csv_path = base_dir / "data" / "sample_postings.csv"
    else:
        csv_path = Path(csv_path)

    skills_path = base_dir / "data" / "skills_seed.json"

    print(f"Loading postings from: {csv_path}")
    postings = load_postings_from_csv(csv_path)
    print(f"Loaded {len(postings)} postings")

    print(f"Loading skills from: {skills_path}")
    matcher = SkillMatcher(skills_path=skills_path)

    print("Extracting skills...")
    df = extract_skills_from_postings(postings, matcher)
    print(f"Extracted {len(df)} skill mentions")

    total_postings = len(postings)
    freq_df = analyze_skill_frequency(df, total_postings)
    company_df = analyze_by_company(df)
    category_df = analyze_by_category(df, total_postings)

    report = generate_report(freq_df, company_df, category_df, total_postings)

    # Print to console
    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)

    # Save report
    report_path = base_dir / "docs" / "phase0_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"\nReport saved to: {report_path}")

    # Save raw data
    freq_path = base_dir / "data" / "phase0_skill_frequency.csv"
    freq_df.to_csv(freq_path, index=False, encoding="utf-8")
    print(f"Frequency data saved to: {freq_path}")


if __name__ == "__main__":
    csv_arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(csv_arg)
