from pathlib import Path
import subprocess
import time
from openai import OpenAI
from dotenv import load_dotenv
import os

import yaml
from unit_test_gen.data_preparation.db_construct import DataBaseConstructor
from unit_test_gen.prompt_management import save_prompt
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
                 error_info_dir : Path = None,
                 fix_info_dir: Path = None,
                 maven_bin : Path = Path(r"D:\apache-maven-3.9.11\bin"),
                 max_retry: int = 3
                 ):
        self.repo_root = java_repo_root 
        self.java_code_dir = java_code_dir
        self.boundary_dir = boundary_dir
        self.mock_dir = mock_dir
        self.java_test_dir = java_test_dir
        self.error_info_dir = error_info_dir
        self.fix_info_dir = fix_info_dir
        self.log_info_dir = log_info_dir
        self.maven_bin = maven_bin
        self.max_retry = max_retry
        self.file_name = file_name
        self.model = model
        self.client = OpenAI(
            api_key=os.getenv("MOONSHOT_API_KEY"),
            base_url="https://api.moonshot.cn/v1"
        )
        with open(Path(__file__).resolve().parent.parent / "prompt_template.yaml", "r", encoding="utf-8") as f:
            self.prompt_template = yaml.safe_load(f)

        
    def begin_gen_single_file(self):
        """开始生成单个文件的测试用例"""
        print(f"开始生成单个文件的测试用例...")
        self.case_gen()
        max_retries = self.max_retry
        round = 1
        while round <= max_retries:
            print(f"测试用例生成完毕，开始运行第{4-max_retries}次测试...")
            self.run_test()
            print("测试运行完毕，开始修复错误...")
            if self.error_fix(round = round):
                break
            round += 1
        print("错误修复完毕，保存提示词版本信息...")
        save_prompt()

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
        resp = self.send_request(prompt=self.prompt_template['SYS_PROMPT'] + self.prompt_template['UT_GEN'].format(code=code, abs=abs, mock_cond=mock_cond, boundary=boundary, ref=ref))
        print("正在生成测试用例...")

        # 将 '''java... ''' 中的内容保存到文件
        with open(self.java_test_dir, "w", encoding="utf-8") as f:
            f.write(resp.split("```java")[1].split("```")[0])

    def run_test(self):
        print(f'repo_root: {self.repo_root}')
        print(f'log_file: {self.log_info_dir}')
        print(f'error_file: {self.error_info_dir}')
        print(f'maven_bin: {self.maven_bin}')
        cmd = [str(self.maven_bin / "mvn.cmd"), "test", "-DtrimStackTrace=false"]
        print(">>> 执行:", " ".join(cmd))
        with self.log_info_dir.open("w", encoding="utf-8") as f:
            proc = subprocess.run(cmd, cwd=self.repo_root, stdout=f, stderr=subprocess.STDOUT, text=True)
        with self.error_info_dir.open("w", encoding="utf-8") as f:
            f.write("错误信息提取中 " + str(self.error_info_dir) + "\n")
            with open(self.log_info_dir, "r", encoding="utf-8") as logf:
                # 提取所有[ERROR]信息
                errors = logf.read().split('[ERROR]')[1:]
                f.write("[ERROR]".join(errors))
        print(">>> 控制台输出已保存到", self.log_info_dir)
        print(">>> 错误信息已保存到", self.error_info_dir)
        print(">>> Maven exit code:", proc.returncode)

    def error_fix(self, round: int) -> bool:

        print("正在读取错误信息...")
        with open(self.error_info_dir, "r", encoding="utf-8") as f:
            error_info = f.read()
        with open(self.java_code_dir, "r", encoding="utf-8") as f:
            code = f.read()
        with open(self.java_test_dir, "r", encoding="utf-8") as f:
            test_code = f.read()
        resp = self.send_request(prompt=self.prompt_template["ERROR_FIX"].format(code=code, test_code=test_code, error_info=error_info))
        print("正在修复错误...")
        if "```java" not in resp:
            print("Error: 修复后的代码中不包含 ```java 标记，错误可能来自于源码。")
            return True
        # 将 '''java... ''' 中的内容保存到文件
        code = resp.split("```java")[1].split("```")[0]
        with open(self.java_test_dir, "w", encoding="utf-8") as f:
            f.write(code)
        with open(Path(self.log_info_dir).resolve().parent / f"{self.file_name}_fix_{round}.log", "w", encoding="utf-8") as f:
            f.write(code)

        # 将其他内容保存到文件
        with open(self.fix_info_dir, "a", encoding="utf-8") as f:
            f.write(f'----------------\n文件: {self.java_test_dir}修复信息:\n')
            f.write(f'修复时间: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}\n')
            f.write(resp.split("```java")[0])
        return False
        