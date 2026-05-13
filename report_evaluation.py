import marker
import json
import matplotlib.pyplot as plt

from enum import StrEnum
from datetime import datetime
from time import time
from pathlib import Path
from marker.cases import fc_test_cases
from marker.perf import PerfEvent, plot_results


class Branch(StrEnum):
    FT = 'factor-trimming'
    FT_NC = 'factor-trimming-no-collect'
    FT_NUC = 'factor-trimming-no-universe-check'
    FT_NUC_AHASH = 'ft-nuc-ahash'
    FT_NUC_FXHASH = 'ft-nuc-fxhash'
    FT_NUC_NOHASH = 'ft-nuc-nohash'
    FT_NUC_NOHASH_LCP = 'ft-nuc-nohash-lcp'
    FT_NUC_NOHASH_LCP_ENUM = 'ft-nuc-nohash-lcp-enum'
    GROUNDUP = 'groundup'
    GROUNDUP_LCP = 'groundup-lcp'
    GROUNDUP_LCP_JOIN = 'groundup-lcp-join'
    GROUNDUP_LCP_JOIN_TEMP = 'groundup-lcp-join-temp'
    GROUNDUP_LCP_MEMO = 'groundup-lcp-memo'
    GROUNDUP_LCP_MEMO_HEURISTICS = 'groundup-lcp-memo-heuristics'
    GROUNDUP_LCP_NC_HEURISTICS = 'groundup-lcp-nc-heuristics'
    GROUNDUP_LCP_PREGEN = 'groundup-lcp-pregen'
    LCP = 'lcp'
    LCP_FACTORS = 'lcp-factors'
    MAIN = 'main'
    NAIVE = 'naive'
    NAIVE_NC = 'naive-no-collect'
    NAIVE_NUC = 'naive-no-universe-check'
    NC_NUC = 'nc-nuc'
    NC_NUC_NOHASH = 'nc-nuc-nohash'
    PARALLEL = 'parallel'


pretty_branch_names = {
    str(Branch.FT): "Heuristics",
    str(Branch.FT_NC): "",
    str(Branch.FT_NUC): "stdlib Hash",
    str(Branch.FT_NUC_AHASH): "A Hash",
    str(Branch.FT_NUC_FXHASH): "FX Hash",
    str(Branch.FT_NUC_NOHASH): "No Hash",
    str(Branch.FT_NUC_NOHASH_LCP): "",
    str(Branch.FT_NUC_NOHASH_LCP_ENUM): "Best Naive",
    str(Branch.GROUNDUP): "V2",
    str(Branch.GROUNDUP_LCP): "",
    str(Branch.GROUNDUP_LCP_JOIN): "Join Approach",
    str(Branch.GROUNDUP_LCP_JOIN_TEMP): "",
    str(Branch.GROUNDUP_LCP_MEMO): "",
    str(Branch.GROUNDUP_LCP_MEMO_HEURISTICS): "Final A",
    str(Branch.GROUNDUP_LCP_NC_HEURISTICS): "Final B",
    str(Branch.GROUNDUP_LCP_PREGEN): "",
    str(Branch.LCP): "",
    str(Branch.LCP_FACTORS): "",
    str(Branch.MAIN): "Main",
    str(Branch.NAIVE): "Total Brute Force",
    str(Branch.NAIVE_NC): "Brute Force w/ iter",
    str(Branch.NAIVE_NUC): "Brute Force NUC",
    str(Branch.NC_NUC): "",
    str(Branch.NC_NUC_NOHASH): "Brute force no hash",
    str(Branch.PARALLEL): "",

}


def save_results(name, results: dict, metric=PerfEvent.DURATION_TIME):
    timestamp = datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H-%M-%S")
    Path(f"./out/report/{name}/{timestamp}/").mkdir(parents=True, exist_ok=True)
    with open(f"./out/report/{name}/{timestamp}/data.json", "w") as f:
        json.dump(results, f, indent=4)
    dims = (8, 3)
    plot_results(PerfEvent.DURATION_TIME, results, dimensions=dims, x_rotation=0, branch_labels=pretty_branch_names)
    plt.savefig(f"./out/report/{name}/{timestamp}/plot.png")
    plot_results(PerfEvent.DURATION_TIME, results, dimensions=dims,
                 x_rotation=0, log_scale=True, branch_labels=pretty_branch_names)
    plt.savefig(f"./out/report/{name}/{timestamp}/plot_log.png")


def fake_csv():
    test_runner = marker.Benchmarker("/home/ahutton/dev/uni/Part D Project/fc-implementation")

    formula = 'l=";"c";" && c=a "," b && ¬exists p exists s  c = p ";"  s && ¬exists p exists s  a = p "," s'

    words = [';aa,cc;11,22;something here,more content;',
             ';aa,cc;11,22;something here,more content;', ';aasdasda,ccasdasdas;1sdasda1,23asd21as3d2;something here,more content;']
    results = test_runner.benchmark_branches(
        cases=[*fc_test_cases(formula, *words),
               ],
        branches=[Branch.GROUNDUP, Branch.GROUNDUP_LCP_MEMO_HEURISTICS,
                  Branch.GROUNDUP_LCP_NC_HEURISTICS, Branch.FT_NUC_NOHASH_LCP_ENUM],
        num_trials=3,
        timeout=120
    )
    save_results("fake_csv", results)


def rust_functions():
    test_runner = marker.Benchmarker("/home/ahutton/dev/uni/Part D Project/fc-implementation",
                                     run_command=["./target/release/fc-implementation",
                                                  "--pattern", "$FORMULA$", "--file", "$WORD$"]
                                     )

    formula = 'sig = "fn " name "(" ∧ ¬∃ p ∃ s name = p " " s'

    words = [
        '/home/ahutton/dev/uni/Part D Project/tests/rust-tests/src/main.rs',
        '/home/ahutton/dev/uni/Part D Project/tests/rust-tests/src/fake_formula_parser.rs',
        '/home/ahutton/dev/uni/Part D Project/tests/rust-tests/src/formula_parser.rs',
    ]
    results = test_runner.benchmark_branches(
        cases=[*fc_test_cases(formula, *words),
               ],
        branches=[Branch.GROUNDUP, Branch.GROUNDUP_LCP_MEMO_HEURISTICS,
                  Branch.GROUNDUP_LCP_NC_HEURISTICS, Branch.FT_NUC_NOHASH_LCP_ENUM],
        num_trials=3,
        timeout=120
    )
    save_results("rust_functions", results)


fake_csv()
rust_functions()
