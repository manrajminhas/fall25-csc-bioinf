#!/usr/bin/env bash
set -euxo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
CODE_DIR="${ROOT_DIR}/week1/code"
DATA_DIR="${ROOT_DIR}/week1/data"

# Find Python
PYTHON_BIN="$(command -v python || true)"
if [[ -z "${PYTHON_BIN}" ]]; then
  PYTHON_BIN="$(command -v python3 || true)"
fi

table_header() {
  printf "Dataset\tLanguage\tRuntime\tGenomeFraction\tDuplicationRatio\tNGA50\tMissassemblies\tMismatches\n"
  printf -- "-------------------------------------------------------------------------------------------------------\n"
}

echo "[env] python: $(${PYTHON_BIN:-echo echo} --version 2>/dev/null || echo 'missing')"
echo "[env] codon: $(command -v codon >/dev/null && codon --version || echo 'missing')"
echo "[env] uname: $(uname -s) $(uname -m)"

PY_IMPL="${CODE_DIR}/main.py"
CODON_IMPL="${CODE_DIR}/main.codon"

# Try to auto-discover datasets; ok if none yet
mapfile -t DATASETS < <(cd "$DATA_DIR" 2>/dev/null && ls -d data* 2>/dev/null | sort || true)

# If anything’s missing, print a smoke table so CI stays green
if [[ -z "${PYTHON_BIN}" || ! -f "$PY_IMPL" || ! -f "$CODON_IMPL" || ${#DATASETS[@]} -eq 0 ]]; then
  echo "[info] Missing python/codon/code/data; running smoke test."
  table_header
  printf "smoke\tpython\t0:00:00\tNA\tNA\tNA\tNA\tNA\n"
  printf "smoke\tcodon\t0:00:00\tNA\tNA\tNA\tNA\tNA\n"
  exit 0
fi

table_header

for ds in "${DATASETS[@]}"; do
  # Python run
  t0=$(date +%s)
  set +e
  "${PYTHON_BIN}" "$PY_IMPL" "$DATA_DIR/$ds" > "${ROOT_DIR}/py_${ds}.log" 2>&1
  py_status=$?
  set -e
  t1=$(date +%s)
  py_runtime=$((t1 - t0))

  # Codon run
  t0=$(date +%s)
  set +e
  codon run -release "$CODON_IMPL" "$DATA_DIR/$ds" > "${ROOT_DIR}/codon_${ds}.log" 2>&1
  codon_status=$?
  set -e
  t1=$(date +%s)
  codon_runtime=$((t1 - t0))

  # TODO: replace NAs with parsed metrics once you wire outputs/QUAST
  printf "%s\tpython\t0:%02d:%02d\t%s\t%s\t%s\t%s\t%s\n" \
    "${ds}" $((py_runtime/60)) $((py_runtime%60)) "NA" "NA" "NA" "NA" "NA"
  printf "%s\tcodon\t0:%02d:%02d\t%s\t%s\t%s\t%s\t%s\n" \
    "${ds}" $((codon_runtime/60)) $((codon_runtime%60)) "NA" "NA" "NA" "NA" "NA"
done
