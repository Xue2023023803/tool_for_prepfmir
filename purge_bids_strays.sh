#!/usr/bin/env bash
# 强力清理 BIDS 根目录下的“野文件”
# 用法：bash purge_bids_strays.sh /path/to/BIDS_root

set -euo pipefail

ROOT="${1:-}"
if [[ -z "${ROOT}" ]]; then
  echo "用法：bash $(basename "$0") /path/to/BIDS_root" >&2
  exit 1
fi
if [[ ! -d "${ROOT}" ]]; then
  echo "错误：目录不存在：${ROOT}" >&2
  exit 2
fi
# 简单校验：必须是 BIDS 根目录（含 dataset_description.json）
if [[ ! -f "${ROOT}/dataset_description.json" ]]; then
  echo "错误：这里看起来不是 BIDS 根目录（缺 dataset_description.json）：" >&2
  echo "      ${ROOT}" >&2
  exit 3
fi

echo "[INFO] BIDS 根目录：${ROOT}"
echo "[INFO] 开始删除会影响 BIDS 验证的野文件 ..."

# 1) heudiconv 残留（当前你的错误就是这个）
find "${ROOT}" -type f -name '*_heudiconv*.json' -print -delete

# 2) 常见系统/编辑器垃圾
find "${ROOT}" -type f \( \
  -name '.DS_Store' -o \
  -name 'Thumbs.db' -o \
  -name 'desktop.ini' -o \
  -name 'Icon?' -o \
  -name '._*' -o \
  -name '*~' -o \
  -name '*.tmp' -o \
  -name '*.bak' -o \
  -name '*.swp' -o \
  -name '*.swo' \
\) -print -delete

# 3) 清空可能的空文件夹（不影响 BIDS 结构）
find "${ROOT}" -type d -empty -print -delete

echo "[DONE] 清理完成。建议立刻验证："
echo "docker run --rm -v \"${ROOT}\":/data:ro bids/validator /data"

