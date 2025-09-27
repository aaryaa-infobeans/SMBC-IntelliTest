import argparse
import os
import re
import shutil
import subprocess
from collections import defaultdict

import json
import glob
from pathlib import Path

import logging
import yaml

logger = logging.getLogger(__name__)


def get_bash_executable():
    """Get the appropriate bash executable for the current system"""
    # Common bash locations on Windows
    bash_locations = [
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
        r"C:\msys64\usr\bin\bash.exe",
        r"C:\cygwin64\bin\bash.exe",
        r"C:\Windows\System32\bash.exe",  # WSL bash
        "bash",  # If bash is in PATH
    ]

    for bash_path in bash_locations:
        if shutil.which(bash_path) or os.path.exists(bash_path):
            return bash_path

    # Fallback - try to find bash in PATH
    bash_in_path = shutil.which("bash")
    if bash_in_path:
        return bash_in_path

    raise FileNotFoundError("Bash executable not found. Please install Git Bash, WSL, or another bash implementation.")


def load_config(path):
    with open(path, "r") as f:
        cfg = yaml.safe_load(f) or {}
    return (
        cfg.get("default_workers", 4),
        cfg.get("default_dist_scope", "loadscope"),
        cfg.get("folders", {}),
        cfg.get("report", {}).get("unified_report_path", "report.html"),
        cfg.get("report", {}).get("batch_report_folder", "batch_reports"),
    )


def build_pytest_cmd(files_to_run, workers, dist_scope, env, load_type, batch_report, json_report):

    cmd = [
        get_bash_executable(),
        "./pyRunner.sh",
        "-m",
        "pytest",
        "-v",
        "--reruns",
        "3",
        "--reruns-delay",
        "7",
        "-n",
        str(workers),
        f"--dist={dist_scope}",
        f"--env={env}",
        f"--load_type={load_type}",
        f"--html={batch_report}",
        f"--self-contained-html",
        "--json-report",
        f"--json-report-file={json_report}",
        *files_to_run,
    ]
    return cmd


def merge_html_reports(unified_report, batch_report_location):
    cmd = [
        get_bash_executable(),
        "./pyRunner.sh",
        "-m",
        "pytest_html_merger",
        "-i",
        batch_report_location,
        "-o",
        unified_report,
    ]

    try:
        subprocess.run(cmd)
    except OSError as e:
        logger.error(f"Error: {e}")
        logger.error("Ensure the shell interpreter (bash/sh) is installed and the script is valid.")
        raise
    logger.info(f"Report generated: {unified_report}")


def merge_json_reports(batch_report_folder, output_file="test-results.json"):
    folder = Path(batch_report_folder)
    merged = {
        "tests": [],
        "summary": {"passed": 0, "failed": 0, "skipped": 0, "total": 0},
        "exitcode": 0,
        "duration": 0.0,
    }

    json_files = glob.glob(str(folder / "*.json"))
    if not json_files:
        logger.warning(f"No JSON files found in {batch_report_folder}")
        return

    for file_path in json_files:
        with open(file_path, "r") as f:
            report = json.load(f)

        # Merge test cases
        merged["tests"].extend(report.get("tests", []))

        # Update summary counts
        summary = report.get("summary", {})
        for key in ["passed", "failed", "skipped"]:
            merged["summary"][key] += summary.get(key, 0)

        # Exitcode: set to 1 if any report has failure
        if report.get("summary", {}).get("failed", 0) > 0:
            merged["exitcode"] = 1

        # Add durations
        merged["duration"] += report.get("duration", 0.0)

    # Compute total
    merged["summary"]["total"] = (
        merged["summary"]["passed"] + merged["summary"]["failed"] + merged["summary"]["skipped"]
    )

    # Save merged file at repo root
    out_path = Path(output_file)
    out_path.write_text(json.dumps(merged, indent=2))
    logger.info(f"✅ Merged {len(json_files)} files into {out_path.resolve()}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--env", default="PROD")
    ap.add_argument("--load_type", default="load")
    ap.add_argument("--base-dir", default=".\\SRC\\tests\\reports\\")
    ap.add_argument("--active_batch_list", type=lambda s: s.split(","), default=[], help="Comma-separated list")
    args = ap.parse_args()

    default_workers, default_dist_scope, folder_cfg, unified_report_path, batch_report_folder = load_config(args.config)

    eligible = [f for f in folder_cfg]

    if not eligible:
        logger.warning(f"No folders eligible for run in env: '{args.env}'  for load type: '{args.load_type}'. Exiting.")
        return

    os.makedirs(os.path.dirname(unified_report_path), exist_ok=True)
    os.makedirs(os.path.dirname(batch_report_folder), exist_ok=True)
    # Ensure the batch report directory itself exists (pytest-html won't create nested dirs)
    os.makedirs(batch_report_folder, exist_ok=True)

    for folder in folder_cfg:
        workers = folder_cfg.get(folder, {}).get("workers", default_workers)
        dist_scope = folder_cfg.get(folder, {}).get("dist_scope", default_dist_scope)
        # files_to_run = " ".join(folder_cfg.get(folder, {}).get("testfiles", []))
        files_to_run = folder_cfg.get(folder, {}).get("testfiles", [])

        batch_report = f"{batch_report_folder}//report_{os.path.basename(folder)}.html"
        json_report = f"{batch_report_folder}//report_{os.path.basename(folder)}.json"

        if args.active_batch_list and folder not in args.active_batch_list:
            logger.warning(f"Skipping batch {folder} as it's not in active_batch_list")
            logger.warning(f"Regression would only run for {args.active_batch_list}")
            continue

        logger.info(f"\nRunning batch {folder} with {workers} workers " f"(env={args.env}, load_type={args.load_type})")

        cmd = build_pytest_cmd(files_to_run, workers, dist_scope, args.env, args.load_type, batch_report, json_report)

        logger.info(f"CMD: {' '.join(cmd)}")
        logger.info(cmd)

        try:
            subprocess.run(cmd, shell=False, check=True)
        except Exception as e:
            logger.error(f"Error: {e}")
            logger.error("Ensure the shell interpreter (bash/sh) is installed and the script is valid.")
        logger.info(f"Report generated: {batch_report}")

    merge_html_reports(unified_report_path, batch_report_folder)
    merge_json_reports(batch_report_folder, "test-results.json")

    logger.info(f"Unified report generated: {unified_report_path}")


if __name__ == "__main__":
    main()
