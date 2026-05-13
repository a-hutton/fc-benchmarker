from .cases import TestCase
from .perf import PerfEvent, perf_stat, check_kernel_params
from . import git
import subprocess
import csv

from pathlib import Path


PERF_EVENTS = [
    PerfEvent.DURATION_TIME, PerfEvent.CYCLES, PerfEvent.BRANCHES, PerfEvent.CONTEXT_SWITCHES, PerfEvent.CPU_MIGRATIONS, PerfEvent.CACHE_REFERENCES, PerfEvent.CACHE_MISSES, PerfEvent.TASK_CLOCK
]


def format_command(command: list[str], replacements: dict[str, str]) -> list[str]:
    """
    Replaces arguments in command using a dictionary of replacement values
    """
    copied = command.copy()
    for key, val in replacements.items():
        if key in copied:
            key_idx = copied.index(key)
            copied[key_idx] = val
        else:
            print(f"Placeholder {key} not found in in command")

    return copied


DEFAULT_RUN_COMMAND = ["./target/release/fc-implementation", "--quiet", "--pattern", "$FORMULA$", "--text", "$WORD$"]
OLD_COMMAND = ["./target/release/fc-implementation", "--quiet", "$FORMULA$", "$WORD$"]
DEFAULT_BUILD_COMMAND = ["cargo", "build", "--release"]


class BuildError(Exception):
    """An Eror occured while building"""

    def __init__(self, inner: subprocess.CalledProcessError, branch: str | None = None) -> None:
        self.inner = inner
        self.branch = branch

    def __str__(self) -> str:
        return f"Run Error - issue when running benchmark\nbranch:{self.branch}\n{self.inner.output}"


class RunError(Exception):
    """An Error occured while running"""

    def __init__(self, inner: subprocess.CalledProcessError, branch: str | None = None, command=None) -> None:
        self.inner = inner
        self.branch = branch
        self.command = command

    def __str__(self) -> str:
        return f"Run Error - issue when running benchmark\nbranch:{self.branch}\ncommand:{self.command}\n{self.inner.output}"


class Benchmarker():
    """
    The core of the tool - create an instance of this with the given source code
    """

    def __init__(self, working_dir: str, build_command: list[str] = DEFAULT_BUILD_COMMAND, run_command: list[str] = DEFAULT_RUN_COMMAND) -> None:
        self.repo = git.Repo(working_dir)
        self.build_command = build_command
        self.run_command = run_command

    def benchmark_branches(self, cases: list[TestCase], num_trials=1, branches=None, print_output=False, timeout: int | None = None) -> dict[str, list]:
        check_kernel_params()
        if branches is None:
            branches = self.repo.list_branches()
        else:
            possible_branches = self.repo.list_branches()
            for branch in branches:
                if branch not in possible_branches:
                    raise IOError(f"Branch {branch} not found in repository")
        results: dict[str, list[dict]] = {}
        for branch in branches:
            print(
                f"*********************** Branch {branch} ***********************")
            self.repo.checkout(branch)
            results[branch] = self.run_benchmark(cases, num_trials, print_output=print_output, timeout=timeout)
        return results

    def run_benchmark(self, cases: list[TestCase], num_trials: int = 1,  print_output=False, timeout: int | None = None) -> list[dict]:
        try:
            res = subprocess.run(self.build_command, cwd=self.repo.dir, check=True)
            res.check_returncode()
        except subprocess.CalledProcessError as e:
            print(f"Build command failed ({self.build_command})\nError:\n{e}")
            raise BuildError(e, self.repo.dir) from None
        # make a folder in the tmp directory for our output files
        Path("/tmp/parkbench").mkdir(parents=True, exist_ok=True)

        file_idx = 0
        output_files = []
        for case in cases:
            out_file = f"/tmp/parkbench/run_{file_idx}.csv"
            output_files.append(out_file)
            file_idx += 1
            formatted_command = format_command(self.run_command, case)
            print(f"Now Running {formatted_command}")
            try:
                res = perf_stat(
                    command=formatted_command,
                    cwd=self.repo.dir,
                    repeats=num_trials,
                    out_file=out_file,
                    events=PERF_EVENTS,
                    stdout=print_output,
                    timeout=timeout
                )
                res.check_returncode()
            except subprocess.CalledProcessError as e:
                print(f"!!! ERROR running benchmark (possible timeout)\n{self.repo.dir}\n{format_command}\n{e.output}")
                # raise RunError(e, self.repo.dir, formatted_command) from None

        print(output_files)
        if len(output_files) != len(cases):
            print(
                f"!!!!! SOMETHING HAS GONE VERY WRONG !!!!!\n output files: len: {len(output_files)}\ntest cases: len: {len(cases)}")
            print("Don't trust the output JSON - data *will* be misaligned and attributed to wrong case")
        bench_data = []
        for i in range(len(cases)):
            case = cases[i]
            filename = output_files[i]
            # read data for this run
            with open(filename, "r") as f:
                reader = csv.reader(f)
                run_data: dict[str, dict] = {}
                for line in reader:
                    if len(line) <= 1:
                        continue

                    value = line[0]
                    unit = line[1]
                    variance = "single_trial"
                    value_dt = line[5]
                    unit_dt = line[6]
                    if num_trials > 1:  # or if "%" in line[3]:
                        variance = line[3]
                        value_dt = line[6]
                        unit_dt = line[7]

                    metric_data = {
                        "value": value,
                        "unit": unit,
                        "variance": variance,
                        "value_dt": value_dt,
                        "unit_dt": unit_dt
                    }

                    metric_name = line[2]
                    run_data[metric_name] = metric_data
                case_data = {
                    "parameters": case,
                    "data": run_data
                }
                bench_data.append(case_data)

        return bench_data


if __name__ == "__main__":
    cmd = ["./test", "$FORMULA$", "-t", "$WORD$"]

    print(cmd)
    print(format_command(cmd, {
        "$FORMULA$": "x = aby",
    }))
    print(cmd)
