package com.devpulse.posting;

import com.devpulse.company.CompanyCategory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface PostingSkillRepository extends JpaRepository<PostingSkill, Long> {

    List<PostingSkill> findByPostingId(Long postingId);

    @Query("SELECT ps.skill.name, COUNT(DISTINCT ps.posting.id) as cnt " +
           "FROM PostingSkill ps " +
           "WHERE ps.posting.positionType = :positionType " +
           "GROUP BY ps.skill.name " +
           "ORDER BY cnt DESC")
    List<Object[]> findSkillRankingByPositionType(
            @Param("positionType") PositionType positionType
    );

    @Query("SELECT ps.skill.name, COUNT(DISTINCT ps.posting.id) as cnt " +
           "FROM PostingSkill ps " +
           "WHERE ps.posting.company.id = :companyId " +
           "GROUP BY ps.skill.name " +
           "ORDER BY cnt DESC")
    List<Object[]> findSkillRankingByCompany(@Param("companyId") Long companyId);

    @Query("SELECT ps.skill.name, " +
           "COUNT(DISTINCT ps.posting.id) as cnt, " +
           "SUM(CASE WHEN ps.isRequired = true THEN 1 ELSE 0 END) as requiredCount " +
           "FROM PostingSkill ps " +
           "WHERE (:positionType IS NULL OR ps.posting.positionType = :positionType) " +
           "AND (:includeClosedPostings = true OR ps.posting.status = com.devpulse.posting.PostingStatus.ACTIVE) " +
           "AND (:categories IS NULL OR ps.posting.company.category IN :categories) " +
           "GROUP BY ps.skill.name " +
           "ORDER BY cnt DESC")
    List<Object[]> findSkillRankingWithFilters(
            @Param("positionType") PositionType positionType,
            @Param("includeClosedPostings") boolean includeClosedPostings,
            @Param("categories") List<CompanyCategory> categories
    );

    @Query("SELECT COUNT(DISTINCT ps.posting.id) " +
           "FROM PostingSkill ps " +
           "WHERE (:positionType IS NULL OR ps.posting.positionType = :positionType) " +
           "AND (:includeClosedPostings = true OR ps.posting.status = com.devpulse.posting.PostingStatus.ACTIVE) " +
           "AND (:categories IS NULL OR ps.posting.company.category IN :categories)")
    long countPostingsWithFilters(
            @Param("positionType") PositionType positionType,
            @Param("includeClosedPostings") boolean includeClosedPostings,
            @Param("categories") List<CompanyCategory> categories
    );

    @Query("SELECT ps.posting.positionType, COUNT(DISTINCT ps.posting.id) " +
           "FROM PostingSkill ps " +
           "WHERE ps.posting.company.id = :companyId " +
           "GROUP BY ps.posting.positionType")
    List<Object[]> findPositionBreakdownByCompany(@Param("companyId") Long companyId);
}
