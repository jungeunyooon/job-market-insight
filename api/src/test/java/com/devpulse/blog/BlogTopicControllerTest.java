package com.devpulse.blog;

import com.devpulse.blog.BlogTopicResponse;
import com.devpulse.blog.BlogTopicResponse.BlogTopicItem;
import com.devpulse.blog.SkillCompanyDistributionResponse;
import com.devpulse.blog.SkillCompanyDistributionResponse.CompanyCount;
import com.devpulse.blog.YearlyTrendResponse;
import com.devpulse.blog.YearlyTrendResponse.SkillCount;
import com.devpulse.blog.YearlyTrendResponse.YearlySkillData;
import com.devpulse.blog.BlogTopicTrendService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDate;
import java.util.List;

import static org.mockito.BDDMockito.given;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(BlogTopicController.class)
class BlogTopicControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private BlogTopicTrendService blogTopicTrendService;

    @Test
    @DisplayName("GET /api/v1/analysis/blog-topics/company/{id} — 회사별 블로그 토픽")
    void getCompanyBlogTopics() throws Exception {
        var response = new BlogTopicResponse(
                LocalDate.now(), "카카오", 1L, 50,
                List.of(new BlogTopicItem(1, "Kotlin", 20, 40.0),
                        new BlogTopicItem(2, "Spring Boot", 15, 30.0))
        );
        given(blogTopicTrendService.getCompanyBlogTopics(1L, null, null, 20))
                .willReturn(response);

        mockMvc.perform(get("/api/v1/analysis/blog-topics/company/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.companyName").value("카카오"))
                .andExpect(jsonPath("$.totalPosts").value(50))
                .andExpect(jsonPath("$.skills[0].skill").value("Kotlin"))
                .andExpect(jsonPath("$.skills[0].rank").value(1));
    }

    @Test
    @DisplayName("GET /api/v1/analysis/blog-topics/yearly-trend — 연도별 트렌드")
    void getYearlySkillTrend() throws Exception {
        var response = new YearlyTrendResponse(
                LocalDate.now(), "2023-2024",
                List.of(
                        new YearlySkillData(2023, List.of(new SkillCount("Kafka", 10))),
                        new YearlySkillData(2024, List.of(new SkillCount("Kafka", 15)))
                )
        );
        given(blogTopicTrendService.getYearlySkillTrend(2023, 2024, 10))
                .willReturn(response);

        mockMvc.perform(get("/api/v1/analysis/blog-topics/yearly-trend")
                        .param("fromYear", "2023")
                        .param("toYear", "2024"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.period").value("2023-2024"))
                .andExpect(jsonPath("$.yearlyData[0].year").value(2023))
                .andExpect(jsonPath("$.yearlyData[0].skills[0].skill").value("Kafka"));
    }

    @Test
    @DisplayName("GET /api/v1/analysis/blog-topics/skill/{name} — 스킬별 회사 분포")
    void getSkillCompanyDistribution() throws Exception {
        var response = new SkillCompanyDistributionResponse(
                LocalDate.now(), "Kafka", "ALL",
                List.of(new CompanyCount("카카오", 15), new CompanyCount("네이버", 12))
        );
        given(blogTopicTrendService.getSkillCompanyDistribution("Kafka", null, null))
                .willReturn(response);

        mockMvc.perform(get("/api/v1/analysis/blog-topics/skill/Kafka"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.skillName").value("Kafka"))
                .andExpect(jsonPath("$.companies[0].company").value("카카오"))
                .andExpect(jsonPath("$.companies[0].postCount").value(15));
    }

    @Test
    @DisplayName("GET /api/v1/analysis/blog-topics/company/{id} — 존재하지 않는 회사")
    void getCompanyBlogTopics_notFound() throws Exception {
        given(blogTopicTrendService.getCompanyBlogTopics(999L, null, null, 20))
                .willThrow(new IllegalArgumentException("Company not found: 999"));

        mockMvc.perform(get("/api/v1/analysis/blog-topics/company/999"))
                .andExpect(status().isBadRequest());
    }
}
