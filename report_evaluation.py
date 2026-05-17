import marker
import json
import matplotlib.pyplot as plt

from enum import StrEnum
from datetime import datetime
from time import time
from pathlib import Path
from marker.cases import fc_test_cases
from marker.perf import PerfEvent, plot_results
from marker.cases.generation import random_word
from string import ascii_letters
from random import randint


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
    GROUNDUP_LCP_JOIN_HEURISTICS = 'groundup-lcp-join-heuristics'
    GROUNDUP_LCP_JOIN_NC_HEURISTICS = 'groundup-lcp-join-nc-heuristics'
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
    str(Branch.FT_NUC_NOHASH_LCP): "ft-nuc-nohash-lcp",
    str(Branch.FT_NUC_NOHASH_LCP_ENUM): "Best Naive",
    str(Branch.GROUNDUP): "V2",
    str(Branch.GROUNDUP_LCP): "",
    str(Branch.GROUNDUP_LCP_JOIN): "Join Approach (old)",
    str(Branch.GROUNDUP_LCP_JOIN_TEMP): "",
    str(Branch.GROUNDUP_LCP_JOIN_HEURISTICS): "Join Approach (old)",
    str(Branch.GROUNDUP_LCP_JOIN_NC_HEURISTICS): "Join Approach",
    str(Branch.GROUNDUP_LCP_MEMO): "",
    str(Branch.GROUNDUP_LCP_MEMO_HEURISTICS): "Elimination Approach (memo)",
    str(Branch.GROUNDUP_LCP_NC_HEURISTICS): "Elimination Approach",
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

BRANCHES = [
    # Branch.GROUNDUP_LCP_JOIN_HEURISTICS,
    Branch.GROUNDUP_LCP_JOIN_NC_HEURISTICS,
    Branch.GROUNDUP_LCP_NC_HEURISTICS,
    # Branch.GROUNDUP_LCP_MEMO_HEURISTICS,
    # Branch.GROUNDUP,
]


def save_results(name, results: dict, metric=PerfEvent.DURATION_TIME, case_labels=None):
    timestamp = datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H-%M-%S")
    Path(f"./out/report/{name}/{timestamp}/").mkdir(parents=True, exist_ok=True)
    with open(f"./out/report/{name}/{timestamp}/data.json", "w") as f:
        json.dump(results, f, indent=4)
    dims = (8, 3)
    plot_results(PerfEvent.DURATION_TIME, results, dimensions=dims, x_rotation=90,
                 branch_labels=pretty_branch_names, case_labels=case_labels)
    plt.title("Linear Scale")
    plt.savefig(f"./out/report/{name}/{timestamp}/plot.png", bbox_inches="tight", dpi=300)
    plot_results(PerfEvent.DURATION_TIME, results, dimensions=dims, x_rotation=90,
                 log_scale=True, branch_labels=pretty_branch_names, case_labels=case_labels)
    plt.title("Logarithmic Scale")
    plt.savefig(f"./out/report/{name}/{timestamp}/plot_log.png", bbox_inches="tight", dpi=300)


def fake_csv():
    test_runner = marker.Benchmarker("/home/ahutton/dev/uni/Part D Project/fc-implementation")

    formula = 'l=";"c";" && c=a "," b && ¬exists p exists s  c = p ";"  s && ¬exists p exists s  a = p "," s'

    words = [';aa,cc;11,22;something here,more content;',
             ';aa,cc;11,22;something here,more content;', ';aasdasda,ccasdasdas;1sdasda1,23asd21as3d2;something here,more content;']
    results = test_runner.benchmark_branches(
        cases=[*fc_test_cases(formula, *words),
               ],
        branches=BRANCHES,
        num_trials=3,
        timeout=120
    )
    save_results("fake_csv", results)


def fake_csv_ordering():
    test_runner = marker.Benchmarker("/home/ahutton/dev/uni/Part D Project/fc-implementation")
    formula = 'l=";"c";" && c=a "," b && ¬(exists p exists s  c = p ";"  s) && ¬(exists p exists s  a = p "," s)'

    formula2 = 'c=a "," b && l=";"c";" && ¬(exists p exists s  c = p ";"  s) && ¬(exists p exists s  a = p "," s)'

    n_rows = 7
    words = [f";{random_word(ascii_letters, randint(1, 10))},{random_word(ascii_letters, randint(1, 10))};"]
    for i in range(1, n_rows):
        last_word = words[i-1]
        new_word = last_word + \
            f"{random_word(ascii_letters, randint(1, 10))},{random_word(ascii_letters, randint(1, 10))};"
        words.append(new_word)

    cases = [{"$FORMULA$": f, "$WORD$": w} for w in words for f in [formula, formula2]]
    # print(str(cases))
    results = test_runner.benchmark_branches(
        cases=cases,
        branches=BRANCHES,
        num_trials=3,
        timeout=120,
        skip_branch_on_fail=False,
        print_output=True
    )
    case_labels = [f"{order} | {n+1} rows" for n in range(n_rows) for order in ['A', 'B']]

    save_results("fake_csv_ordering", results, case_labels=case_labels)


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
    labels = []
    for i in range(len(words)):
        filename = words[i]
        with open(filename) as f:
            n_chars = len(f.read())
            labels.append(f"{i}: (len={n_chars})")

    results = test_runner.benchmark_branches(
        cases=[*fc_test_cases(formula, *words),
               ],
        branches=BRANCHES,
        num_trials=3,
        timeout=120
    )
    save_results("rust_functions", results, case_labels=labels)


def p_tag():
    test_runner = marker.Benchmarker("/home/ahutton/dev/uni/Part D Project/fc-implementation",
                                     run_command=["./target/release/fc-implementation",
                                                  "--pattern", "$FORMULA$", "--file", "$WORD$", "--quiet"]
                                     )

    formula = '∃T (T = "<p>"c"</p>" ∧ ¬∃p ∃s c = p "<p>" s)'

    words = [
        # '/home/ahutton/dev/uni/Part D Project/fc-tester/test cases/html/acc1.html',
        # '/home/ahutton/dev/uni/Part D Project/fc-tester/test cases/html/acc2.html',
        # '/home/ahutton/dev/uni/Part D Project/fc-tester/test cases/html/acc3.html',
        '/home/ahutton/dev/uni/Part D Project/fc-tester/test cases/html/intro.html',
        '/home/ahutton/dev/uni/Part D Project/fc-tester/test cases/html/unit-testing.html',
        '/home/ahutton/dev/uni/Part D Project/fc-tester/test cases/html/brute-force-optimisations.html',
        '/home/ahutton/dev/uni/Part D Project/fc-tester/test cases/html/benchmark-implementation.html',
        # '/home/ahutton/dev/uni/Part D Project/fc-tester/test cases/html/tool-usage.html',
        '/home/ahutton/dev/uni/Part D Project/fc-tester/test cases/html/background-chapter.html',
    ]
    labels = []
    for i in range(len(words)):
        filename = words[i]
        with open(filename) as f:
            n_chars = len(f.read())
            labels.append(f"{i}: (len={n_chars})")

    results = test_runner.benchmark_branches(
        cases=[*fc_test_cases(formula, *words),
               ],
        branches=BRANCHES,
        num_trials=3,
        timeout=120,
        print_output=True
    )
    save_results("p_tag", results, case_labels=labels)


def naive_p_tag():
    test_runner = marker.Benchmarker("/home/ahutton/dev/uni/Part D Project/fc-implementation")

    formula = '∃T (T = "<p>"c"</p>" ∧ ¬∃p ∃s c = p "<p>" s)'

    max_n_ps = 4
    words = [f"<p>{random_word(ascii_letters, 13)}</p>"]
    for i in range(1, max_n_ps):
        last_word = words[i-1]
        words.append(last_word + f"<p>{random_word(ascii_letters, 13)}</p>")

    labels = [f"|w|={len(w)}" for w in words]

    results = test_runner.benchmark_branches(
        cases=[*fc_test_cases(formula, *words),],
        branches=[Branch.FT_NUC_NOHASH_LCP_ENUM],
        num_trials=3,
        timeout=120,
        print_output=True
    )
    save_results("naive_p_tag", results, case_labels=labels)


def multiple_occurrences():
    test_runner = marker.Benchmarker("/home/ahutton/dev/uni/Part D Project/fc-implementation",
                                     run_command=["./target/release/fc-implementation",
                                                  "--pattern", "$FORMULA$", "--file", "$WORD$", "--quiet"]
                                     )

    formula = 'exists p1(exists p2(exists s1(exists s2((($U=p1 x s1 && $U=p2 x s2)&&¬p1=p2)))))'

    words = [
        '/home/ahutton/dev/uni/Part D Project/fc-tester/test cases/html/acc3.html',
        '/home/ahutton/dev/uni/Part D Project/fc-tester/test cases/html/benchmark-implementation.html',
        '/home/ahutton/dev/uni/Part D Project/tests/rust-tests/src/fake_formula_parser.rs',
    ]
    labels = [
        "3 paragraphs",
        "Background",
        "Rust file #2",
    ]
    for i in range(len(words)):
        filename = words[i]
        with open(filename) as f:
            n_chars = len(f.read())
            labels[i] += (f" (len={n_chars})")

    results = test_runner.benchmark_branches(
        cases=[*fc_test_cases(formula, *words),
               ],
        branches=BRANCHES,
        num_trials=3,
        timeout=120,
        print_output=True
    )
    save_results("multiple_occurrences", results, case_labels=labels)


def random_conjugates():
    """
    Conjugate, as defined in Lothaire:
    Two words x and y are said to be conjugate if there exist words u,v in A* such thhat
        x = uv
        y = vu
    """
    num_cases = 15
    step = 5
    word = ""
    cases = []
    labels = []
    conjugate_formula = 'exists u exists v(x=u v && y = v u)'
    for i in range(num_cases):
        word += random_word(ascii_letters, step)
        cases.append(
            {"$FORMULA$": conjugate_formula, "$WORD$": word}
        )
        labels.append(f"|w|={(i+1)*step}")

    test_runner = marker.Benchmarker("/home/ahutton/dev/uni/Part D Project/fc-implementation",
                                     )
    results = test_runner.benchmark_branches(
        cases=cases,
        branches=[Branch.FT_NUC_NOHASH_LCP_ENUM, Branch.GROUNDUP_LCP_NC_HEURISTICS,
                  Branch.GROUNDUP_LCP_JOIN_NC_HEURISTICS],
        num_trials=3,
        timeout=120,
        print_output=True,
        skip_branch_on_fail=True

    )
    save_results("conjugates", results, case_labels=labels)


def growing_equations():
    num_words = 10
    word_growth_step = 5
    max_n_vars = 5

    equations = ["a = v0 "]
    for n_vars in range(1, max_n_vars):
        last_eq = equations[n_vars-1]
        new_eq = last_eq + f" v{n_vars}"
        equations.append(new_eq)

    words = [random_word(ascii_letters, word_growth_step)]
    for i in range(1, num_words):
        last_word = words[i-1]
        new_word = last_word + random_word(ascii_letters, word_growth_step)
        words.append(new_word)

    cases = []
    labels = []
    for (i, eq) in enumerate(equations):
        for word in words:
            labels.append(f"{i+1} vars |w|={len(word)}")
            cases.append({"$FORMULA$": eq, "$WORD$": word})

    test_runner = marker.Benchmarker("/home/ahutton/dev/uni/Part D Project/fc-implementation",
                                     )
    results = test_runner.benchmark_branches(
        cases=cases,
        branches=[Branch.GROUNDUP_LCP_JOIN_NC_HEURISTICS],
        num_trials=3,
        timeout=120,
        print_output=True,
        skip_branch_on_fail=True

    )
    save_results("growing_equations", results, case_labels=labels)


def growing_disjunctions():
    n_fragments = 4
    num_words = 5
    word_growth_step = 5

    equations = ['a = v0']
    for i in range(1, n_fragments):
        last_eq = equations[i-1]
        new_eq = last_eq + f" || v{i}=v{i-1}"
        equations.append(new_eq)

    words = [random_word(ascii_letters, word_growth_step)]
    for i in range(1, num_words):
        last_word = words[i-1]
        new_word = last_word + random_word(ascii_letters, word_growth_step)
        words.append(new_word)

    labels = []
    results = {}
    test_runner = marker.Benchmarker("/home/ahutton/dev/uni/Part D Project/fc-implementation",)

    # This allows the branch to, for each formula, keep going on larger words until the timeout is reached, then go on to the next formula, storing all results
    for (i, eq) in enumerate(equations):
        cases = []
        for word in words:
            labels.append(f"D={i+1}  W={len(word)}")
            cases.append({"$FORMULA$": eq, "$WORD$": word})

        branches = BRANCHES
        loop_results = test_runner.benchmark_branches(
            cases=cases,
            branches=branches,
            num_trials=3,
            timeout=120,
            print_output=True,
            skip_branch_on_fail=True

        )
        for branch in branches:
            if branch not in results:
                results[branch] = loop_results[branch]
            else:
                results[branch] += loop_results[branch]

    save_results("growing_disjunctions", results, case_labels=labels)


def growing_conjunctions():
    # same as above, but for conjunctions (hopefully will be much nicer)
    n_fragments = 4
    num_words = 5
    word_growth_step = 5

    equations = ['a = v0']
    for i in range(1, n_fragments):
        last_eq = equations[i-1]
        new_eq = last_eq + f" && v{i}=v{i-1}"
        equations.append(new_eq)

    words = [random_word(ascii_letters, word_growth_step)]
    for i in range(1, num_words):
        last_word = words[i-1]
        new_word = last_word + random_word(ascii_letters, word_growth_step)
        words.append(new_word)

    labels = []
    results = {}
    test_runner = marker.Benchmarker("/home/ahutton/dev/uni/Part D Project/fc-implementation",)

    # This allows the branch to, for each formula, keep going on larger words until the timeout is reached, then go on to the next formula, storing all results
    for (i, eq) in enumerate(equations):
        cases = []
        for word in words:
            labels.append(f"D={i+1}  W={len(word)}")
            cases.append({"$FORMULA$": eq, "$WORD$": word})

        branches = BRANCHES
        loop_results = test_runner.benchmark_branches(
            cases=cases,
            branches=branches,
            num_trials=3,
            timeout=120,
            print_output=True,
            skip_branch_on_fail=True

        )
        for branch in branches:
            if branch not in results:
                results[branch] = loop_results[branch]
            else:
                results[branch] += loop_results[branch]

    save_results("growing_conjunctions", results, case_labels=labels)


def factor_enumeration():
    test_runner = marker.Benchmarker("/home/ahutton/dev/uni/Part D Project/fc-implementation",
                                     run_command=["./target/release/fc-implementation",
                                                  "--command", "generate-factors", "--file", "$WORD$", "--quiet"])
    files = [
        "/home/ahutton/dev/uni/Part D Project/fc-tester/test cases/texts/basic-rust.rs",
        "/home/ahutton/dev/uni/Part D Project/fc-tester/test cases/texts/short-xmas.txt",
    ]
    labels = ["basic rust", "xmas"]
    cases = [{"$WORD$": f}for f in files]

    results = test_runner.benchmark_branches(
        cases=cases,
        branches=[Branch.FT_NUC_NOHASH_LCP, Branch.FT_NUC_NOHASH],
        num_trials=1,
        timeout=120,
        print_output=True,
        skip_branch_on_fail=True

    )

    save_results("factor_enumeration", results, case_labels=labels)


# fake_csv()
# rust_functions()
# fake_csv_ordering()
# p_tag()
# multiple_occurrences()
# random_conjugates()
# growing_equations()
# growing_conjunctions()
# naive_p_tag()
factor_enumeration()
