from marker.cases import load_csv
from marker import Benchmarker


PROJECT_PATH = "/home/ahutton/dev/uni/Part D Project/fc-implementation"


tester = Benchmarker(PROJECT_PATH)
res = tester.benchmark_branches(
    load_csv("./test cases/cases.csv"), num_trials=2, branches=["parallel"])
print(res)
