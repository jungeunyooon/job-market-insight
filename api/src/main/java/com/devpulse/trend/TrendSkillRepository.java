package com.devpulse.trend;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;

public interface TrendSkillRepository extends JpaRepository<TrendSkill, Long> {

    @Query("SELECT ts.skill.name, COUNT(DISTINCT ts.trendPost.id) as cnt " +
           "FROM TrendSkill ts " +
           "WHERE ts.trendPost.source = :source " +
           "AND ts.trendPost.publishedAt >= :since " +
           "GROUP BY ts.skill.name " +
           "ORDER BY cnt DESC")
    List<Object[]> findSkillRankingBySourceSince(
            @Param("source") TrendSource source,
            @Param("since") LocalDateTime since
    );

    @Query("SELECT ts.skill.name, COUNT(DISTINCT ts.trendPost.id) as cnt " +
           "FROM TrendSkill ts " +
           "WHERE ts.trendPost.publishedAt >= :since " +
           "GROUP BY ts.skill.name " +
           "ORDER BY cnt DESC")
    List<Object[]> findSkillRankingSince(@Param("since") LocalDateTime since);

    @Query("SELECT COUNT(DISTINCT ts.trendPost.id) " +
           "FROM TrendSkill ts " +
           "WHERE ts.trendPost.publishedAt >= :since")
    long countTrendPostsSince(@Param("since") LocalDateTime since);
}
