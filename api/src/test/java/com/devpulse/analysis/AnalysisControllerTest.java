package com.devpulse.analysis;

import com.devpulse.analysis.SkillRankingResponse.SkillRankItem;
import com.devpulse.company.CompanyCategory;
import com.devpulse.posting.PositionType;
import com.devpulse.analysis.AnalysisService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.BDDMockito.given;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(AnalysisController.class)
class AnalysisControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockitoBean
    private AnalysisService analysisService;

    @Test
    @DisplayName("GET /api/v1/analysis/skill-ranking — 스킬 랭킹 조회")
    void getSkillRanking() throws Exception {
        SkillRankingResponse response = new SkillRankingResponse(
                LocalDate.of(2026, 3, 4), 523, PositionType.BACKEND,
                List.of(
                        new SkillRankItem(1, "Java", 465, 88.9, 0.76),
                        new SkillRankItem(2, "Spring Boot", 429, 82.0, 0.71)
                )
        );
        given(analysisService.getSkillRanking(eq(PositionType.BACKEND), isNull(), eq(false), eq(20)))
                .willReturn(response);

        mockMvc.perform(get("/api/v1/analysis/skill-ranking")
                        .param("positionType", "BACKEND"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalPostings").value(523))
                .andExpect(jsonPath("$.positionType").value("BACKEND"))
                .andExpect(jsonPath("$.rankings[0].skill").value("Java"))
                .andExpect(jsonPath("$.rankings[0].percentage").value(88.9))
                .andExpect(jsonPath("$.rankings[1].skill").value("Spring Boot"));
    }

    @Test
    @DisplayName("GET /api/v1/analysis/company-profile/{id} — 회사 프로필 조회")
    void getCompanyProfile() throws Exception {
        CompanyProfileResponse response = new CompanyProfileResponse(
                1L, "네이버", CompanyCategory.BIGTECH, 50,
                List.of(
                        new CompanyProfileResponse.SkillUsage("Java", 45, 90.0),
                        new CompanyProfileResponse.SkillUsage("Kotlin", 30, 60.0)
                ),
                Map.of(PositionType.BACKEND, 40L, PositionType.FDE, 10L)
        );
        given(analysisService.getCompanyProfile(1L)).willReturn(response);

        mockMvc.perform(get("/api/v1/analysis/company-profile/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.companyName").value("네이버"))
                .andExpect(jsonPath("$.totalPostings").value(50))
                .andExpect(jsonPath("$.topSkills[0].skill").value("Java"))
                .andExpect(jsonPath("$.positionBreakdown.BACKEND").value(40));
    }

    @Test
    @DisplayName("GET /api/v1/analysis/company-profile/{id} — 존재하지 않는 회사 404")
    void getCompanyProfile_notFound() throws Exception {
        given(analysisService.getCompanyProfile(999L))
                .willThrow(new AnalysisService.CompanyNotFoundException(999L));

        mockMvc.perform(get("/api/v1/analysis/company-profile/999"))
                .andExpect(status().isNotFound());
    }

    @Test
    @DisplayName("GET /api/v1/analysis/position-comparison — 포지션 비교")
    void getPositionComparison() throws Exception {
        PositionComparisonResponse response = new PositionComparisonResponse(
                List.of(
                        new PositionComparisonResponse.PositionSkillProfile(
                                PositionType.BACKEND, 100,
                                List.of(new SkillRankItem(1, "Java", 90, 90.0, 0.78))
                        ),
                        new PositionComparisonResponse.PositionSkillProfile(
                                PositionType.FDE, 40,
                                List.of(new SkillRankItem(1, "React", 30, 75.0, 0.60))
                        )
                ),
                List.of("Docker"),
                Map.of("BACKEND", List.of("Spring Boot"), "FDE", List.of("React"))
        );
        given(analysisService.getPositionComparison(eq(List.of(PositionType.BACKEND, PositionType.FDE)), eq(20)))
                .willReturn(response);

        mockMvc.perform(get("/api/v1/analysis/position-comparison")
                        .param("positions", "BACKEND", "FDE"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.positions").isArray())
                .andExpect(jsonPath("$.positions[0].positionType").value("BACKEND"))
                .andExpect(jsonPath("$.commonSkills[0]").value("Docker"))
                .andExpect(jsonPath("$.uniqueSkills.BACKEND[0]").value("Spring Boot"));
    }

    @Test
    @DisplayName("POST /api/v1/analysis/gap — 갭 분석")
    void analyzeGap() throws Exception {
        GapAnalysisResponse response = new GapAnalysisResponse(
                PositionType.BACKEND, 50,
                List.of(
                        new GapAnalysisResponse.SkillGap("Java", 1, 90.0, "OWNED", "MAINTAINED"),
                        new GapAnalysisResponse.SkillGap("Kubernetes", 3, 40.0, "NOT_OWNED", "CRITICAL")
                )
        );
        given(analysisService.analyzeGap(any(), eq(PositionType.BACKEND))).willReturn(response);

        GapAnalysisRequest request = new GapAnalysisRequest(List.of(
                new GapAnalysisRequest.UserSkill("Java", GapAnalysisRequest.SkillStatus.OWNED),
                new GapAnalysisRequest.UserSkill("Kubernetes", GapAnalysisRequest.SkillStatus.NOT_OWNED)
        ));

        mockMvc.perform(post("/api/v1/analysis/gap")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.matchPercentage").value(50))
                .andExpect(jsonPath("$.gaps[0].skill").value("Java"))
                .andExpect(jsonPath("$.gaps[0].priority").value("MAINTAINED"))
                .andExpect(jsonPath("$.gaps[1].priority").value("CRITICAL"));
    }

    @Test
    @DisplayName("POST /api/v1/analysis/gap — 빈 요청 400 Bad Request")
    void analyzeGap_emptyRequest() throws Exception {
        mockMvc.perform(post("/api/v1/analysis/gap")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"mySkills\": []}"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("GET /api/v1/analysis/skill-mindmap — 스킬 마인드맵 키워드 조회")
    void getSkillMindmap_returnsKeywordData() throws Exception {
        SkillMindmapResponse response = new SkillMindmapResponse(
                "Redis", "레디스", "database",
                List.of("캐싱 전략", "TTL", "캐시 미스"),
                Map.of("keywords", List.of(
                        new SkillMindmapResponse.KeywordNode("캐싱 전략", 15, 22.1),
                        new SkillMindmapResponse.KeywordNode("TTL", 10, 14.7)
                )),
                68
        );
        given(analysisService.getSkillMindmap("Redis")).willReturn(response);

        mockMvc.perform(get("/api/v1/analysis/skill-mindmap").param("skill", "Redis"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.skillName").value("Redis"))
                .andExpect(jsonPath("$.keywordGroups.keywords[0].keyword").value("캐싱 전략"));
    }
}
