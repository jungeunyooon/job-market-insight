package com.devpulse.skill;

import com.devpulse.posting.PostingSkillRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class SkillKeywordService {

    private final SkillRepository skillRepository;
    private final PostingSkillRepository postingSkillRepository;

    public SkillKeywordResponse getSkillKeywords(Long skillId) {
        Skill skill = skillRepository.findById(skillId)
                .orElseThrow(() -> new IllegalArgumentException("Skill not found: " + skillId));

        List<Object[]> rows = postingSkillRepository.findKeywordFrequenciesBySkillId(skillId);
        List<SkillKeywordResponse.KeywordFrequency> keywords = rows.stream()
                .map(row -> new SkillKeywordResponse.KeywordFrequency(
                        (String) row[0],
                        ((Number) row[1]).intValue()
                ))
                .toList();

        long totalPostings = postingSkillRepository.countBySkillId(skillId);

        return new SkillKeywordResponse(
                skill.getName(),
                skill.getCategory(),
                keywords,
                (int) totalPostings
        );
    }
}
