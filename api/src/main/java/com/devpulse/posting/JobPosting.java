package com.devpulse.posting;

import com.devpulse.company.Company;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

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
    @Column(name = "position_type", columnDefinition = "position_type")
    private PositionType positionType;

    @Column(name = "experience_level", length = 100)
    private String experienceLevel;

    @Column(name = "description_raw", columnDefinition = "TEXT")
    private String descriptionRaw;

    @Column(name = "description_cleaned", columnDefinition = "TEXT")
    private String descriptionCleaned;

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
