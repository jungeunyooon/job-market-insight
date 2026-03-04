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
           "WHERE (:positionType IS NULL OR jp.positionType = :positionType) " +
           "AND (:statuses IS NULL OR jp.status IN :statuses) " +
           "AND (:categories IS NULL OR jp.company.category IN :categories) " +
           "AND s.name IN :skillNames " +
           "AND (:dateFrom IS NULL OR jp.postedAt >= :dateFrom) " +
           "AND (:dateTo IS NULL OR jp.postedAt <= :dateTo)")
    Page<JobPosting> findByFiltersWithSkills(
            @Param("positionType") PositionType positionType,
            @Param("statuses") List<PostingStatus> statuses,
            @Param("categories") List<CompanyCategory> categories,
            @Param("skillNames") List<String> skillNames,
            @Param("dateFrom") LocalDateTime dateFrom,
            @Param("dateTo") LocalDateTime dateTo,
            Pageable pageable
    );

    @Query("SELECT jp FROM JobPosting jp " +
           "WHERE (:positionType IS NULL OR jp.positionType = :positionType) " +
           "AND (:statuses IS NULL OR jp.status IN :statuses) " +
           "AND (:categories IS NULL OR jp.company.category IN :categories) " +
           "AND (:dateFrom IS NULL OR jp.postedAt >= :dateFrom) " +
           "AND (:dateTo IS NULL OR jp.postedAt <= :dateTo)")
    Page<JobPosting> findByFiltersExtended(
            @Param("positionType") PositionType positionType,
            @Param("statuses") List<PostingStatus> statuses,
            @Param("categories") List<CompanyCategory> categories,
            @Param("dateFrom") LocalDateTime dateFrom,
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
}
