package com.devpulse.trend;

import com.devpulse.trend.BuzzHiringGapResponse;
import com.devpulse.trend.TrendRankingResponse;
import com.devpulse.trend.TrendSource;
import com.devpulse.trend.BuzzHiringGapService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/analysis")
@RequiredArgsConstructor
public class TrendController {

    private final BuzzHiringGapService buzzHiringGapService;

    @GetMapping("/trend-ranking")
    public ResponseEntity<TrendRankingResponse> getTrendRanking(
            @RequestParam(required = false) TrendSource source,
            @RequestParam(defaultValue = "30") int days,
            @RequestParam(defaultValue = "20") int topN
    ) {
        return ResponseEntity.ok(buzzHiringGapService.getTrendRanking(source, days, topN));
    }

    @GetMapping("/buzz-vs-hiring")
    public ResponseEntity<BuzzHiringGapResponse> getBuzzVsHiring(
            @RequestParam(defaultValue = "20") int topN,
            @RequestParam(defaultValue = "30") int days
    ) {
        return ResponseEntity.ok(buzzHiringGapService.analyzeBuzzVsHiring(topN, days));
    }
}
