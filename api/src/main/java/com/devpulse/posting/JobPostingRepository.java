package com.devpulse.posting;

import com.devpulse.company.CompanyCategory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;

public interface JobPostingRepository extends JpaRepository<JobPosting, Long> {

    Page<JobPosting> findByPositionType(PositionType positionType, Pageable pageable);

    Page<JobPosting> findByStatus(PostingStatus status, Pageable pageable);

    @Query("SELECT jp FROM JobPosting jp WHERE jp.company.category IN :categories")
    Page<JobPosting> findByCompanyCategories(
            @Param("categories") List<CompanyCategory> categories,
            Pageable pageable
    );

    @Query("SELECT jp FROM JobPosting jp " +
           "WHERE (:positionType IS NULL OR jp.positionType = :positionType) " +
           "AND (:status IS NULL OR jp.status = :status) " +
           "AND (:categories IS NULL OR jp.company.category IN :categories)")
    Page<JobPosting> findByFilters(
            @Param("positionType") PositionType positionType,
            @Param("status") PostingStatus status,
            @Param("categories") List<CompanyCategory> categories,
            Pageable pageable
    );

    @Query("SELECT DISTINCT jp FROM JobPosting jp " +
           "JOIN PostingSkill ps ON ps.posting = jp " +
           "JOIN ps.skill s " +
           "WHERE (:hasPosition = false OR jp.positionType = :positionType) " +
           "AND jp.status IN :statuses " +
           "AND jp.company.category IN :categories " +
           "AND s.name IN :skillNames " +
           "AND (:hasDateFrom = false OR jp.postedAt >= :dateFrom) " +
           "AND (:hasDateTo = false OR jp.postedAt <= :dateTo)")
    Page<JobPosting> findByFiltersWithSkills(
            @Param("hasPosition") boolean hasPosition,
            @Param("positionType") PositionType positionType,
            @Param("statuses") List<PostingStatus> statuses,
            @Param("categories") List<CompanyCategory> categories,
            @Param("skillNames") List<String> skillNames,
            @Param("hasDateFrom") boolean hasDateFrom,
            @Param("dateFrom") LocalDateTime dateFrom,
            @Param("hasDateTo") boolean hasDateTo,
            @Param("dateTo") LocalDateTime dateTo,
            Pageable pageable
    );

    @Query("SELECT jp FROM JobPosting jp " +
           "WHERE (:hasPosition = false OR jp.positionType = :positionType) " +
           "AND jp.status IN :statuses " +
           "AND jp.company.category IN :categories " +
           "AND (:hasDateFrom = false OR jp.postedAt >= :dateFrom) " +
           "AND (:hasDateTo = false OR jp.postedAt <= :dateTo)")
    Page<JobPosting> findByFiltersExtended(
            @Param("hasPosition") boolean hasPosition,
            @Param("positionType") PositionType positionType,
            @Param("statuses") List<PostingStatus> statuses,
            @Param("categories") List<CompanyCategory> categories,
            @Param("hasDateFrom") boolean hasDateFrom,
            @Param("dateFrom") LocalDateTime dateFrom,
            @Param("hasDateTo") boolean hasDateTo,
            @Param("dateTo") LocalDateTime dateTo,
            Pageable pageable
    );

    long countByStatus(PostingStatus status);

    long countByPositionType(PositionType positionType);

    long countByCompanyId(Long companyId);

    @Query("SELECT jp.positionType, COUNT(jp) FROM JobPosting jp " +
           "WHERE jp.company.id = :companyId " +
           "GROUP BY jp.positionType")
    List<Object[]> countByCompanyIdGroupByPositionType(@Param("companyId") Long companyId);

    @Query(value = """
        SELECT req->>'normalized' AS normalized,
               req->>'category' AS category,
               COUNT(*) AS cnt
        FROM job_posting jp,
             jsonb_array_elements(jp.normalized_requirements) AS req
        WHERE (:hasPosition = false OR jp.position_type = :positionType)
          AND jp.status = 'ACTIVE'
          AND jsonb_array_length(jp.normalized_requirements) > 0
        GROUP BY req->>'normalized', req->>'category'
        ORDER BY cnt DESC
        """, nativeQuery = true)
    List<Object[]> findNormalizedRequirementAggregation(
            @Param("hasPosition") boolean hasPosition,
            @Param("positionType") String positionType
    );

    long countByPositionTypeAndStatus(PositionType positionType, PostingStatus status);
}
