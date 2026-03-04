package com.devpulse.posting;

import com.devpulse.posting.PostingDetailResponse;
import com.devpulse.posting.PostingResponse;
import com.devpulse.company.Company;
import com.devpulse.company.CompanyCategory;
import com.devpulse.posting.*;
import com.devpulse.skill.Skill;
import com.devpulse.skill.SkillSourceScope;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.BDDMockito.given;

@ExtendWith(MockitoExtension.class)
class PostingServiceTest {

    @Mock
    private JobPostingRepository jobPostingRepository;

    @Mock
    private PostingSkillRepository postingSkillRepository;

    @InjectMocks
    private PostingService postingService;

    private Company testCompany;
    private JobPosting testPosting;
    private Skill testSkill;
    private PostingSkill testPostingSkill;

    @BeforeEach
    void setUp() {
        testCompany = Company.builder()
                .name("네이버")
                .category(CompanyCategory.BIGTECH)
                .build();

        testPosting = JobPosting.builder()
                .company(testCompany)
                .title("백엔드 개발자")
                .positionType(PositionType.BACKEND)
                .sourcePlatform("wanted")
                .sourceUrl("https://wanted.co.kr/wd/12345")
                .status(PostingStatus.ACTIVE)
                .build();

        testSkill = Skill.builder()
                .name("Java")
                .category("language")
                .sourceScope(SkillSourceScope.BOTH)
                .build();

        testPostingSkill = PostingSkill.builder()
                .posting(testPosting)
                .skill(testSkill)
                .isRequired(true)
                .isPreferred(false)
                .build();
    }

    @Nested
    @DisplayName("findAll")
    class FindAll {

        @Test
        @DisplayName("필터 없이 전체 조회")
        void findAll_noFilters() {
            Pageable pageable = PageRequest.of(0, 20);
            Page<JobPosting> page = new PageImpl<>(List.of(testPosting), pageable, 1);
            given(jobPostingRepository.findByFiltersExtended(null, null, null, null, null, pageable))
                    .willReturn(page);
            given(postingSkillRepository.findByPostingId(any())).willReturn(List.of(testPostingSkill));

            Page<PostingResponse> result = postingService.findAll(null, null, null, null, null, null, pageable);

            assertThat(result.getTotalElements()).isEqualTo(1);
            assertThat(result.getContent().getFirst().companyName()).isEqualTo("네이버");
            assertThat(result.getContent().getFirst().skills()).containsExactly("Java");
        }

        @Test
        @DisplayName("positionType으로 필터링")
        void findAll_byPositionType() {
            Pageable pageable = PageRequest.of(0, 20);
            Page<JobPosting> page = new PageImpl<>(List.of(testPosting), pageable, 1);
            given(jobPostingRepository.findByFiltersExtended(eq(PositionType.BACKEND), isNull(), isNull(), isNull(), isNull(), eq(pageable)))
                    .willReturn(page);
            given(postingSkillRepository.findByPostingId(any())).willReturn(List.of(testPostingSkill));

            Page<PostingResponse> result = postingService.findAll(
                    PositionType.BACKEND, null, null, null, null, null, pageable
            );

            assertThat(result.getTotalElements()).isEqualTo(1);
            assertThat(result.getContent().getFirst().positionType()).isEqualTo(PositionType.BACKEND);
        }

        @Test
        @DisplayName("skillName으로 필터링 — 스킬 기반 조인 쿼리 사용")
        void findAll_bySkillName() {
            Pageable pageable = PageRequest.of(0, 20);
            List<String> skillNames = List.of("Java");
            Page<JobPosting> page = new PageImpl<>(List.of(testPosting), pageable, 1);
            given(jobPostingRepository.findByFiltersWithSkills(isNull(), isNull(), isNull(), eq(skillNames), isNull(), isNull(), eq(pageable)))
                    .willReturn(page);
            given(postingSkillRepository.findByPostingId(any())).willReturn(List.of(testPostingSkill));

            Page<PostingResponse> result = postingService.findAll(
                    null, null, null, skillNames, null, null, pageable
            );

            assertThat(result.getTotalElements()).isEqualTo(1);
            assertThat(result.getContent().getFirst().skills()).contains("Java");
        }

        @Test
        @DisplayName("빈 결과")
        void findAll_empty() {
            Pageable pageable = PageRequest.of(0, 20);
            Page<JobPosting> emptyPage = new PageImpl<>(List.of(), pageable, 0);
            given(jobPostingRepository.findByFiltersExtended(any(), any(), any(), any(), any(), any()))
                    .willReturn(emptyPage);

            Page<PostingResponse> result = postingService.findAll(null, null, null, null, null, null, pageable);

            assertThat(result.getTotalElements()).isZero();
            assertThat(result.getContent()).isEmpty();
        }
    }

    @Nested
    @DisplayName("findById")
    class FindById {

        @Test
        @DisplayName("존재하는 공고 조회")
        void findById_exists() {
            given(jobPostingRepository.findById(1L)).willReturn(Optional.of(testPosting));
            given(postingSkillRepository.findByPostingId(any())).willReturn(List.of(testPostingSkill));

            PostingDetailResponse result = postingService.findById(1L);

            assertThat(result.title()).isEqualTo("백엔드 개발자");
            assertThat(result.company().name()).isEqualTo("네이버");
            assertThat(result.skills()).hasSize(1);
            assertThat(result.skills().getFirst().name()).isEqualTo("Java");
            assertThat(result.skills().getFirst().isRequired()).isTrue();
        }

        @Test
        @DisplayName("존재하지 않는 공고 — PostingNotFoundException")
        void findById_notFound() {
            given(jobPostingRepository.findById(999L)).willReturn(Optional.empty());

            assertThatThrownBy(() -> postingService.findById(999L))
                    .isInstanceOf(PostingService.PostingNotFoundException.class)
                    .hasMessageContaining("999");
        }
    }
}
