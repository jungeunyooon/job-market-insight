package com.devpulse.company;

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
@Table(name = "company")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Company {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String name;

    @Column(name = "name_en", length = 200)
    private String nameEn;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, columnDefinition = "company_category")
    private CompanyCategory category;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    private List<String> tags;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    private List<String> aliases;

    @Column(name = "careers_url", length = 500)
    private String careersUrl;

    @Column(name = "tech_blog_url", length = 500)
    private String techBlogUrl;

    @Column(name = "tech_blog_type", length = 20)
    private String techBlogType;

    @Column(name = "employee_count_range", length = 50)
    private String employeeCountRange;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    @Builder
    public Company(String name, String nameEn, CompanyCategory category,
                   List<String> tags, List<String> aliases,
                   String careersUrl, String techBlogUrl, String techBlogType) {
        this.name = name;
        this.nameEn = nameEn;
        this.category = category != null ? category : CompanyCategory.UNCATEGORIZED;
        this.tags = tags != null ? tags : List.of();
        this.aliases = aliases != null ? aliases : List.of();
        this.careersUrl = careersUrl;
        this.techBlogUrl = techBlogUrl;
        this.techBlogType = techBlogType;
    }
}
