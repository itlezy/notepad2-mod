"""Manual, paired Windows benchmark. No telemetry or application instrumentation."""
import argparse
import ctypes
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import statistics
import time

import psutil
from pywinauto.remote_memory_block import RemoteMemoryBlock
from pywinauto.timings import wait_until
import win32con
import win32gui
import win32api

from windows_app import Editor


def repaint(editor):
    win32gui.RedrawWindow(editor.editor.handle, None, None,
                         win32con.RDW_INVALIDATE | win32con.RDW_UPDATENOW)


def sample(executable, document, settings, expected_size):
    start = time.perf_counter()
    editor = Editor(executable, settings, document, "txt")
    try:
        wait_until(60, 0.01, lambda: editor.sci(2006) == expected_size)
        startup_ms = (time.perf_counter() - start) * 1000
        paint = time.perf_counter()
        editor.main.restore()
        editor.main.move_window(50, 50, 1000, 700, repaint=True)
        repaint(editor)
        first_paint_ms = (time.perf_counter() - paint) * 1000

        needle = ctypes.create_string_buffer(b"UNIQUE_SEARCH_TAIL")
        remote = RemoteMemoryBlock(editor.editor, size=len(needle))
        try:
            remote.Write(needle)
            editor.sci(2190, 0)  # Target start/end; literal search, not regex.
            editor.sci(2192, expected_size)
            started = time.perf_counter()
            found = editor.sci(2197, len(needle.value), remote.Address())
            search_ms = (time.perf_counter() - started) * 1000
            assert found == expected_size - len(needle.value)
        finally:
            remote.CleanUp()

        editor.sci(2160, 0, 0)
        char = ctypes.create_string_buffer(b"x")
        remote = RemoteMemoryBlock(editor.editor, size=len(char))
        try:
            remote.Write(char)
            started = time.perf_counter()
            for _ in range(100):
                editor.sci(2001, 1, remote.Address())
                editor.sci(2176)  # Undo: keep workload bytes unchanged.
            edit_ms = (time.perf_counter() - started) * 1000
        finally:
            remote.CleanUp()
        assert editor.sci(2006) == expected_size

        started = time.perf_counter()
        for _ in range(20):
            editor.sci(2168, 20, 20)
            repaint(editor)
            editor.sci(2168, -20, -20)
            repaint(editor)
        scroll_ms = (time.perf_counter() - started) * 1000

        process = psutil.Process(editor.process.pid)
        memory = process.memory_info()
        cpu = process.cpu_times()
        started = time.perf_counter()
        time.sleep(1)
        after_cpu = process.cpu_times()
        return {
            "startup_loaded_ms": startup_ms, "first_paint_ms": first_paint_ms,
            "literal_search_ms": search_ms, "edit_undo_100_pairs_ms": edit_ms,
            "scroll_repaint_40_moves_ms": scroll_ms,
            "private_kib": memory.private / 1024, "working_set_kib": memory.rss / 1024,
            "idle_cpu_ms": ((after_cpu.user + after_cpu.system) - (cpu.user + cpu.system)) * 1000,
            "idle_wall_ms": (time.perf_counter() - started) * 1000,
        }
    finally:
        editor.close()


def summarize(samples):
    result = {}
    for metric in samples[0]:
        values = [row[metric] for row in samples]
        median = statistics.median(values)
        result[metric] = {
            "median": median, "min": min(values), "max": max(values),
            "mad": statistics.median(abs(value - median) for value in values),
        }
    return result


def binary_info(path):
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    version = win32api.GetFileVersionInfo(str(path), "\\")
    ms, ls = version["FileVersionMS"], version["FileVersionLS"]
    return {"path": str(path), "sha256": digest,
            "file_version": f"{ms >> 16}.{ms & 65535}.{ls >> 16}.{ls & 65535}"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--runs", type=int, default=7)
    args = parser.parse_args()
    if args.runs < 3:
        parser.error("Use at least three measured runs per workload/mode.")
    baseline, candidate = args.baseline.resolve(strict=True), args.candidate.resolve(strict=True)
    output = args.output.resolve()
    if output.exists():
        parser.error("Output already exists; use a fresh report directory.")
    output.parent.mkdir(parents=True, exist_ok=True)
    fixtures = output.parent / "fixtures"
    fixtures.mkdir()  # Never overwrite or delete an existing workload directory.
    tail = b"UNIQUE_SEARCH_TAIL"
    line = b"alpha beta gamma delta 1234567890\r\n"
    workloads = {
        "small_128k": (line * (128 * 1024 // len(line))) + tail,
        "large_25m": (line * (25 * 1024 * 1024 // len(line))) + tail,
        "long_line_1m": b"a" * (1024 * 1024) + tail,
    }
    modes = [("baseline_original", baseline, 0), ("candidate_original", candidate, 0), ("candidate_dark", candidate, 1)]
    report = {
        "schema": 1, "utc": datetime.now(timezone.utc).isoformat(),
        "machine": {"platform": platform.platform(), "cpu": platform.processor(),
                    "logical_cpus": psutil.cpu_count(), "python": platform.python_version()},
        "runs": args.runs, "viewport": [1000, 700],
        "method": "Plain-text lexer, warm filesystem cache, one discarded warmup per mode/workload, rotated mode order. Visible target windows and synchronous repaint; timings include automation/Win32 round-trip overhead. No clipboard or real user files/settings. Idle sampled for one second. Not cold-start, syntax-heavy or physical-input latency measurement. Foreground occlusion, antivirus, DPI and machine load affect results; no automatic regression verdict.",
        "executables": {label: binary_info(path)
                        for label, path, _ in modes},
        "workloads": {},
    }
    settings = "[Settings]\nSaveSettings=0\nSaveRecentFiles=0\nFileWatchingMode=0\nMarkOccurrences=0\n[Settings2]\nFileLoadWarningMB=0\n[Styles]\nEditorTheme={theme}\n"
    for name, content in workloads.items():
        document = fixtures / f"{name}.txt"
        document.write_bytes(content)
        rows = {label: [] for label, _, _ in modes}
        for run in range(-1, args.runs):
            offset = max(run, 0) % len(modes)
            for label, executable, theme in modes[offset:] + modes[:offset]:
                ini = fixtures / f"{label}.ini"
                ini.write_text(settings.format(theme=theme), encoding="utf-16")
                measured = sample(executable, document, ini, len(content))
                if run >= 0:
                    rows[label].append(measured)
                    print(f"{name} {label} run {run + 1}/{args.runs}: loaded {measured['startup_loaded_ms']:.1f}ms", flush=True)
        report["workloads"][name] = {
            "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest(),
            "raw": rows, "summary": {label: summarize(values) for label, values in rows.items()},
        }
        output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Report: {output}")


if __name__ == "__main__":
    main()
