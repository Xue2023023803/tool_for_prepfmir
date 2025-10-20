#!/bin/bash
# HeuDiConv batch runner (sub-/ses- prefixed DICOM tree) — zero‑touch runnable
# Input DICOMs assumed at: ./dataset/sub-XX/ses-YY/**.dcm
# Output BIDS will be written to: ./BIDS_number/
# Logs: ./heudiconv_logs/

set -euo pipefail

# -------- range settings (edit if needed) --------
start_subject_id=1
end_subject_id=10
start_session_id=1
end_session_id=3
# -------------------------------------------------

LOG_DIR="${PWD}/heudiconv_logs"
mkdir -p "${LOG_DIR}"

for sid in $(seq "${start_subject_id}" "${end_subject_id}"); do
  subject_label=$(printf "%02d" "${sid}")
  LOG_FILE="${LOG_DIR}/sub-${subject_label}.log"
  echo "==== Processing sub-${subject_label} ====" | tee -a "${LOG_FILE}"

  for ses in $(seq "${start_session_id}" "${end_session_id}"); do
    session_label=$(printf "%02d" "${ses}")
    echo "-- ses-${session_label} --" | tee -a "${LOG_FILE}"

    # NOTE: -s/-ss are numeric labels (01, 02, ...). The 'sub-'/'ses-' prefixes are added only in the -d pattern.
    docker run --rm -it \
      -v "${PWD}:/base" \
      nipy/heudiconv:latest \
      -d /base/dataset/sub-{subject}/ses-{session}/*/*.dcm \
      -o /base/BIDS_number/ \
      -f /base/heuristic_final.py \
      -s "${subject_label}" \
      -ss "${session_label}" \
      -c dcm2niix \
      -b --minmeta \
      --overwrite 2>&1 | tee -a "${LOG_FILE}"

    status=${PIPESTATUS[0]}
    if [ "${status}" -ne 0 ]; then
      echo "!! FAILED: sub-${subject_label} ses-${session_label}" | tee -a "${LOG_FILE}"
    else
      echo "OK: sub-${subject_label} ses-${session_label}" | tee -a "${LOG_FILE}"
    fi
    echo "" | tee -a "${LOG_FILE}"
  done
done

echo "All done. BIDS dataset at ./BIDS_number/"
