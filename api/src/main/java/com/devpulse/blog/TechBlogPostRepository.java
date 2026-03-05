package com.devpulse.blog;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface TechBlogPostRepository extends JpaRepository<TechBlogPost, Long> {

    Optional<TechBlogPost> findByUrl(String url);

    List<TechBlogPost> findByCompanyIdOrderByPublishedAtDesc(Long companyId);

    Page<TechBlogPost> findAllByOrderByPublishedAtDesc(Pageable pageable);

    Page<TechBlogPost> findByCompanyIdOrderByPublishedAtDesc(Long companyId, Pageable pageable);

    @Query("SELECT bp.publishedYear, COUNT(bp) FROM TechBlogPost bp " +
           "WHERE bp.company.id = :companyId " +
           "AND bp.publishedYear IS NOT NULL " +
           "GROUP BY bp.publishedYear " +
           "ORDER BY bp.publishedYear")
    List<Object[]> countByCompanyGroupByYear(@Param("companyId") Long companyId);

    long countByCompanyId(Long companyId);
}
