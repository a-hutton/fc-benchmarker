from dataclasses import dataclass
from string import ascii_letters, ascii_uppercase
import random
from enum import Enum
from string import ascii_lowercase


class ContentType(Enum):
    VARIABLE = 0
    CONSTANT = 1


@dataclass
class EquationContent:
    content_type: ContentType
    content: str

    def __str__(self) -> str:
        match self.content_type:
            case ContentType.VARIABLE:
                return self.content
            case ContentType.CONSTANT:
                return f'"{self.content.replace("\\", "\\\\")}"'
        return "default"


# Base class for all formula types, never directly implemented
class Formula:
    def __init__(self) -> None:
        raise Exception("Don't directly create `Formula`, use the subclasses")

    @property
    def vars(self) -> set[str]:
        raise Exception("`Formula` subclasses must implement `vars()`")

    def __str__(self) -> str:
        raise Exception("`Formula` subclasses must implement `__str()__`")


@dataclass
class Equation(Formula):
    lhs: str
    rhs: list[EquationContent]
    free_vars: set[str]

    def __str__(self) -> str:
        return self.lhs + "=" + " ".join([str(c) for c in self.rhs])

    @property
    def vars(self) -> set[str]:
        return self.free_vars


@dataclass
class Negation(Formula):
    inner: Formula

    def __str__(self) -> str:
        return "¬" + self.inner.__str__()

    @property
    def vars(self) -> set[str]:
        return self.inner.vars


@dataclass
class Conjunction(Formula):
    lhs: Formula
    rhs: Formula

    def __str__(self) -> str:
        return f"({self.lhs} ∧ {self.rhs})"

    @property
    def vars(self) -> set[str]:
        return self.lhs.vars.union(self.rhs.vars)


@dataclass
class Disjunction(Formula):
    lhs: Formula
    rhs: Formula

    def __str__(self) -> str:
        return f"({self.lhs} ∨ {self.rhs})"

    @property
    def vars(self) -> set[str]:
        return self.lhs.vars.union(self.rhs.vars)


def create_equation(alphabet: str, word_len: int, num_vars: int = 3) -> tuple[Equation, str]:
    vars = create_var_set(num_vars)
    assignments = {}

    rhs: list[EquationContent] = []
    word = ""

    while len(word) < word_len:
        is_const = random.random() > 0.5
        if is_const:
            const = random_word(alphabet, random.randint(1, 4))
            word += const
            rhs.append(EquationContent(ContentType.CONSTANT, const))
        else:
            var: str = random.choice(list(vars))
            if var not in assignments:
                assignments[var] = random_word(alphabet, random.randint(1, 4))
            word += assignments[var]
            rhs.append(EquationContent(ContentType.VARIABLE, var))

    eq = Equation("$U", rhs, vars)
    return eq, word


def true_equation(vars: set[str]) -> Equation:
    var = random.choice(list(vars))
    return Equation(var, [EquationContent(ContentType.VARIABLE, var)], vars)


def false_equation(vars: set[str]) -> Formula:
    inner = true_equation(vars)
    return Negation(inner)


def tautology(formula: Formula, *types: str) -> Formula:
    output = formula
    for type in types:
        match type:
            case "AND_SELF":
                output = Conjunction(output, output)
            case "OR_SELF":
                output = Disjunction(output, output)
            case "AND_TRUE":
                other = true_equation(output.vars)
                output = Conjunction(output, other)
            case "OR_FALSE":
                other = false_equation(output.vars)
                output = Disjunction(output, other)
            case _:
                raise Exception("WTF IS going on?")
    return output


def create_var_set(num_vars: int) -> set[str]:
    vars = set()
    i = 0
    while len(vars) < num_vars:
        label = ""
        x = i
        while True:
            label = chr(ord('A') + x % 26) + label
            x = x // 26 - 1
            if x < 0:
                break
        vars.add(label)
        i += 1

    return vars


def random_word(alphabet: str, len: int) -> str:
    return "".join(random.choices(alphabet, k=len))


if __name__ == "__main__":
    eq, word = create_equation("ab", 20)
    print(eq)
    print(len(word), word)
    print("---")
    conj = tautology(eq,
                     "AND_TRUE",
                     "OR_SELF",
                     "OR_FALSE",
                     )
    print(conj)
