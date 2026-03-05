package com.devpulse.posting;

import com.devpulse.company.Company;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Entity
@Table(name = "job_posting")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class JobPosting {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "company_id", nullable = false)
    private Company company;

    @Column(nullable = false, length = 500)
    private String title;

    @Column(name = "title_normalized", length = 500)
    private String titleNormalized;

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.NAMED_ENUM)
    @Column(name = "position_type", columnDefinition = "position_type")
    private PositionType positionType;

    @Column(name = "experience_level", length = 100)
    private String experienceLevel;

    @Column(name = "description_raw", columnDefinition = "TEXT")
    private String descriptionRaw;

    @Column(name = "description_cleaned", columnDefinition = "TEXT")
    private String descriptionCleaned;

    @Column(name = "requirements_raw", columnDefinition = "TEXT")
    private String requirementsRaw;

    @Column(name = "preferred_raw", columnDefinition = "TEXT")
    private String preferredRaw;

    @Column(name = "responsibilities_raw", columnDefinition = "TEXT")
    private String responsibilitiesRaw;

    @Column(name = "tech_stack_raw", columnDefinition = "TEXT")
    private String techStackRaw;

    @Column(name = "benefits_raw", columnDefinition = "TEXT")
    private String benefitsRaw;

    @Column(name = "company_size", length = 100)
    private String companySize;

    @Column(name = "team_info", columnDefinition = "TEXT")
    private String teamInfo;

    @Column(name = "hiring_process", columnDefinition = "TEXT")
    private String hiringProcess;

    @Column(name = "employment_type", length = 50)
    private String employmentType;

    @Column(name = "work_type", length = 50)
    private String workType;

    @Column(name = "source_platform", nullable = false, length = 50)
    private String sourcePlatform;

    @Column(name = "source_url", nullable = false, length = 1000)
    private String sourceUrl;

    @Column(name = "salary_min")
    private Integer salaryMin;

    @Column(name = "salary_max")
    private Integer salaryMax;

    @Column(length = 200)
    private String location;

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.NAMED_ENUM)
    @Column(nullable = false, columnDefinition = "posting_status")
    private PostingStatus status;

    @Column(name = "closed_at")
    private LocalDateTime closedAt;

    @Column(name = "posted_at")
    private LocalDateTime postedAt;

    @Column(name = "crawled_at", nullable = false)
    private LocalDateTime crawledAt;

    @Column(name = "last_seen_at", nullable = false)
    private LocalDateTime lastSeenAt;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "llm_keywords", columnDefinition = "jsonb")
    private List<Map<String, String>> llmKeywords;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "normalized_requirements", columnDefinition = "jsonb")
    private List<Map<String, String>> normalizedRequirements;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        if (crawledAt == null) crawledAt = LocalDateTime.now();
        if (lastSeenAt == null) lastSeenAt = LocalDateTime.now();
        if (status == null) status = PostingStatus.ACTIVE;
    }

    @Builder
    public JobPosting(Company company, String title, String titleNormalized,
                      PositionType positionType, String experienceLevel,
                      String descriptionRaw, String descriptionCleaned,
                      String requirementsRaw, String preferredRaw,
                      String responsibilitiesRaw, String techStackRaw,
                      String benefitsRaw, String companySize, String teamInfo,
                      String hiringProcess, String employmentType, String workType,
                      String sourcePlatform, String sourceUrl,
                      Integer salaryMin, Integer salaryMax, String location,
                      PostingStatus status, LocalDateTime postedAt) {
        this.company = company;
        this.title = title;
        this.titleNormalized = titleNormalized;
        this.positionType = positionType;
        this.experienceLevel = experienceLevel;
        this.descriptionRaw = descriptionRaw;
        this.descriptionCleaned = descriptionCleaned;
        this.requirementsRaw = requirementsRaw;
        this.preferredRaw = preferredRaw;
        this.responsibilitiesRaw = responsibilitiesRaw;
        this.techStackRaw = techStackRaw;
        this.benefitsRaw = benefitsRaw;
        this.companySize = companySize;
        this.teamInfo = teamInfo;
        this.hiringProcess = hiringProcess;
        this.employmentType = employmentType;
        this.workType = workType;
        this.sourcePlatform = sourcePlatform;
        this.sourceUrl = sourceUrl;
        this.salaryMin = salaryMin;
        this.salaryMax = salaryMax;
        this.location = location;
        this.status = status != null ? status : PostingStatus.ACTIVE;
        this.postedAt = postedAt;
    }

    /** 공고 마감 처리 (영구 보관 — 절대 삭제 금지) */
    public void close() {
        this.status = PostingStatus.CLOSED;
        this.closedAt = LocalDateTime.now();
    }

    /** 만료 처리 */
    public void expire() {
        this.status = PostingStatus.EXPIRED;
        this.closedAt = LocalDateTime.now();
    }

    /** 최종 확인 시점 갱신 */
    public void updateLastSeen() {
        this.lastSeenAt = LocalDateTime.now();
    }
}
