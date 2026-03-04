package com.devpulse.trend;

import java.time.LocalDate;
import java.util.List;

public record TrendRankingResponse(
        LocalDate snapshotDate,
        String source,
        String period,
        long totalPosts,
        List<TrendRankItem> rankings
) {
    public record TrendRankItem(
            int rank,
            String skill,
            long mentions,
            double percentage
    ) {}
}
