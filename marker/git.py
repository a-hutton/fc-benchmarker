import subprocess


class Repo():
    def __init__(self, dir: str) -> None:
        self.dir = dir

    def checkout(self, branch: str):
        if branch not in self.list_branches():
            raise IOError(f"Branch {branch} not in repository")
        res = subprocess.run(["git", "checkout", branch], cwd=self.dir)
        res.check_returncode()

    def list_branches(self, include_remote: bool = False) -> list[str]:
        command = ["git", "branch"]
        if include_remote:
            command.append("--all")
        branches = subprocess.run(
            command, capture_output=True, cwd=self.dir)
        return [name.strip(" *") for name in branches.stdout.decode().splitlines()]


if __name__ == "__main__":
    r = Repo("/home/ahutton/dev/uni/Part D Project/fc-implementation")
    r.checkout("Parallelised")
