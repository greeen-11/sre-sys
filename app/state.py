
from typing import Any, List, Optional, TypedDict

class AgentState(TypedDict):
    repo_path: str               # where the target project lives
    validation_command: List[str] # e.g. ["pytest"]
    max_retries: int             # e.g. 5
    attempt_count: int           # how many repair attempts so far
    last_exit_code: Optional[int] # exit code from last pytest run
    last_stdout: str             # stdout from last run
    last_stderr: str             # stderr from last run
    failure_summary: str         # human-readable summary of what failed
    suspected_files: List[str]   # files the agent thinks are relevant
    selected_files: List[str]    # files actually read for context
    patch_text: str              # the patch the LLM proposed
    patch_applied: bool          # whether the patch was applied
    dashboard_events: List[dict[str, Any]]  # events for the UI
    run_history: List[dict[str, Any]]       # log of all attempts
    final_status: str            # "success", "failed", "aborted"
    file_contents: dict[str, str]   # filename → file content

