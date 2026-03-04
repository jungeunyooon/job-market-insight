package com.devpulse.trend;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;

@Entity
@Table(name = "trend_post",
        uniqueConstraints = @UniqueConstraint(columnNames = {"source", "external_id"}))
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class TrendPost {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.NAMED_ENUM)
    @Column(nullable = false, columnDefinition = "trend_source")
    private TrendSource source;

    @Column(name = "external_id", nullable = false, length = 200)
    private String externalId;

    @Column(nullable = false, length = 500)
    private String title;

    @Column(nullable = false, length = 1000)
    private String url;

    @Column(name = "score")
    private Integer score;

    @Column(name = "comment_count")
    private Integer commentCount;

    @Column(name = "published_at")
    private LocalDateTime publishedAt;

    @Column(name = "crawled_at", nullable = false)
    private LocalDateTime crawledAt;

    @PrePersist
    protected void onCreate() {
        if (crawledAt == null) crawledAt = LocalDateTime.now();
    }

    @Builder
    public TrendPost(TrendSource source, String externalId, String title, String url,
                     Integer score, Integer commentCount, LocalDateTime publishedAt) {
        this.source = source;
        this.externalId = externalId;
        this.title = title;
        this.url = url;
        this.score = score != null ? score : 0;
        this.commentCount = commentCount != null ? commentCount : 0;
        this.publishedAt = publishedAt;
    }
}
