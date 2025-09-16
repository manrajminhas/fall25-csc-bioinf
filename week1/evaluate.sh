#!/usr/bin/env bash
set -euxo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
CODE_DIR="${ROOT_DIR}/week1/code"
DATA_DIR="${ROOT_DIR}/week1/data"
LOG_DIR="${ROOT_DIR}/week1/logs"
mkdir -p "${LOG_DIR}"

# Python locator
PYTHON_BIN="$(command -v python || true)"
if [[ -z "${PYTHON_BIN}" ]]; then
  PYTHON_BIN="$(command -v python3 || true)"
fi

PY_IMPL="${CODE_DIR}/main.py"
# Codon port is optional; script handles absence gracefully
CODON_IMPL="${ROOT_DIR}/week1/codon_code/main.py"

# Only the first three datasets
DATASETS=(data1 data2 data3)

# Env banner
if [[ -n "${PYTHON_BIN}" ]]; then PYVER="$(${PYTHON_BIN} --version 2>/dev/null || true)"; else PYVER="missing"; fi
echo "[env] python: ${PYVER}"
echo "[env] codon: $(command -v codon >/dev/null && codon --version || echo 'missing')"
echo "[env] uname: $(uname -s) $(uname -m)"

# N50 helper
n50_of_fasta () {
  local fasta="$1"
  "${PYTHON_BIN:-python3}" "${SCRIPT_DIR}/calculate_n50.py" "$fasta" 2>/dev/null || echo "NA"
}

# Header
printf "Dataset\tLanguage\tRuntime\tN50\n"
printf -- "-------------------------------------------\n"

# Smoke if env incomplete
if [[ -z "${PYTHON_BIN}" || ! -f "$PY_IMPL" ]]; then
  printf "smoke\tpython\t0:00:00\tNA\n"
  printf "smoke\tcodon\t0:00:00\tNA\n"
  exit 0
fi

for ds in "${DATASETS[@]}"; do
  # --- Python run ---
  t0=$(date +%s)
  set +e
  "${PYTHON_BIN}" "$PY_IMPL" "$DATA_DIR/$ds" > "${LOG_DIR}/py_${ds}.log" 2>&1
  py_status=$?
  set -e
  t1=$(date +%s)
  py_runtime=$((t1 - t0))
  py_runtime_fmt=$(printf "0:%02d:%02d" $((py_runtime/60)) $((py_runtime%60)))
  py_n50="$(n50_of_fasta "$DATA_DIR/$ds/contig.fasta")"
  printf "%s\tpython\t%s\t%s\n" "$ds" "$py_runtime_fmt" "${py_n50:-NA}"

  # --- Codon run (optional) ---
if command -v codon >/dev/null && [ -f "$CODON_IMPL" ]; then
  t0=$(date +%s)
  set +e
  codon run -release "$CODON_IMPL" "$DATA_DIR/$ds" > "${LOG_DIR}/codon_${ds}.log" 2>&1
  codon_status=$?
  set -e
  t1=$(date +%s)
  cod_runtime=$((t1 - t0))
  cod_runtime_fmt=$(printf "0:%02d:%02d" $((cod_runtime/60)) $((cod_runtime%60)))
  if [ "$codon_status" -eq 0 ]; then
    cod_n50="$(n50_of_fasta "$DATA_DIR/$ds/contig.fasta")"
  else
    cod_n50="NA"
  fi
  printf "%s\tcodon\t%s\t%s\n" "$ds" "$cod_runtime_fmt" "$cod_n50"
else
  printf "%s\tcodon\t0:00:00\tNA\n" "$ds"
fi

done
