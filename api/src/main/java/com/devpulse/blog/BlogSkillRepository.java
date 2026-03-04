package com.devpulse.blog;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface BlogSkillRepository extends JpaRepository<BlogSkill, Long> {

    @Query("SELECT bs.skill.name, COUNT(DISTINCT bs.blogPost.id) as cnt " +
           "FROM BlogSkill bs " +
           "WHERE bs.blogPost.company.id = :companyId " +
           "AND (:fromYear IS NULL OR bs.blogPost.publishedYear >= :fromYear) " +
           "AND (:toYear IS NULL OR bs.blogPost.publishedYear <= :toYear) " +
           "GROUP BY bs.skill.name " +
           "ORDER BY cnt DESC")
    List<Object[]> findSkillRankingByCompanyAndYear(
            @Param("companyId") Long companyId,
            @Param("fromYear") Integer fromYear,
            @Param("toYear") Integer toYear
    );

    @Query("SELECT bs.blogPost.publishedYear, bs.skill.name, COUNT(DISTINCT bs.blogPost.id) as cnt " +
           "FROM BlogSkill bs " +
           "WHERE bs.blogPost.publishedYear IS NOT NULL " +
           "AND (:fromYear IS NULL OR bs.blogPost.publishedYear >= :fromYear) " +
           "AND (:toYear IS NULL OR bs.blogPost.publishedYear <= :toYear) " +
           "GROUP BY bs.blogPost.publishedYear, bs.skill.name " +
           "ORDER BY bs.blogPost.publishedYear, cnt DESC")
    List<Object[]> findYearlySkillTrend(
            @Param("fromYear") Integer fromYear,
            @Param("toYear") Integer toYear
    );

    @Query("SELECT bs.blogPost.company.name, COUNT(DISTINCT bs.blogPost.id) as cnt " +
           "FROM BlogSkill bs " +
           "WHERE bs.skill.name = :skillName " +
           "AND (:fromYear IS NULL OR bs.blogPost.publishedYear >= :fromYear) " +
           "AND (:toYear IS NULL OR bs.blogPost.publishedYear <= :toYear) " +
           "GROUP BY bs.blogPost.company.name " +
           "ORDER BY cnt DESC")
    List<Object[]> findCompanyDistributionBySkill(
            @Param("skillName") String skillName,
            @Param("fromYear") Integer fromYear,
            @Param("toYear") Integer toYear
    );
}
