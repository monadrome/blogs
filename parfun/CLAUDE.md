# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Playground project for parallel programming and functional programming experiments in Java. Contains standalone `main` method demos that explore concurrency patterns, parallel execution strategies, and functional idioms. Code here backs blog articles in `../articles/` covering these topics.

## Tech Stack

- **Language:** Java 21
- **Framework:** Spring Boot 3.5.4 (used sparingly; most classes have their own `main`)
- **Build:** Gradle with Kotlin DSL (`build.gradle.kts`)
- **Key Libraries:**
  - **Caffeine 3.2.2** -- async caching, read-through patterns
  - **CFFU 2.0.2** -- enhanced CompletableFuture utilities
  - **parallel-collectors 3.3.0** -- parallel stream collection
  - **Guava 33.4.8** -- ListenableFuture, ImmutableList, Uninterruptibles, TypeToken
  - **jOOL 0.9.15** -- tuple collectors, functional extensions
  - **Transmittable Thread Local (TTL) 2.14.5** -- context propagation across thread pools
  - **throwing-function 1.6.1** -- sneaky throw wrappers for checked exceptions

## Build and Run

```bash
# Build
./gradlew build

# Run a specific demo class
./gradlew bootRun               # runs ParfunApplication.main()
# Or run individual demo files directly from IDE (each has a public static void main)
```

Most experiment classes have their own `main` method and are intended to be run individually from an IDE rather than through the boot task.

## Key Experiment Files

| File | Topic |
|---|---|
| `ParallelismDemo.java` | Guava ListenableFuture-based parallel execution with controlled concurrency; race-queue pattern using `Futures.inCompletionOrder` |
| `aa/ParallelismDemo.java` | Advanced variant using `ExecutorCompletionService`, `SettableFuture`, and a `ConcurrentLimitExecutor` abstraction |
| `Main.java` | ConcurrentHashMap `computeIfAbsent` deadlock scenario (AaAa/BBBB hash collision) |
| `ParfunApplication.java` | Caffeine async cache read-through demo; Guava `Equivalence` and `Iterables` usage; HashMap entry removal with `removeIf` |
| `DiscardDemo.java` | ThreadPoolExecutor with AbortPolicy + CompletableFuture timeout behavior |
| `JooqCollector.java` | jOOL `Tuple.collectors` for combining multiple stream collectors into a tuple result |
| `InterruptionExample.java` | Thread interruption patterns: standard `Thread.interrupted()` loop vs Guava `Uninterruptibles.sleepUninterruptibly` |
| `DefensiveHashMap.java` | Demonstrates HashMap thread-safety issues with parallel streams |
| `JDK25.java` | CompletableFuture `orTimeout` behavior experiments |
| `A.java` | Guava `TypeToken` for capturing generic type information at runtime |
| `AA.java` | Forbidding `equals`/`hashCode` override using `final` |
| `T.java` | Guava `Throwables.throwIfInstanceOf` for checked exception handling |

## Package Structure

```
src/main/java/com/example/parfun/
  ParfunApplication.java        # Spring Boot entry point (also contains demos)
  Main.java                     # Standalone demos
  ParallelismDemo.java          # Parallel execution experiments
  DiscardDemo.java              # Thread pool rejection policy demos
  JooqCollector.java            # jOOL tuple collector demo
  InterruptionExample.java      # Thread interruption patterns
  DefensiveHashMap.java         # Concurrent HashMap issues
  JDK25.java                    # JDK CompletableFuture experiments
  A.java, AA.java, T.java       # Miscellaneous experiments
  aa/
    ParallelismDemo.java        # Advanced parallel execution patterns
    test.java                   # Placeholder
```

## Relationship to Articles

This project is a companion to `../articles/`. Articles covering CompletableFuture, parallel execution, Guava utilities, functional programming, and concurrency patterns reference runnable demos from this project.

## Conventions

- Each experiment is a standalone class with `public static void main` -- run directly from IDE
- Lombok `@Slf4j` is used for logging
- Group ID: `com.example`
- Commented-out code blocks are intentional -- they show alternative approaches or experiments in progress
