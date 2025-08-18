import json
import pickle
import re
import os
from pathlib import Path
from typing import List, Dict
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import glob

class DataBaseConstructor:
    """
    用于构建向量数据库的类
    """
    def __init__(self, backend: str = "faiss", 
                 embed_model: str = "BAAI/bge-small-zh-v1.5", 
                 chunk_size: int = 4096):
        '''Input:
        src_proj_dir: 待测项目根目录（不包含test目录）
        backend: 向量数据库后端
        model: 使用的模型名称
        prompt_template_path: prompt模板文件路径
        '''
        
        self.md_files = glob.glob(str(Path(__file__).resolve().parent / "reverse_data" / "*.md"))
        self.index_dir = Path(__file__).resolve().parent / "db_data"
        os.makedirs(self.index_dir, exist_ok=True)
        self.embed_model = SentenceTransformer(embed_model)
        self.dim = self.embed_model.get_sentence_embedding_dimension()
    
    def construct_faiss(self):
        raw = ''
        for md_file in self.md_files:
            with open(md_file, encoding="utf-8") as f:
                raw += f.read() + '\n\n'

            chunks = self.parse_markdown(raw)
            self.build_faiss_index(chunks)

            # 测试知识库
            print("正在测试知识库...")
            query = "如何根据历史轨迹数据，预测未来的轨迹？"
            self.search_index(query)

            self.dump_records()
    
    def dump_records(self):
        records = pickle.load(open(os.path.join(self.index_dir, "records.pkl"), "rb"))
        with open(os.path.join(self.index_dir, "records.json"), "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    
    def search_index(self, query: str, top_k: int = 5):
        index = faiss.read_index(os.path.join(self.index_dir, "index.faiss"))
        meta = json.load(open(os.path.join(self.index_dir, "meta.json"), "r", encoding="utf-8"))
        records = pickle.load(open(os.path.join(self.index_dir, "records.pkl"), "rb"))

        query_vector = self.embed_model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        distances, indices = index.search(query_vector, top_k)

        for i in range(top_k):
            record = records[indices[0][i]]
            print(f"距离: {distances[0][i]:.4f}")
            print(f"路径: {' / '.join(record['tags'])}")
            print(f"内容: {record['text']}")
            print("="*50)
        
        return records
    
    def build_faiss_index(self, records: List[Dict]):
        texts = [f"{' / '.join(r['tags'])}\n\n{r['text']}" for r in records]
        vectors = self.embed_model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        vectors = vectors.astype("float32")
        index = faiss.IndexFlatIP(self.dim)
        index.add(vectors)

        faiss.write_index(index, os.path.join(self.index_dir, "index.faiss"))
        with open(os.path.join(self.index_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump([{"tags": r["tags"]} for r in records], f, ensure_ascii=False, indent=2)
        pickle.dump(records, open(os.path.join(self.index_dir, "records.pkl"), "wb"))
        print(f"✅ 已索引 {len(records)} 个 chunk")
        
    def parse_markdown(self, raw: str) -> List[Dict]:
        """
        返回 List[Dict]:
            {
                "text": 当前标题下的正文（不含父标题文本）,
                "tags": [父标题1, 父标题2, ..., 当前标题],
            }
        """
        lines = raw.splitlines()
        chunks: List[Dict] = []

        stack: List[tuple] = []
        buffer: List[str] = []   # 当前标题下的正文行

        def emit():
            """把当前标题之前的内容封装为 chunk"""
            if not stack:
                return
            levels, titles = zip(*stack)
            tags = list(titles)
            body = "\n".join(buffer).strip()
            chunks.append({
                "text": body,
                "tags": tags
            })
            buffer.clear()

        for line in lines:
            m = re.match(r'^(#{1,6})\s+(.*)', line)
            if m:
                level = len(m.group(1))
                title = m.group(2).strip()
                emit()
                while stack and stack[-1][0] >= level:
                    stack.pop()
                stack.append((level, title))
            else:
                buffer.append(line)

        emit()

        # 返回text不为空的chunk
        return [chunk for chunk in chunks if chunk['text']]




