package com.devpulse.analysis;

import com.devpulse.company.CompanyCategory;
import com.devpulse.posting.PositionType;
import com.devpulse.analysis.AnalysisService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/analysis")
@RequiredArgsConstructor
public class AnalysisController {

    private final AnalysisService analysisService;

    @GetMapping("/skill-ranking")
    public ResponseEntity<SkillRankingResponse> getSkillRanking(
            @RequestParam(required = false) PositionType positionType,
            @RequestParam(required = false) List<CompanyCategory> companyCategory,
            @RequestParam(defaultValue = "false") boolean includeClosedPostings,
            @RequestParam(defaultValue = "20") int topN
    ) {
        return ResponseEntity.ok(
                analysisService.getSkillRanking(positionType, companyCategory, includeClosedPostings, topN)
        );
    }

    @GetMapping("/company-profile/{companyId}")
    public ResponseEntity<CompanyProfileResponse> getCompanyProfile(@PathVariable Long companyId) {
        return ResponseEntity.ok(analysisService.getCompanyProfile(companyId));
    }

    @GetMapping("/position-comparison")
    public ResponseEntity<PositionComparisonResponse> getPositionComparison(
            @RequestParam List<PositionType> positions,
            @RequestParam(defaultValue = "20") int topN
    ) {
        return ResponseEntity.ok(analysisService.getPositionComparison(positions, topN));
    }

    @PostMapping("/gap")
    public ResponseEntity<GapAnalysisResponse> analyzeGap(
            @Valid @RequestBody GapAnalysisRequest request,
            @RequestParam(defaultValue = "BACKEND") PositionType positionType
    ) {
        return ResponseEntity.ok(analysisService.analyzeGap(request, positionType));
    }
}
