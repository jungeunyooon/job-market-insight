package com.devpulse.trend;

import com.devpulse.skill.Skill;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "trend_skill",
        uniqueConstraints = @UniqueConstraint(columnNames = {"trend_post_id", "skill_id"}))
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class TrendSkill {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "trend_post_id", nullable = false)
    private TrendPost trendPost;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "skill_id", nullable = false)
    private Skill skill;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    @Builder
    public TrendSkill(TrendPost trendPost, Skill skill) {
        this.trendPost = trendPost;
        this.skill = skill;
    }
}
