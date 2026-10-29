# Performance notes

This project intentionally prioritizes correctness before optimization.

## Current approach

The Python reference implementation uses straightforward O(n) traversal for:
- UTF-8 validation
- code-point counting
- byte counting
- NFC normalization
- metadata extraction

The pipeline has been adjusted to reject oversized inputs before expensive UTF-8 encoding and to avoid re-encoding values that are already validated and unchanged.

## Measurement methodology

The benchmark script measures steady-state processing without active memory tracing during timed calls. It warms the interpreter and then records repeated timings for representative workloads. Memory is profiled separately and reported as peak tracked allocation during a dedicated pass.

## Current benchmark baseline

Measured on the project's current Windows Python 3.14 environment with the default configuration:

- ascii_short: median=0.00001070s, p95=0.00002100s, peak_mem=432 bytes
- ascii_long: median=0.00004250s, p95=0.00008170s, peak_mem=432 bytes
- unicode_mixed: median=0.00001525s, p95=0.00001880s, peak_mem=556 bytes
- combining: median=0.00002660s, p95=0.00003290s, peak_mem=524 bytes
- near_limit: median=0.00007360s, p95=0.00014700s, peak_mem=1185 bytes

These numbers are a baseline for the Python reference implementation. They are intentionally reported as measured values and not as claimed improvements against an unavailable old run.

## Benchmark targets

Representative workloads include:
- ASCII-only passwords
- mixed-script passwords
- combining-mark inputs
- values near configured limits
- normalized and non-normalized inputs

The library is designed for future Rust parity while preserving a simple Python reference model.
