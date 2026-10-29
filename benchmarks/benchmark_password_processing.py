"""Micro-benchmark for representative PassText workloads.

This benchmark is intentionally simple and reproducible. It measures steady-state
password processing without including import-time overhead.
"""

from __future__ import annotations

import statistics
import time
import tracemalloc
from pathlib import Path

from passtext import PassTextConfig, process_password

WORKLOADS = [
    ("ascii_short", "P@ssw0rd!"),
    ("ascii_long", "Tr0ub4dor&3" * 20),
    ("unicode_mixed", "Hello世界🙂123"),
    ("combining", "e\u0301e\u0301e\u0301"),
    ("near_limit", "é" * 512),
]


def benchmark_once(value: str, normalization: str) -> tuple[float, int]:
    config = PassTextConfig(max_utf8_bytes=4096, max_codepoints=1024, normalization=normalization)
    tracemalloc.start()
    start = time.perf_counter()
    process_password(value, config=config)
    elapsed = time.perf_counter() - start
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return elapsed, peak


def run_suite() -> dict[str, list[tuple[float, int]]]:
    results: dict[str, list[tuple[float, int]]] = {}
    for label, value in WORKLOADS:
        timings: list[tuple[float, int]] = []
        for _ in range(200):
            timings.append(benchmark_once(value, normalization="none"))
        results[label] = timings
    return results


def print_summary(results: dict[str, list[tuple[float, int]]]) -> None:
    print("PassText benchmark summary")
    print("=" * 28)
    for label, timings in results.items():
        elapsed_values = [item[0] for item in timings]
        peaks = [item[1] for item in timings]
        median = statistics.median(elapsed_values)
        average = statistics.fmean(elapsed_values)
        p95 = sorted(elapsed_values)[int(len(elapsed_values) * 0.95) - 1]
        peak_memory = max(peaks)
        print(
            f"{label:>15}: avg={average:.8f}s median={median:.8f}s p95={p95:.8f}s "
            f"peak_mem={peak_memory} bytes"
        )


if __name__ == "__main__":
    output = run_suite()
    print_summary(output)
    Path("benchmarks/output.txt").write_text("PassText benchmark executed\n", encoding="utf-8")
