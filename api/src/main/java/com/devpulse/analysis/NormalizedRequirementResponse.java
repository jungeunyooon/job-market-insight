package com.devpulse.analysis;

import java.time.LocalDate;
import java.util.List;

public record NormalizedRequirementResponse(
    LocalDate snapshotDate,
    String positionType,
    int totalPostings,
    List<RequirementItem> requirements
) {
    public record RequirementItem(
        int rank,
        String requirement,
        String category,
        long count,
        double percentage
    ) {}
}
