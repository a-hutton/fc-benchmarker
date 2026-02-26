import csv
import copy
from itertools import islice
from random import choice
from cases.generation import create_equation, tautology


type TestCase = dict[str, str]


def formula_test_cases(formula: str, *words: str) -> list[TestCase]:
    cases = []
    for word in words:
        cases.append({"$FORMULA$": formula, "$WORD$": word})
    return cases


def load_csv(filename: str) -> list[TestCase]:
    cases = []
    with open(filename, "r") as f:
        reader = csv.reader(f)
        # skip first row in iter, keep going until end
        for row in islice(reader, 1, None):
            formula = row[0]
            words = row[1:]
            cases.append(formula_test_cases(formula, *words))

    return cases


def generate_random_cases(num: int, alphabet="abcd", num_vars=3, word_len=20, connectives_range: list[int] = [0, 1, 2]) -> list[TestCase]:
    cases = []
    for i in range(num):
        case = random_case(alphabet, num_vars, word_len,
                           choice(connectives_range))
        cases.append(case)
    return cases


TAUTOLOGY_OPTIONS = [
    "AND_SELF",
    "OR_SELF",
    "AND_TRUE",
    "OR_FALSE",
]


def random_case(alphabet="abcd", num_vars=3, word_len=20, num_connectives=2) -> TestCase:
    formula, word = create_equation(alphabet, word_len, num_vars)
    for i in range(num_connectives):
        tautology_type = choice(TAUTOLOGY_OPTIONS)
        f = copy.deepcopy(formula)
        formula = tautology(f, tautology_type)

    return formula_test_cases(str(formula),  word)[0]
