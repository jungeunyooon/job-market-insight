package com.devpulse.posting;

import com.devpulse.posting.PostingDetailResponse;
import com.devpulse.posting.PostingResponse;
import com.devpulse.company.CompanyCategory;
import com.devpulse.posting.*;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PostingService {

    private final JobPostingRepository jobPostingRepository;
    private final PostingSkillRepository postingSkillRepository;

    public Page<PostingResponse> findAll(
            PositionType positionType,
            List<CompanyCategory> categories,
            List<PostingStatus> statuses,
            List<String> skillNames,
            LocalDate dateFrom,
            LocalDate dateTo,
            Pageable pageable
    ) {
        LocalDateTime from = dateFrom != null ? dateFrom.atStartOfDay() : null;
        LocalDateTime to = dateTo != null ? dateTo.atTime(23, 59, 59) : null;

        Page<JobPosting> postings;
        if (skillNames != null && !skillNames.isEmpty()) {
            postings = jobPostingRepository.findByFiltersWithSkills(
                    positionType, statuses, categories, skillNames, from, to, pageable
            );
        } else {
            postings = jobPostingRepository.findByFiltersExtended(
                    positionType, statuses, categories, from, to, pageable
            );
        }

        return postings.map(posting -> {
            List<PostingSkill> skills = postingSkillRepository.findByPostingId(posting.getId());
            return PostingResponse.from(posting, skills);
        });
    }

    public PostingDetailResponse findById(Long id) {
        JobPosting posting = jobPostingRepository.findById(id)
                .orElseThrow(() -> new PostingNotFoundException(id));
        List<PostingSkill> skills = postingSkillRepository.findByPostingId(id);
        return PostingDetailResponse.from(posting, skills);
    }

    public static class PostingNotFoundException extends RuntimeException {
        public PostingNotFoundException(Long id) {
            super("Posting not found: " + id);
        }
    }
}
