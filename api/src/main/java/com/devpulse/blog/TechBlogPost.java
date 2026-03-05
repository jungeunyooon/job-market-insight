package com.devpulse.blog;

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

@Entity
@Table(name = "tech_blog_post",
        uniqueConstraints = @UniqueConstraint(columnNames = "url"))
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class TechBlogPost {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "company_id", nullable = false)
    private Company company;

    @Column(nullable = false, length = 500)
    private String title;

    @Column(nullable = false, length = 1000)
    private String url;

    @Column(name = "content_raw", columnDefinition = "TEXT")
    private String contentRaw;

    @Column(name = "content_cleaned", columnDefinition = "TEXT")
    private String contentCleaned;

    @Column(columnDefinition = "TEXT")
    private String summary;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    private List<String> topics;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "llm_keywords", columnDefinition = "jsonb")
    private List<Object> llmKeywords;

    @Column(name = "published_at")
    private LocalDateTime publishedAt;

    @Column(name = "published_year")
    private Integer publishedYear;

    @Column(name = "crawled_at", nullable = false)
    private LocalDateTime crawledAt;

    @PrePersist
    protected void onCreate() {
        if (crawledAt == null) crawledAt = LocalDateTime.now();
    }

    @Builder
    public TechBlogPost(Company company, String title, String url,
                        String contentRaw, String summary, List<String> topics,
                        LocalDateTime publishedAt, Integer publishedYear) {
        this.company = company;
        this.title = title;
        this.url = url;
        this.contentRaw = contentRaw;
        this.summary = summary;
        this.topics = topics != null ? topics : List.of();
        this.publishedAt = publishedAt;
        this.publishedYear = publishedYear;
    }
}
