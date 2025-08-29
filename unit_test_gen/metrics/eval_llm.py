import json
from pathlib import Path
from typing import Optional,Dict, List, Tuple
from dotenv import load_dotenv
import javalang
import os
from openai import OpenAI
import glob
import re
from collections import defaultdict
load_dotenv()

client = OpenAI(
            api_key="sk-jcK260y9Z40an9itPpM3AHUA9hHfHzmzjVaYfe6s5SBGVWAq",
            base_url="https://api.moonshot.cn/v1"
        )

def split_test_cases(java_file: Path) -> list[str]:
    java_file = Path(java_file)
    with java_file.open(encoding='utf-8') as f:
        lines = f.readlines()

    src = ''.join(lines)
    tree = javalang.parse.parse(src)

    cases = []
    for _, node in tree.filter(javalang.tree.MethodDeclaration):
        # 只保留带 @Test（或以 Test 结尾的注解）的方法
        if not any(ann.name.endswith('Test') for ann in node.annotations):
            continue

        # 起始行号（javalang 行号从 1 开始）
        start_line = node.position.line - 1

        # 从起始行开始扫描，找匹配的右大括号
        brace_count = 0
        found_first_lbrace = False
        end_line = start_line
        for i in range(start_line, len(lines)):
            for ch in lines[i]:
                if ch == '{':
                    brace_count += 1
                    found_first_lbrace = True
                elif ch == '}':
                    brace_count -= 1
                if found_first_lbrace and brace_count == 0:
                    end_line = i
                    break
            else:
                continue
            break

        snippet = ''.join(lines[start_line:end_line + 1]).rstrip()
        cases.append(snippet)

    return cases


# 从测试用例片段中提取被测方法名
def _get_target_method_name(case_snippet: str) -> Optional[str]:
    """
    仅用 javalang 提取测试用例的方法名，并去掉前缀/后缀的 test/Test。
    """
    try:
        # 用 javalang 解析单段方法代码
        tree = javalang.parse.parse('class Dummy { ' + case_snippet + ' }')
        for _, node in tree.filter(javalang.tree.MethodDeclaration):
            name = node.name
            # 去掉前缀或后缀 test/Test（(?i) 忽略大小写）
            name = re.sub(r'(?i)^(test)+|(test)+$', '', name)
            return name if name else None
    except Exception:
        pass
    return None
  


# 在源文件中找到同名方法
def find_source_method(source_file: Path, method_name: str):
    """
    返回源文件中与 method_name 匹配的方法完整代码段，未找到返回 None。
    """
    if not method_name:
        return ''
    source_file = Path(source_file)
    with source_file.open(encoding="utf-8") as f:
        tree = javalang.parse.parse(f.read())

    for _, node in tree.filter(javalang.tree.MethodDeclaration):
        # print(node.name)
        # print(method_name)

        if node.name.lower() in method_name.lower():
            start = node.position.line - 1
            lines = source_file.read_text(encoding="utf-8").splitlines(keepends=True)
            brace = 0
            found = False
            end = start
            for i in range(start, len(lines)):
                for ch in lines[i]:
                    if ch == '{':
                        brace += 1
                        found = True
                    elif ch == '}':
                        brace -= 1
                    if found and brace == 0:
                        end = i
                        break
                else:
                    continue
                break
            return ''.join(lines[start:end + 1]).rstrip()
    return ''


# 批量映射
def map_cases_to_sources(cases: list[str], source_file: Path) -> dict[str, str]:
    """
    参数：
        cases: split_test_cases 返回的用例片段列表
        source_file: 被测源码 .java 文件
    返回：
        用例片段 -> 源码片段 的映射字典
    """
    mapping = {}
    for case in cases:
        target = _get_target_method_name(case)
        if not target:
            mapping[case] = ''
            continue
        src = find_source_method(source_file, target)
        mapping[case] = src
    return mapping

def map_cases_to_sources_by_content(cases: list[str], source_file: Path) -> tuple[dict[str, str], dict[str, str]]:
    """
    返回两个映射：
        1. 用例片段 -> 源码片段
        2. 用例片段 -> 源函数名
    """
    with source_file.open(encoding="utf-8") as f:
        tree = javalang.parse.parse(f.read())

    source_methods = {}          # {方法名: 方法代码}
    lines = source_file.read_text(encoding="utf-8").splitlines(keepends=True)

    for _, node in tree.filter(javalang.tree.MethodDeclaration):
        method_name = node.name
        start = node.position.line - 1
        brace = 0
        found = False
        end = start
        for i in range(start, len(lines)):
            for ch in lines[i]:
                if ch == '{':
                    brace += 1
                    found = True
                elif ch == '}':
                    brace -= 1
                if found and brace == 0:
                    end = i
                    break
            else:
                continue
            break
        source_methods[method_name] = ''.join(lines[start:end + 1]).rstrip()

    mapping_code = {}   # 用例 -> 源码片段
    mapping_name = {}   # 用例 -> 源函数名

    for case in cases:
        matched_name = None
        for method_name, method_code in source_methods.items():
            if method_name in case:
                matched_name = method_name
                mapping_code[case] = method_code
                mapping_name[case] = method_name
                break
        if matched_name is None:
            mapping_code[case] = ''
            mapping_name[case] = None

    return mapping_code, mapping_name


def reverse_mapping(
    case_to_code: Dict[str, str],
    case_to_name: Dict[str, str]
) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    将原映射关系反转：
    返回
        1. 源码片段 -> 用例列表
        2. 源函数名 -> 用例列表
    同一个源码片段 / 函数名可能对应多条用例。
    """

    code_to_cases: Dict[str, List[str]] = defaultdict(list)
    name_to_cases: Dict[str, List[str]] = defaultdict(list)

    for case, code in case_to_code.items():
        # 可能遇到空串或未匹配的情况，可按需要过滤
        if code:
            code_to_cases[code].append(case)

    for case, name in case_to_name.items():
        if name:
            name_to_cases[name].append(case)

    return dict(code_to_cases), dict(name_to_cases)

# def begin_search(test_file: Path, src_file: Path):
#     cases = split_test_cases(test_file)
#     mapping_code, mapping_name = map_cases_to_sources_by_content(cases, src_file)

#     res = []
#     for idx, case in enumerate(cases, 1):
#         # print(f'------ Test {idx}/{len(cases)} ------')
#         # print(case, end='\n\n')
#         src = mapping_code[case]
#         func = mapping_name[case]
#         # print(src, end='\n\n')
#         res.append({
#             'test': case,
#             'src': src,
#             'function_name': func       # 直接从这里取
#         })
#     return res

def begin_search(test_file: Path, src_file: Path):
    cases = split_test_cases(test_file)
    mapping_code, mapping_name = map_cases_to_sources_by_content(cases, src_file)
    _, name_to_cases = reverse_mapping(mapping_code, mapping_name)
    res = []
    for func, case_list in name_to_cases.items():
        # 任意取一条用例即可拿到该函数的源码片段
        sample_case = case_list[0]
        src = mapping_code[sample_case]
        res.append({
            'function_name': func,
            'src': src,
            'test': case_list          # 所有属于该函数的用例
        })
    return res

def begin_eval(test_file: Path, src_file: Path, mcdc_file: Path):

    src_to_cases = begin_search(test_file, src_file)
    with open(mcdc_file, 'r', encoding='utf-8') as f:
        mcdc_info = json.load(f)
    ans = []
    count = 0
    skip_count = 0
    for item in src_to_cases:
        test_code = item['test']
        src_code = item['src']
        if src_code == '':
            continue
        mcdc_nodes = mcdc_info.get(item['function_name'], {}).get('cfg_nodes', [])
        if not mcdc_nodes:
            print(f"⚠️ {item['function_name']} 缺失 mcdc 配置，跳过")
            continue
        # mcdc_nodes = mcdc_info[item['function_name']]['cfg_nodes']
        mcdc = []
        for node in mcdc_nodes:
            if node['mcdc_inputs']:
                mcdc.append({
                    'cond': node['cond'],
                    'mcdc_inputs': node['mcdc_inputs']
                })
                # mcdc += f"cond: {node['cond']}\nmcdc_inputs: {node['mcdc_inputs']}\n"
        print('---------------------')
        # print(f"src: {src_code}")
        # print(f"test: {test_code}")
        # print(f"mcdc: {mcdc}")
        if mcdc:
            res = send_request(test_code, src_code, mcdc)
        else:
            skip_count += 1
            res = '否'
        print(f'file_name: {test_file.name}')
        print(f"mcdc_judge_res: {res}")
        
        if res == '是':
            count += 1
        ans.append(res)
    # print(ans)
    print(f'accuracy: {count}/{skip_count}/{len(src_to_cases)}')
    return count,  skip_count, len(src_to_cases)




def send_request(test_code: str, src_code: str, mcdc: list):

    model = "kimi-latest"
    self_consistency = 3
    mcdc_str = json.dumps(mcdc, ensure_ascii=False, separators=(',', ':'))
    # prompt = """下面是一段Java代码以及关于它的多个 Java JUnit 测试用例代码，我将给出你一段对源代码的边界值描述，请你判断该测试用例是否考虑到了所有的在边界值内、边界值本身和边界值之外的约束。只输出“是”或者“否”，不要输出任何思考过程。
    # JAVA源代码
    # {src_code}
    # JAVA测试用例
    # {test_code}
    # 边界值描述
    # {boundary}
    # """
    prompt = """下面是一段Java代码以及关于它的多个 Java JUnit 测试用例代码，我将给出你一段对源代码中各个条件的MC/DC全覆盖的条件布尔取值约束(约束默认都是正确完整的)，请你判断这些测试用例集合是否在总体上满足所有源函数条件的MC/DC约束。只输出“是”或者“否”，不要输出任何思考过程。

    说明：
    例如对于条件(count1<1||count2<1)，每个原子条件依次记为AT0,AT1...,我给你的约束为：
    [{{"AT0":false,"AT1":true}},{{"AT0":true,"AT1":false}},{{"AT0":false,"AT1":false}}]
    你只需要判断总体的测试用例的代码里是否所有的约束都被考虑到了，如果全部考虑到了，回答“是”。特别的，如果源代码里没有条件判断，则自动认为满足MC/DC约束。下面我给出你需要判断的内容：
    JAVA源代码
    {src_code}
    JAVA测试用例
    {test_code}
    条件布尔取值约束
    {mcdc}

    """
    ans = []
    flag = True
    for i in range(self_consistency):
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt.format(src_code=src_code, test_code=test_code, mcdc=mcdc)}],
            temperature=0.2,
            max_tokens=256
        )
        ans.append(resp.choices[0].message.content.strip())
        if '否' in ans[i]:
            flag = False
            break
    # print(ans)
    if flag:
        return '是'
    return '否'


from pathlib import Path
import json

# 统一根目录
base = Path(__file__).resolve().parent.parent.parent

# 三个根目录
src_root   = base / "java_project" / "src" / "main" / "java" / "gov" / "nasa" / "alsUtility"
test_root  = base / "java_project" / "src" / "test" / "java" / "gov" / "nasa" / "alsUtility"
mcdc_root  = Path(__file__).resolve().parent.parent / "data_preparation" / "mcdc_output"

def iter_triples():
    """
    生成器：每次返回 (src_file, test_file, mcdc_file)
    任一文件缺失就跳过，并 print 提示
    """
    for src_file in src_root.glob("*.java"):
        stem = src_file.stem                       # 去掉 .java
        pattern = f"*{stem}Test*.java"
        test_files = list(test_root.glob(pattern))
        mcdc_file = mcdc_root / f"{stem}_mcdc_cfg.json"
        missing = []
        if not test_files:
            missing.append("test")
        if not mcdc_file.exists():
            missing.append("mcdc")
        if missing:
            print(f"[跳过] {src_file.name} 缺失 {' & '.join(missing)}")
            # 写入到log
            with open(Path(__file__).resolve().parent / "log.txt", "a") as f:
                f.write(f"{src_file.name} 缺失 {' & '.join(missing)}\n")
            continue
        for test_file in test_files:
            yield src_file, test_file, mcdc_file
    # for src_file in src_root.glob("*.java"):
    #     stem = src_file.stem                       # 去掉 .java
    #     test_file = test_root / f"{stem}_ESTest.java"
    #     mcdc_file = mcdc_root / f"{stem}_mcdc_cfg.json"

    #     missing = []
    #     if not test_file.exists():
    #         missing.append("test")
    #     if not mcdc_file.exists():
    #         missing.append("mcdc")

    #     if missing:
    #         print(f"[跳过] {src_file.name} 缺失 {' & '.join(missing)}")
    #         # 写入到log
    #         with open(Path(__file__).resolve().parent / "log.txt", "a") as f:
    #             f.write(f"{src_file.name} 缺失 {' & '.join(missing)}\n")
    #         continue

    #     yield src_file, test_file, mcdc_file

# 主入口
def run_all():
    all_count = 0
    all_skip = 0

    all_total = 0
    for src_file, test_file, mcdc_file in iter_triples():
        print(f"\n====== 开始处理 {src_file.name} ======")
        

        count, skip, total= begin_eval(test_file, src_file, mcdc_file)

        all_count += count
        all_skip += skip
        all_total += total
    print(f'all_count: {all_count}')
    print(f'all_total: {all_total}')
    print(f'all_skip: {all_skip}')

    print(f'all_accuracy: {all_count}/{all_skip}/{all_total}')
    
    



if __name__ == "__main__":
    run_all()

# if __name__ == "__main__":
#     base = Path(__file__).resolve().parent.parent.parent
#     test_file = base / "java_project" / "src" / "test" / "java" / "gov" / "nasa" / "alsUtility" / "Brick3d_ESTest.java"
#     src_file = base / "java_project" / "src" / "main" / "java" / "gov" / "nasa" / "alsUtility" / "Brick3d.java"
#     mcdc_file = Path(__file__).resolve().parent.parent / "data_preparation" / "mcdc_output" / "Brick3d_mcdc_cfg.json"
#     begin_eval(test_file, src_file, mcdc_file)
