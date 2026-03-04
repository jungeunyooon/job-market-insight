"""Tests for job title and company name normalizer."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from nlp.normalizer import CompanyNormalizer, PositionNormalizer


class TestPositionNormalizer:
    """Position title normalization tests."""

    @pytest.fixture
    def normalizer(self) -> PositionNormalizer:
        return PositionNormalizer()

    @pytest.mark.parametrize(
        "title,expected",
        [
            ("백엔드 개발자", "BACKEND"),
            ("서버 개발자", "BACKEND"),
            ("서버개발자", "BACKEND"),
            ("Backend Engineer", "BACKEND"),
            ("Backend Developer", "BACKEND"),
            ("Server Developer", "BACKEND"),
            ("backend engineer", "BACKEND"),
        ],
    )
    def test_backend_positions(
        self, normalizer: PositionNormalizer, title: str, expected: str
    ) -> None:
        assert normalizer.normalize(title) == expected

    @pytest.mark.parametrize(
        "title,expected",
        [
            ("프로덕트 엔지니어", "PRODUCT"),
            ("Product Engineer", "PRODUCT"),
            ("풀스택 개발자", "PRODUCT"),
            ("Full-stack Developer", "PRODUCT"),
            ("Fullstack Engineer", "PRODUCT"),
        ],
    )
    def test_product_positions(
        self, normalizer: PositionNormalizer, title: str, expected: str
    ) -> None:
        assert normalizer.normalize(title) == expected

    @pytest.mark.parametrize(
        "title,expected",
        [
            ("FDE", "FDE"),
            ("Forward Deployed Engineer", "FDE"),
            ("Solutions Engineer", "FDE"),
        ],
    )
    def test_fde_positions(
        self, normalizer: PositionNormalizer, title: str, expected: str
    ) -> None:
        assert normalizer.normalize(title) == expected

    def test_unknown_position(self, normalizer: PositionNormalizer) -> None:
        assert normalizer.normalize("마케팅 매니저") is None

    def test_empty_title(self, normalizer: PositionNormalizer) -> None:
        assert normalizer.normalize("") is None

    def test_load_from_file(self) -> None:
        aliases_path = (
            Path(__file__).parent.parent.parent / "data" / "position_aliases.json"
        )
        if not aliases_path.exists():
            pytest.skip("position_aliases.json not found")

        normalizer = PositionNormalizer(aliases_path=aliases_path)
        assert normalizer.normalize("백엔드 개발자") == "BACKEND"


class TestCompanyNormalizer:
    """Company name normalization tests."""

    @pytest.fixture
    def normalizer(self) -> CompanyNormalizer:
        companies = [
            {
                "name": "우아한형제들",
                "name_en": "Woowa Brothers",
                "aliases": ["배달의민족", "배민"],
            },
            {
                "name": "비바리퍼블리카",
                "name_en": "Viva Republica",
                "aliases": ["토스", "Toss"],
            },
            {
                "name": "네이버",
                "name_en": "Naver",
                "aliases": ["NAVER"],
            },
        ]
        normalizer = CompanyNormalizer(companies=companies)
        return normalizer

    def test_exact_match(self, normalizer: CompanyNormalizer) -> None:
        assert normalizer.normalize("네이버") == "네이버"

    def test_english_name(self, normalizer: CompanyNormalizer) -> None:
        assert normalizer.normalize("Woowa Brothers") == "우아한형제들"

    def test_alias_match(self, normalizer: CompanyNormalizer) -> None:
        assert normalizer.normalize("배민") == "우아한형제들"
        assert normalizer.normalize("토스") == "비바리퍼블리카"

    def test_case_insensitive(self, normalizer: CompanyNormalizer) -> None:
        assert normalizer.normalize("NAVER") == "네이버"
        assert normalizer.normalize("naver") == "네이버"

    def test_unknown_company(self, normalizer: CompanyNormalizer) -> None:
        assert normalizer.normalize("알수없는회사") is None

    def test_empty_name(self, normalizer: CompanyNormalizer) -> None:
        assert normalizer.normalize("") is None

    def test_whitespace_handling(self, normalizer: CompanyNormalizer) -> None:
        assert normalizer.normalize("  네이버  ") == "네이버"
