package com.devpulse.analysis;

import java.util.List;
import java.util.Map;

public record SkillMindmapResponse(
    String skillName,
    String nameKo,
    String category,
    List<KeywordNode> allKeywords,
    Map<String, List<KeywordNode>> keywordGroups,
    int totalPostingMentions
) {
    public record KeywordNode(
        String keyword,
        int postingCount,
        double percentage
    ) {}
}
