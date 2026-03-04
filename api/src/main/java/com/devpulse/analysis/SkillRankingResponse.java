package com.devpulse.analysis;

import com.devpulse.posting.PositionType;

import java.time.LocalDate;
import java.util.List;

public record SkillRankingResponse(
        LocalDate snapshotDate,
        long totalPostings,
        PositionType positionType,
        List<SkillRankItem> rankings
) {
    public record SkillRankItem(
            int rank,
            String skill,
            long count,
            double percentage,
            double requiredRatio
    ) {}
}
