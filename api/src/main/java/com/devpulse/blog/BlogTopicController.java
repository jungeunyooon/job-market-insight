package com.devpulse.blog;

import com.devpulse.blog.BlogTopicResponse;
import com.devpulse.blog.SkillCompanyDistributionResponse;
import com.devpulse.blog.YearlyTrendResponse;
import com.devpulse.blog.BlogTopicTrendService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.ResponseEntity;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

@Tag(name = "블로그 토픽", description = "기업 기술 블로그 토픽 분석 API")
@RestController
@RequestMapping("/api/v1/analysis/blog-topics")
@RequiredArgsConstructor
public class BlogTopicController {

    private final BlogTopicTrendService blogTopicTrendService;
    private final TechBlogPostRepository techBlogPostRepository;

    @Operation(
            summary = "회사별 블로그 토픽 랭킹",
            description = "특정 회사의 기술 블로그에서 다루는 기술 토픽을 빈도순으로 조회합니다."
    )
    @GetMapping("/company/{companyId}")
    public ResponseEntity<BlogTopicResponse> getCompanyBlogTopics(
            @Parameter(description = "회사 ID") @PathVariable Long companyId,
            @Parameter(description = "조회 시작 연도") @RequestParam(required = false) Integer fromYear,
            @Parameter(description = "조회 종료 연도") @RequestParam(required = false) Integer toYear,
            @Parameter(description = "상위 N개 반환 (기본 20)") @RequestParam(defaultValue = "20") int topN
    ) {
        return ResponseEntity.ok(blogTopicTrendService.getCompanyBlogTopics(companyId, fromYear, toYear, topN));
    }

    @Operation(
            summary = "연도별 스킬 트렌드",
            description = "전체 기술 블로그의 연도별 스킬 언급 트렌드를 조회합니다. 연도별로 상위 스킬 랭킹이 어떻게 변화하는지 확인 가능."
    )
    @GetMapping("/yearly-trend")
    public ResponseEntity<YearlyTrendResponse> getYearlySkillTrend(
            @Parameter(description = "조회 시작 연도") @RequestParam(required = false) Integer fromYear,
            @Parameter(description = "조회 종료 연도") @RequestParam(required = false) Integer toYear,
            @Parameter(description = "연도별 상위 N개 스킬 (기본 10)") @RequestParam(defaultValue = "10") int topN
    ) {
        return ResponseEntity.ok(blogTopicTrendService.getYearlySkillTrend(fromYear, toYear, topN));
    }

    @Operation(
            summary = "스킬별 회사 분포",
            description = "특정 스킬을 블로그에서 언급하는 회사 분포를 조회합니다. 어떤 회사가 해당 기술에 대해 가장 많이 글을 쓰는지 확인 가능."
    )
    @GetMapping("/skill/{skillName}")
    public ResponseEntity<SkillCompanyDistributionResponse> getSkillCompanyDistribution(
            @Parameter(description = "스킬명 (예: Kubernetes, React)") @PathVariable String skillName,
            @Parameter(description = "조회 시작 연도") @RequestParam(required = false) Integer fromYear,
            @Parameter(description = "조회 종료 연도") @RequestParam(required = false) Integer toYear
    ) {
        return ResponseEntity.ok(blogTopicTrendService.getSkillCompanyDistribution(skillName, fromYear, toYear));
    }

    @Operation(
            summary = "블로그 포스트 목록",
            description = "기술 블로그 포스트를 최신순으로 페이지네이션 조회합니다. 회사 ID로 필터링 가능. 각 포스트의 제목, URL, 요약, 회사명 포함."
    )
    @GetMapping("/posts")
    public ResponseEntity<Page<BlogPostListResponse>> getBlogPosts(
            @Parameter(description = "회사 ID (미지정 시 전체 조회)") @RequestParam(required = false) Long companyId,
            @Parameter(description = "페이지 번호 (0부터 시작)") @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "페이지 크기 (기본 20)") @RequestParam(defaultValue = "20") int size
    ) {
        PageRequest pageRequest = PageRequest.of(page, size);
        Page<TechBlogPost> posts;
        if (companyId != null) {
            posts = techBlogPostRepository.findByCompanyIdOrderByPublishedAtDesc(companyId, pageRequest);
        } else {
            posts = techBlogPostRepository.findAllByOrderByPublishedAtDesc(pageRequest);
        }
        return ResponseEntity.ok(posts.map(BlogPostListResponse::from));
    }
}
