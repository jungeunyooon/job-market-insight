package com.devpulse.blog;

import java.time.LocalDateTime;

public record BlogPostListResponse(
    Long id,
    String title,
    String url,
    String summary,
    String companyName,
    LocalDateTime publishedAt
) {
    public static BlogPostListResponse from(TechBlogPost post) {
        return new BlogPostListResponse(
            post.getId(),
            post.getTitle(),
            post.getUrl(),
            post.getSummary(),
            post.getCompany().getName(),
            post.getPublishedAt()
        );
    }
}
