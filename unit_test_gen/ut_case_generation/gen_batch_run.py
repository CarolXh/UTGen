#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path
import time

# 1. 配置：把 A_DIR 换成你的实际目录
SRC_DIR = Path(__file__).resolve().parent.parent.parent / "java_project" / "src" / "main" / "java" / "gov" / "nasa" / "alsUtility"    
JAVA_TEST_DIR= (Path(__file__).resolve().parent.parent.parent / "java_project" / "src" / "test" / "java" / "gov" / "nasa")
# 2. 获取所有 .java 文件名（纯文件名，按字典序）
java_files = sorted(f.stem for f in SRC_DIR.glob("*.java"))
if not java_files:
    print("SRC_DIR 目录下未找到任何 .java 文件！")
    exit(0)

print(f'java_files: {java_files}')


# 3. 逐个执行
for file_name in java_files:
    # if file_name != "minDistanceCal":
    #     continue
    start_time = time.time()
    # 备份并删除java_test_dir目录下的所有文件
    for f in JAVA_TEST_DIR.iterdir():
        if f.name.endswith("Test.java"):
            os.rename(f, f.with_suffix(".bak"))
    
    print(f'file_name: {file_name}')

    # 如果出错，把file_name保存到log
    try:
        cmd = [
            "python", "-m",
            "unit_test_gen.ut_case_generation.test_gen",
            "--case_gen",
            "--file_name", file_name
        ]
        print(f"\n==== 正在处理：{file_name} ====")
        print("执行命令：", " ".join(cmd))
        subprocess.run(cmd, check=False)   # check=False 允许单条失败继续下一条
        end_time = time.time()
        print(f"处理 {file_name} 耗时: {end_time - start_time:.2f} 秒")

    except:
        with open(Path(__file__).resolve().parent / "gen_batch_log.txt", "a") as f:
            f.write(file_name + "\n")
        continue
    
