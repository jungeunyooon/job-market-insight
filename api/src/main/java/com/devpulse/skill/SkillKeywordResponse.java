package com.devpulse.skill;

import java.util.List;

public record SkillKeywordResponse(
        String skillName,
        String category,
        List<KeywordFrequency> keywords,
        int totalPostings
) {
    public record KeywordFrequency(String keyword, int frequency) {}
}
