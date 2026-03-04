package com.devpulse.blog;

import java.time.LocalDate;
import java.util.List;

public record SkillCompanyDistributionResponse(
        LocalDate date,
        String skillName,
        String period,
        List<CompanyCount> companies
) {
    public record CompanyCount(
            String company,
            long postCount
    ) {}
}
