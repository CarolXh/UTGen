from unit_test_gen.ut_case_generation.auto_gen_single import UnitTestGenerator
from pathlib import Path
import argparse
    # def __init__(self, 
    #              model = "kimi-latest",
    #              java_repo_root: Path = None,
    #              java_code_dir: Path = None,
    #              boundary_dir : Path = None,
    #              mock_dir: Path = None,
    #              java_test_dir: Path = None,
    #              log_info_dir: Path = None,
    #              error_info_dir : Path = None,
    #              fix_info_dir: Path = None,
    #              maven_bin : Path = Path(r"D:\apache-maven-3.9.11\bin")):

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Unit Test Case Generation")
    argparser.add_argument("--model", type=str, default="kimi-latest", help="使用的模型名称")
    argparser.add_argument("--java_repo_root", type=Path, default=Path(__file__).resolve().parent.parent.parent / "java_project", help="Java项目根目录")
    argparser.add_argument("--java_code_dir", type=Path, default=Path(__file__).resolve().parent.parent.parent / "java_project" / "src" / "main" / "java"/ "org" / "example" , help="待测试的Java main代码目录")
    argparser.add_argument("--java_test_dir", type=Path, default=Path(__file__).resolve().parent.parent.parent / "java_project" / "src" / "test" / "java"/ "org" / "example" , help="待测试的Java test代码目录")
    argparser.add_argument("--log_dir", type=Path, default=Path(__file__).resolve().parent / "log", help="日志目录")
    argparser.add_argument("--boundary_dir", type=Path, default=Path(__file__).resolve().parent.parent / "data_preparation" / "reverse_data", help="边界值和mock链目录")
    argparser.add_argument("--file_name", type=str, default="DataCleaner", help="Java文件名,不带后缀")
    argparser.add_argument("--maven_bin", type=Path, default=Path(r"D:\apache-maven-3.9.11\bin"), help="maven bin目录")
    argparser.add_argument("--max_retry", type=int, default=3, help="最大重试次数")
    argparser.add_argument("--ablation",action="store_true",help="是否启用消融实验") 
    argparser.add_argument("--case_gen",action="store_true",help="是否启用用例生成")

    args = argparser.parse_args()

    ut = UnitTestGenerator(
        java_repo_root=args.java_repo_root,
        java_code_dir=args.java_code_dir / f"{args.file_name}.java",
        java_test_dir=args.java_test_dir / f"{args.file_name}Test.java",
        boundary_dir=args.boundary_dir / f"{args.file_name}_bound.txt",
        mock_dir=args.boundary_dir / f"{args.file_name}_mock.txt",
        log_info_dir=args.log_dir,
        maven_bin=args.maven_bin,
        max_retry=args.max_retry,
        file_name=args.file_name,
        ablation=args.ablation,
        case_gen=args.case_gen
    )
    ut.begin_gen_single_file()
    if args.ablation:
        ut.begin_ablation()



