package com.devpulse.blog;

import com.devpulse.blog.BlogTopicResponse;
import com.devpulse.blog.SkillCompanyDistributionResponse;
import com.devpulse.blog.YearlyTrendResponse;
import com.devpulse.blog.BlogTopicTrendService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/analysis/blog-topics")
@RequiredArgsConstructor
public class BlogTopicController {

    private final BlogTopicTrendService blogTopicTrendService;

    @GetMapping("/company/{companyId}")
    public ResponseEntity<BlogTopicResponse> getCompanyBlogTopics(
            @PathVariable Long companyId,
            @RequestParam(required = false) Integer fromYear,
            @RequestParam(required = false) Integer toYear,
            @RequestParam(defaultValue = "20") int topN
    ) {
        return ResponseEntity.ok(blogTopicTrendService.getCompanyBlogTopics(companyId, fromYear, toYear, topN));
    }

    @GetMapping("/yearly-trend")
    public ResponseEntity<YearlyTrendResponse> getYearlySkillTrend(
            @RequestParam(required = false) Integer fromYear,
            @RequestParam(required = false) Integer toYear,
            @RequestParam(defaultValue = "10") int topN
    ) {
        return ResponseEntity.ok(blogTopicTrendService.getYearlySkillTrend(fromYear, toYear, topN));
    }

    @GetMapping("/skill/{skillName}")
    public ResponseEntity<SkillCompanyDistributionResponse> getSkillCompanyDistribution(
            @PathVariable String skillName,
            @RequestParam(required = false) Integer fromYear,
            @RequestParam(required = false) Integer toYear
    ) {
        return ResponseEntity.ok(blogTopicTrendService.getSkillCompanyDistribution(skillName, fromYear, toYear));
    }
}
