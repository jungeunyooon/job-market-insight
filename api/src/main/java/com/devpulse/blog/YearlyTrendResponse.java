package com.devpulse.blog;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

public record YearlyTrendResponse(
        LocalDate date,
        String period,
        List<YearlySkillData> yearlyData
) {
    public record YearlySkillData(
            int year,
            List<SkillCount> skills
    ) {}

    public record SkillCount(
            String skill,
            long postCount
    ) {}
}
