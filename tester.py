from cases import TestCase,  generate_random_cases
from perf import PerfEvent, perf_stat
import git
import subprocess
import csv
import json

from pathlib import Path
from time import time

# formula -> word -> perf_metric -> values
type BenchmarkResults = dict[str, dict[str, dict[str, dict[str, str]]]]

# branch name -> BenchmarkResults
type BranchesBenchmarkResults = dict[str, BenchmarkResults]

PERF_EVENTS = [
    PerfEvent.DURATION_TIME, PerfEvent.CYCLES, PerfEvent.BRANCHES, PerfEvent.CONTEXT_SWITCHES, PerfEvent.CPU_MIGRATIONS, PerfEvent.CACHE_REFERENCES, PerfEvent.CACHE_MISSES, PerfEvent.TASK_CLOCK
]


class Tester():
    def __init__(self, working_dir: str) -> None:
        self.repo = git.Repo(working_dir)

    def benchmark_branches(self, cases: list[TestCase], num_trials=1, branches=None) -> dict[str, BenchmarkResults]:
        if branches is None:
            branches = self.repo.list_branches()
        else:
            possible_branches = self.repo.list_branches()
            for branch in branches:
                if branch not in possible_branches:
                    raise IOError(f"Branch {branch} not found in repository")
        results: dict[str, BenchmarkResults] = {}
        for branch in branches:
            print(
                f"*********************** Branch {branch} ***********************")
            self.repo.checkout(branch)
            results[branch] = self.run_benchmark(cases, num_trials)
        return results

    def run_benchmark(self, cases: list[TestCase], num_trials: int) -> BenchmarkResults:
        build_command = ["cargo", "build", "--release"]
        res = subprocess.run(build_command, cwd=self.repo.dir)
        res.check_returncode()

        # make a folder in the tmp directory for our output files
        Path("/tmp/parkbench").mkdir(parents=True, exist_ok=True)

        file_idx = 0
        output_files: dict[tuple[str, str], str] = {}
        for case in cases:
            for word in case.words:
                out_file = f"/tmp/parkbench/run_{file_idx}.csv"
                output_files[(case.formula, word)] = out_file
                file_idx += 1
                res = perf_stat(
                    command=["./target/release/fc-implementation", "--quiet", case.formula, word],
                    cwd=self.repo.dir,
                    repeats=num_trials,
                    out_file=out_file,
                    events=PERF_EVENTS,
                )

        print(output_files)
        bench_data: BenchmarkResults = {}
        for (formula, word), filename in output_files.items():
            with open(filename, "r") as f:
                reader = csv.reader(f)
                for line in reader:
                    if len(line) <= 1:
                        continue
                    if formula not in bench_data:
                        bench_data[formula] = {}
                    if word not in bench_data[formula]:
                        bench_data[formula][word] = {}

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
                    bench_data[formula][word][metric_name] = metric_data

        return bench_data

    def time_command(self, command: list[str], id=None) -> float:
        if id is not None:
            print(f"Running benchmark {id}")
        start = time()
        res = subprocess.run(
            command,
            cwd=self.repo.dir)

        end = time()
        id_str = "" if id is None else f"({id})"
        if res.returncode != 0:
            print(f"Benchmark {id_str} - code: {res.returncode}")
            return -1
        else:
            runtime = end-start
            print(f"Benchmark {id_str} finished in {runtime:.2f}s")
            return runtime


if __name__ == "__main__":
    tester = Tester("/home/ahutton/dev/uni/Part D Project/fc-implementation")
    # cases = load_csv("./test cases/cases.csv")
    cases = generate_random_cases(3, connectives_range=[0], word_len=5)
    data = tester.benchmark_branches(cases, branches=["factor-trimming"], num_trials=3)
    with open("./out/data.json", "w") as f:
        json.dump(data, f, indent=4)
