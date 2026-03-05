package com.devpulse.analysis;

import com.devpulse.company.CompanyCategory;
import com.devpulse.posting.PositionType;
import com.devpulse.analysis.AnalysisService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Tag(name = "분석", description = "스킬 랭킹, 회사 프로필, 포지션 비교, 갭 분석, 마인드맵 API")
@RestController
@RequestMapping("/api/v1/analysis")
@RequiredArgsConstructor
public class AnalysisController {

    private final AnalysisService analysisService;

    @Operation(
            summary = "스킬 랭킹 조회",
            description = "채용공고에서 가장 많이 요구되는 기술 스택을 랭킹으로 조회합니다. 포지션, 회사 카테고리, 마감 공고 포함 여부로 필터링 가능."
    )
    @GetMapping("/skill-ranking")
    public ResponseEntity<SkillRankingResponse> getSkillRanking(
            @Parameter(description = "포지션 타입 필터") @RequestParam(required = false) PositionType positionType,
            @Parameter(description = "회사 카테고리 필터 (복수 선택 가능)") @RequestParam(required = false) List<CompanyCategory> companyCategory,
            @Parameter(description = "마감된 공고 포함 여부") @RequestParam(defaultValue = "false") boolean includeClosedPostings,
            @Parameter(description = "상위 N개 반환 (기본 20)") @RequestParam(defaultValue = "20") int topN
    ) {
        return ResponseEntity.ok(
                analysisService.getSkillRanking(positionType, companyCategory, includeClosedPostings, topN)
        );
    }

    @Operation(
            summary = "회사 프로필 조회 (ID)",
            description = "회사 ID로 기술 스택 프로필을 조회합니다. 해당 회사의 공고에서 요구하는 스킬 빈도, 포지션 분포 등을 포함."
    )
    @GetMapping("/company-profile/{companyId}")
    public ResponseEntity<CompanyProfileResponse> getCompanyProfile(
            @Parameter(description = "회사 ID") @PathVariable Long companyId
    ) {
        return ResponseEntity.ok(analysisService.getCompanyProfile(companyId));
    }

    @Operation(
            summary = "회사 프로필 조회 (이름)",
            description = "회사명으로 기술 스택 프로필을 조회합니다."
    )
    @GetMapping("/company-profile")
    public ResponseEntity<CompanyProfileResponse> getCompanyProfileByName(
            @Parameter(description = "회사명 (예: 토스, 카카오)") @RequestParam String companyName
    ) {
        return ResponseEntity.ok(analysisService.getCompanyProfileByName(companyName));
    }

    @Operation(
            summary = "포지션 비교 분석",
            description = "2~3개 포지션의 기술 스택을 비교합니다. 각 포지션별 상위 스킬 랭킹과 겹치는 스킬을 보여줍니다."
    )
    @GetMapping("/position-comparison")
    public ResponseEntity<PositionComparisonResponse> getPositionComparison(
            @Parameter(description = "비교할 포지션 목록 (2~3개, 예: BACKEND,FDE)") @RequestParam List<PositionType> positions,
            @Parameter(description = "포지션별 상위 N개 스킬 (기본 20)") @RequestParam(defaultValue = "20") int topN
    ) {
        return ResponseEntity.ok(analysisService.getPositionComparison(positions, topN));
    }

    @Operation(
            summary = "갭 분석",
            description = "보유 스킬 목록과 채용 시장 요구 스킬을 비교하여 부족한 스킬(gap)과 강점(strength)을 분석합니다."
    )
    @PostMapping("/gap")
    public ResponseEntity<GapAnalysisResponse> analyzeGap(
            @Valid @RequestBody GapAnalysisRequest request,
            @Parameter(description = "분석 대상 포지션 (기본 BACKEND)") @RequestParam(defaultValue = "BACKEND") PositionType positionType
    ) {
        return ResponseEntity.ok(analysisService.analyzeGap(request, positionType));
    }

    @Operation(
            summary = "스킬 마인드맵",
            description = "특정 스킬의 세부 키워드를 마인드맵 형태로 조회합니다. 채용공고에서 해당 스킬과 함께 언급되는 실무 키워드(캐싱 전략, MSA 전환 등)와 빈도를 반환."
    )
    @GetMapping("/skill-mindmap")
    public ResponseEntity<SkillMindmapResponse> getSkillMindmap(
            @Parameter(description = "스킬명 (예: Redis, Kafka, Spring)") @RequestParam String skill
    ) {
        return ResponseEntity.ok(analysisService.getSkillMindmap(skill));
    }

    @Operation(
            summary = "정규화된 요구사항 집계",
            description = "LLM으로 정규화된 채용 요구사항을 빈도순으로 집계합니다. 다양하게 표현된 같은 요구사항을 하나로 통일하여 실제 시장 수요를 파악."
    )
    @GetMapping("/normalized-requirements")
    public ResponseEntity<NormalizedRequirementResponse> getNormalizedRequirements(
            @Parameter(description = "포지션 타입 필터") @RequestParam(required = false) PositionType positionType,
            @Parameter(description = "상위 N개 반환 (기본 30)") @RequestParam(defaultValue = "30") int topN
    ) {
        return ResponseEntity.ok(analysisService.getNormalizedRequirements(positionType, topN));
    }
}
