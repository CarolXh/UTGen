import csv
from pathlib import Path
import shutil
import subprocess
import time
from openai import OpenAI
from dotenv import load_dotenv
import os

import yaml
from unit_test_gen.data_preparation.db_construct import DataBaseConstructor
from unit_test_gen.prompt_management import save_prompt
from unit_test_gen.data_preparation.mcdc_case_gen import solve_mcdc
load_dotenv()

class UnitTestGenerator:
    def __init__(self, 
                 model = "kimi-latest",
                 java_repo_root: Path = None,
                 file_name: str = None,
                 java_code_dir: Path = None,
                 boundary_dir : Path = None,
                 mock_dir: Path = None,
                 java_test_dir: Path = None,
                 log_info_dir: Path = None,
                 maven_bin : Path = Path(r"D:\apache-maven-3.9.11\bin"),
                 max_retry: int = 3,
                 ablation: bool = False,
                 case_gen: bool = True,

                 ):
        self.repo_root = java_repo_root 
        self.java_code_dir = java_code_dir
        self.boundary_dir = boundary_dir
        self.mock_dir = mock_dir
        self.java_test_dir = java_test_dir
        self.log_info_dir = log_info_dir
        self.error_info_dir = log_info_dir / "error"
        self.fix_info_dir = log_info_dir / "fix"
        self.ablation_dir = log_info_dir / "ablation"
        self.case_gen_enable = case_gen
        os.makedirs(self.fix_info_dir, exist_ok=True)
        os.makedirs(self.log_info_dir, exist_ok=True)
        os.makedirs(self.error_info_dir, exist_ok=True)
        os.makedirs(self.ablation_dir, exist_ok=True)

        self.maven_bin = maven_bin
        self.max_retry = max_retry
        self.file_name = file_name
        self.model = model
        self.client = OpenAI(
            api_key=os.getenv("MOONSHOT_API_KEY"),
            base_url="https://api.moonshot.cn/v1"
        )
        self.ablation = ablation
        if self.ablation:
            print("启用消融实验...")
        with open(Path(__file__).resolve().parent.parent / "prompt_template.yaml", "r", encoding="utf-8") as f:
            self.prompt_template = yaml.safe_load(f)

        
    def begin_gen_single_file(self):
        """开始生成单个文件的测试用例"""
        print(f"开始生成单个文件的测试用例...")
        print(f"用例生成启用状态: {self.case_gen_enable}")

        if self.case_gen_enable == True:
            self.case_gen()
        else:
            print("用例生成已禁用，跳过用例生成...")

        max_retries = self.max_retry
        round = 1
        # 将待测试的单个文件单独放到java_test_dir目录下
        shutil.copy(self.ablation_dir / f'{self.file_name}_all_Test.java', self.java_test_dir / f"{self.file_name}Test.java")
        while round <= max_retries:
            print(f"测试用例生成完毕，开始运行第{round}次测试...")
            no_error_flag = self.run_test()
            if no_error_flag:
                break
            print("测试运行完毕，开始修复错误...")
            if self.error_fix(round = round, file_name=f'{self.file_name}_all_Test'):
                break
            round += 1
        os.makedirs(self.log_info_dir / "result", exist_ok=True)
        with open(self.log_info_dir / "result" / f"{self.file_name}_all_Test_result.java", "w", encoding="utf-8") as f:

            with open(self.java_test_dir / f"{self.file_name}Test.java", "r", encoding="utf-8") as f2:
                f.write(f2.read())
        print("错误修复完毕，保存提示词版本信息...")
        save_prompt()

    def begin_ablation(self):
        """开始消融实验"""
        # 将ablation_dir中的文件依次替换java_test_dir中的文件
        for ablation_file in self.ablation_dir.iterdir():
            # 跳过文件名开头不是self.file_name的文件
            if not ablation_file.name.startswith(self.file_name):
                continue
            print(f"开始消融实验，当前文件: {ablation_file}")
            if ablation_file.name == f"{self.file_name}_all_Test.java":
                print("跳过原始文件...")
                continue
            with open(ablation_file, "r", encoding="utf-8") as f:
                code = f.read()
            with open(self.java_test_dir / f"{self.file_name}Test.java", "w", encoding="utf-8") as f:
                f.write(code)
            round = 1
            while round <= self.max_retry:
                no_error_flag = self.run_test()
                if no_error_flag:
                    break
                print("测试运行完毕，开始修复错误...")
                if self.error_fix(round = round, file_name=ablation_file.stem):
                    break
                round += 1
            # 保存实验结果
            os.makedirs(self.log_info_dir / "result", exist_ok=True)
            with open(self.log_info_dir / "result" / f"{ablation_file.stem}_result.java", "w", encoding="utf-8") as f:

                f.write(code)


    def send_request(self, prompt: str) -> str:
        """调用聊天接口"""
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user",   "content": prompt}
            ],
            temperature=0.9,
            max_tokens=8192
        )
        return resp.choices[0].message.content.strip()
    
    def case_gen(self):
        print("读取配置信息中...")

        with open(self.java_code_dir, "r", encoding="utf-8") as f:
            code = f.read()
        abs = self.send_request(prompt=self.prompt_template["CODE_ABS"].format(code=code))
        ref = DataBaseConstructor().search_index(query=abs)
        with open(self.boundary_dir, "r", encoding="utf-8") as f:
            boundary = f.read()
        with open(self.mock_dir, "r", encoding="utf-8") as f:
            mock_cond = f.read()
        mcdc_constraints = solve_mcdc(self.java_code_dir)
        print("正在生成测试用例...")
        cases_path = []
        resp = self.send_request(prompt=self.prompt_template['SYS_PROMPT'] + self.prompt_template['UT_GEN'].format(code=code, abs=abs, mock_cond=mock_cond, boundary=boundary, ref=ref, mcdc=mcdc_constraints))
        # 将 '''java... ''' 中的内容保存到文件
        with open(self.ablation_dir / f"{self.file_name}_all_Test.java", "w", encoding="utf-8") as f:
            f.write(resp.split("```java")[1].split("```")[0])
        cases_path.append(self.ablation_dir / f"{self.file_name}_all_Test.java")
        if self.ablation:
            print("单变量消融实验开始...")
            # 消融abs
            out_path = self.ablation_dir / f"{self.file_name}_abs_Test.java"
            resp = self.send_request(prompt=self.prompt_template['SYS_PROMPT'] + self.prompt_template['UT_GEN_NO_ABS'].format(code=code, mock_cond=mock_cond, boundary=boundary, ref=ref, mcdc=mcdc_constraints))
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(resp.split("```java")[1].split("```")[0])
                print(f"已保存消融abs的测试用例到 {out_path}")
            cases_path.append(out_path)
            # 消融mock_cond
            out_path = self.ablation_dir / f"{self.file_name}_mock_Test.java"
            resp = self.send_request(prompt=self.prompt_template['SYS_PROMPT'] + self.prompt_template['UT_GEN_NO_MOCK'].format(code=code, abs=abs, boundary=boundary, ref=ref, mcdc=mcdc_constraints))
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(resp.split("```java")[1].split("```")[0])
                print(f"已保存消融mock_cond的测试用例到 {out_path}")
            cases_path.append(out_path)

            # 消融boundary
            out_path = self.ablation_dir / f"{self.file_name}_boundary_Test.java"

            resp = self.send_request(prompt=self.prompt_template['SYS_PROMPT'] + self.prompt_template['UT_GEN_NO_BOUNDARY'].format(code=code, abs=abs, mock_cond=mock_cond, ref=ref, mcdc=mcdc_constraints))
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(resp.split("```java")[1].split("```")[0])
                print(f"已保存消融boundary的测试用例到 {out_path}")
            cases_path.append(out_path)
            # 消融mcdc
            out_path = self.ablation_dir / f"{self.file_name}_mcdc_Test.java"

            resp = self.send_request(prompt=self.prompt_template['SYS_PROMPT'] + self.prompt_template['UT_GEN_NO_MCDC'].format(code=code, abs=abs, mock_cond=mock_cond, boundary=boundary, ref=ref))
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(resp.split("```java")[1].split("```")[0])
                print(f"已保存消融mcdc的测试用例到 {out_path}")
            cases_path.append(out_path)
            # 消融ref
            out_path = self.ablation_dir / f"{self.file_name}_ref_Test.java"
            resp = self.send_request(prompt=self.prompt_template['SYS_PROMPT'] + self.prompt_template['UT_GEN_NO_REF'].format(code=code, abs=abs, mock_cond=mock_cond, boundary=boundary, mcdc=mcdc_constraints))
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(resp.split("```java")[1].split("```")[0])
                print(f"已保存消融ref的测试用例到 {out_path}")
            cases_path.append(out_path)
        print("测试用例生成完毕，已保存到", self.ablation_dir)
        return cases_path

    def run_test(self) -> bool:


        print(f'repo_root: {self.repo_root}')
        print(f'log_file: {self.log_info_dir}')
        print(f'error_file: {self.error_info_dir}')
        print(f'maven_bin: {self.maven_bin}')

        
        cmd = [str(self.maven_bin / "mvn.cmd"), "-Dfile.encoding=UTF-8", "test","-DtrimStackTrace=false"]
        print(">>> 执行:", " ".join(cmd))
        
        with (self.log_info_dir / f"{self.file_name}.log").open("w", encoding="utf-8") as f:
            proc = subprocess.run(cmd, cwd=self.repo_root, stdout=f, stderr=subprocess.STDOUT, text=True, encoding="utf-8")

        with (self.error_info_dir / f"{self.file_name}.err").open("w", encoding="utf-8") as f:
            f.write("错误信息提取中 " + str(self.error_info_dir) + "\n")
            # with open(self.log_info_dir / f"{self.file_name}.log", "r", encoding="utf-8") as logf:
            with open(self.log_info_dir / f"{self.file_name}.log", "r", encoding="gbk", errors="ignore") as logf:
                log_content = logf.read()
                if '[ERROR]' not in log_content:
                    print(">>> 控制台输出已保存到", self.log_info_dir)
                    print(">>> 测试通过，未发现错误信息")
                    print(">>> Maven exit code:", proc.returncode)
                    return True
                # 提取所有[ERROR]信息
                errors = log_content.split('[ERROR]')[1:]
                f.write("[ERROR]".join(errors))
        print(">>> 控制台输出已保存到", self.log_info_dir)
        print(">>> 错误信息已保存到", self.error_info_dir)
        print(">>> Maven exit code:", proc.returncode)
        return False


        

        # 立即生成 JaCoCo 报告（XML+CSV）
        # report_cmd = [str(self.maven_bin / "mvn.cmd"),
        #             "-Dfile.encoding=UTF-8",
        #             "jacoco:report"]
        # print(">>> 生成覆盖率报告:", " ".join(report_cmd))
        # with (self.log_info_dir / f"{file_name}_coverage.log").open("a", encoding="utf-8") as f:
        #     f.write("覆盖率报告生成中 " + str(self.log_info_dir) + "\n")

        #     subprocess.run(report_cmd,
        #                 cwd=self.repo_root,
        #                 stdout=f,
        #                 stderr=subprocess.STDOUT,
        #                 text=True,
        #                 encoding="utf-8")

        # # 提取 CSV 中的行/分支覆盖率
        # csv_path = Path(self.repo_root) / "target" / "site" / "jacoco" / "jacoco.csv"
        # total_lines_covered = 0
        # total_lines_total = 0
        # total_branches_covered = 0
        # total_branches_total = 0

        # if csv_path.exists():
        #     with csv_path.open(newline='', encoding='utf-8') as f:
        #         reader = csv.DictReader(f)
        #         for row in reader:
        #             total_lines_covered += int(row['LINE_COVERED'] or 0)
        #             total_lines_total   += int(row['LINE_MISSED'] or 0) + int(row['LINE_COVERED'] or 0)
        #             total_branches_covered += int(row['BRANCH_COVERED'] or 0)
        #             total_branches_total   += int(row['BRANCH_MISSED'] or 0) + int(row['BRANCH_COVERED'] or 0)

        # line_coverage = total_lines_covered / total_lines_total if total_lines_total else 0.0
        # branch_coverage = total_branches_covered / total_branches_total if total_branches_total else 0.0

        # # 把结果写进独立文件
        # coverage_file = self.log_info_dir / f"{file_name}_coverage.json"
        # import json
        # with coverage_file.open("a", encoding="utf-8") as cf:
        #     json.dump({
        #         "line_coverage": round(line_coverage, 4),
        #         "branch_coverage": round(branch_coverage, 4),
        #         "line_covered": total_lines_covered,
        #         "line_total": total_lines_total,
        #         "branch_covered": total_branches_covered,
        #         "branch_total": total_branches_total
        #     }, cf, indent=2)

        # print(">>> 覆盖率统计已保存到", coverage_file)

        

    def error_fix(self, round: int, file_name: Path) -> bool:


        print("正在读取错误信息...")
        with open(self.java_code_dir, "r", encoding="utf-8") as f:
            code = f.read()
        
        error_info_path = self.error_info_dir / f"{self.file_name}.err"
        with open(error_info_path, "r", encoding="utf-8") as f:
            error_info = f.read()
        with open(self.java_test_dir / f"{self.file_name}Test.java", "r", encoding="utf-8") as f:
            test_code = f.read()
        resp = self.send_request(prompt=self.prompt_template["ERROR_FIX"].format(code=code, test_code=test_code, error_info=error_info))
        print("正在修复错误...")
        if "```java" not in resp:
            print("Error: 修复后的代码中不包含 ```java 标记，错误可能来自于源码。")
            return True
        # 将 '''java... ''' 中的内容保存到文件
        code = resp.split("```java")[1].split("```")[0]
        with open(self.java_test_dir / f"{self.file_name}Test.java", "w", encoding="utf-8") as f:
            f.write(code)
        with open(Path(self.fix_info_dir) / f"{file_name}_fix_{round}.log", "a", encoding="utf-8") as f:
            f.write(f'----------------\n文件: {self.file_name}修复信息:\n')
            f.write(f'修复时间: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}\n')
            f.write(resp.split("```java")[0])
            f.write(code)
        return False
        