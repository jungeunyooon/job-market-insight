package com.devpulse.blog;

import com.devpulse.blog.BlogTopicResponse;
import com.devpulse.blog.BlogTopicResponse.BlogTopicItem;
import com.devpulse.blog.SkillCompanyDistributionResponse;
import com.devpulse.blog.SkillCompanyDistributionResponse.CompanyCount;
import com.devpulse.blog.YearlyTrendResponse;
import com.devpulse.blog.YearlyTrendResponse.SkillCount;
import com.devpulse.blog.YearlyTrendResponse.YearlySkillData;
import com.devpulse.blog.BlogSkillRepository;
import com.devpulse.blog.TechBlogPostRepository;
import com.devpulse.company.Company;
import com.devpulse.company.CompanyRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class BlogTopicTrendService {

    private final BlogSkillRepository blogSkillRepository;
    private final TechBlogPostRepository techBlogPostRepository;
    private final CompanyRepository companyRepository;

    public BlogTopicResponse getCompanyBlogTopics(Long companyId, Integer fromYear, Integer toYear, int topN) {
        Company company = companyRepository.findById(companyId)
                .orElseThrow(() -> new IllegalArgumentException("Company not found: " + companyId));

        long totalPosts = techBlogPostRepository.countByCompanyId(companyId);
        List<Object[]> rows = blogSkillRepository.findSkillRankingByCompanyAndYear(companyId, fromYear, toYear);

        List<BlogTopicItem> skills = new ArrayList<>();
        int rank = 1;
        for (Object[] row : rows) {
            if (rank > topN) break;
            String skillName = (String) row[0];
            long count = ((Number) row[1]).longValue();
            double percentage = totalPosts > 0 ? Math.round((count * 100.0) / totalPosts * 10) / 10.0 : 0;
            skills.add(new BlogTopicItem(rank++, skillName, count, percentage));
        }

        return new BlogTopicResponse(LocalDate.now(), company.getName(), companyId, totalPosts, skills);
    }

    public YearlyTrendResponse getYearlySkillTrend(Integer fromYear, Integer toYear, int topNPerYear) {
        List<Object[]> rows = blogSkillRepository.findYearlySkillTrend(fromYear, toYear);

        // Group by year, preserving order
        Map<Integer, List<SkillCount>> yearMap = new LinkedHashMap<>();
        for (Object[] row : rows) {
            int year = ((Number) row[0]).intValue();
            String skillName = (String) row[1];
            long count = ((Number) row[2]).longValue();
            yearMap.computeIfAbsent(year, k -> new ArrayList<>()).add(new SkillCount(skillName, count));
        }

        List<YearlySkillData> yearlyData = new ArrayList<>();
        for (var entry : yearMap.entrySet()) {
            List<SkillCount> skills = entry.getValue();
            if (skills.size() > topNPerYear) {
                skills = skills.subList(0, topNPerYear);
            }
            yearlyData.add(new YearlySkillData(entry.getKey(), skills));
        }

        String period = buildPeriodString(fromYear, toYear);
        return new YearlyTrendResponse(LocalDate.now(), period, yearlyData);
    }

    public SkillCompanyDistributionResponse getSkillCompanyDistribution(String skillName, Integer fromYear, Integer toYear) {
        List<Object[]> rows = blogSkillRepository.findCompanyDistributionBySkill(skillName, fromYear, toYear);

        List<CompanyCount> companies = rows.stream()
                .map(row -> new CompanyCount((String) row[0], ((Number) row[1]).longValue()))
                .toList();

        String period = buildPeriodString(fromYear, toYear);
        return new SkillCompanyDistributionResponse(LocalDate.now(), skillName, period, companies);
    }

    private String buildPeriodString(Integer fromYear, Integer toYear) {
        if (fromYear != null && toYear != null) return fromYear + "-" + toYear;
        if (fromYear != null) return fromYear + "-";
        if (toYear != null) return "-" + toYear;
        return "ALL";
    }
}
