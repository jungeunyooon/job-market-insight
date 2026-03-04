package com.devpulse.trend;

import com.devpulse.trend.BuzzHiringGapResponse;
import com.devpulse.trend.BuzzHiringGapResponse.BuzzHiringGap;
import com.devpulse.trend.BuzzHiringGapResponse.Classification;
import com.devpulse.trend.TrendRankingResponse;
import com.devpulse.trend.TrendRankingResponse.TrendRankItem;
import com.devpulse.posting.PostingSkillRepository;
import com.devpulse.posting.PositionType;
import com.devpulse.trend.TrendSkillRepository;
import com.devpulse.trend.TrendSource;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class BuzzHiringGapService {

    private static final double HIGH_TREND_THRESHOLD = 5.0;  // >= 5% of trend posts
    private static final double HIGH_JOB_THRESHOLD = 10.0;   // >= 10% of job postings

    private final TrendSkillRepository trendSkillRepository;
    private final PostingSkillRepository postingSkillRepository;

    public TrendRankingResponse getTrendRanking(TrendSource source, int days, int topN) {
        LocalDateTime since = LocalDateTime.now().minusDays(days);

        List<Object[]> rows;
        if (source != null) {
            rows = trendSkillRepository.findSkillRankingBySourceSince(source, since);
        } else {
            rows = trendSkillRepository.findSkillRankingSince(since);
        }

        long totalPosts = trendSkillRepository.countTrendPostsSince(since);

        List<TrendRankItem> rankings = new ArrayList<>();
        int rank = 1;
        for (Object[] row : rows) {
            if (rank > topN) break;
            String skillName = (String) row[0];
            long count = ((Number) row[1]).longValue();
            double percentage = totalPosts > 0 ? (count * 100.0) / totalPosts : 0;
            rankings.add(new TrendRankItem(rank++, skillName, count, Math.round(percentage * 10) / 10.0));
        }

        String period = "LAST_" + days + "_DAYS";
        String sourceName = source != null ? source.name() : "ALL";
        return new TrendRankingResponse(LocalDate.now(), sourceName, period, totalPosts, rankings);
    }

    public BuzzHiringGapResponse analyzeBuzzVsHiring(int topN, int trendDays) {
        LocalDateTime since = LocalDateTime.now().minusDays(trendDays);

        // 1. Trend skill mentions (all sources)
        List<Object[]> trendRows = trendSkillRepository.findSkillRankingSince(since);
        long totalTrendPosts = trendSkillRepository.countTrendPostsSince(since);

        // 2. Job posting skill mentions (ACTIVE postings, all positions)
        List<Object[]> jobRows = postingSkillRepository.findSkillRankingWithFilters(null, false, null);
        long totalJobPostings = postingSkillRepository.countPostingsWithFilters(null, false, null);

        // Build maps: skill -> (count, rank)
        Map<String, long[]> trendMap = buildRankMap(trendRows);
        Map<String, long[]> jobMap = buildRankMap(jobRows);

        // Merge all skills
        Set<String> allSkills = new LinkedHashSet<>();
        allSkills.addAll(trendMap.keySet());
        allSkills.addAll(jobMap.keySet());

        List<BuzzHiringGap> gaps = new ArrayList<>();
        for (String skill : allSkills) {
            long[] trendData = trendMap.getOrDefault(skill, new long[]{0, 0});
            long[] jobData = jobMap.getOrDefault(skill, new long[]{0, 0});

            long trendMentions = trendData[0];
            int trendRank = (int) trendData[1];
            long jobPostingCount = jobData[0];
            int jobRank = (int) jobData[1];

            double trendPct = totalTrendPosts > 0 ? (trendMentions * 100.0) / totalTrendPosts : 0;
            double jobPct = totalJobPostings > 0 ? (jobPostingCount * 100.0) / totalJobPostings : 0;

            Classification classification = classify(trendPct, jobPct);
            String insight = generateInsight(skill, classification);

            gaps.add(new BuzzHiringGap(
                    skill, trendMentions, trendRank, jobPostingCount, jobRank,
                    Math.round(jobPct * 10) / 10.0, classification, insight
            ));
        }

        // Sort by combined relevance: trend mentions + job postings
        gaps.sort((a, b) -> Long.compare(b.trendMentions() + b.jobPostings(), a.trendMentions() + a.jobPostings()));
        if (gaps.size() > topN) {
            gaps = gaps.subList(0, topN);
        }

        String period = "LAST_" + trendDays + "_DAYS";
        return new BuzzHiringGapResponse(
                LocalDate.now(), period, "ALL", totalTrendPosts, totalJobPostings, gaps
        );
    }

    private Map<String, long[]> buildRankMap(List<Object[]> rows) {
        Map<String, long[]> map = new LinkedHashMap<>();
        int rank = 1;
        for (Object[] row : rows) {
            String skill = (String) row[0];
            long count = ((Number) row[1]).longValue();
            map.put(skill, new long[]{count, rank++});
        }
        return map;
    }

    Classification classify(double trendPercentage, double jobPercentage) {
        boolean highTrend = trendPercentage >= HIGH_TREND_THRESHOLD;
        boolean highJob = jobPercentage >= HIGH_JOB_THRESHOLD;

        if (highTrend && highJob) return Classification.ADOPTED;
        if (highTrend) return Classification.OVERHYPED;
        if (highJob) return Classification.ESTABLISHED;
        return Classification.EMERGING;
    }

    private String generateInsight(String skill, Classification classification) {
        return switch (classification) {
            case ADOPTED -> skill + ": 커뮤니티 관심과 채용 수요 모두 높음";
            case OVERHYPED -> skill + ": 커뮤니티 관심 대비 채용 수요 낮음";
            case ESTABLISHED -> skill + ": 더 이상 화제가 아니지만 채용 시장의 기본기";
            case EMERGING -> skill + ": 태동기 — 커뮤니티와 채용 모두 아직 소수";
        };
    }
}
