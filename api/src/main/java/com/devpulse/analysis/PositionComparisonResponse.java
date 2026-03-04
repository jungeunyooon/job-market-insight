package com.devpulse.analysis;

import com.devpulse.posting.PositionType;

import java.util.List;
import java.util.Map;

public record PositionComparisonResponse(
        List<PositionSkillProfile> positions,
        List<String> commonSkills,
        Map<String, List<String>> uniqueSkills
) {
    public record PositionSkillProfile(
            PositionType positionType,
            long totalPostings,
            List<SkillRankingResponse.SkillRankItem> topSkills
    ) {}
}
