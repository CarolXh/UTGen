#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
import re
SRC_DIR = Path(__file__).resolve().parent / 'log' / 'result'
DST_DIR = Path(__file__).resolve().parent.parent.parent / 'java_project' / 'src' / 'test' / 'java' / 'org' / 'example'      # 目标目录


# 确保目标目录存在
DST_DIR.mkdir(parents=True, exist_ok=True)

# # 递归遍历源目录
# # [abs, boundary, mcdc, mock , ref]
# for src_path in SRC_DIR.rglob('*Test_result.java'):
#     # 构造目标文件名
    
#     new_name = src_path.stem.replace('Test_result', '') + 'Test.java'
#     print(new_name)

#     dst_path = DST_DIR / new_name

#     # 复制并覆盖
#     shutil.copy2(src_path, dst_path)
#     # print(f'{src_path}  ->  {dst_path}')

# print('全部处理完成。')

pattern = re.compile(r'(?<!_)Test_result\.java$', re.IGNORECASE)

for src_path in SRC_DIR.rglob('*.java'):
    if pattern.search(src_path.name):
        new_name = src_path.name[:-len('Test_result.java')] + 'Test.java'
        dst_path = DST_DIR / new_name
        shutil.copy2(src_path, dst_path)
        print(f'{src_path}  ->  {dst_path}')

print('全部处理完成。')
