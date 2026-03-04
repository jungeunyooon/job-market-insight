package com.devpulse.trend;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

public interface TrendPostRepository extends JpaRepository<TrendPost, Long> {

    Optional<TrendPost> findBySourceAndExternalId(TrendSource source, String externalId);

    List<TrendPost> findBySourceOrderByPublishedAtDesc(TrendSource source);

    @Query("SELECT COUNT(tp) FROM TrendPost tp " +
           "WHERE tp.source = :source " +
           "AND tp.publishedAt >= :since")
    long countBySourceSince(
            @Param("source") TrendSource source,
            @Param("since") LocalDateTime since
    );
}
