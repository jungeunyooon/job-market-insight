package com.devpulse.posting;

import com.devpulse.posting.PostingDetailResponse;
import com.devpulse.posting.PostingResponse;
import com.devpulse.company.CompanyCategory;
import com.devpulse.posting.PostingStatus;
import com.devpulse.posting.PositionType;
import com.devpulse.posting.PostingService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@Tag(name = "채용공고", description = "채용공고 조회 및 필터링 API")
@RestController
@RequestMapping("/api/v1/postings")
@RequiredArgsConstructor
public class PostingController {

    private final PostingService postingService;

    @Operation(
            summary = "채용공고 목록 조회",
            description = "포지션, 회사 카테고리, 상태, 스킬, 날짜 범위 등 다양한 조건으로 채용공고를 필터링하여 페이지네이션 조회합니다."
    )
    @GetMapping
    public ResponseEntity<Page<PostingResponse>> getPostings(
            @Parameter(description = "포지션 타입 필터 (BACKEND, FDE, PRODUCT 등)") @RequestParam(required = false) PositionType positionType,
            @Parameter(description = "회사 카테고리 필터 (복수 선택 가능)") @RequestParam(required = false) List<CompanyCategory> companyCategory,
            @Parameter(description = "공고 상태 필터 (ACTIVE, CLOSED 등)") @RequestParam(required = false) List<PostingStatus> status,
            @Parameter(description = "스킬명 필터 (복수 선택 가능, 예: Java, Spring)") @RequestParam(required = false) List<String> skillName,
            @Parameter(description = "조회 시작일 (yyyy-MM-dd)") @RequestParam(required = false) LocalDate dateFrom,
            @Parameter(description = "조회 종료일 (yyyy-MM-dd)") @RequestParam(required = false) LocalDate dateTo,
            @PageableDefault(size = 20, sort = "postedAt", direction = Sort.Direction.DESC) Pageable pageable
    ) {
        Page<PostingResponse> result = postingService.findAll(
                positionType, companyCategory, status, skillName, dateFrom, dateTo, pageable
        );
        return ResponseEntity.ok(result);
    }

    @Operation(
            summary = "채용공고 상세 조회",
            description = "공고 ID로 상세 정보를 조회합니다. 매칭된 스킬, LLM 키워드, 정규화된 요구사항 등 포함."
    )
    @GetMapping("/{id}")
    public ResponseEntity<PostingDetailResponse> getPosting(
            @Parameter(description = "채용공고 ID") @PathVariable Long id
    ) {
        return ResponseEntity.ok(postingService.findById(id));
    }
}
