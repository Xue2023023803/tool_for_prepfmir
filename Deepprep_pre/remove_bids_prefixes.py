#!/usr/bin/env python3
"""
BIDS数据集目录结构简化工具

功能：移除BIDS格式中的'sub-'和'ses-'前缀，将目录结构从'sub-XX/ses-YY'简化为'XX/YY'
使用示例：
    # 查看计划（干运行模式）
    python script.py --root /path/to/dataset
    
    # 实际执行重命名
    python script.py --root /path/to/dataset --commit
"""

import argparse
from pathlib import Path

def z2(s: str) -> str:
    """将数字字符串填充前导零至2位"""
    return s.zfill(2)

def list_dirs_matching(path: Path, pattern):
    """列出路径下所有匹配模式的目录"""
    return [p for p in path.iterdir() if p.is_dir() and pattern.match(p.name)]

def gather_subject_ids(root: Path):
    """收集所有受试者ID"""
    ids = set()
    # 匹配 sub-XX 格式的目录
    sub_re = re.compile(r"^sub-(\d+)$")
    for p in root.iterdir():
        if not p.is_dir():
            continue
        m = sub_re.match(p.name)
        if m:
            ids.add(z2(m.group(1)))
        # 同时也考虑纯数字目录
        if p.name.isdigit():
            ids.add(z2(p.name))
    return sorted(ids, key=lambda x: int(x))

def plan_sessions_for_subject(root: Path, sid: str):
    """为指定受试者ID规划移除'ses-'前缀的操作
       考虑两种可能的父目录：'sub-XX' 和 'XX'
    """
    ops = []
    sub_parent = root / f"sub-{z2(sid)}"
    num_parent = root / z2(sid)
    parents = []
    if sub_parent.exists():
        parents.append(sub_parent)
    if num_parent.exists():
        parents.append(num_parent)

    seen = set()
    for parent in parents:
        for sdir in list_dirs_matching(parent, SES_RE):
            m = SES_RE.match(sdir.name)
            ses_num = z2(m.group(1))
            if (parent, ses_num) in seen:
                continue
            seen.add((parent, ses_num))
            # 目标路径应该在数字父目录下
            dst_parent = num_parent if num_parent.exists() else parent
            dst = dst_parent / ses_num
            if sdir != dst:
                ops.append(("SES-", sdir, dst))
    return ops

def main():
    ap = argparse.ArgumentParser(description="移除sub-/ses-前缀 (sub-XX/ses-YY -> XX/YY)")
    ap.add_argument("--root", type=Path, default=Path("./dataset"), help="数据集根目录路径（包含受试者文件夹）")
    ap.add_argument("--commit", action="store_true", help="实际执行重命名（默认：干运行模式）")
    args = ap.parse_args()

    root = args.root.resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"[错误] 根目录未找到或不是目录: {root}")

    print(f"[根目录] {root}")

    # 规划操作
    sub_ops = plan_subjects(root)
    ses_ops = []
    for sid in gather_subject_ids(root):
        ses_ops.extend(plan_sessions_for_subject(root, sid))

    if not sub_ops and not ses_ops:
        print("[信息] 无需执行任何操作。")
        return

    print("[计划]")
    for tag, src, dst in sub_ops + ses_ops:
        print(f"  [{tag}] {src} -> {dst}")

    if not args.commit:
        print("[干运行] 未进行任何更改。使用 --commit 参数重新运行以应用更改。")
        return

    # 执行：先处理受试者
    for _, src, dst in sub_ops:
        if dst.exists():
            print(f"[跳过] 受试者目标目录已存在: {dst}")
            continue
        print(f"[受试者] {src} -> {dst}")
        src.rename(dst)

    # 执行：受试者移动后重新计算会话操作
    for sid in gather_subject_ids(root):
        ops = plan_sessions_for_subject(root, sid)
        for _, src, dst in ops:
            if dst.exists():
                print(f"[跳过] 会话目标目录已存在: {dst}")
                continue
            print(f"[会话] {src} -> {dst}")
            dst.parent.mkdir(parents=True, exist_ok=True)
            src.rename(dst)

    print("[完成]")

if __name__ == "__main__":
    main()
