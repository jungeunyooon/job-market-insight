package com.devpulse.posting;

import com.devpulse.skill.Skill;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "posting_skill")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class PostingSkill {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "posting_id", nullable = false)
    private JobPosting posting;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "skill_id", nullable = false)
    private Skill skill;

    @Column(name = "is_required")
    private Boolean isRequired;

    @Column(name = "is_preferred")
    private Boolean isPreferred;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    @Builder
    public PostingSkill(JobPosting posting, Skill skill,
                        Boolean isRequired, Boolean isPreferred) {
        this.posting = posting;
        this.skill = skill;
        this.isRequired = isRequired != null ? isRequired : false;
        this.isPreferred = isPreferred != null ? isPreferred : false;
    }
}
