import subprocess
from enum import StrEnum

import matplotlib.pyplot as plt
import numpy as np


def check_kernel_params():
    perf_event_paranoid = int(open("/proc/sys/kernel/perf_event_paranoid", "r").read())
    print(perf_event_paranoid)
    if perf_event_paranoid > 2:
        raise SystemError(
            f"/proc/sys/kernel/perf_event_paranoid needs to be set to 2 or below for profiling, read {perf_event_paranoid}")


class PerfEvent(StrEnum):
    DURATION_TIME = "duration_time"
    USER_TIME = "user_time"
    SYSTEM_TIME = "system_time"
    BRANCH_INSTRUCTIONS = "branch-instructions"
    BRANCH_MISSES = "branch-misses"
    CACHE_MISSES = "cache-misses"
    CACHE_REFERENCES = "cache-references"
    CYCLES = "cycles"
    INSTRUCTIONS = "instructions"
    STALLED_CYCLES_FRONTEND = "stalled-cycles-frontend"
    CPU_CLOCK = "cpu-clock"
    CPU_MIGRATIONS = "cpu-migrations"
    PAGE_FAULTS = "page-faults"
    BRANCHES = "branches"
    BRANCH_MISPREDICTION_RATIO = "branch_misprediction_ratio"
    CONTEXT_SWITCHES = "context-switches"
    TASK_CLOCK = "task-clock"


def create_event_param(events: list[PerfEvent]) -> str:
    return ",".join(str(e) for e in events)


def perf_stat(command: list[str], cwd: str | None = None, repeats=1, out_file: str | None = None, events: list[PerfEvent] | None = None, csv=True, stdout=False) -> subprocess.CompletedProcess[bytes]:
    # , "--event", "duration_time,cycles,branches,context-switches,migrations,cache-references,cache-misses,task-clock", "-x,", "--repeat", str(repeats), "-o", out_file] + command
    perf_command = ["perf", "stat", "--repeat", str(repeats)]
    if out_file is not None:
        perf_command += ["-o", out_file]
    if csv:
        perf_command += ["-x,"]
    if events is not None:
        perf_command += ["--event", create_event_param(events)]

    try:
        process = subprocess.run(
            perf_command + command,
            cwd=cwd,
            capture_output=not stdout,
            check=True)
        return process
    except subprocess.CalledProcessError as e:
        print(f"Unexpected error calling perf with command {command}\nError:\n{e}")
        raise e


def to_float(num: str):
    if num is None:
        print(f"{num} is None")
        return 0
    try:
        return float(num)
    except ValueError:
        print(f"{num} is not a float")
        return 0


def plot_formula_comparison(metric: PerfEvent, results, perc=False, branch_labels: dict[str, str] | None = None, dimensions: tuple[int, int] = (6, 4), x_rotation=90, short_labels=True, log_scale=False, case_labels: list | None = None):
    branch_counter = 0
    num_branches = len(results)
    width = 1/(num_branches+1)
    json_value_key = "value_dt" if perc else "value"
    json_unit_key = "unit_dt" if perc else "unit"
    plt.figure(figsize=dimensions)
    for (branch, branch_res) in results.items():
        branch_label = branch
        if branch_labels is not None:
            branch_label = branch_labels[branch]
        branch_res = results[branch]
        heights = []
        errors = []
        display_errors = False
        x_labels = []
        x_size = 0
        axis_label = ""
        case_counter = 0
        for (i, case) in enumerate(branch_res):
            case_params: dict[str, str] = case["parameters"]
            case_full_data = case["data"]
            case_metric_data = case_full_data[metric]

            unit = case_metric_data[json_unit_key]
            if case_labels is not None:
                x_labels.append(case_labels[i])
            elif short_labels:
                x_labels.append(f"Case {case_counter}")
            else:
                case_label = ", ".join((val.replace("$", "\\$") for val in case_params.values()))
                x_labels.append(f"Case {case_counter}: {case_label}")

            x_size += 1
            case_counter += 1
            value = to_float(case_metric_data[json_value_key])

            # seconds are much more understandable
            if unit == "ns":
                unit = "s"
                value /= 1e9
            if unit == "":
                unit = "count"
            heights.append(value)

            # label y axis showing unit
            if axis_label == "":
                axis_label = f"{metric} ({unit})"
                display_errors = case_metric_data["variance"] != "single_trial"
                percentage_error = to_float(case_metric_data["variance"].replace("%", ""))
                value_error = percentage_error/100 * value
                errors.append(value_error)

        offset = width * branch_counter + width/2 - width*num_branches/2
        if display_errors:
            plt.bar(np.arange(x_size) + offset, heights, width=width, label=branch_label, yerr=errors)
        else:
            plt.bar(np.arange(x_size) + offset, heights, width=width, label=branch_label)
        branch_counter += 1
        plt.ylabel(axis_label)
        plt.xticks(ticks=np.arange(x_size), labels=x_labels, rotation=x_rotation)
    plt.legend()
    if log_scale:
        plt.yscale("log")
    plt.title(f"Comparison of '{metric}' across {num_branches} branches")


if __name__ == "__main__":
    check_kernel_params()
    print(create_event_param([PerfEvent.DURATION_TIME, PerfEvent.CACHE_REFERENCES]))
    perf_stat(["sleep", "1"], csv=False)
