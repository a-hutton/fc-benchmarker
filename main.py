import subprocess
from time import time
import csv
import json

from cases import random_case
from tester import Tester


PROJECT_PATH = "/home/ahutton/dev/uni/Part D Project/fc-implementation"


tester = Tester(PROJECT_PATH)
res = tester.benchmark_branches(
    "./test cases/cases.csv", num_trials=2, branches=["parallel"])
print(res)
