"""Micro-benchmark for representative PassText workloads.

This benchmark is intentionally simple and reproducible. It measures steady-state
password processing without including import-time overhead.
"""

from __future__ import annotations

import statistics
import time
from pathlib import Path

from passtext import PassTextConfig, process_password

WORKLOADS = [
    ("ascii_short", "P@ssw0rd!"),
    ("ascii_long", "Tr0ub4dor&3" * 20),
    ("unicode_mixed", "Hello世界🙂123"),
    ("combining", "e\u0301e\u0301e\u0301"),
    ("near_limit", "é" * 512),
]


def benchmark_once(value: str, normalization: str) -> float:
    config = PassTextConfig(max_utf8_bytes=4096, max_codepoints=1024, normalization=normalization)
    start = time.perf_counter()
    process_password(value, config=config)
    return time.perf_counter() - start


def run_suite() -> dict[str, list[float]]:
    results: dict[str, list[float]] = {}
    for label, value in WORKLOADS:
        timings: list[float] = []
        for _ in range(200):
            timings.append(benchmark_once(value, normalization="none"))
        results[label] = timings
    return results


def print_summary(results: dict[str, list[float]]) -> None:
    print("PassText benchmark summary")
    print("=" * 28)
    for label, timings in results.items():
        median = statistics.median(timings)
        average = statistics.fmean(timings)
        p95 = sorted(timings)[int(len(timings) * 0.95) - 1]
        print(f"{label:>15}: avg={average:.8f}s median={median:.8f}s p95={p95:.8f}s")


if __name__ == "__main__":
    output = run_suite()
    print_summary(output)
    Path("benchmarks/output.txt").write_text("PassText benchmark executed\n", encoding="utf-8")
