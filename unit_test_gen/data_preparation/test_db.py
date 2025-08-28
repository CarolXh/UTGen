from unit_test_gen.data_preparation.db_construct import DataBaseConstructor
from unit_test_gen.data_preparation.file_generator import FileGenerator
from pathlib import Path
import argparse

# 允许传参
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="构建向量数据库")
    parser.add_argument("--src_proj_dir", type=str, default=None, help="待测项目根目录（不包含test目录）")
    
    args = parser.parse_args()
    if not args.src_proj_dir:
        args.src_proj_dir = Path(__file__).resolve().parent.parent.parent / "java_project" / "src" / "main" / "java" / "gov" / "nasa" / "alsUtility"

    fg = FileGenerator(src_proj_dir=args.src_proj_dir)
    fg.begin_file_gen()
    db = DataBaseConstructor()
    db.construct_faiss()