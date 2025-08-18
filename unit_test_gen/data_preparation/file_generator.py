from pathlib import Path
from dotenv import load_dotenv
import glob
from openai import OpenAI
import os
import yaml


load_dotenv()
# 默认配置
# SRC_DIR   = Path(__file__).resolve().parent.parent.parent / "java_project" / "src" / "main" / "java" / "org" / "example" / "DataCleaner.java"  
# OUT_API_FILE = Path(__file__).resolve().parent.parent / "reverse_text_data" / "api_doc.md"               

# OUT_REQ_FILE  = "../data/req_doc.md"                 
# MODEL     = "kimi-latest"                            
# PROMPT_TEMPLATE_PATH = "../prompt_template.yaml"
class FileGenerator:
    def __init__(self, src_proj_dir, 
                 backend = "faiss", 
                 model = "kimi-latest", 
                 prompt_template_path = Path(__file__).resolve().parent.parent / "prompt_template.yaml"):
        '''属性:
        src_proj_dir: 待测项目根目录（不包含test目录）
        api_file: 接口文档文件路径
        req_file: 需求文档文件路径
        backend: 向量数据库后端
        model: 使用的模型名称
        prompt_template_path: prompt模板文件路径
        '''
        self.src_proj_dir = src_proj_dir
        os.makedirs(Path(__file__).resolve().parent / "reverse_data", exist_ok=True)
        self.api_file = Path(__file__).resolve().parent / "reverse_data" / "api_doc.md"
        self.req_file = Path(__file__).resolve().parent / "reverse_data" / "req_doc.md"
        self.model = model
        if "kimi" in model:
            self.client = OpenAI(
                api_key=os.getenv("MOONSHOT_API_KEY"),
                base_url="https://api.moonshot.cn/v1"
            )
        # 测试client 连通性

        resp =self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": "测试连接"}],
            temperature=0.2,
            max_tokens=10
        )
        print("模型连接测试结果:")
        print(resp)
        print(resp.choices[0].message.content.strip())
        print("✅ 模型连接成功")

        with open(prompt_template_path, "r", encoding="utf-8") as f:
            self.prompt_template = yaml.safe_load(f)
        self.backend = backend
    

    def begin_file_gen(self):
        """开始文件生成"""
        print("准备生成接口文档...")
        self.file_intention_extraction()
        print("准备生成需求描述...")
        self.req_extraction()
        print("文件生成完成！")
        print("接口文档:", self.api_file)
        print("需求文档:", self.req_file)
    
    def file_intention_extraction(self):
        java_files = glob.glob(f"{self.src_proj_dir}/**/*.java", recursive=True)
        with open(self.api_file, "w", encoding="utf-8") as doc:
            for idx, path in enumerate(java_files, 1):
                rel_path = Path(path).relative_to(self.src_proj_dir)
                print(f"正在处理文件 {idx}/{len(java_files)}: {rel_path}")
                try:
                    if "kimi" in self.model:
                        with open(path, "r", encoding="utf-8") as f:
                            code_txt = f.read()
                        # code_txt = self.upload_and_extract_kimi(path, self.client)
                        desc = self.describe_code(code_txt)
                    doc.write(f"{desc}\n\n")
                except Exception as e:
                    doc.write(f"> ⚠️ 解析失败：{e}\n\n")
        print("✅ 接口文档已生成：", self.api_file)
    
    def req_extraction(self):
        print("开始反向生成需求描述")
        with open(self.api_file, "r", encoding="utf-8") as f:
            api_doc = f.read()
        req_desc = self.describe_req(api_doc)
        with open(self.req_file, "w", encoding="utf-8") as f:
            f.write(req_desc)

    # 非纯文本文件，使用模型提取
    def upload_and_extract_kimi(file_path: str, client: OpenAI) -> str:
        """上传文件 -> 抽取内容 -> 返回可直接喂给模型的纯文本"""
        with open(file_path, "rb") as f:
            file_obj = client.files.create(file=f, purpose="file-extract")
        content = client.files.content(file_obj.id).text
        client.files.delete(file_obj.id)
        return content
    
    def describe_code(self, code: str) -> str:

        """调用聊天接口，生成API描述"""
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompt_template["PROMPT_API_GEN"]},

                {"role": "user",   "content": f"```java\n{code}\n```"}
            ],
            temperature=0.2,
            max_tokens=4096
        )
        return resp.choices[0].message.content.strip()
    
    def describe_req(self, req: str) -> str:
        """调用 Kimi 聊天接口，生成需求描述"""
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompt_template["PROMPT_REQ_GEN"]},

                {"role": "user",   "content": f"{req}"}
            ],
            temperature=0.9,
            max_tokens=49152
        )
        return resp.choices[0].message.content.strip()
    
