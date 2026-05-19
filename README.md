# FC Benchmarking Tool

A Python library for benchmarking applications, particularly focusing on the
implementation of FC.

The report goes into more detail on the purpose and usage of this tool

## Prerequisites

The tool must run on a Linux system, with the following programs installed:

- Git
- Perf
- Python ≥ 3.12
- Cargo (installed via [rustup](https://rust-lang.org/learn/get-started/))

Python must have access to the Matplotlib library.

## Giving perf permissions

Perf requires access to hardware-level counters that are protected by the OS.
Before running the tool, run

```bash
sudo echo 0 > /proc/sys/kernel/perf_event_paranoid
sudo echo 0 > /proc/sys/kernel/kptr_restrict
```

This will _temporarily_ allow the profiler access to the required information.
This change will last until the computer restarts.

## Jupyter Notebook

The Jupyter Notebook `Benchmarking Example.ipynb` is included to show examples
of the benchmarking tool's usage. An exported HTML version is included as
`Benchmarking Example.html`.

## Basic Usage

Benchmark how long it takes for every local branch to enumerate all factors that
occur twice in the word "ananas".

```python
import marker
from marker.cases import fc_test_cases

# Initialise the testing object, using default parameters
test_runner = marker.Benchmarker("...") # Path to FC repository

# Run the benchmark, using the built-in convenience function, which handles the
# parameters for this specific FC implementation 'behind the scenes'
results = test_runner.benchmark_branches(
    fc_test_cases(
        "∃ p ∃ s ($U = p x s ∧ ¬(∃ ph ∃ sh ($U = ph x sh ∧ ¬ph = p)))",
        "ananas" # Any number of words could be given here
    ),
)
```

### Customising Run Command

You can change the command run when each branch is built or run

```python
import marker

test_runner = marker.Benchmarker(
    "...", # Path to repository
    build_command=["cargo", "build", "--release"],
    run_command=[
        "./target/release/fc-implementation", "-c", "generate-factors", "-t", "<WORD>"
    ],
)

results = test_runner.benchmark_branches(
    cases=[
        {"<WORD>": "ananas"},
        {"<WORD>": "bananas"},
        {"<WORD>": "pineapple"},
    ],
    branches=["main", "naive"],
    num_trials=3,
)
```

### Plot results

```python
from marker.perf import plot_results, PerfEvent
# ... create `results`
plot_results(PerfEvent.DURATION_TIME,results)
```
