package com.devpulse.company;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface CompanyRepository extends JpaRepository<Company, Long> {

    Optional<Company> findByName(String name);

    List<Company> findByCategory(CompanyCategory category);

    List<Company> findByCategoryIn(List<CompanyCategory> categories);
}
