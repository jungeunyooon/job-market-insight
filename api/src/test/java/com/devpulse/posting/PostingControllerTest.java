package com.devpulse.posting;

import com.devpulse.posting.PostingDetailResponse;
import com.devpulse.posting.PostingDetailResponse.CompanyInfo;
import com.devpulse.posting.PostingDetailResponse.SkillInfo;
import com.devpulse.posting.PostingResponse;
import com.devpulse.company.CompanyCategory;
import com.devpulse.posting.PostingStatus;
import com.devpulse.posting.PositionType;
import com.devpulse.posting.PostingService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.BDDMockito.given;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(PostingController.class)
class PostingControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private PostingService postingService;

    @Test
    @DisplayName("GET /api/v1/postings — 기본 조회 200 OK")
    void getPostings_default() throws Exception {
        PostingResponse response = new PostingResponse(
                1L, "백엔드 개발자", "네이버", CompanyCategory.BIGTECH,
                PositionType.BACKEND, "3년 이상", "판교",
                PostingStatus.ACTIVE, "wanted", "https://wanted.co.kr/wd/1",
                List.of("Java", "Spring Boot"),
                LocalDateTime.of(2026, 3, 1, 0, 0),
                LocalDateTime.of(2026, 3, 1, 12, 0)
        );
        given(postingService.findAll(any(), any(), any(), any(), any(), any(), any()))
                .willReturn(new PageImpl<>(List.of(response), PageRequest.of(0, 20), 1));

        mockMvc.perform(get("/api/v1/postings"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content[0].title").value("백엔드 개발자"))
                .andExpect(jsonPath("$.content[0].companyName").value("네이버"))
                .andExpect(jsonPath("$.content[0].skills[0]").value("Java"))
                .andExpect(jsonPath("$.totalElements").value(1));
    }

    @Test
    @DisplayName("GET /api/v1/postings?positionType=BACKEND — 필터 파라미터 전달")
    void getPostings_withPositionType() throws Exception {
        given(postingService.findAll(eq(PositionType.BACKEND), any(), any(), any(), any(), any(), any()))
                .willReturn(new PageImpl<>(List.of(), PageRequest.of(0, 20), 0));

        mockMvc.perform(get("/api/v1/postings")
                        .param("positionType", "BACKEND"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalElements").value(0));
    }

    @Test
    @DisplayName("GET /api/v1/postings/{id} — 단건 조회 200 OK")
    void getPosting_byId() throws Exception {
        PostingDetailResponse detail = new PostingDetailResponse(
                1L, "백엔드 개발자",
                new CompanyInfo(1L, "네이버", CompanyCategory.BIGTECH),
                PositionType.BACKEND, "3년 이상",
                "Java, Spring Boot 기반 서버 개발",
                "판교", 5000, 8000,
                PostingStatus.ACTIVE, "wanted", "https://wanted.co.kr/wd/1",
                List.of(new SkillInfo(1L, "Java", "language", true, false)),
                LocalDateTime.of(2026, 3, 1, 0, 0),
                null,
                LocalDateTime.of(2026, 3, 1, 12, 0)
        );
        given(postingService.findById(1L)).willReturn(detail);

        mockMvc.perform(get("/api/v1/postings/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.title").value("백엔드 개발자"))
                .andExpect(jsonPath("$.company.name").value("네이버"))
                .andExpect(jsonPath("$.skills[0].name").value("Java"))
                .andExpect(jsonPath("$.skills[0].isRequired").value(true));
    }

    @Test
    @DisplayName("GET /api/v1/postings/{id} — 존재하지 않는 공고 404")
    void getPosting_notFound() throws Exception {
        given(postingService.findById(999L))
                .willThrow(new PostingService.PostingNotFoundException(999L));

        mockMvc.perform(get("/api/v1/postings/999"))
                .andExpect(status().isNotFound());
    }
}
