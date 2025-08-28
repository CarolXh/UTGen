#!/usr/bin/env python3
import os, re
from pathlib import Path
from typing import List

def to_path(cls: str, src_root: Path) -> Path:
    return src_root / f"{cls.replace('.', '/')}.java"

def direct_deps(file: Path, src_root: Path) -> List[Path]:
    IMP_RE = re.compile(r'^\s*import\s+(?:static\s+)?([a-zA-Z0-9_.*]+)\s*;', re.M)
    if not file.exists():
        return []
    text = file.read_text(encoding='utf-8', errors='ignore')
    deps = set()
    for m in IMP_RE.finditer(text):
        imp = m.group(1)
        if imp.endswith('.*') or imp.startswith(('java.', 'javax.')):
            continue
        dep = to_path(imp, src_root).resolve()
        if dep.exists():
            deps.add(dep)
    return sorted(deps)

def calc_structure(entry_file: Path, src_root_dir: Path) -> str:
    """
    返回以 entry_file 所在包为根、只包含直接依赖的纯文本树。
    所有路径都使用相对 src_root_dir 的 POSIX 形式，避免跨盘符问题。
    """
    entry_file = entry_file.resolve()
    src_root_dir = src_root_dir.resolve()

    # 计算相对根：包目录
    pkg_dir = entry_file.parent
    deps = direct_deps(entry_file, src_root_dir)

    # 把入口文件本身也加进来
    files = sorted({entry_file} | set(deps), key=lambda p: (p.parent, p.name))

    # 统一用 src_root_dir 为基准算相对路径，永远不会抛异常
    root_rel = os.path.relpath(pkg_dir, src_root_dir).replace(os.sep, '/')
    lines = [root_rel]

    for f in files:
        depth = len(f.parent.relative_to(pkg_dir).parts) if f.parent != pkg_dir else 0
        indent = '└──' * (depth + 1) + ' '
        file_rel = os.path.relpath(f, src_root_dir).replace(os.sep, '/')
        lines.append(indent + file_rel)

    tree = '\n'.join(lines) + '\n'
    print(tree)
    return tree
