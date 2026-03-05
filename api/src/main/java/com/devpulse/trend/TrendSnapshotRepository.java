package com.devpulse.trend;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.data.jpa.repository.Query;

import java.time.LocalDateTime;
import java.util.List;

public interface TrendSnapshotRepository extends JpaRepository<TrendSnapshot, Long> {

    @Query("SELECT ts FROM TrendSnapshot ts " +
           "WHERE ts.source = :source " +
           "AND ts.skillName = :skillName " +
           "AND ts.snapshotAt BETWEEN :from AND :to " +
           "ORDER BY ts.snapshotAt ASC")
    List<TrendSnapshot> findBySourceAndSkillNameAndSnapshotAtBetween(
            @Param("source") TrendSource source,
            @Param("skillName") String skillName,
            @Param("from") LocalDateTime from,
            @Param("to") LocalDateTime to
    );
}
