package com.devpulse.skill;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface SkillRepository extends JpaRepository<Skill, Long> {

    Optional<Skill> findByName(String name);

    List<Skill> findByCategory(String category);

    List<Skill> findBySourceScope(SkillSourceScope sourceScope);

    List<Skill> findBySourceScopeIn(List<SkillSourceScope> scopes);
}
