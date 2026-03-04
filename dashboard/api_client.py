"""API client for DevPulse Spring Boot backend."""

from __future__ import annotations

import requests

DEFAULT_BASE_URL = "http://localhost:8080/api/v1"


class DevPulseClient:
    """Simple HTTP client for the DevPulse REST API."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})

    def get_postings(
        self,
        position_type: str | None = None,
        company_category: list[str] | None = None,
        status: list[str] | None = None,
        skill_name: list[str] | None = None,
        page: int = 0,
        size: int = 20,
    ) -> dict:
        params: dict = {"page": page, "size": size}
        if position_type:
            params["positionType"] = position_type
        if company_category:
            params["companyCategory"] = company_category
        if status:
            params["status"] = status
        if skill_name:
            params["skillName"] = skill_name
        return self._get("/postings", params=params)

    def get_posting_detail(self, posting_id: int) -> dict:
        return self._get(f"/postings/{posting_id}")

    def get_skill_ranking(
        self,
        position_type: str | None = None,
        company_category: list[str] | None = None,
        include_closed: bool = False,
        top_n: int = 20,
    ) -> dict:
        params: dict = {"includeClosedPostings": str(include_closed).lower(), "topN": top_n}
        if position_type:
            params["positionType"] = position_type
        if company_category:
            params["companyCategory"] = company_category
        return self._get("/analysis/skill-ranking", params=params)

    def get_company_profile(self, company_id: int) -> dict:
        return self._get(f"/analysis/company-profile/{company_id}")

    def get_position_comparison(self, positions: list[str], top_n: int = 20) -> dict:
        return self._get("/analysis/position-comparison", params={"positions": positions, "topN": top_n})

    def analyze_gap(self, my_skills: list[dict], position_type: str = "BACKEND") -> dict:
        return self._post(
            "/analysis/gap",
            params={"positionType": position_type},
            json={"mySkills": my_skills},
        )

    def _get(self, path: str, params: dict | None = None) -> dict:
        resp = self._session.get(f"{self._base_url}{path}", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, params: dict | None = None, json: dict | None = None) -> dict:
        resp = self._session.post(f"{self._base_url}{path}", params=params, json=json, timeout=10)
        resp.raise_for_status()
        return resp.json()
