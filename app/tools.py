
from pathlib import Path
from subprocess import run
from time import perf_counter
from subprocess import TimeoutExpired



def ensure_within_repo(path: str, repo_path: str) -> Path:
    repo = Path(repo_path).resolve()

    if not repo.exists():
        raise FileNotFoundError(f"Repository path '{repo_path}' does not exist")
    if not repo.is_dir():
        raise NotADirectoryError(f"Repository path '{repo_path}' is not a directory")
    
    target = (repo / path).resolve()

    try :
        target.relative_to(repo)
    except ValueError:
        raise ValueError("Path is not within the repository")
    return target



def run_command(command: list[str], cwd: str) -> dict:
    if not command:
        raise ValueError("Command cannot be empty")
    
    if command[0] != "pytest":
        raise ValueError("Only pytest commands are allowed")
    
    working_dir = Path(cwd).resolve()
    if not working_dir.exists():
        raise FileNotFoundError(f"Working directory '{cwd}' does not exist")
    
    start = perf_counter()
    try:
        result = run(
            command,
            cwd=working_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        duration = perf_counter() - start

        return {
            "command": command,
            "cwd": str(working_dir),
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration_seconds": duration,
        }
    except TimeoutExpired as e:
        duration = perf_counter() - start
        return {
            "command": command,
            "cwd": str(working_dir),
            "exit_code": None,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "duration_seconds": duration,
            "error": "Command timed out",
        }

def read_file(path: str, repo_path: str) -> str:
    pass


def write_file(path: str, content: str, repo_path: str) -> None:
    pass


def list_files(repo_path: str) -> list[str]:
    pass


def search_in_files(repo_path: str, query: str) -> list[str]:
    pass
