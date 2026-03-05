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
@Table(name = "trend_snapshot")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class TrendSnapshot {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.NAMED_ENUM)
    @Column(nullable = false, columnDefinition = "trend_source")
    private TrendSource source;

    @Column(name = "skill_name", nullable = false, length = 100)
    private String skillName;

    @Column(nullable = false)
    private Integer rank;

    @Column(name = "mention_count")
    private Integer mentionCount;

    @Column(name = "snapshot_at", nullable = false)
    private LocalDateTime snapshotAt;

    @PrePersist
    protected void onCreate() {
        if (snapshotAt == null) snapshotAt = LocalDateTime.now();
    }

    @Builder
    public TrendSnapshot(TrendSource source, String skillName, Integer rank,
                         Integer mentionCount, LocalDateTime snapshotAt) {
        this.source = source;
        this.skillName = skillName;
        this.rank = rank;
        this.mentionCount = mentionCount != null ? mentionCount : 0;
        this.snapshotAt = snapshotAt;
    }
}
