import time
import yaml
import json
from pathlib import Path
def save_prompt():
    """保存prompt到log文件"""
    log_file = Path(__file__).resolve().parent / "prompts_version.json"
    prompt_file = Path(__file__).resolve().parent / "prompt_template.yaml"
    # 获取当前prompt
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_template = yaml.safe_load(f)
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(log_file, "a", encoding="utf-8") as f:
        log_data = {
            "update_time": time_str,
            "prompt_template": prompt_template
        }
        f.write(json.dumps(log_data, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    save_prompt()

    