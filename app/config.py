
# The Ollama model to use for patch generation
MODEL_NAME = "qwen2.5-coder"

# Maximum number of repair attempts before aborting
MAX_RETRIES = 5

# Maximum time (in seconds) a single pytest run is allowed to take
VALIDATION_TIMEOUT = 60

# The default validation command
DEFAULT_VALIDATION_COMMAND = ["pytest"]

# Maximum number of files the agent is allowed to read per attempt
MAX_FILES_TO_READ = 5
