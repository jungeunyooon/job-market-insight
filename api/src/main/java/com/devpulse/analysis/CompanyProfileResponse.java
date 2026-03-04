package com.devpulse.analysis;

import com.devpulse.company.CompanyCategory;
import com.devpulse.posting.PositionType;

import java.util.List;
import java.util.Map;

public record CompanyProfileResponse(
        Long companyId,
        String companyName,
        CompanyCategory category,
        long totalPostings,
        List<SkillUsage> topSkills,
        Map<PositionType, Long> positionBreakdown
) {
    public record SkillUsage(String skill, long count, double percentage) {}
}
