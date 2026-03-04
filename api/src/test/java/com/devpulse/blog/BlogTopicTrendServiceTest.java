package com.devpulse.blog;

import com.devpulse.blog.BlogTopicResponse;
import com.devpulse.blog.SkillCompanyDistributionResponse;
import com.devpulse.blog.YearlyTrendResponse;
import com.devpulse.blog.BlogSkillRepository;
import com.devpulse.blog.TechBlogPostRepository;
import com.devpulse.company.Company;
import com.devpulse.company.CompanyRepository;
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
import static org.mockito.BDDMockito.given;

@ExtendWith(MockitoExtension.class)
class BlogTopicTrendServiceTest {

    @Mock
    private BlogSkillRepository blogSkillRepository;

    @Mock
    private TechBlogPostRepository techBlogPostRepository;

    @Mock
    private CompanyRepository companyRepository;

    @InjectMocks
    private BlogTopicTrendService service;

    @Nested
    @DisplayName("getCompanyBlogTopics")
    class GetCompanyBlogTopics {

        @Test
        @DisplayName("회사별 블로그 토픽 랭킹 조회")
        void companyBlogTopics_success() {
            Company company = Company.builder().name("카카오").build();
            given(companyRepository.findById(1L)).willReturn(Optional.of(company));
            given(techBlogPostRepository.countByCompanyId(1L)).willReturn(50L);

            List<Object[]> rows = List.of(
                    new Object[]{"Kotlin", 20L},
                    new Object[]{"Spring Boot", 15L},
                    new Object[]{"Kafka", 8L}
            );
            given(blogSkillRepository.findSkillRankingByCompanyAndYear(1L, null, null))
                    .willReturn(rows);

            BlogTopicResponse result = service.getCompanyBlogTopics(1L, null, null, 20);

            assertThat(result.companyName()).isEqualTo("카카오");
            assertThat(result.totalPosts()).isEqualTo(50);
            assertThat(result.skills()).hasSize(3);
            assertThat(result.skills().getFirst().skill()).isEqualTo("Kotlin");
            assertThat(result.skills().getFirst().rank()).isEqualTo(1);
            assertThat(result.skills().getFirst().postCount()).isEqualTo(20);
            assertThat(result.skills().getFirst().percentage()).isEqualTo(40.0);
        }

        @Test
        @DisplayName("연도 필터 적용")
        void companyBlogTopics_withYearFilter() {
            Company company = Company.builder().name("네이버").build();
            given(companyRepository.findById(2L)).willReturn(Optional.of(company));
            given(techBlogPostRepository.countByCompanyId(2L)).willReturn(30L);

            List<Object[]> rows = List.<Object[]>of(
                    new Object[]{"Java", 10L}
            );
            given(blogSkillRepository.findSkillRankingByCompanyAndYear(2L, 2024, 2025))
                    .willReturn(rows);

            BlogTopicResponse result = service.getCompanyBlogTopics(2L, 2024, 2025, 20);

            assertThat(result.skills()).hasSize(1);
            assertThat(result.skills().getFirst().skill()).isEqualTo("Java");
        }

        @Test
        @DisplayName("존재하지 않는 회사 → 예외")
        void companyBlogTopics_notFound() {
            given(companyRepository.findById(999L)).willReturn(Optional.empty());

            assertThatThrownBy(() -> service.getCompanyBlogTopics(999L, null, null, 20))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("999");
        }

        @Test
        @DisplayName("빈 결과")
        void companyBlogTopics_empty() {
            Company company = Company.builder().name("테스트").build();
            given(companyRepository.findById(1L)).willReturn(Optional.of(company));
            given(techBlogPostRepository.countByCompanyId(1L)).willReturn(0L);
            given(blogSkillRepository.findSkillRankingByCompanyAndYear(1L, null, null))
                    .willReturn(List.of());

            BlogTopicResponse result = service.getCompanyBlogTopics(1L, null, null, 20);

            assertThat(result.skills()).isEmpty();
            assertThat(result.totalPosts()).isZero();
        }
    }

    @Nested
    @DisplayName("getYearlySkillTrend")
    class GetYearlySkillTrend {

        @Test
        @DisplayName("연도별 스킬 트렌드")
        void yearlyTrend_success() {
            List<Object[]> rows = List.of(
                    new Object[]{2023, "Kafka", 10L},
                    new Object[]{2023, "Spring Boot", 8L},
                    new Object[]{2024, "Kafka", 15L},
                    new Object[]{2024, "Kotlin", 12L}
            );
            given(blogSkillRepository.findYearlySkillTrend(2023, 2024)).willReturn(rows);

            YearlyTrendResponse result = service.getYearlySkillTrend(2023, 2024, 10);

            assertThat(result.yearlyData()).hasSize(2);

            var year2023 = result.yearlyData().get(0);
            assertThat(year2023.year()).isEqualTo(2023);
            assertThat(year2023.skills()).hasSize(2);
            assertThat(year2023.skills().getFirst().skill()).isEqualTo("Kafka");

            var year2024 = result.yearlyData().get(1);
            assertThat(year2024.year()).isEqualTo(2024);
            assertThat(year2024.skills()).hasSize(2);
        }

        @Test
        @DisplayName("빈 트렌드")
        void yearlyTrend_empty() {
            given(blogSkillRepository.findYearlySkillTrend(null, null)).willReturn(List.of());

            YearlyTrendResponse result = service.getYearlySkillTrend(null, null, 10);

            assertThat(result.yearlyData()).isEmpty();
        }
    }

    @Nested
    @DisplayName("getSkillCompanyDistribution")
    class GetSkillCompanyDistribution {

        @Test
        @DisplayName("스킬별 회사 분포")
        void distribution_success() {
            List<Object[]> rows = List.of(
                    new Object[]{"카카오", 15L},
                    new Object[]{"네이버", 12L},
                    new Object[]{"배민", 5L}
            );
            given(blogSkillRepository.findCompanyDistributionBySkill("Kafka", null, null))
                    .willReturn(rows);

            SkillCompanyDistributionResponse result = service.getSkillCompanyDistribution("Kafka", null, null);

            assertThat(result.skillName()).isEqualTo("Kafka");
            assertThat(result.companies()).hasSize(3);
            assertThat(result.companies().getFirst().company()).isEqualTo("카카오");
            assertThat(result.companies().getFirst().postCount()).isEqualTo(15);
        }

        @Test
        @DisplayName("빈 분포")
        void distribution_empty() {
            given(blogSkillRepository.findCompanyDistributionBySkill("Unknown", null, null))
                    .willReturn(List.of());

            SkillCompanyDistributionResponse result = service.getSkillCompanyDistribution("Unknown", null, null);

            assertThat(result.companies()).isEmpty();
        }
    }
}
