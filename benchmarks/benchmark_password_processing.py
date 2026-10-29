"""Micro-benchmark for representative PassText workloads.

This benchmark separates steady-state latency measurement from memory profiling so the
performance numbers reflect realistic processing cost rather than instrumentation overhead.
"""

from __future__ import annotations

import json
import statistics
import sys
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


def benchmark_latency(
    value: str, normalization: str, *, iterations: int = 400, warmup: int = 50
) -> list[float]:
    config = PassTextConfig(max_utf8_bytes=4096, max_codepoints=1024, normalization=normalization)
    for _ in range(warmup):
        process_password(value, config=config)

    timings: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        process_password(value, config=config)
        timings.append(time.perf_counter() - start)
    return timings


def benchmark_memory(value: str, normalization: str, *, iterations: int = 250) -> int:
    config = PassTextConfig(max_utf8_bytes=4096, max_codepoints=1024, normalization=normalization)
    tracemalloc.start()
    for _ in range(iterations):
        process_password(value, config=config)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


def summarize_timings(timings: list[float]) -> dict[str, float | int]:
    median = statistics.median(timings)
    average = statistics.fmean(timings)
    p95 = sorted(timings)[int(len(timings) * 0.95) - 1]
    throughput = 1.0 / average if average > 0 else 0.0
    return {
        "median_seconds": median,
        "p95_seconds": p95,
        "average_seconds": average,
        "throughput_per_second": throughput,
    }


def run_suite() -> dict[str, dict[str, float | int]]:
    results: dict[str, dict[str, float | int]] = {}
    for label, value in WORKLOADS:
        latency = benchmark_latency(value, normalization="none")
        peak_memory = benchmark_memory(value, normalization="none")
        summary = summarize_timings(latency)
        summary["peak_memory_bytes"] = peak_memory
        results[label] = summary
    return results


def print_summary(results: dict[str, dict[str, float | int]]) -> None:
    print("PassText benchmark summary")
    print("=" * 28)
    for label, metrics in results.items():
        print(
            f"{label:>15}: median={metrics['median_seconds']:.8f}s "
            f"p95={metrics['p95_seconds']:.8f}s avg={metrics['average_seconds']:.8f}s "
            f"throughput={metrics['throughput_per_second']:.2f}/s peak_mem={metrics['peak_memory_bytes']} bytes"
        )


if __name__ == "__main__":
    suite = run_suite()
    print_summary(suite)
    payload = {
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "workloads": suite,
    }
    output_path = Path("benchmarks/output.txt")
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
