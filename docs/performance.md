# Performance notes

This project intentionally prioritizes correctness before optimization.

## Current approach

The initial implementation uses straightforward O(n) traversal for:
- UTF-8 validation
- code-point counting
- byte counting
- NFC normalization

## Benchmark targets

Planned benchmark scenarios include:
- ASCII-only passwords
- mixed-script passwords
- combining-mark inputs
- values near configured limits
- normalized and non-normalized inputs

The library is designed for future Rust parity while preserving a simple Python reference model.
