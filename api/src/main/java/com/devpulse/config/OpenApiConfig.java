package com.devpulse.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI openAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("DevPulse API")
                        .description("채용시장 기술 스택 분석 API")
                        .version("1.0.0")
                        .contact(new Contact()
                                .name("Jungeun Yoon")
                                .email("yje00731@gmail.com")));
    }
}
