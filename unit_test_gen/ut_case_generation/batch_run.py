#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

# 1. 配置：把 A_DIR 换成你的实际目录
A_DIR = Path(__file__).resolve().parent.parent.parent / "java_project" / "src" / "main" / "java" / "org" / "example"    

# 2. 获取所有 .java 文件名（纯文件名，按字典序）
java_files = sorted(f.stem for f in A_DIR.glob("*.java"))
if not java_files:
    print("A 目录下未找到任何 .java 文件！")
    exit(0)

# 3. 逐个执行
for file_name in java_files:
    if file_name == "DataCleaner":
        continue
    cmd = [
        "python", "-m",
        "unit_test_gen.ut_case_generation.test_gen",
        "--ablation",
        "--case_gen",
        "--file_name", file_name
    ]
    print(f"\n==== 正在处理：{file_name} ====")
    print("执行命令：", " ".join(cmd))
    subprocess.run(cmd, check=False)   # check=False 允许单条失败继续下一条
