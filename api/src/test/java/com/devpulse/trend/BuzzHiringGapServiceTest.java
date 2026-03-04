package com.devpulse.trend;

import com.devpulse.trend.BuzzHiringGapResponse;
import com.devpulse.trend.BuzzHiringGapResponse.Classification;
import com.devpulse.trend.TrendRankingResponse;
import com.devpulse.posting.PostingSkillRepository;
import com.devpulse.trend.TrendSkillRepository;
import com.devpulse.trend.TrendSource;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.BDDMockito.given;

@ExtendWith(MockitoExtension.class)
class BuzzHiringGapServiceTest {

    @Mock
    private TrendSkillRepository trendSkillRepository;

    @Mock
    private PostingSkillRepository postingSkillRepository;

    @InjectMocks
    private BuzzHiringGapService service;

    @Nested
    @DisplayName("getTrendRanking")
    class GetTrendRanking {

        @Test
        @DisplayName("GeekNews 트렌드 랭킹 조회")
        void trendRanking_geeknews() {
            List<Object[]> rows = List.of(
                    new Object[]{"LangChain", 47L},
                    new Object[]{"Rust", 35L},
                    new Object[]{"Kafka", 12L}
            );
            given(trendSkillRepository.findSkillRankingBySourceSince(eq(TrendSource.GEEKNEWS), any()))
                    .willReturn(rows);
            given(trendSkillRepository.countTrendPostsSince(any())).willReturn(247L);

            TrendRankingResponse result = service.getTrendRanking(TrendSource.GEEKNEWS, 30, 20);

            assertThat(result.totalPosts()).isEqualTo(247);
            assertThat(result.source()).isEqualTo("GEEKNEWS");
            assertThat(result.rankings()).hasSize(3);
            assertThat(result.rankings().getFirst().skill()).isEqualTo("LangChain");
            assertThat(result.rankings().getFirst().mentions()).isEqualTo(47);
        }

        @Test
        @DisplayName("빈 트렌드 결과")
        void trendRanking_empty() {
            given(trendSkillRepository.findSkillRankingBySourceSince(any(), any()))
                    .willReturn(List.of());
            given(trendSkillRepository.countTrendPostsSince(any())).willReturn(0L);

            TrendRankingResponse result = service.getTrendRanking(TrendSource.GEEKNEWS, 30, 20);

            assertThat(result.totalPosts()).isZero();
            assertThat(result.rankings()).isEmpty();
        }
    }

    @Nested
    @DisplayName("analyzeBuzzVsHiring")
    class AnalyzeBuzzVsHiring {

        @Test
        @DisplayName("2x2 분류 — OVERHYPED, ADOPTED, ESTABLISHED")
        void buzzVsHiring_classification() {
            // Trend: LangChain 많이 언급, Kafka 중간, Java 거의 안 나옴
            List<Object[]> trendRows = List.of(
                    new Object[]{"LangChain", 47L},
                    new Object[]{"Kafka", 12L},
                    new Object[]{"Java", 5L}
            );
            given(trendSkillRepository.findSkillRankingSince(any())).willReturn(trendRows);
            given(trendSkillRepository.countTrendPostsSince(any())).willReturn(247L);

            // Job: Java 압도적, Kafka 높음, LangChain 거의 없음
            List<Object[]> jobRows = List.of(
                    new Object[]{"Java", 465L, 350L},
                    new Object[]{"Kafka", 251L, 100L},
                    new Object[]{"LangChain", 16L, 5L}
            );
            given(postingSkillRepository.findSkillRankingWithFilters(isNull(), eq(false), isNull()))
                    .willReturn(jobRows);
            given(postingSkillRepository.countPostingsWithFilters(isNull(), eq(false), isNull()))
                    .willReturn(523L);

            BuzzHiringGapResponse result = service.analyzeBuzzVsHiring(20, 30);

            assertThat(result.totalTrendPosts()).isEqualTo(247);
            assertThat(result.totalJobPostings()).isEqualTo(523);
            assertThat(result.gaps()).isNotEmpty();

            // Find classifications
            var langchain = result.gaps().stream()
                    .filter(g -> g.skill().equals("LangChain")).findFirst().orElseThrow();
            var kafka = result.gaps().stream()
                    .filter(g -> g.skill().equals("Kafka")).findFirst().orElseThrow();
            var java = result.gaps().stream()
                    .filter(g -> g.skill().equals("Java")).findFirst().orElseThrow();

            // LangChain: trend 19% (HIGH), job 3.1% (LOW) → OVERHYPED
            assertThat(langchain.classification()).isEqualTo(Classification.OVERHYPED);

            // Kafka: trend 4.9% (LOW), job 48% (HIGH) → ESTABLISHED
            assertThat(kafka.classification()).isEqualTo(Classification.ESTABLISHED);

            // Java: trend 2% (LOW), job 88.9% (HIGH) → ESTABLISHED
            assertThat(java.classification()).isEqualTo(Classification.ESTABLISHED);
        }
    }

    @Nested
    @DisplayName("classify")
    class Classify {

        @Test
        @DisplayName("2x2 매트릭스 분류")
        void classifyMatrix() {
            assertThat(service.classify(10.0, 50.0)).isEqualTo(Classification.ADOPTED);
            assertThat(service.classify(10.0, 3.0)).isEqualTo(Classification.OVERHYPED);
            assertThat(service.classify(2.0, 50.0)).isEqualTo(Classification.ESTABLISHED);
            assertThat(service.classify(2.0, 3.0)).isEqualTo(Classification.EMERGING);
        }

        @Test
        @DisplayName("경계값 테스트")
        void classifyBoundary() {
            // Exactly at threshold
            assertThat(service.classify(5.0, 10.0)).isEqualTo(Classification.ADOPTED);
            assertThat(service.classify(4.9, 9.9)).isEqualTo(Classification.EMERGING);
        }
    }
}
