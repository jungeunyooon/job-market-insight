package com.devpulse.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI openAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("DevPulse API")
                        .description("""
                                개발자 채용시장 분석 서비스 API.

                                ## 주요 기능
                                - **채용공고**: 공고 목록 조회, 필터링, 상세 조회
                                - **스킬 분석**: 기술 스택 랭킹, 포지션 비교, 갭 분석, 마인드맵
                                - **트렌드**: 커뮤니티 트렌드 랭킹, Buzz vs 채용 분석, 3축 분석
                                - **블로그**: 기업 기술 블로그 토픽 분석, 연도별 트렌드

                                ## 공통 사항
                                - 모든 엔드포인트는 `/api/v1/` prefix 사용
                                - 에러 응답은 RFC 7807 ProblemDetail 형식
                                """)
                        .version("2.0.0")
                        .contact(new Contact()
                                .name("Jungeun Yoon")
                                .email("yje00731@gmail.com")))
                .servers(List.of(
                        new Server().url("http://localhost:8080").description("로컬 개발 서버")
                ));
    }
}
