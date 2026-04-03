from app.logging_utils import get_logger
from app.config import MAX_RETRIES, MAX_FILES_TO_READ, DEFAULT_VALIDATION_COMMAND
from app.tools import run_command, read_file, write_file, search_in_files
from app.prompts import DIAGNOSIS_PROMPT, PATCH_PROMPT
from app.state import AgentState
from langchain_community.llms import Ollama
from app.config import MODEL_NAME



logger = get_logger(__name__)

def start_run(state: AgentState) -> dict:
    logger.info("Starting new repair run")
    return {
        "attempt_count": 0,
        "last_exit_code": None,
        "last_stdout": "",
        "last_stderr": "",
        "failure_summary": "",
        "suspected_files": [],
        "selected_files": [],
        "patch_text": "",
        "patch_applied": False,
        "dashboard_events": [],
        "run_history": [],
        "final_status": "",
        "file_contents": {},

    }

def run_validation(state: AgentState) -> dict:
    new_attempt = state["attempt_count"] + 1
    try:
        result = run_command(state["validation_command"], state["repo_path"])
        logger.info(f"Attempt {new_attempt}: exit code {result['exit_code']}")
        return {
            "attempt_count": new_attempt,
            "last_exit_code": result["exit_code"],
            "last_stdout": result["stdout"],
            "last_stderr": result["stderr"],
        }
    except Exception as e:
        logger.error(f"Validation command failed to run: {e}")
        return {
            "attempt_count": new_attempt,
            "last_exit_code": -1,
            "last_stdout": "",
            "last_stderr": str(e),
        }


def analyze_failure(state: AgentState) -> dict:
    output = state["last_stdout"] + "\n" + state["last_stderr"]

    lines = output.strip().splitlines()
    summary = "\n".join(lines[-30:])  # last 30 lines

    suspected = []
    for line in lines:
        if "FAILED" in line or ".py" in line:
            # extract the part before "::" if present
            part = line.strip().split("::")[0]
            if part.endswith(".py"):
                suspected.append(part.strip())
    suspected = list(dict.fromkeys(suspected))
    logger.info(f"Suspected files: {suspected}")
    return {
        "failure_summary": summary,
        "suspected_files": suspected,
    }



def gather_context(state: AgentState) -> dict:
    files_to_read = state["suspected_files"][:MAX_FILES_TO_READ]
    selected = {}
    for file in files_to_read:
        try:
            content = read_file(file, state["repo_path"])
            selected[file] = content
        except Exception as e:
            logger.warning(f"Could not read {file}: {e}")
    
    logger.info(f"Gathered context from {len(selected)} file(s)")
    return {
        "selected_files": list(selected.keys()),
        "file_contents": selected,
    }


    
def generate_patch(state: AgentState) -> dict:
    if not state["selected_files"]:
        logger.warning("No files selected, cannot generate patch")
        return {"patch_text": ""}

    file_name = state["selected_files"][0]
    file_content = state["file_contents"].get(file_name, "")

    prompt = PATCH_PROMPT.format(
        failure_summary=state["failure_summary"],
        file_name=file_name,
        file_content=file_content,
        )
    try:
        llm = Ollama(model=MODEL_NAME)
        patch = llm.invoke(prompt)
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return {"patch_text": ""}

    logger.info(f"Patch generated for {file_name}")
    return {
        "patch_text": patch,
        "suspected_files": [file_name],  # narrow focus to the file being patched
    }


def apply_patch(state: AgentState) -> dict:
    if not state["patch_text"] or not state["selected_files"]:
        logger.warning("No patch or selected files, cannot apply patch")
        return {"patch_applied": False}

    file_to_patch = state["selected_files"][0]
    new_content = state["patch_text"]

    try:
        write_file(file_to_patch, new_content, state["repo_path"])
        logger.info(f"Patch applied to {file_to_patch}")
        return {"patch_applied": True}
    except Exception as e:
        logger.error(f"Failed to apply patch: {e}")
        return {"patch_applied": False}

    
def summarize_result(state: AgentState) -> dict:
    record = {
        "attempt": state["attempt_count"],
        "status": "success",
        "suspected_files": state["suspected_files"],
        "patch_applied": state["patch_applied"],
    }
    history = state["run_history"] + [record]
    logger.info(f"Run completed successfully after {state['attempt_count']} attempt(s)")
    return {
        "final_status": "success",
        "run_history": history,
    }


def abort(state: AgentState) -> dict:
    record = {
        "attempt": state["attempt_count"],
        "status": "aborted",
        "suspected_files": state["suspected_files"],
        "patch_applied": state["patch_applied"],
    }
    history = state["run_history"] + [record]
    logger.warning(f"Run aborted after {state['attempt_count']} attempt(s)")
    return {
        "final_status": "aborted",
        "run_history": history,
    }


                                                                                    
