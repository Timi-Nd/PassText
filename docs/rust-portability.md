# Rust portability specification

The Python implementation is the behavioral reference for a future Rust port. The goal is to preserve the same values, boundaries, and error classification while allowing a lower-allocation native implementation.

## Cross-language contract

### 1. Input validation

- Accept only Python `str`/Rust `&str` equivalents.
- Empty strings are valid.
- Reject isolated surrogate code points and other non-UTF-8 representations before processing.
- Enforce `max_codepoints` and `max_utf8_bytes` before heavy analysis.
- Raise equivalent typed error categories, without exposing password content.

Time complexity: O(n)
Space complexity: O(1) beyond the input itself
Rust ownership concern: borrowed string slices avoid copying unless normalization or prepared output requires a new allocation

### 2. Unicode processing

- Count Unicode code points using the actual string length in code points.
- Count UTF-8 bytes via strict UTF-8 encoding length.
- Preserve `contains_non_ascii` semantics and reject unsupported encodings.

Time complexity: O(n)
Space complexity: O(1) for counts and ASCII detection; O(n) for encoded byte arrays if materialized
Rust ownership concern: Rust string slices already give UTF-8-safe indexing; no lossy conversion is allowed

### 3. Normalization

- Support only `none` and `nfc` in this phase.
- Apply normalization explicitly and deterministically.
- Keep the original input available for metadata and comparison.

Time complexity: O(n)
Space complexity: O(n) for normalized output
Rust ownership concern: normalization may allocate a new `String` in the Rust impl; the original borrowed input must remain separate

### 4. Metadata

- Produce immutable metadata values only.
- Never serialize or expose password text through metadata or repr output.
- Track original and processed code points and bytes, normalization mode, and whether normalization changed the input.

Time complexity: O(n)
Space complexity: O(1)
Rust ownership concern: immutable metadata can be represented as a compact struct with borrowed or owned values

### 5. Safe indexing

- Use half-open ranges `[start, end)` defined over Unicode code points.
- Byte offsets are separate and must not be silently interchanged with code-point offsets.
- Reject offsets that fall in the middle of a UTF-8 sequence.

Time complexity: O(n) to build or O(k) for direct offset conversion on a single boundary
Space complexity: O(1) for direct conversions; O(n) for cached offset tables if later needed
Rust ownership concern: Rust slices and byte offsets are naturally explicit but must remain clearly documented to avoid code-point/byte confusion

## Portable fixture set

The project includes cross-language vectors in [tests/fixtures/rust_portability_vectors.json](../tests/fixtures/rust_portability_vectors.json). These fixtures include:

- ASCII input
- NFC combining-mark normalization
- isolated surrogate rejection
- expected counts and normalization results

These fixtures are intentionally free of real password secrets and are suitable for future Rust parity testing.

## Required parity rules

A Rust implementation must preserve these Python semantics exactly:

- same valid/invalid string classification
- same code-point and byte counts for each input
- same processed text after normalization
- same normalization changed flag
- same boundary validation for UTF-8 offsets
- same no-logging/no-secret exposure contract

## Residual limitations

This Python implementation does not include grapheme-cluster counting or password-strength scoring. Those are intentionally left out to keep the contract precise and portable.
