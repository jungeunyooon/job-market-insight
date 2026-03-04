package com.devpulse.posting;

import com.devpulse.company.CompanyCategory;
import com.devpulse.posting.JobPosting;
import com.devpulse.posting.PostingSkill;
import com.devpulse.posting.PostingStatus;
import com.devpulse.posting.PositionType;

import java.time.LocalDateTime;
import java.util.List;

public record PostingResponse(
        Long id,
        String title,
        String companyName,
        CompanyCategory companyCategory,
        PositionType positionType,
        String experienceLevel,
        String location,
        PostingStatus status,
        String sourcePlatform,
        String sourceUrl,
        List<String> skills,
        LocalDateTime postedAt,
        LocalDateTime crawledAt
) {
    public static PostingResponse from(JobPosting posting, List<PostingSkill> postingSkills) {
        List<String> skillNames = postingSkills.stream()
                .map(ps -> ps.getSkill().getName())
                .toList();

        return new PostingResponse(
                posting.getId(),
                posting.getTitle(),
                posting.getCompany().getName(),
                posting.getCompany().getCategory(),
                posting.getPositionType(),
                posting.getExperienceLevel(),
                posting.getLocation(),
                posting.getStatus(),
                posting.getSourcePlatform(),
                posting.getSourceUrl(),
                skillNames,
                posting.getPostedAt(),
                posting.getCrawledAt()
        );
    }
}
