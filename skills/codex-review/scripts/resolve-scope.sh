#!/usr/bin/env bash
# codex-review — scope resolver
#
# Turns any argument form into ONE concrete git diff invocation.
# Emits KEY=value lines on stdout; diagnostics go to stderr.
#
# Usage:
#   resolve-scope.sh                          # auto-detect
#   resolve-scope.sh HEAD~3                   # since a ref
#   resolve-scope.sh 8d90758b b7e57ffd        # explicit range
#   resolve-scope.sh a..b | a...b             # range syntax passthrough
#   resolve-scope.sh <merge-sha>              # merge commit -> first-parent diff
#   resolve-scope.sh --commit <sha>           # that one commit only
#   resolve-scope.sh --pr 140                 # GitHub PR (needs gh)
#   resolve-scope.sh --staged | --uncommitted
#   resolve-scope.sh <any of the above> src/lib components/Foo.tsx
#
# Emitted keys:
#   SCOPE_LABEL     human-readable description of what will be reviewed
#   DIFF_ARGS       args to pass to `git diff`
#   PATHSPEC        space-separated paths, or empty
#   REF_SHA         short sha the review artifact is named after
#   CHANGED_FILES   file count
#   CHANGED_LINES   insertions + deletions
#   OVERSIZED       true when CHANGED_LINES exceeds SIZE_GUARD

set -uo pipefail

SIZE_GUARD="${CODEX_REVIEW_SIZE_GUARD:-2000}"

die() { echo "resolve-scope: $*" >&2; exit 1; }

git rev-parse --git-dir >/dev/null 2>&1 || die "not inside a git repository"

MODE=""
PR_NUM=""
REVS=()
PATHS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --staged|--cached)   MODE="staged"; shift ;;
    --uncommitted|--dirty) MODE="uncommitted"; shift ;;
    --commit)            MODE="commit"; REVS+=("${2:-}"); shift 2 ;;
    --pr)                MODE="pr"; PR_NUM="${2:-}"; shift 2 ;;
    --)                  shift; while [ $# -gt 0 ]; do PATHS+=("$1"); shift; done ;;
    -*)                  die "unknown flag: $1" ;;
    *)
      # An existing file or directory is a path; anything else is a rev.
      if [ -e "$1" ]; then
        PATHS+=("$1")
      elif git rev-parse --verify --quiet "$1" >/dev/null 2>&1 || [[ "$1" == *".."* ]]; then
        REVS+=("$1")
      else
        die "'$1' is neither an existing path nor a valid git revision"
      fi
      shift ;;
  esac
done

default_branch() {
  local d
  d=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')
  if [ -n "$d" ]; then echo "$d"; return; fi
  local b
  for b in main master trunk develop; do
    if git show-ref --verify --quiet "refs/heads/$b"; then echo "$b"; return; fi
  done
  echo ""
}

is_merge() {
  [ "$(git rev-list --parents -n1 "$1" 2>/dev/null | wc -w | tr -d ' ')" -gt 2 ]
}

DIFF_ARGS=""
SCOPE_LABEL=""
REF_SHA=""

case "$MODE" in
  staged)
    DIFF_ARGS="--cached"
    SCOPE_LABEL="staged changes"
    REF_SHA="staged"
    ;;
  uncommitted)
    DIFF_ARGS="HEAD"
    SCOPE_LABEL="uncommitted changes (staged + unstaged) vs HEAD"
    REF_SHA="working"
    ;;
  commit)
    [ "${#REVS[@]}" -eq 1 ] || die "--commit takes exactly one revision"
    SHA=$(git rev-parse --verify "${REVS[0]}") || die "bad revision: ${REVS[0]}"
    if is_merge "$SHA"; then
      DIFF_ARGS="${SHA}^1 ${SHA}"
      SCOPE_LABEL="merge commit $(git rev-parse --short "$SHA") (vs first parent)"
    else
      DIFF_ARGS="${SHA}^ ${SHA}"
      SCOPE_LABEL="commit $(git rev-parse --short "$SHA") only"
    fi
    REF_SHA=$(git rev-parse --short "$SHA")
    ;;
  pr)
    [ -n "$PR_NUM" ] || die "--pr requires a number"
    command -v gh >/dev/null 2>&1 || die "--pr requires the gh CLI"
    PR_JSON=$(gh pr view "$PR_NUM" --json baseRefOid,headRefOid,title 2>/dev/null) \
      || die "could not read PR #${PR_NUM} (is gh authenticated, and does the PR exist?)"
    BASE=$(printf '%s' "$PR_JSON" | sed -n 's/.*"baseRefOid":"\([0-9a-f]*\)".*/\1/p')
    HEAD=$(printf '%s' "$PR_JSON" | sed -n 's/.*"headRefOid":"\([0-9a-f]*\)".*/\1/p')
    [ -n "$BASE" ] && [ -n "$HEAD" ] || die "could not extract PR refs for #${PR_NUM}"
    git cat-file -e "${HEAD}^{commit}" 2>/dev/null \
      || die "PR head ${HEAD:0:8} is not in this clone — run: git fetch origin pull/${PR_NUM}/head"
    DIFF_ARGS="${BASE}..${HEAD}"
    SCOPE_LABEL="PR #${PR_NUM} (${BASE:0:8}..${HEAD:0:8})"
    REF_SHA="pr${PR_NUM}"
    ;;
  *)
    case "${#REVS[@]}" in
      0)
        if [ -n "$(git status --porcelain --untracked-files=no 2>/dev/null)" ]; then
          DIFF_ARGS="HEAD"
          SCOPE_LABEL="uncommitted changes (staged + unstaged) vs HEAD"
          REF_SHA="working"
        else
          DEF=$(default_branch)
          CUR=$(git rev-parse --abbrev-ref HEAD)
          MB=""
          [ -n "$DEF" ] && [ "$DEF" != "$CUR" ] && MB=$(git merge-base "$DEF" HEAD 2>/dev/null)
          if [ -n "$MB" ] && [ "$MB" != "$(git rev-parse HEAD)" ]; then
            DIFF_ARGS="${MB}..HEAD"
            SCOPE_LABEL="branch ${CUR} vs ${DEF} (merge-base ${MB:0:8}..HEAD)"
          else
            DIFF_ARGS="HEAD~1..HEAD"
            SCOPE_LABEL="last commit ($(git rev-parse --short HEAD))"
          fi
          REF_SHA=$(git rev-parse --short HEAD)
        fi
        ;;
      1)
        R="${REVS[0]}"
        if [[ "$R" == *".."* ]]; then
          DIFF_ARGS="$R"
          SCOPE_LABEL="range ${R}"
          REF_SHA=$(git rev-parse --short "${R##*..}" 2>/dev/null || echo "range")
        else
          SHA=$(git rev-parse --verify "$R")
          if is_merge "$SHA"; then
            DIFF_ARGS="${SHA}^1 ${SHA}"
            SCOPE_LABEL="merge commit $(git rev-parse --short "$SHA") (vs first parent)"
            REF_SHA=$(git rev-parse --short "$SHA")
          elif [ "$SHA" = "$(git rev-parse HEAD)" ]; then
            DIFF_ARGS="HEAD~1..HEAD"
            SCOPE_LABEL="last commit ($(git rev-parse --short HEAD))"
            REF_SHA=$(git rev-parse --short HEAD)
          else
            DIFF_ARGS="${SHA}..HEAD"
            SCOPE_LABEL="everything since $(git rev-parse --short "$SHA") (use --commit for that commit alone)"
            REF_SHA=$(git rev-parse --short HEAD)
          fi
        fi
        ;;
      2)
        A=$(git rev-parse --verify "${REVS[0]}") || die "bad revision: ${REVS[0]}"
        B=$(git rev-parse --verify "${REVS[1]}") || die "bad revision: ${REVS[1]}"
        DIFF_ARGS="${A}..${B}"
        SCOPE_LABEL="range $(git rev-parse --short "$A")..$(git rev-parse --short "$B")"
        REF_SHA=$(git rev-parse --short "$B")
        ;;
      *) die "too many revisions (got ${#REVS[@]}, expected at most 2)" ;;
    esac
    ;;
esac

PATHSPEC="${PATHS[*]:-}"
if [ -n "$PATHSPEC" ]; then
  SCOPE_LABEL="${SCOPE_LABEL}, limited to: ${PATHSPEC}"
fi

# shellcheck disable=SC2086
if [ -n "$PATHSPEC" ]; then
  STAT=$(git diff --numstat $DIFF_ARGS -- $PATHSPEC 2>/dev/null)
else
  STAT=$(git diff --numstat $DIFF_ARGS 2>/dev/null)
fi

CHANGED_FILES=$(printf '%s' "$STAT" | grep -c . || true)
CHANGED_LINES=$(printf '%s\n' "$STAT" | awk '{a+=$1; d+=$2} END {print (a+d)+0}')
OVERSIZED=false
[ "${CHANGED_LINES:-0}" -gt "$SIZE_GUARD" ] && OVERSIZED=true

# An empty diff is almost always a reversed range or an over-narrow pathspec.
if [ "${CHANGED_FILES:-0}" -eq 0 ]; then
  echo "resolve-scope: WARNING — this scope contains no changes." >&2
  echo "  Check for a reversed range (older..newer, not newer..older) or too narrow a pathspec." >&2
fi

cat << OUT
SCOPE_LABEL=${SCOPE_LABEL}
DIFF_ARGS=${DIFF_ARGS}
PATHSPEC=${PATHSPEC}
REF_SHA=${REF_SHA}
CHANGED_FILES=${CHANGED_FILES}
CHANGED_LINES=${CHANGED_LINES}
OVERSIZED=${OVERSIZED}
OUT
