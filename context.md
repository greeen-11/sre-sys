# Autonomous Zero-Budget SRE Agent

## 1. Project Description

This project is a local-first autonomous SRE agent built to help a student or solo developer learn three things at the same time:

1. How to design and orchestrate AI agents with LangChain and LangGraph.
2. How modern software reliability work is done in practice.
3. How to build safe automation that can inspect failures, propose fixes, and verify them locally.

The core idea is simple: when a local project has a failing test or broken build, the agent should be able to read the failure output, inspect the relevant code, generate a patch with a local LLM, apply the patch, and run the validation step again. The loop continues until the issue is fixed or the agent reaches a retry limit.

The project is intentionally "zero-budget" in the sense that it should run on a local machine using free tools and local models. That constraint is not just about cost. It is also a design choice that forces the system to be observable, controlled, and safe to experiment with while learning.

This is not meant to replace real SRE teams or production engineering workflows. It is a learning project that combines agent engineering with practical reliability concepts such as incident diagnosis, debugging under constraints, verification, rollback thinking, and operational guardrails.

---

## 2. Why This Project Matters

Most tutorials on AI agents focus on toy tasks. Most tutorials on DevOps and SRE focus on infrastructure or CI/CD tooling. This project sits between them.

By building it, you will practice:

- Translating an ambiguous problem into a stateful workflow.
- Designing tools that an agent can use safely.
- Handling failure loops instead of one-shot prompts.
- Turning logs and test failures into actionable debugging context.
- Creating explicit stop conditions, retry policies, and validation gates.
- Thinking like an engineer responsible for reliability, not just code generation.

The project is valuable because it teaches both orchestration and discipline. A useful autonomous agent is not just a model call. It is a controlled system with state, tools, routing logic, memory, observability, and hard safety boundaries.

---

## 3. Main Goal

Build a local autonomous agent that can:

1. Run a validation command such as `pytest`.
2. Detect whether the command succeeded or failed.
3. Capture and summarize the error output.
4. Identify the most relevant files and code regions.
5. Ask a local LLM to generate a targeted fix.
6. Apply the patch to the local workspace.
7. Re-run validation to verify the fix.
8. Stop on success or fail safely after a maximum number of attempts.

The first version should focus on small Python projects with failing tests. That narrow scope keeps the system realistic and learnable.

---

## 4. Learning Objectives

### A. LangChain and LangGraph

You should understand:

- How to define agent state.
- How to model a workflow as nodes and edges.
- How routing decisions are made from state.
- How to attach tools to an agent.
- How to persist and inspect execution state.
- How to separate reasoning, tool use, and validation.

### B. SRE and DevOps Concepts

You should also learn:

- The purpose of CI/CD pipelines.
- Why failing tests are a reliability signal.
- How to treat logs as operational evidence.
- Why observability matters during automated workflows.
- The difference between detection, diagnosis, remediation, and verification.
- Why safe rollback and bounded retries are essential in automation.

### C. Practical Engineering Discipline

This project should reinforce:

- Small, testable iterations.
- Clear system boundaries.
- Controlled permissions.
- Measurable success criteria.
- Avoiding infinite loops and unsafe automation.

---

## 5. High-Level System Overview

The system acts like a junior autonomous SRE assistant running locally on a developer machine.

It has five core responsibilities:

- Observe: run commands and capture logs.
- Reason: analyze the failure and decide what to do next.
- Act: edit code or configuration in the local repository.
- Verify: rerun tests or checks to confirm whether the change worked.
- Expose control and visibility through a local dashboard.

The agent should operate as a state machine rather than a simple chatbot. Each cycle updates structured state and routes to the next step based on the outcome.

---

## 6. Proposed Tech Stack

| Layer | Tooling | Role |
| :--- | :--- | :--- |
| Language | Python 3.10+ | Main implementation language |
| Model Runtime | Ollama | Runs local LLMs |
| Coding Model | `qwen2.5-coder`, `codellama`, or similar | Generates reasoning and code patches |
| Agent Framework | LangChain | Model/tool integration |
| Workflow Engine | LangGraph | Stateful orchestration and routing |
| Validation | `pytest` | Test execution and verification |
| File + Command Access | Local tool layer or MCP-style tools | Read, write, and execute commands safely |
| Logging | Structured Python logging | Traceability and debugging |
| Dashboard | Streamlit, FastAPI + simple frontend, or similar | Manual control, run inspection, and monitoring |

Recommended default assumption:

- Start with a direct Python tool layer for file and command operations.
- Add MCP later if the goal is to explicitly learn protocol-based tool integration.

This is important because MCP is valuable, but it should not become an unnecessary blocker before the core repair loop works.

---

## 7. Scope of Version 1

Version 1 should be intentionally narrow.

### In Scope

- Local Python repository only.
- One validation entrypoint such as `pytest`.
- Workspace-limited file reads and writes.
- Text-based logs and error parsing.
- Single-agent repair loop.
- Max retry count and explicit stop conditions.
- Basic run history for debugging.
- Local control and monitoring dashboard.

### Out of Scope

- Production infrastructure changes.
- Kubernetes, cloud remediation, or live system automation.
- Multi-repo support.
- Large codebase semantic indexing.
- Autonomous dependency upgrades.
- Broad shell access without restrictions.

Keeping the first version small is not a compromise. It is the correct engineering choice.

---

## 8. Core Workflow

The agent should follow a deterministic high-level loop:

1. Run the validation command.
2. If validation passes, terminate successfully.
3. If validation fails, capture command output, exit code, and relevant metadata.
4. Extract likely failing files, stack traces, test names, and error summaries.
5. Read a bounded set of relevant files.
6. Ask the model for a minimal patch based on the code and failure context.
7. Apply the patch.
8. Re-run validation.
9. Repeat until success or retry limit is reached.

This workflow sounds simple, but the quality of the project depends on how well each step is bounded and observed.

---

## 9. LangGraph Design

The project should be implemented as a graph with explicit nodes and transitions.

### Suggested Nodes

- `start_run`
- `run_validation`
- `analyze_failure`
- `gather_context`
- `generate_patch`
- `apply_patch`
- `verify_fix`
- `summarize_result`
- `abort`

### Suggested Routing Logic

- If validation succeeds, route to `summarize_result`.
- If validation fails and retries remain, route to `analyze_failure`.
- If the model cannot produce a safe patch, route to `abort`.
- If retries are exhausted, route to `abort`.

### Why LangGraph Fits

LangGraph is useful here because the system is not a single conversation. It is a loop with memory, branching, retries, and explicit state transitions. That is exactly the kind of problem graph orchestration is built for.

---

## 10. Agent State Design

The state should be structured, not ad hoc. A suggested schema:

```python
from typing import Any, List, Optional, TypedDict


class AgentState(TypedDict):
    repo_path: str
    validation_command: List[str]
    max_retries: int
    attempt_count: int
    last_exit_code: Optional[int]
    last_stdout: str
    last_stderr: str
    failure_summary: str
    suspected_files: List[str]
    selected_files: List[str]
    patch_text: str
    patch_applied: bool
    dashboard_events: List[dict[str, Any]]
    run_history: List[dict[str, Any]]
    final_status: str
```

This state is intentionally explicit so that:

- Every node has clear inputs and outputs.
- Execution can be debugged after failures.
- You can inspect why the graph routed a certain way.

---

## 11. Tooling Layer

The agent needs a minimal but safe set of tools.

### Required Tools

- `run_command`
  - Runs only approved commands such as `pytest`.
  - Captures exit code, stdout, stderr, and duration.

- `read_file`
  - Reads only files within the workspace.

- `write_file` or `apply_patch`
  - Applies targeted edits within the workspace.

- `list_files`
  - Helps the agent discover relevant files.

- `search_in_files`
  - Finds symbols, test names, trace references, and related code.

### Safety Requirements

- No unrestricted shell execution.
- No writes outside the workspace.
- No network access required for the repair loop.
- No destructive commands.
- All file modifications should be logged.

If MCP is used, these constraints should still exist. MCP does not replace safe design. It only standardizes tool access.

---

## 12. Control and Monitoring Dashboard

The project should include a local dashboard for control, transparency, and debugging.

The dashboard is important for two reasons:

- It makes the agent easier to understand while learning.
- It gives you a manual control layer so the system is not a blind loop.

### Dashboard Goals

- Start a repair run manually.
- Display the current graph node and agent status.
- Show attempt count, validation command, and last exit code.
- Show failure summaries and suspected files.
- Show the proposed patch before or after application.
- Show run history and timestamps.
- Allow pause, resume, or abort for a run.

### Minimum Dashboard Views

- Run overview.
- Current state snapshot.
- Validation logs.
- File changes or patch preview.
- Final result summary.

### Recommended Implementation Approach

For a student project, the dashboard should be simple:

- Start with Streamlit if the goal is speed and easy local visibility.
- Use FastAPI plus a lightweight frontend later if you want a cleaner separation between backend and UI.

The dashboard does not need to be fancy. It needs to make the system inspectable and controllable.

---

## 13. Role of the Local LLM

The local model is the reasoning and patch-generation engine. Its job is not to "solve everything." Its job is to produce a small, targeted, verifiable change from bounded context.

The model should receive:

- The validation command that failed.
- The most relevant failure output.
- A shortlist of relevant files.
- Current file contents.
- Clear instructions to minimize the patch.

The model should return:

- A concise diagnosis.
- A proposed code change.
- Ideally a structured patch format or replacement block.

The system should prefer small diffs over full-file rewrites whenever possible.

---

## 14. Prompting Strategy

The prompting strategy matters more than raw model size in this kind of project.

Good prompts should:

- State the failing command and error clearly.
- Bound the file context.
- Ask for the smallest valid fix.
- Tell the model not to refactor unrelated code.
- Require a brief explanation of why the patch should work.

Bad prompts will cause:

- Large unnecessary rewrites.
- Fixes that ignore the actual failure.
- Regression risk in unrelated files.
- Infinite "guess and retry" behavior.

---

## 15. Safety and Guardrails

This project only makes sense if the automation is bounded.

### Minimum Guardrails

- Maximum retry count, for example 3 to 5 attempts.
- Maximum validation runtime per attempt.
- Workspace-only file edits.
- Allowlist for executable commands.
- Abort if the model suggests editing too many files.
- Abort if the same failure repeats with no useful change.
- Log every attempt, prompt, patch, and validation result.

### Optional Extra Guardrails

- Git diff check before and after each attempt.
- Automatic snapshot or temporary branch before modification.
- Confidence score or heuristic for patch quality.
- Reject patches that touch forbidden paths.

Without these controls, the system is not an engineering project. It is just an uncontrolled loop.

---

## 16. Observability

Observability is a major learning objective.

The project should produce enough information to answer:

- What command was run?
- What failed?
- Which files were selected?
- What prompt was sent to the model?
- What patch was applied?
- Why did the graph choose the next node?
- How many retries happened?
- Why did the run end?

At minimum, log:

- Node execution start and end.
- Validation command results.
- File operations.
- Retry count.
- Final status.
- Dashboard events such as manual start, pause, resume, and abort.

Structured logs or JSON logs would be a good learning choice.

---

## 17. Evaluation Criteria

The project needs measurable outcomes.

### Success Metrics

- Percentage of seeded failures fixed successfully.
- Average number of attempts per successful fix.
- Percentage of runs that terminate safely.
- Percentage of fixes that introduce regressions.
- Time per repair cycle.

### Good Demo Scenarios

- A simple failing unit test caused by a logic bug.
- A broken import or wrong function name.
- A small edge-case bug in a utility function.

### Bad Early Scenarios

- Large refactors.
- Multi-module architectural failures.
- Missing dependencies or environment corruption.

Start with easy, well-bounded failure cases. That is how you make the project teachable.

---

## 18. Proposed Repository Structure

```text
project/
├── context.md
├── requirements.txt
├── README.md
├── app/
│   ├── state.py
│   ├── graph.py
│   ├── nodes.py
│   ├── tools.py
│   ├── prompts.py
│   ├── config.py
│   └── logging_utils.py
├── dashboard/
│   ├── app.py
│   ├── components.py
│   └── services.py
├── examples/
│   ├── broken_case_1/
│   └── broken_case_2/
├── tests/
│   ├── test_tools.py
│   ├── test_graph.py
│   └── test_end_to_end.py
└── runs/
    └── .gitkeep
```

This structure keeps orchestration, tools, prompts, and tests clearly separated.

---

## 19. Suggested Development Milestones

### Milestone 1: Basic Local Tooling

Build and test:

- Command runner.
- File reader/writer.
- Workspace safety checks.

Goal:

- Run `pytest`, capture failure output, and read the suspected source file.

### Milestone 2: First LangGraph Loop

Build:

- State definition.
- Minimal graph with validation, analysis, and stop/success branches.

Goal:

- A graph that can complete one full pass and log its state transitions.

### Milestone 3: Model Integration

Build:

- Ollama-backed model call.
- Prompt templates for diagnosis and patch creation.

Goal:

- The model can propose a small patch from a failing test case.

### Milestone 4: Patch Application and Retry

Build:

- Patch application logic.
- Retry loop with stop conditions.

Goal:

- The agent can attempt at least one autonomous repair cycle.

### Milestone 5: Observability and Evaluation

Build:

- Structured logs.
- Run history.
- Simple benchmark scenarios.
- First local monitoring dashboard.

Goal:

- You can inspect what happened and measure whether the system is improving.

### Milestone 6: Dashboard Control Layer

Build:

- Manual run trigger.
- Current state panel.
- Log viewer.
- Patch preview and final result screen.

Goal:

- You can operate and monitor the agent without reading raw files only.

### Milestone 7: Optional MCP Integration

Build:

- MCP-compatible tools for file and command operations.

Goal:

- Learn how protocol-based tool access compares to direct Python tooling.

---

## 20. Risks and Challenges

The main technical risks are:

- Local models may produce weak or overconfident patches.
- Failure logs may not clearly identify the real bug.
- The agent may select irrelevant files.
- Retry loops may repeat ineffective fixes.
- Unsafe tool access may cause unintended edits.

These are not reasons to avoid the project. They are the reason the project is useful.

If the system fails in visible ways, you will learn:

- How to tighten prompts.
- How to improve state design.
- How to improve file selection.
- How to add better stop conditions.
- How to think like a reliability engineer instead of a prompt writer.

---

## 21. Definition of Success

This project is successful if:

- It can autonomously fix a small set of seeded Python test failures locally.
- It does so using bounded retries and explicit safety rules.
- Its internal decisions are observable and debuggable.
- It provides a local dashboard to inspect and control runs.
- It teaches the builder how agent orchestration and operational reliability intersect.

Success does not require a perfect autonomous debugger. Success means building a reliable learning system that demonstrates real agent engineering patterns.

---

## 22. Final Vision

The long-term vision is an educational autonomous repair agent that behaves like a careful junior SRE:

- It watches for failure signals.
- It gathers evidence before acting.
- It changes only what is necessary.
- It verifies every action.
- It stops safely when confidence is low.
- It exposes its state through a dashboard so a human can supervise it.

That combination of reasoning, tooling, verification, and guardrails is the real lesson of the project.

The final product should not just showcase AI. It should demonstrate engineering judgment.
