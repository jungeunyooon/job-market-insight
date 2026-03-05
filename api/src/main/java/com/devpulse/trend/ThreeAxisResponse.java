package com.devpulse.trend;

import java.time.LocalDate;
import java.util.List;

public record ThreeAxisResponse(
        LocalDate snapshotDate,
        String period,
        long totalTrendPosts,
        long totalBlogPosts,
        long totalJobPostings,
        List<ThreeAxisItem> items
) {
    public record ThreeAxisItem(
            String skill,
            long trendMentions,
            int trendRank,
            long blogMentions,
            int blogRank,
            double blogPercentage,
            long jobPostings,
            int jobRank,
            double jobPercentage,
            ThreeAxisClassification classification,
            String insight
    ) {}

    public enum ThreeAxisClassification {
        ADOPTED,       // trend HIGH, job HIGH  — 시장 + 커뮤니티 모두 채택
        OVERHYPED,     // trend HIGH, job LOW, blog LOW  — 버즈만 높음
        ESTABLISHED,   // trend LOW, job HIGH   — 정착된 기술
        EMERGING,      // trend LOW, job LOW, blog LOW  — 태동기
        PRACTICAL,     // trend LOW, job HIGH, blog HIGH — 조용히 쓰이는 기술
        HYPE_ONLY,     // trend HIGH, job LOW, blog LOW — 과대광고
        BLOG_DRIVEN    // trend LOW, job LOW, blog HIGH — 블로그에서만 화제
    }
}
