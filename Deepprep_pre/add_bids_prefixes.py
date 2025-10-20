#!/usr/bin/env python3
"""
BIDS数据集目录结构转换工具

功能：将普通数字目录结构转换为BIDS格式，添加'sub-'和'ses-'前缀，将目录结构从'XX/YY'转换为'sub-XX/ses-YY'
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

def list_numeric_dirs(path: Path):
    """列出路径下所有数字名称的目录"""
    return [p for p in path.iterdir() if p.is_dir() and p.name.isdigit()]

def list_sub_dirs(path: Path):
    """列出路径下所有sub-XX格式的目录"""
    sub_re = re.compile(r"^sub-\d+$")
    return [p for p in path.iterdir() if p.is_dir() and sub_re.match(p.name)]

def plan_sessions_under(root: Path, sid: str):
    """为指定受试者ID规划添加'ses-'前缀的操作"""
    ops = []
    subxx = root / f"sub-{z2(sid)}"
    nump = root / z2(sid)
    parents = []
    if subxx.exists():
        parents.append(subxx)
    if nump.exists():
        parents.append(nump)

    seen = set()
    for parent in parents:
        for sesdir in list_numeric_dirs(parent):
            ses_id = z2(sesdir.name)
            if ses_id in seen:
                continue
            seen.add(ses_id)
            dst = subxx / f"ses-{ses_id}"
            if sesdir != dst:
                ops.append(("SES", sesdir, dst))
    return ops

def main():
    ap = argparse.ArgumentParser(description="重命名为BIDS格式的sub-XX/ses-YY目录结构")
    ap.add_argument("--root", type=Path, default=Path("./dataset"), help="数据集根目录路径（包含受试者文件夹）")
    ap.add_argument("--commit", action="store_true", help="实际执行重命名（默认：干运行模式）")
    args = ap.parse_args()

    root = args.root.resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"[错误] 根目录未找到或不是目录: {root}")

    print(f"[根目录] {root}")

    # 第一遍：处理受试者
    sub_ops = plan_subjects(root)
    # 构建受试者ID集合（根目录中的数字名称和映射的sub-XX）
    subj_ids = set([p.name for p in list_numeric_dirs(root)] + [p.name.replace("sub-", "") for p in list_sub_dirs(root)])

    # 第二遍：处理会话（在受试者处理后计算，但现在只做计划；提交时会重新扫描）
    ses_ops = []
    for sid in sorted(subj_ids, key=lambda x: int(x)):
        ses_ops.extend(plan_sessions_under(root, sid))

    # 打印计划
    if not sub_ops and not ses_ops:
        print("[信息] 无需执行任何操作。")
        return

    print("[计划]")
    for tag, src, dst in sub_ops + ses_ops:
        print(f"  [{tag}] {src} -> {dst}")

    if not args.commit:
        print("[干运行] 未进行任何更改。使用 --commit 参数重新运行以应用更改。")
        return

    # 执行：第一遍处理受试者
    for _, src, dst in sub_ops:
        if dst.exists():
            print(f"[跳过] 受试者目标目录已存在: {dst}")
            continue
        print(f"[受试者] {src} -> {dst}")
        src.rename(dst)

    # 执行：受试者移动后重新计算会话操作
    # 再次查找所有受试者数字ID（如果目标已存在，某些数字目录可能保留）
    subj_ids = set([p.name for p in list_numeric_dirs(root)] + [p.name.replace("sub-", "") for p in list_sub_dirs(root)])
    for sid in sorted(subj_ids, key=lambda x: int(x)):
        ops = plan_sessions_under(root, sid)
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
