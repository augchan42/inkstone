#!/usr/bin/env bash
# Plan Review Loop — Stop Hook (inkstone)
#
# Enforces completion of the plan-review-loop skill. Unlike the original
# review-loop plugin, the review itself is orchestrated by the skill
# (Codex CLI or context-blind subagents); this hook only guarantees the
# loop cannot be silently abandoned:
#
#   phase locate/review + no review file  → block: finish the review
#   phase addressing + no disposition log → block once: address findings
#   phase addressing + disposition logged → approve, clean up state
#
# Coexistence with hamel-review/review-loop: if its state file
# (.claude/review-loop.local.md) exists, approve immediately so its own
# stop hook drives that stop cycle. Never double-block.
#
# On any error, default to allowing exit (never trap the user).

LOG_FILE=".claude/plan-review-loop.log"

log() {
  mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null || return 0
  echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] $*" >> "$LOG_FILE"
}

approve() {
  printf '{"decision":"approve"}\n'
  exit 0
}

trap 'log "ERROR: hook exited via ERR trap (line $LINENO)"; printf "{\"decision\":\"approve\"}\n"; exit 0' ERR

# Consume stdin (hook input JSON) — must read to avoid broken pipe
HOOK_INPUT=$(cat)

STATE_FILE=".claude/plan-review-loop.local.md"
ORIGINAL_STATE=".claude/review-loop.local.md"

# Fast path: no plan review loop active → this hook is a no-op
[ ! -f "$STATE_FILE" ] && approve

# Play nice: the original review-loop's stop hook owns this stop cycle
if [ -f "$ORIGINAL_STATE" ]; then
  log "DEFER: original review-loop active; approving so its hook drives this stop"
  approve
fi

parse_field() {
  sed -n "s/^${1}: *//p" "$STATE_FILE" | head -1
}

ACTIVE=$(parse_field "active")
PHASE=$(parse_field "phase")
REVIEW_ID=$(parse_field "review_id")

if [ "$ACTIVE" != "true" ]; then
  rm -f "$STATE_FILE"
  approve
fi

# Validate review_id format to prevent path traversal
if ! echo "$REVIEW_ID" | grep -qE '^[0-9]{8}-[0-9]{6}-[0-9a-f]{6}$'; then
  log "ERROR: invalid review_id format: $REVIEW_ID"
  rm -f "$STATE_FILE"
  approve
fi

REVIEW_FILE="reviews/plan-review-${REVIEW_ID}.md"

STOP_HOOK_ACTIVE=$(echo "$HOOK_INPUT" | jq -r '.stop_hook_active // false' 2>/dev/null || echo "false")

block() {
  local REASON="$1"
  local SYS_MSG="$2"
  if command -v jq >/dev/null 2>&1; then
    jq -n --arg r "$REASON" --arg s "$SYS_MSG" '{decision:"block", reason:$r, systemMessage:$s}'
  else
    # Reasons below contain no characters needing JSON escaping beyond newlines
    printf '{"decision":"block","reason":"%s","systemMessage":"%s"}\n' \
      "$(printf '%s' "$REASON" | tr '\n' ' ')" "$SYS_MSG"
  fi
  exit 0
}

case "$PHASE" in
  locate|review)
    # Safety: if we already blocked this cycle and phase never advanced,
    # fail open rather than trapping the user in a loop.
    if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
      log "WARN: stop_hook_active=true but phase still '$PHASE'; aborting loop (fail-open)"
      rm -f "$STATE_FILE"
      approve
    fi
    log "BLOCK: loop ${REVIEW_ID} stopped in phase '$PHASE'"
    block "A plan review loop is active (id: ${REVIEW_ID}) but has not completed its review phase.

Per the plan-review-loop skill:
1. Finish the target plan if it is not complete
2. Run the independent review (Codex CLI if available, else context-blind subagents — see the skill's Phase 2) and write the consolidated review to ${REVIEW_FILE}
3. Update ${STATE_FILE} to 'phase: addressing'
4. Address each finding with judgment (agree → fix the plan; disagree → note why) and append a '## Disposition' log to ${REVIEW_FILE}
5. Then stop

To abandon the loop instead, run the plan-review-loop skill with argument 'cancel' (or delete ${STATE_FILE})." \
      "Plan Review Loop [${REVIEW_ID}] — review phase incomplete"
    ;;

  addressing)
    if [ ! -f "$REVIEW_FILE" ]; then
      log "WARN: phase=addressing but ${REVIEW_FILE} missing; failing open"
      rm -f "$STATE_FILE"
      approve
    fi
    if ! grep -q '^## Disposition' "$REVIEW_FILE" 2>/dev/null; then
      if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
        log "WARN: stop_hook_active=true, no disposition; aborting loop (fail-open)"
        rm -f "$STATE_FILE"
        approve
      fi
      log "BLOCK: loop ${REVIEW_ID} in addressing phase, no disposition log"
      block "The independent review at ${REVIEW_FILE} has not been dispositioned.

Please:
1. Read the review carefully
2. For each finding, independently decide if you agree — do not blindly accept every suggestion
3. For findings you AGREE with: fix the plan
4. For findings you DISAGREE with: briefly note why you are skipping them
5. Append a '## Disposition' section to ${REVIEW_FILE} recording FIXED / SKIPPED / ESCALATED per finding
6. Then stop" \
        "Plan Review Loop [${REVIEW_ID}] — address review findings"
    fi
    log "COMPLETE: loop ${REVIEW_ID} dispositioned; cleaning up"
    rm -f "$STATE_FILE"
    approve
    ;;

  *)
    log "WARN: unknown phase '$PHASE', cleaning up"
    rm -f "$STATE_FILE"
    approve
    ;;
esac
