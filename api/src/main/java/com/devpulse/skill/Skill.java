package com.devpulse.skill;

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
@Table(name = "skill")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Skill {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100, unique = true)
    private String name;

    @Column(name = "name_ko", length = 100)
    private String nameKo;

    @Column(nullable = false, length = 50)
    private String category;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    private List<String> aliases;

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.NAMED_ENUM)
    @Column(name = "source_scope", nullable = false, columnDefinition = "skill_source_scope")
    private SkillSourceScope sourceScope;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    @Builder
    public Skill(String name, String nameKo, String category,
                 List<String> aliases, SkillSourceScope sourceScope) {
        this.name = name;
        this.nameKo = nameKo;
        this.category = category;
        this.aliases = aliases != null ? aliases : List.of();
        this.sourceScope = sourceScope != null ? sourceScope : SkillSourceScope.BOTH;
    }
}
