package com.devpulse.trend;

import com.devpulse.trend.BuzzHiringGapResponse;
import com.devpulse.trend.SnapshotHistoryResponse;
import com.devpulse.trend.ThreeAxisResponse;
import com.devpulse.trend.TrendRankingResponse;
import com.devpulse.trend.TrendSource;
import com.devpulse.trend.BuzzHiringGapService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

@Tag(name = "트렌드", description = "커뮤니티 트렌드 랭킹, Buzz vs 채용 분석, 3축 분석, 스냅샷 히스토리 API")
@RestController
@RequestMapping("/api/v1/analysis")
@RequiredArgsConstructor
public class TrendController {

    private final BuzzHiringGapService buzzHiringGapService;

    @Operation(
            summary = "트렌드 스킬 랭킹",
            description = "GeekNews, HackerNews, dev.to 등 커뮤니티에서 언급되는 기술 스택을 빈도순으로 랭킹합니다. 소스별 또는 전체 통합 조회 가능."
    )
    @GetMapping("/trend-ranking")
    public ResponseEntity<TrendRankingResponse> getTrendRanking(
            @Parameter(description = "트렌드 소스 필터 (GEEKNEWS, HN, DEVTO). 미지정 시 전체 통합") @RequestParam(required = false) TrendSource source,
            @Parameter(description = "분석 기간 (일, 기본 30)") @RequestParam(defaultValue = "30") int days,
            @Parameter(description = "상위 N개 반환 (기본 20)") @RequestParam(defaultValue = "20") int topN
    ) {
        return ResponseEntity.ok(buzzHiringGapService.getTrendRanking(source, days, topN));
    }

    @Operation(
            summary = "Buzz vs 채용 갭 분석 (2축)",
            description = """
                    커뮤니티 관심도(Buzz)와 채용 수요(Hiring)를 비교하여 4가지로 분류합니다:
                    - **ADOPTED**: 관심도 HIGH + 채용 HIGH (시장에서 채택된 기술)
                    - **OVERHYPED**: 관심도 HIGH + 채용 LOW (과대평가된 기술)
                    - **ESTABLISHED**: 관심도 LOW + 채용 HIGH (정착된 기술)
                    - **EMERGING**: 관심도 LOW + 채용 LOW (태동기 기술)
                    """
    )
    @GetMapping("/buzz-vs-hiring")
    public ResponseEntity<BuzzHiringGapResponse> getBuzzVsHiring(
            @Parameter(description = "상위 N개 반환 (기본 20)") @RequestParam(defaultValue = "20") int topN,
            @Parameter(description = "트렌드 분석 기간 (일, 기본 30)") @RequestParam(defaultValue = "30") int days
    ) {
        return ResponseEntity.ok(buzzHiringGapService.analyzeBuzzVsHiring(topN, days));
    }

    @Operation(
            summary = "트렌드 스냅샷 히스토리",
            description = "특정 스킬의 트렌드 순위 변화를 시계열로 조회합니다. 동기화 시점마다 기록된 스냅샷을 기반으로 순위와 언급 수 추이를 확인 가능."
    )
    @GetMapping("/snapshot-history")
    public ResponseEntity<SnapshotHistoryResponse> getSnapshotHistory(
            @Parameter(description = "트렌드 소스 (GEEKNEWS, HN, DEVTO)", required = true) @RequestParam TrendSource source,
            @Parameter(description = "스킬명 (예: React, LangChain)", required = true) @RequestParam String skill,
            @Parameter(description = "조회 기간 (일, 기본 30)") @RequestParam(defaultValue = "30") int days
    ) {
        return ResponseEntity.ok(buzzHiringGapService.getSnapshotHistory(source, skill, days));
    }

    @Operation(
            summary = "3축 분석 (Buzz + Hiring + Blog)",
            description = """
                    커뮤니티 관심도(Buzz), 채용 수요(Hiring), 블로그 실무 언급(Blog) 3축으로 기술을 7가지로 분류합니다:
                    - **ADOPTED**: Buzz HIGH + Hiring HIGH — 시장과 커뮤니티 모두 채택
                    - **HYPE_ONLY**: Buzz HIGH + Hiring LOW + Blog LOW — 과대광고 (실무 채택 미미)
                    - **OVERHYPED**: Buzz HIGH + Hiring LOW + Blog HIGH — 커뮤니티 관심 + 블로그 언급 있으나 채용 수요 낮음
                    - **PRACTICAL**: Buzz LOW + Hiring HIGH + Blog HIGH — 조용히 쓰이는 기술 (채용+실무 블로그 활발)
                    - **ESTABLISHED**: Buzz LOW + Hiring HIGH + Blog LOW — 정착된 기술
                    - **BLOG_DRIVEN**: Buzz LOW + Hiring LOW + Blog HIGH — 블로그에서만 화제
                    - **EMERGING**: 모두 LOW — 태동기
                    """
    )
    @GetMapping("/three-axis")
    public ResponseEntity<ThreeAxisResponse> getThreeAxisAnalysis(
            @Parameter(description = "상위 N개 반환 (기본 20)") @RequestParam(defaultValue = "20") int topN,
            @Parameter(description = "분석 기간 (일, 기본 30)") @RequestParam(defaultValue = "30") int days
    ) {
        return ResponseEntity.ok(buzzHiringGapService.analyzeThreeAxis(topN, days));
    }
}
