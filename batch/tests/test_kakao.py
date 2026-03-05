"""Tests for Kakao Career API crawler."""

import sys
from pathlib import Path

import pytest
import responses

sys.path.insert(0, str(Path(__file__).parent.parent))

from crawlers.kakao import KakaoCareerCrawler, KAKAO_JOB_LIST_URL


SAMPLE_JOB_LIST = {
    "jobList": [
        {
            "realId": "P-14318",
            "jobOfferTitle": "Machine Learning Engineer (Search) (경력)",
            "introduction": "카카오 검색 팀은 수억 건의 데이터를 실시간으로 처리합니다.",
            "workContentDesc": "- 검색 랭킹 모델 개발\n- A/B 테스트 설계 및 분석\n- 실시간 추천 시스템 운영",
            "qualification": "- Python, TensorFlow 또는 PyTorch 경험 3년 이상\n- 검색 또는 추천 시스템 경험",
            "jobOfferProcessDesc": "서류전형 → 1차 면접 → 2차 면접 → 최종합격",
            "companyName": "카카오",
            "locationName": "판교",
            "employeeTypeName": "정규직",
            "skillSetList": ["Python", "TensorFlow", "PyTorch", "Elasticsearch"],
            "regDate": "2026-02-10",
            "endDate": "2026-03-31",
        },
        {
            "realId": "P-14400",
            "jobOfferTitle": "Backend Engineer (카카오페이) (신입/경력)",
            "introduction": "카카오페이 서버 팀에서 함께할 분을 찾습니다.",
            "workContentDesc": "- REST API 설계 및 구현\n- 대용량 트래픽 처리 아키텍처 설계",
            "qualification": "- Java, Spring Boot 경험\n- RDB 설계 능숙",
            "jobOfferProcessDesc": "서류 → 코딩테스트 → 기술면접 → 임원면접",
            "companyName": "카카오페이",
            "locationName": "강남",
            "employeeTypeName": "정규직",
            "skillSetList": ["Java", "Spring Boot", "MySQL", "Kafka"],
            "regDate": "2026-02-20",
            "endDate": "2026-04-15",
        },
    ]
}

SAMPLE_JOB_NO_QUALIFICATION = {
    "realId": "P-99999",
    "jobOfferTitle": "DevOps Engineer (경력)",
    "introduction": "인프라 팀 소개입니다.",
    "workContentDesc": "- Kubernetes 운영\n- CI/CD 파이프라인 구축",
    "qualification": None,
    "jobOfferProcessDesc": "서류 → 면접",
    "companyName": "카카오",
    "locationName": "판교",
    "employeeTypeName": "계약직",
    "skillSetList": ["Kubernetes", "Terraform"],
    "regDate": "2026-03-01",
    "endDate": None,
}

SAMPLE_JOB_WITH_PII = {
    "realId": "P-88888",
    "jobOfferTitle": "HR Manager (경력)",
    "introduction": "문의: hr@kakao.com 또는 010-1234-5678로 연락주세요.",
    "workContentDesc": "채용 전략 수립 및 실행",
    "qualification": "HR 경험 5년 이상",
    "jobOfferProcessDesc": "서류 → 면접",
    "companyName": "카카오",
    "locationName": "판교",
    "employeeTypeName": "정규직",
    "skillSetList": [],
    "regDate": "2026-03-01",
    "endDate": None,
}


class TestKakaoCareerCrawlerInit:

    def test_source_name(self) -> None:
        crawler = KakaoCareerCrawler()
        assert crawler.get_source_name() == "kakao_career"

    def test_rate_limit(self) -> None:
        crawler = KakaoCareerCrawler()
        assert crawler.get_rate_limit_delay() == 1.0


class TestKakaoFetchJobList:

    @responses.activate
    def test_fetch_job_list_returns_jobs(self) -> None:
        responses.add(
            responses.GET,
            KAKAO_JOB_LIST_URL,
            json=SAMPLE_JOB_LIST,
            status=200,
        )

        crawler = KakaoCareerCrawler()
        jobs = crawler._fetch_job_list()

        assert len(jobs) == 2
        assert jobs[0]["realId"] == "P-14318"
        assert jobs[1]["realId"] == "P-14400"

    @responses.activate
    def test_fetch_empty_job_list(self) -> None:
        responses.add(
            responses.GET,
            KAKAO_JOB_LIST_URL,
            json={"jobList": []},
            status=200,
        )

        crawler = KakaoCareerCrawler()
        jobs = crawler._fetch_job_list()
        assert jobs == []

    @responses.activate
    def test_api_error_returns_empty(self) -> None:
        responses.add(
            responses.GET,
            KAKAO_JOB_LIST_URL,
            status=503,
        )

        crawler = KakaoCareerCrawler()
        jobs = crawler._fetch_job_list()
        assert jobs == []

    @responses.activate
    def test_missing_job_list_key_returns_empty(self) -> None:
        responses.add(
            responses.GET,
            KAKAO_JOB_LIST_URL,
            json={"error": "not found"},
            status=200,
        )

        crawler = KakaoCareerCrawler()
        jobs = crawler._fetch_job_list()
        assert jobs == []


class TestKakaoJobToPosting:

    def test_basic_fields(self) -> None:
        crawler = KakaoCareerCrawler()
        job = SAMPLE_JOB_LIST["jobList"][0]
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert posting.title == "Machine Learning Engineer (Search) (경력)"
        assert posting.company_name == "카카오"
        assert posting.source_platform == "kakao_career"
        assert posting.source_url == "https://careers.kakao.com/jobs/P-14318"

    def test_company_name_always_kakao(self) -> None:
        """companyName from API may differ (e.g. 카카오페이) — always use 카카오."""
        crawler = KakaoCareerCrawler()
        job = SAMPLE_JOB_LIST["jobList"][1]  # companyName = "카카오페이"
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert posting.company_name == "카카오"

    def test_responsibilities_raw(self) -> None:
        crawler = KakaoCareerCrawler()
        job = SAMPLE_JOB_LIST["jobList"][0]
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert posting.responsibilities_raw is not None
        assert "검색 랭킹 모델" in posting.responsibilities_raw

    def test_requirements_raw(self) -> None:
        crawler = KakaoCareerCrawler()
        job = SAMPLE_JOB_LIST["jobList"][0]
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert posting.requirements_raw is not None
        assert "Python" in posting.requirements_raw

    def test_description_raw_combines_fields(self) -> None:
        crawler = KakaoCareerCrawler()
        job = SAMPLE_JOB_LIST["jobList"][0]
        posting = crawler._job_to_posting(job)

        assert posting is not None
        # description_raw should include introduction + workContentDesc + qualification
        assert "카카오 검색 팀" in posting.description_raw
        assert "검색 랭킹 모델" in posting.description_raw
        assert "TensorFlow" in posting.description_raw

    def test_tags_from_skill_set_list(self) -> None:
        crawler = KakaoCareerCrawler()
        job = SAMPLE_JOB_LIST["jobList"][0]
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert "Python" in posting.tags
        assert "TensorFlow" in posting.tags
        assert "PyTorch" in posting.tags
        assert "Elasticsearch" in posting.tags

    def test_location_field(self) -> None:
        crawler = KakaoCareerCrawler()
        job = SAMPLE_JOB_LIST["jobList"][0]
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert posting.location == "판교"

    def test_employment_type_field(self) -> None:
        crawler = KakaoCareerCrawler()
        job = SAMPLE_JOB_LIST["jobList"][0]
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert posting.employment_type == "정규직"

    def test_posted_at_parsed(self) -> None:
        crawler = KakaoCareerCrawler()
        job = SAMPLE_JOB_LIST["jobList"][0]
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert posting.posted_at is not None
        assert posting.posted_at.year == 2026
        assert posting.posted_at.month == 2
        assert posting.posted_at.day == 10

    def test_none_qualification_maps_to_none(self) -> None:
        crawler = KakaoCareerCrawler()
        posting = crawler._job_to_posting(SAMPLE_JOB_NO_QUALIFICATION)

        assert posting is not None
        assert posting.requirements_raw is None

    def test_empty_skill_set_list_gives_empty_tags(self) -> None:
        crawler = KakaoCareerCrawler()
        posting = crawler._job_to_posting(SAMPLE_JOB_WITH_PII)

        assert posting is not None
        assert posting.tags == []

    def test_pii_masked_in_description(self) -> None:
        crawler = KakaoCareerCrawler()
        posting = crawler._job_to_posting(SAMPLE_JOB_WITH_PII)

        assert posting is not None
        assert "hr@kakao.com" not in posting.description_raw
        assert "010-1234-5678" not in posting.description_raw
        assert "[EMAIL]" in posting.description_raw
        assert "[PHONE]" in posting.description_raw

    def test_missing_real_id_returns_none(self) -> None:
        crawler = KakaoCareerCrawler()
        job = {
            "jobOfferTitle": "No ID Job",
            "introduction": "some intro",
            "workContentDesc": "some work",
        }
        posting = crawler._job_to_posting(job)
        assert posting is None

    def test_empty_title_returns_none(self) -> None:
        crawler = KakaoCareerCrawler()
        job = {
            "realId": "P-00000",
            "jobOfferTitle": "",
            "introduction": "intro",
            "workContentDesc": "work",
        }
        posting = crawler._job_to_posting(job)
        assert posting is None


class TestKakaoFullCrawl:

    @responses.activate
    def test_full_crawl_returns_postings(self) -> None:
        responses.add(
            responses.GET,
            KAKAO_JOB_LIST_URL,
            json=SAMPLE_JOB_LIST,
            status=200,
        )

        crawler = KakaoCareerCrawler()
        postings = crawler.crawl()

        assert len(postings) == 2
        assert all(p.source_platform == "kakao_career" for p in postings)
        assert all(p.company_name == "카카오" for p in postings)

    @responses.activate
    def test_full_crawl_source_urls(self) -> None:
        responses.add(
            responses.GET,
            KAKAO_JOB_LIST_URL,
            json=SAMPLE_JOB_LIST,
            status=200,
        )

        crawler = KakaoCareerCrawler()
        postings = crawler.crawl()

        urls = {p.source_url for p in postings}
        assert "https://careers.kakao.com/jobs/P-14318" in urls
        assert "https://careers.kakao.com/jobs/P-14400" in urls

    @responses.activate
    def test_full_crawl_api_error_returns_empty(self) -> None:
        responses.add(
            responses.GET,
            KAKAO_JOB_LIST_URL,
            status=500,
        )

        crawler = KakaoCareerCrawler()
        postings = crawler.crawl()
        assert postings == []

    @responses.activate
    def test_full_crawl_empty_list(self) -> None:
        responses.add(
            responses.GET,
            KAKAO_JOB_LIST_URL,
            json={"jobList": []},
            status=200,
        )

        crawler = KakaoCareerCrawler()
        postings = crawler.crawl()
        assert postings == []
