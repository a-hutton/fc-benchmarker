from cases import TestCase, load_csv

import git
import subprocess
import csv

from time import time
from itertools import islice

type BenchmarkResults = dict[str, dict[str, list[float]]]


class Tester():
    def __init__(self, working_dir: str) -> None:
        self.repo = git.Repo(working_dir)

    def benchmark_branches(self, cases_filename: str,  num_trials=3, branches=None) -> dict[str, BenchmarkResults]:
        if branches == None:
            branches = self.repo.list_branches()
        results: dict[str, BenchmarkResults] = {}
        for branch in branches:
            print(
                f"*********************** Branch {branch} ***********************")
            self.repo.checkout(branch)
            results[branch] = self.run_benchmark(
                load_csv(cases_filename), num_trials)
        return results

    def run_benchmark(self, cases: list[TestCase], num_trials=3) -> BenchmarkResults:
        build_command = ["cargo", "build", "--release"]
        subprocess.run(build_command, cwd=self.repo.dir)

        command_template = ["./target/release/fc-implementation", "--quiet"]

        results: BenchmarkResults = {}

        for case in cases:
            formula_times: dict[str, list[float]] = {}
            for word in case.words:
                word_times: list[float] = []
                for i in range(num_trials):
                    command = command_template + [case.formula, word]
                    runtime = self.time_command(command)
                    word_times.append(runtime)
                formula_times[word] = word_times
            results[case.formula] = formula_times

        return results

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
    tester.benchmark_branches("./cases.csv", branches=["main"])
