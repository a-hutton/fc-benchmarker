from cases import TestCase, load_csv, generate_random_cases

import git
import subprocess
import csv
import json
from pathlib import Path

from time import time
from itertools import islice

type BenchmarkResults = dict[str, dict[str, list[float]]]


class Tester():
    def __init__(self, working_dir: str) -> None:
        self.repo = git.Repo(working_dir)

    def benchmark_branches(self, cases: list[TestCase],  num_trials=3, branches=None) -> dict[str, BenchmarkResults]:
        if branches == None:
            branches = self.repo.list_branches()
        results: dict[str, BenchmarkResults] = {}
        for branch in branches:
            print(
                f"*********************** Branch {branch} ***********************")
            self.repo.checkout(branch)
            results[branch] = self.run_benchmark(cases, num_trials)
        return results

    def run_benchmark(self, cases: list[TestCase], num_trials=3) -> BenchmarkResults:
        build_command = ["cargo", "build", "--release"]
        subprocess.run(build_command, cwd=self.repo.dir)

        Path("/tmp/parkbench").mkdir(parents=True, exist_ok=True)

        perf_template = ["perf", "stat", "-x,", "-o"]
        command_template = ["./target/release/fc-implementation", "--quiet"]

        results: BenchmarkResults = {}

        file_idx = 0
        output_files: dict[tuple[str, str], str] = {}
        for case in cases:
            for word in case.words:
                for i in range(num_trials):
                    out_file = f"/tmp/parkbench/run_{file_idx}.csv"
                    output_files[(case.formula, word)] = out_file
                    file_idx += 1
                    command = perf_template + \
                        [out_file] + command_template + [case.formula, word]
                    res = subprocess.run(
                        command,
                        cwd=self.repo.dir)

        print(output_files)
        bench_data = {}
        for (formula, word), filename in output_files.items():
            with open(filename, "r") as f:
                reader = csv.reader(f)
                for line in reader:
                    if len(line) <= 1:
                        continue
                    [val, _, metric, _, _, val_dt, unit] = line
                    if formula not in bench_data:
                        bench_data[formula] = {}
                    bench_data[formula][word] = {
                        "Value": val,
                        "Measurement": metric,
                        "Value2": val_dt,
                        "Measurement2": unit
                    }
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
    data = tester.benchmark_branches(cases, branches=["main"])
    with open("./out/data.json", "w") as f:
        json.dump(data, f, indent=4)
