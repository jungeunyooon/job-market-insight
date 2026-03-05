package com.devpulse.posting;

import com.devpulse.company.Company;
import com.devpulse.company.CompanyCategory;

import java.time.LocalDateTime;
import java.util.List;

public record PostingDetailResponse(
        Long id,
        String title,
        CompanyInfo company,
        PositionType positionType,
        String experienceLevel,
        String descriptionRaw,
        String requirementsRaw,
        String preferredRaw,
        String responsibilitiesRaw,
        String techStackRaw,
        String benefitsRaw,
        String companySize,
        String teamInfo,
        String hiringProcess,
        String employmentType,
        String workType,
        String location,
        Integer salaryMin,
        Integer salaryMax,
        PostingStatus status,
        String sourcePlatform,
        String sourceUrl,
        List<SkillInfo> skills,
        LocalDateTime postedAt,
        LocalDateTime closedAt,
        LocalDateTime crawledAt
) {
    public record CompanyInfo(Long id, String name, CompanyCategory category) {
        public static CompanyInfo from(Company company) {
            return new CompanyInfo(company.getId(), company.getName(), company.getCategory());
        }
    }

    public record SkillInfo(Long id, String name, String category, boolean isRequired, boolean isPreferred) {
        public static SkillInfo from(PostingSkill ps) {
            return new SkillInfo(
                    ps.getSkill().getId(),
                    ps.getSkill().getName(),
                    ps.getSkill().getCategory(),
                    Boolean.TRUE.equals(ps.getIsRequired()),
                    Boolean.TRUE.equals(ps.getIsPreferred())
            );
        }
    }

    public static PostingDetailResponse from(JobPosting posting, List<PostingSkill> postingSkills) {
        return new PostingDetailResponse(
                posting.getId(),
                posting.getTitle(),
                CompanyInfo.from(posting.getCompany()),
                posting.getPositionType(),
                posting.getExperienceLevel(),
                posting.getDescriptionRaw(),
                posting.getRequirementsRaw(),
                posting.getPreferredRaw(),
                posting.getResponsibilitiesRaw(),
                posting.getTechStackRaw(),
                posting.getBenefitsRaw(),
                posting.getCompanySize(),
                posting.getTeamInfo(),
                posting.getHiringProcess(),
                posting.getEmploymentType(),
                posting.getWorkType(),
                posting.getLocation(),
                posting.getSalaryMin(),
                posting.getSalaryMax(),
                posting.getStatus(),
                posting.getSourcePlatform(),
                posting.getSourceUrl(),
                postingSkills.stream().map(SkillInfo::from).toList(),
                posting.getPostedAt(),
                posting.getClosedAt(),
                posting.getCrawledAt()
        );
    }
}
