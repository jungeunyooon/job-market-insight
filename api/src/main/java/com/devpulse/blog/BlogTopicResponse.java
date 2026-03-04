package com.devpulse.blog;

import java.time.LocalDate;
import java.util.List;

public record BlogTopicResponse(
        LocalDate date,
        String companyName,
        Long companyId,
        long totalPosts,
        List<BlogTopicItem> skills
) {
    public record BlogTopicItem(
            int rank,
            String skill,
            long postCount,
            double percentage
    ) {}
}
