#!/usr/bin/env bash
set -euo pipefail

#############################################
# Settings
#############################################

# Default timeout (override with: CLAUDE_TIMEOUT="5m" ./run_claude.sh ...)
CLAUDE_TIMEOUT="${CLAUDE_TIMEOUT:-10m}"

#############################################
# Pre-checks
#############################################

# jq check
if ! command -v jq >/dev/null 2>&1; then
  echo "Error: 'jq' is not installed." >&2
  echo "Please install jq:" >&2
  echo "  macOS : brew install jq" >&2
  echo "  Ubuntu: sudo apt-get install jq" >&2
  echo "  Fedora: sudo dnf install jq" >&2
  echo "  Arch  : sudo pacman -S jq" >&2
  exit 1
fi

# timeout check
if ! command -v timeout >/dev/null 2>&1; then
  echo "Error: 'timeout' command not found (coreutils)." >&2
  echo "Install via:" >&2
  echo "  macOS (brew coreutils): brew install coreutils" >&2
  echo "  Ubuntu: sudo apt-get install coreutils" >&2
  exit 1
fi

# argument check
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <file_name> [prompt_file]" >&2
  echo "  <file_name>   : File name to reference inside the prompt." >&2
  echo "  [prompt_file] : Optional. Default: ./prompt.md" >&2
  exit 1
fi

file_name="$1"
prompt_file="${2:-prompt.md}"

if [ ! -f "$prompt_file" ]; then
  echo "Error: prompt file '$prompt_file' not found." >&2
  exit 1
fi

#############################################
# Output filenames
#############################################

timestamp="$(date +"%Y%m%d-%H%M%S")"

stream_file="stream-${timestamp}.jsonl"
debug_file="debug-${timestamp}.log"
result_file="result-${timestamp}.txt"

#############################################
# Build final prompt
#############################################

prompt="$(
  printf 'read: %s, then:\n\n%s\n' \
    "$file_name" \
    "$(cat "$prompt_file")"
)"

#############################################
# Record start time
#############################################

start_time=$(date +%s)

echo "Running with timeout: $CLAUDE_TIMEOUT"
echo "Press Ctrl+C anytime to abort."

#############################################
# Execute Claude (wrapped in timeout)
#############################################

if [ -t 1 ]; then
  # Interactive terminal: show stream in real time
  timeout "$CLAUDE_TIMEOUT" \
    claude --dangerously-skip-permissions -p "$prompt" \
      --output-format stream-json --verbose \
      2> >(tee "$debug_file" >&2) \
  | tee "$stream_file" \
  | tee /dev/tty \
  | jq -r -s 'map(select(.type=="result")) | last | .result' \
  > "$result_file"
else
  # Non-interactive environment
  timeout "$CLAUDE_TIMEOUT" \
    claude --dangerously-skip-permissions -p "$prompt" \
      --output-format stream-json --verbose \
      2> >(tee "$debug_file" >&2) \
  | tee "$stream_file" \
  | jq -r -s 'map(select(.type=="result")) | last | .result' \
  > "$result_file"
fi

#############################################
# Record end time & compute duration
#############################################

end_time=$(date +%s)
duration=$(( end_time - start_time ))

# Convert to XmYs
duration_min=$(( duration / 60 ))
duration_sec=$(( duration % 60 ))
duration_fmt="${duration_min}m${duration_sec}s"

#############################################
# Summary
#############################################

echo "Execution completed."
echo "Generated files:"
echo "  Stream log : $stream_file"
echo "  Debug log  : $debug_file"
echo "  Result     : $result_file"
echo "Execution time: $duration_fmt"
