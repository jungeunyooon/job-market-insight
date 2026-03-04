package com.devpulse.trend;

import java.time.LocalDate;
import java.util.List;

public record BuzzHiringGapResponse(
        LocalDate snapshotDate,
        String trendPeriod,
        String trendSource,
        long totalTrendPosts,
        long totalJobPostings,
        List<BuzzHiringGap> gaps
) {
    public record BuzzHiringGap(
            String skill,
            long trendMentions,
            int trendRank,
            long jobPostings,
            int jobRank,
            double jobPercentage,
            Classification classification,
            String insight
    ) {}

    public enum Classification {
        OVERHYPED,   // trend HIGH, job LOW — 커뮤니티 관심 대비 채용 수요 낮음
        ADOPTED,     // trend HIGH, job HIGH — 커뮤니티 관심과 채용 수요 모두 높음
        ESTABLISHED, // trend LOW, job HIGH — 정착된 기술 (더 이상 화제 아님)
        EMERGING     // trend LOW, job LOW — 태동기
    }
}
