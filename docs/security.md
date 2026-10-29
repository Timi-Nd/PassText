# Security

Passwords are handled as sensitive data.

## Mandatory safeguards

- Never log raw passwords
- Never include password content in exceptions
- Never persist values in memory beyond the current processing step
- Never automatically serialize a prepared password object
- Keep repr output safe and metadata-only

## Known limitation

Python immutable strings cannot be reliably zeroized from memory after use. This library therefore documents the risk and avoids unsupported claims about secure erasure.
