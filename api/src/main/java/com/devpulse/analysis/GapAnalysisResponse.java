package com.devpulse.analysis;

import com.devpulse.posting.PositionType;

import java.util.List;

public record GapAnalysisResponse(
        PositionType positionType,
        int matchPercentage,
        List<SkillGap> gaps
) {
    public record SkillGap(
            String skill,
            int marketRank,
            double marketPercentage,
            String userStatus,
            String priority
    ) {}
}
