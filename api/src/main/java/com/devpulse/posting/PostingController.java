package com.devpulse.posting;

import com.devpulse.posting.PostingDetailResponse;
import com.devpulse.posting.PostingResponse;
import com.devpulse.company.CompanyCategory;
import com.devpulse.posting.PostingStatus;
import com.devpulse.posting.PositionType;
import com.devpulse.posting.PostingService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/v1/postings")
@RequiredArgsConstructor
public class PostingController {

    private final PostingService postingService;

    @GetMapping
    public ResponseEntity<Page<PostingResponse>> getPostings(
            @RequestParam(required = false) PositionType positionType,
            @RequestParam(required = false) List<CompanyCategory> companyCategory,
            @RequestParam(required = false) List<PostingStatus> status,
            @RequestParam(required = false) List<String> skillName,
            @RequestParam(required = false) LocalDate dateFrom,
            @RequestParam(required = false) LocalDate dateTo,
            @PageableDefault(size = 20, sort = "postedAt", direction = Sort.Direction.DESC) Pageable pageable
    ) {
        Page<PostingResponse> result = postingService.findAll(
                positionType, companyCategory, status, skillName, dateFrom, dateTo, pageable
        );
        return ResponseEntity.ok(result);
    }

    @GetMapping("/{id}")
    public ResponseEntity<PostingDetailResponse> getPosting(@PathVariable Long id) {
        return ResponseEntity.ok(postingService.findById(id));
    }
}
