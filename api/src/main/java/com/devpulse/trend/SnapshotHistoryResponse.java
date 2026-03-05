package com.devpulse.trend;

import java.time.LocalDateTime;
import java.util.List;

public record SnapshotHistoryResponse(
        String source,
        String skill,
        List<SnapshotPoint> history
) {
    public record SnapshotPoint(
            LocalDateTime snapshotAt,
            int rank,
            int mentionCount
    ) {}
}
