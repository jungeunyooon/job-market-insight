"""Tests for extractive summarizer."""

from nlp.summarizer import extractive_summary, _split_sentences, _score_sentence


class TestExtractSummary:
    def test_empty_text(self):
        assert extractive_summary("") == ""
        assert extractive_summary(None) == ""

    def test_short_text_returned_as_is(self):
        text = "First sentence. Second sentence. Third sentence."
        result = extractive_summary(text, max_sentences=5)
        assert "First sentence" in result

    def test_selects_top_sentences(self):
        text = (
            "Our team implemented a new caching architecture. "
            "The weather was nice that day. "
            "Redis cache hit rate improved by 95% after optimization. "
            "We had lunch at noon. "
            "The server performance increased 3배 after the deployment."
        )
        result = extractive_summary(text, max_sentences=2)
        # Should select technical sentences, not fluff
        assert "cache" in result.lower() or "performance" in result.lower() or "Redis" in result

    def test_preserves_original_order(self):
        text = (
            "Architecture design was the first step. "
            "Some filler text here. "
            "Performance testing showed 10x improvement."
        )
        result = extractive_summary(text, max_sentences=2)
        # Sentences should be in original order
        if "Architecture" in result and "Performance" in result:
            assert result.index("Architecture") < result.index("Performance")

    def test_handles_korean_text(self):
        text = "Redis 캐시 아키텍처를 도입했습니다. 날씨가 좋았습니다. 성능이 3배 개선되었습니다."
        result = extractive_summary(text, max_sentences=2)
        assert len(result) > 0


class TestSplitSentences:
    def test_splits_english(self):
        result = _split_sentences("First sentence. Second sentence. Third.")
        assert len(result) >= 2

    def test_strips_html(self):
        result = _split_sentences("<p>Hello world.</p> <b>Test sentence here.</b>")
        assert all("<" not in s for s in result)

    def test_empty_input(self):
        assert _split_sentences("") == []


class TestScoreSentence:
    def test_technical_keywords_increase_score(self):
        tech = _score_sentence("Redis cache optimization improved performance", 5, 10)
        plain = _score_sentence("The weather was very nice today indeed", 5, 10)
        assert tech > plain

    def test_first_sentence_bonus(self):
        score_first = _score_sentence("Some text here about things", 0, 10)
        score_middle = _score_sentence("Some text here about things", 5, 10)
        assert score_first > score_middle

    def test_numbers_bonus(self):
        with_numbers = _score_sentence("성능이 95% 향상되었습니다", 5, 10)
        without_numbers = _score_sentence("성능이 향상되었습니다", 5, 10)
        assert with_numbers > without_numbers
