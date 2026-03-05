package com.devpulse.analysis;

import com.devpulse.analysis.GapAnalysisRequest.SkillStatus;
import com.devpulse.analysis.SkillRankingResponse.SkillRankItem;
import com.devpulse.company.Company;
import com.devpulse.company.CompanyCategory;
import com.devpulse.company.CompanyRepository;
import com.devpulse.posting.*;
import com.devpulse.skill.Skill;
import com.devpulse.skill.SkillRepository;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class AnalysisService {

    private final PostingSkillRepository postingSkillRepository;
    private final JobPostingRepository jobPostingRepository;
    private final CompanyRepository companyRepository;
    private final SkillRepository skillRepository;

    public SkillRankingResponse getSkillRanking(
            PositionType positionType,
            List<CompanyCategory> categories,
            boolean includeClosedPostings,
            int topN
    ) {
        boolean hasPosition = positionType != null;
        PositionType resolvedPositionType = hasPosition ? positionType : PositionType.BACKEND;
        List<CompanyCategory> resolvedCategories = (categories == null || categories.isEmpty())
                ? Arrays.asList(CompanyCategory.values())
                : categories;

        List<Object[]> rows = postingSkillRepository.findSkillRankingWithFilters(
                hasPosition, resolvedPositionType, includeClosedPostings, PostingStatus.ACTIVE, resolvedCategories
        );
        long totalPostings = postingSkillRepository.countPostingsWithFilters(
                hasPosition, resolvedPositionType, includeClosedPostings, PostingStatus.ACTIVE, resolvedCategories
        );

        List<SkillRankItem> rankings = new ArrayList<>();
        int rank = 1;
        for (Object[] row : rows) {
            if (rank > topN) break;
            String skillName = (String) row[0];
            long count = ((Number) row[1]).longValue();
            long requiredCount = ((Number) row[2]).longValue();
            double percentage = totalPostings > 0 ? (count * 100.0) / totalPostings : 0;
            double requiredRatio = count > 0 ? (double) requiredCount / count : 0;
            rankings.add(new SkillRankItem(rank++, skillName, count, Math.round(percentage * 10) / 10.0, Math.round(requiredRatio * 100) / 100.0));
        }

        return new SkillRankingResponse(LocalDate.now(), totalPostings, positionType, rankings);
    }

    public CompanyProfileResponse getCompanyProfile(Long companyId) {
        Company company = companyRepository.findById(companyId)
                .orElseThrow(() -> new CompanyNotFoundException(companyId));
        return buildCompanyProfile(company);
    }

    public CompanyProfileResponse getCompanyProfileByName(String companyName) {
        Company company = companyRepository.findByName(companyName)
                .orElseThrow(() -> new CompanyNotFoundByNameException(companyName));
        return buildCompanyProfile(company);
    }

    private CompanyProfileResponse buildCompanyProfile(Company company) {
        Long companyId = company.getId();
        long totalPostings = jobPostingRepository.countByCompanyId(companyId);

        List<Object[]> skillRows = postingSkillRepository.findSkillRankingByCompany(companyId);
        List<CompanyProfileResponse.SkillUsage> topSkills = new ArrayList<>();
        for (Object[] row : skillRows) {
            String skillName = (String) row[0];
            long count = ((Number) row[1]).longValue();
            double percentage = totalPostings > 0 ? (count * 100.0) / totalPostings : 0;
            topSkills.add(new CompanyProfileResponse.SkillUsage(
                    skillName, count, Math.round(percentage * 10) / 10.0
            ));
        }

        List<Object[]> positionRows = jobPostingRepository.countByCompanyIdGroupByPositionType(companyId);
        Map<PositionType, Long> positionBreakdown = new EnumMap<>(PositionType.class);
        for (Object[] row : positionRows) {
            PositionType type = (PositionType) row[0];
            long count = ((Number) row[1]).longValue();
            positionBreakdown.put(type, count);
        }

        return new CompanyProfileResponse(
                company.getId(), company.getName(), company.getCategory(),
                totalPostings, topSkills, positionBreakdown
        );
    }

    public PositionComparisonResponse getPositionComparison(List<PositionType> positions, int topN) {
        List<PositionComparisonResponse.PositionSkillProfile> profiles = new ArrayList<>();
        Map<PositionType, Set<String>> skillSets = new LinkedHashMap<>();

        for (PositionType position : positions) {
            SkillRankingResponse ranking = getSkillRanking(position, null, false, topN);
            profiles.add(new PositionComparisonResponse.PositionSkillProfile(
                    position, ranking.totalPostings(), ranking.rankings()
            ));
            skillSets.put(position, ranking.rankings().stream()
                    .map(SkillRankItem::skill)
                    .collect(Collectors.toCollection(LinkedHashSet::new)));
        }

        // Find common skills across ALL positions
        Set<String> commonSkills = skillSets.values().stream()
                .reduce((a, b) -> {
                    Set<String> intersection = new LinkedHashSet<>(a);
                    intersection.retainAll(b);
                    return intersection;
                })
                .orElse(Set.of());

        // Find unique skills per position
        Map<String, List<String>> uniqueSkills = new LinkedHashMap<>();
        for (var entry : skillSets.entrySet()) {
            Set<String> others = skillSets.entrySet().stream()
                    .filter(e -> !e.getKey().equals(entry.getKey()))
                    .flatMap(e -> e.getValue().stream())
                    .collect(Collectors.toSet());
            List<String> unique = entry.getValue().stream()
                    .filter(s -> !others.contains(s))
                    .toList();
            uniqueSkills.put(entry.getKey().name(), unique);
        }

        return new PositionComparisonResponse(profiles, new ArrayList<>(commonSkills), uniqueSkills);
    }

    public GapAnalysisResponse analyzeGap(GapAnalysisRequest request, PositionType positionType) {
        SkillRankingResponse ranking = getSkillRanking(positionType, null, false, 50);

        Map<String, SkillStatus> userSkillMap = request.mySkills().stream()
                .collect(Collectors.toMap(
                        s -> s.name().toLowerCase(),
                        GapAnalysisRequest.UserSkill::status,
                        (a, b) -> a
                ));

        int ownedInTop = 0;
        List<GapAnalysisResponse.SkillGap> gaps = new ArrayList<>();

        for (SkillRankItem item : ranking.rankings()) {
            String skillLower = item.skill().toLowerCase();
            SkillStatus userStatus = userSkillMap.getOrDefault(skillLower, SkillStatus.NOT_OWNED);

            if (userStatus == SkillStatus.OWNED) {
                ownedInTop++;
            }

            String priority = determinePriority(item.rank(), item.percentage(), userStatus);
            gaps.add(new GapAnalysisResponse.SkillGap(
                    item.skill(), item.rank(), item.percentage(),
                    userStatus.name(), priority
            ));
        }

        int matchPercentage = ranking.rankings().isEmpty() ? 0 :
                (ownedInTop * 100) / ranking.rankings().size();

        return new GapAnalysisResponse(positionType, matchPercentage, gaps);
    }

    private String determinePriority(int rank, double percentage, SkillStatus status) {
        if (status == SkillStatus.OWNED) return "MAINTAINED";
        if (status == SkillStatus.LEARNING) return "CONTINUE";
        // NOT_OWNED
        if (rank <= 5 && percentage >= 50) return "CRITICAL";
        if (rank <= 10) return "HIGH";
        if (rank <= 20) return "MEDIUM";
        return "LOW";
    }

    public SkillMindmapResponse getSkillMindmap(String skillName) {
        Skill skill = skillRepository.findByName(skillName)
                .orElseThrow(() -> new EntityNotFoundException("Skill not found: " + skillName));

        List<String> keywords = skill.getKeywords() != null ? skill.getKeywords() : List.of();

        Map<String, List<SkillMindmapResponse.KeywordNode>> keywordGroups = new LinkedHashMap<>();

        long totalPostings = postingSkillRepository.countBySkillId(skill.getId());

        List<Object[]> kwFreqs = postingSkillRepository.findKeywordFrequenciesBySkillId(skill.getId());
        Map<String, Integer> freqMap = new HashMap<>();
        for (Object[] row : kwFreqs) {
            freqMap.put((String) row[0], ((Number) row[1]).intValue());
        }

        List<SkillMindmapResponse.KeywordNode> nodes = keywords.stream()
                .map(kw -> {
                    int count = freqMap.getOrDefault(kw, 0);
                    double pct = totalPostings > 0 ? (count * 100.0 / totalPostings) : 0.0;
                    return new SkillMindmapResponse.KeywordNode(kw, count, Math.round(pct * 10.0) / 10.0);
                })
                .sorted((a, b) -> Integer.compare(b.postingCount(), a.postingCount()))
                .toList();

        keywordGroups.put("keywords", nodes);

        return new SkillMindmapResponse(
                skill.getName(),
                skill.getNameKo(),
                skill.getCategory(),
                keywords,
                keywordGroups,
                (int) totalPostings
        );
    }

    public static class CompanyNotFoundException extends RuntimeException {
        public CompanyNotFoundException(Long id) {
            super("Company not found: " + id);
        }
    }

    public static class CompanyNotFoundByNameException extends RuntimeException {
        public CompanyNotFoundByNameException(String name) {
            super("Company not found: " + name);
        }
    }
}
