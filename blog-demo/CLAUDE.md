# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Demo/playground project for runnable code examples accompanying blog articles in `../articles/`. Each article may reference or link to code snippets hosted here, allowing readers to experiment with working examples rather than just reading static code blocks.

## Tech Stack

- **Language:** Groovy (on JVM 21)
- **Framework:** Spring Boot 3.2.3
- **Security:** Spring Security (starter included for articles covering auth/security topics)
- **Build:** Gradle (Groovy DSL)
- **Testing:** JUnit 5, Spring Boot Test, Spring Security Test, Testcontainers
- **Other:** Lombok, Spring Validation, Spring DevTools

## Build and Run

```bash
# Build
./gradlew build

# Run the application
./gradlew bootRun

# Run tests
./gradlew test
```

## Package Structure

```
src/main/groovy/com/huashuo/blogdemo/
  BlogDemoApplication.groovy    # Spring Boot entry point

src/test/groovy/com/huashuo/blogdemo/
  BlogDemoApplicationTests.groovy
  TestBlogDemoApplication.groovy
```

## Relationship to Articles

This project is a companion to `../articles/`. Blog articles that include runnable Spring Boot or Groovy code examples should have their code placed here. When writing an article that references code in this project, link to the relevant source files.

## Conventions

- Source files are Groovy (`.groovy`), not Java
- Group ID: `com.huashuo`
- Tests use Testcontainers for integration testing with real infrastructure
- Use `./gradlew bootRun` to start the app; it runs on the default Spring Boot port (8080)
