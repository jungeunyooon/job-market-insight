package com.devpulse.analysis;

import com.devpulse.analysis.GapAnalysisRequest.SkillStatus;
import com.devpulse.company.Company;
import com.devpulse.company.CompanyCategory;
import com.devpulse.company.CompanyRepository;
import com.devpulse.posting.*;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.BDDMockito.given;

@ExtendWith(MockitoExtension.class)
class AnalysisServiceTest {

    @Mock
    private PostingSkillRepository postingSkillRepository;

    @Mock
    private JobPostingRepository jobPostingRepository;

    @Mock
    private CompanyRepository companyRepository;

    @InjectMocks
    private AnalysisService analysisService;

    @Nested
    @DisplayName("getSkillRanking")
    class GetSkillRanking {

        @Test
        @DisplayName("BACKEND 포지션 스킬 랭킹 — Top 3")
        void skillRanking_backend_top3() {
            // skill_name, count, required_count
            List<Object[]> rows = List.of(
                    new Object[]{"Java", 90L, 70L},
                    new Object[]{"Spring Boot", 80L, 60L},
                    new Object[]{"MySQL", 50L, 30L},
                    new Object[]{"Docker", 40L, 10L}
            );
            given(postingSkillRepository.findSkillRankingWithFilters(anyBoolean(), eq(PositionType.BACKEND), anyBoolean(), any(), anyList()))
                    .willReturn(rows);
            given(postingSkillRepository.countPostingsWithFilters(anyBoolean(), eq(PositionType.BACKEND), anyBoolean(), any(), anyList()))
                    .willReturn(100L);

            SkillRankingResponse result = analysisService.getSkillRanking(PositionType.BACKEND, null, false, 3);

            assertThat(result.totalPostings()).isEqualTo(100);
            assertThat(result.positionType()).isEqualTo(PositionType.BACKEND);
            assertThat(result.rankings()).hasSize(3);
            assertThat(result.rankings().getFirst().skill()).isEqualTo("Java");
            assertThat(result.rankings().getFirst().count()).isEqualTo(90);
            assertThat(result.rankings().getFirst().percentage()).isEqualTo(90.0);
            assertThat(result.rankings().getFirst().requiredRatio()).isEqualTo(0.78);
        }

        @Test
        @DisplayName("빈 결과")
        void skillRanking_empty() {
            given(postingSkillRepository.findSkillRankingWithFilters(anyBoolean(), any(), anyBoolean(), any(), anyList()))
                    .willReturn(List.of());
            given(postingSkillRepository.countPostingsWithFilters(anyBoolean(), any(), anyBoolean(), any(), anyList()))
                    .willReturn(0L);

            SkillRankingResponse result = analysisService.getSkillRanking(PositionType.BACKEND, null, false, 20);

            assertThat(result.totalPostings()).isZero();
            assertThat(result.rankings()).isEmpty();
        }

        @Test
        @DisplayName("companyCategory 필터 적용")
        void skillRanking_withCategoryFilter() {
            List<CompanyCategory> categories = List.of(CompanyCategory.BIGTECH, CompanyCategory.UNICORN);
            List<Object[]> rows = List.<Object[]>of(new Object[]{"Kotlin", 30L, 20L});
            given(postingSkillRepository.findSkillRankingWithFilters(anyBoolean(), any(), anyBoolean(), any(), eq(categories)))
                    .willReturn(rows);
            given(postingSkillRepository.countPostingsWithFilters(anyBoolean(), any(), anyBoolean(), any(), eq(categories)))
                    .willReturn(50L);

            SkillRankingResponse result = analysisService.getSkillRanking(null, categories, true, 20);

            assertThat(result.rankings()).hasSize(1);
            assertThat(result.rankings().getFirst().skill()).isEqualTo("Kotlin");
            assertThat(result.rankings().getFirst().percentage()).isEqualTo(60.0);
        }
    }

    @Nested
    @DisplayName("getCompanyProfile")
    class GetCompanyProfile {

        @Test
        @DisplayName("회사 프로필 조회 — 스킬 + 포지션 분포")
        void companyProfile_success() {
            Company company = Company.builder()
                    .name("네이버")
                    .category(CompanyCategory.BIGTECH)
                    .build();
            given(companyRepository.findById(1L)).willReturn(Optional.of(company));
            given(jobPostingRepository.countByCompanyId(1L)).willReturn(20L);
            given(postingSkillRepository.findSkillRankingByCompany(1L))
                    .willReturn(List.of(
                            new Object[]{"Java", 18L},
                            new Object[]{"Spring Boot", 15L}
                    ));
            given(jobPostingRepository.countByCompanyIdGroupByPositionType(1L))
                    .willReturn(List.of(
                            new Object[]{PositionType.BACKEND, 15L},
                            new Object[]{PositionType.FDE, 5L}
                    ));

            CompanyProfileResponse result = analysisService.getCompanyProfile(1L);

            assertThat(result.companyName()).isEqualTo("네이버");
            assertThat(result.totalPostings()).isEqualTo(20);
            assertThat(result.topSkills()).hasSize(2);
            assertThat(result.topSkills().getFirst().skill()).isEqualTo("Java");
            assertThat(result.topSkills().getFirst().percentage()).isEqualTo(90.0);
            assertThat(result.positionBreakdown()).containsEntry(PositionType.BACKEND, 15L);
        }

        @Test
        @DisplayName("존재하지 않는 회사 — CompanyNotFoundException")
        void companyProfile_notFound() {
            given(companyRepository.findById(999L)).willReturn(Optional.empty());

            assertThatThrownBy(() -> analysisService.getCompanyProfile(999L))
                    .isInstanceOf(AnalysisService.CompanyNotFoundException.class)
                    .hasMessageContaining("999");
        }
    }

    @Nested
    @DisplayName("getPositionComparison")
    class GetPositionComparison {

        @Test
        @DisplayName("BACKEND vs FDE 비교")
        void positionComparison() {
            // BACKEND ranking
            given(postingSkillRepository.findSkillRankingWithFilters(anyBoolean(), eq(PositionType.BACKEND), anyBoolean(), any(), anyList()))
                    .willReturn(List.of(
                            new Object[]{"Java", 90L, 70L},
                            new Object[]{"Spring Boot", 80L, 60L},
                            new Object[]{"Docker", 40L, 10L}
                    ));
            given(postingSkillRepository.countPostingsWithFilters(anyBoolean(), eq(PositionType.BACKEND), anyBoolean(), any(), anyList()))
                    .willReturn(100L);

            // FDE ranking
            given(postingSkillRepository.findSkillRankingWithFilters(anyBoolean(), eq(PositionType.FDE), anyBoolean(), any(), anyList()))
                    .willReturn(List.of(
                            new Object[]{"Java", 30L, 20L},
                            new Object[]{"React", 25L, 15L},
                            new Object[]{"Docker", 15L, 5L}
                    ));
            given(postingSkillRepository.countPostingsWithFilters(anyBoolean(), eq(PositionType.FDE), anyBoolean(), any(), anyList()))
                    .willReturn(40L);

            PositionComparisonResponse result = analysisService.getPositionComparison(
                    List.of(PositionType.BACKEND, PositionType.FDE), 20
            );

            assertThat(result.positions()).hasSize(2);
            assertThat(result.commonSkills()).contains("Java", "Docker");
            assertThat(result.uniqueSkills().get("BACKEND")).contains("Spring Boot");
            assertThat(result.uniqueSkills().get("FDE")).contains("React");
        }
    }

    @Nested
    @DisplayName("analyzeGap")
    class AnalyzeGap {

        @Test
        @DisplayName("갭 분석 — OWNED/LEARNING/NOT_OWNED 분류")
        void gapAnalysis() {
            List<Object[]> rows = List.of(
                    new Object[]{"Java", 90L, 70L},
                    new Object[]{"Spring Boot", 80L, 60L},
                    new Object[]{"Kubernetes", 60L, 10L},
                    new Object[]{"Kafka", 30L, 5L}
            );
            given(postingSkillRepository.findSkillRankingWithFilters(anyBoolean(), eq(PositionType.BACKEND), anyBoolean(), any(), anyList()))
                    .willReturn(rows);
            given(postingSkillRepository.countPostingsWithFilters(anyBoolean(), eq(PositionType.BACKEND), anyBoolean(), any(), anyList()))
                    .willReturn(100L);

            GapAnalysisRequest request = new GapAnalysisRequest(List.of(
                    new GapAnalysisRequest.UserSkill("Java", SkillStatus.OWNED),
                    new GapAnalysisRequest.UserSkill("Spring Boot", SkillStatus.LEARNING),
                    new GapAnalysisRequest.UserSkill("Kafka", SkillStatus.NOT_OWNED)
            ));

            GapAnalysisResponse result = analysisService.analyzeGap(request, PositionType.BACKEND);

            assertThat(result.positionType()).isEqualTo(PositionType.BACKEND);
            assertThat(result.matchPercentage()).isEqualTo(25); // 1 owned out of 4

            // Java — OWNED → MAINTAINED
            assertThat(result.gaps().get(0).userStatus()).isEqualTo("OWNED");
            assertThat(result.gaps().get(0).priority()).isEqualTo("MAINTAINED");

            // Spring Boot — LEARNING → CONTINUE
            assertThat(result.gaps().get(1).userStatus()).isEqualTo("LEARNING");
            assertThat(result.gaps().get(1).priority()).isEqualTo("CONTINUE");

            // Kubernetes — NOT_OWNED, rank 3 (<=5, >=50%) → CRITICAL
            assertThat(result.gaps().get(2).userStatus()).isEqualTo("NOT_OWNED");
            assertThat(result.gaps().get(2).priority()).isEqualTo("CRITICAL");

            // Kafka — NOT_OWNED, rank 4 (<=5, 30% < 50%) → HIGH (rank <= 5 but < 50%)
            assertThat(result.gaps().get(3).userStatus()).isEqualTo("NOT_OWNED");
        }
    }
}
