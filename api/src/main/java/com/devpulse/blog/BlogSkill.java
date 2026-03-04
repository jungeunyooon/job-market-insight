package com.devpulse.blog;

import com.devpulse.skill.Skill;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "blog_skill",
        uniqueConstraints = @UniqueConstraint(columnNames = {"blog_post_id", "skill_id"}))
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class BlogSkill {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "blog_post_id", nullable = false)
    private TechBlogPost blogPost;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "skill_id", nullable = false)
    private Skill skill;

    @Column(name = "mention_count")
    private Integer mentionCount;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    @Builder
    public BlogSkill(TechBlogPost blogPost, Skill skill, Integer mentionCount) {
        this.blogPost = blogPost;
        this.skill = skill;
        this.mentionCount = mentionCount != null ? mentionCount : 1;
    }
}
