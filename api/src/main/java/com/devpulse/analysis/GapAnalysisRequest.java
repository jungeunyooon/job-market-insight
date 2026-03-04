package com.devpulse.analysis;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;

import java.util.List;

public record GapAnalysisRequest(
        @NotEmpty @Valid List<UserSkill> mySkills
) {
    public record UserSkill(
            @NotNull String name,
            @NotNull SkillStatus status
    ) {}

    public enum SkillStatus {
        OWNED, LEARNING, NOT_OWNED
    }
}
