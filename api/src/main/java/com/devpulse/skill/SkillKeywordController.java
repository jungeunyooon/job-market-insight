package com.devpulse.skill;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/skills")
@RequiredArgsConstructor
public class SkillKeywordController {

    private final SkillKeywordService skillKeywordService;

    @GetMapping("/{skillId}/keywords")
    public ResponseEntity<SkillKeywordResponse> getSkillKeywords(@PathVariable Long skillId) {
        return ResponseEntity.ok(skillKeywordService.getSkillKeywords(skillId));
    }
}
