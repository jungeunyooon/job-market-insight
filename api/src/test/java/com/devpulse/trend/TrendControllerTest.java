package com.devpulse.trend;

import com.devpulse.trend.BuzzHiringGapResponse;
import com.devpulse.trend.BuzzHiringGapResponse.BuzzHiringGap;
import com.devpulse.trend.BuzzHiringGapResponse.Classification;
import com.devpulse.trend.TrendRankingResponse;
import com.devpulse.trend.TrendRankingResponse.TrendRankItem;
import com.devpulse.trend.TrendSource;
import com.devpulse.trend.BuzzHiringGapService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDate;
import java.util.List;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.BDDMockito.given;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(TrendController.class)
class TrendControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private BuzzHiringGapService buzzHiringGapService;

    @Test
    @DisplayName("GET /api/v1/analysis/trend-ranking — 트렌드 랭킹 조회")
    void getTrendRanking() throws Exception {
        TrendRankingResponse response = new TrendRankingResponse(
                LocalDate.of(2026, 3, 4), "GEEKNEWS", "LAST_30_DAYS", 247,
                List.of(
                        new TrendRankItem(1, "LangChain", 47, 19.0),
                        new TrendRankItem(2, "Rust", 35, 14.2)
                )
        );
        given(buzzHiringGapService.getTrendRanking(eq(TrendSource.GEEKNEWS), eq(30), eq(20)))
                .willReturn(response);

        mockMvc.perform(get("/api/v1/analysis/trend-ranking")
                        .param("source", "GEEKNEWS"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalPosts").value(247))
                .andExpect(jsonPath("$.source").value("GEEKNEWS"))
                .andExpect(jsonPath("$.rankings[0].skill").value("LangChain"))
                .andExpect(jsonPath("$.rankings[0].mentions").value(47));
    }

    @Test
    @DisplayName("GET /api/v1/analysis/buzz-vs-hiring — Buzz vs Hiring Gap 분석")
    void getBuzzVsHiring() throws Exception {
        BuzzHiringGapResponse response = new BuzzHiringGapResponse(
                LocalDate.of(2026, 3, 4), "LAST_30_DAYS", "ALL", 247, 523,
                List.of(
                        new BuzzHiringGap("Kafka", 12, 8, 251, 5, 48.0,
                                Classification.ADOPTED, "Kafka: 커뮤니티 관심과 채용 수요 모두 높음"),
                        new BuzzHiringGap("LangChain", 47, 2, 16, 34, 3.1,
                                Classification.OVERHYPED, "LangChain: 커뮤니티 관심 대비 채용 수요 낮음"),
                        new BuzzHiringGap("Java", 5, 22, 465, 1, 88.9,
                                Classification.ESTABLISHED, "Java: 더 이상 화제가 아니지만 채용 시장의 기본기")
                )
        );
        given(buzzHiringGapService.analyzeBuzzVsHiring(eq(20), eq(30))).willReturn(response);

        mockMvc.perform(get("/api/v1/analysis/buzz-vs-hiring"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalTrendPosts").value(247))
                .andExpect(jsonPath("$.totalJobPostings").value(523))
                .andExpect(jsonPath("$.gaps[0].skill").value("Kafka"))
                .andExpect(jsonPath("$.gaps[0].classification").value("ADOPTED"))
                .andExpect(jsonPath("$.gaps[1].classification").value("OVERHYPED"))
                .andExpect(jsonPath("$.gaps[2].classification").value("ESTABLISHED"));
    }

    @Test
    @DisplayName("GET /api/v1/analysis/trend-ranking — 기본 파라미터")
    void getTrendRanking_defaults() throws Exception {
        TrendRankingResponse response = new TrendRankingResponse(
                LocalDate.of(2026, 3, 4), "ALL", "LAST_30_DAYS", 0, List.of()
        );
        given(buzzHiringGapService.getTrendRanking(isNull(), eq(30), eq(20)))
                .willReturn(response);

        mockMvc.perform(get("/api/v1/analysis/trend-ranking"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.source").value("ALL"));
    }
}
