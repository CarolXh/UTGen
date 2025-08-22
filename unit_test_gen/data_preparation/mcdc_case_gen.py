#!/usr/bin/env python3
"""
- 构建 Java 函数级别的控制流图（CFG）
- 把条件节点拆成原子条件
- 把 Java 条件转成 Z3 布尔表达式
- 利用Z3求解器在CFG上枚举 MCDC 100 % 输入
- 输出 JSON + .dot 图
"""
import json
import re
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import List, Dict, Any, Tuple, Set, Optional
from tree_sitter import Language, Parser, Node
import tree_sitter_java as tsjava
import javalang
from javalang import tree
import z3
from anytree import Node as ANode, RenderTree, PreOrderIter
import argparse
from anytree.exporter import DotExporter

# --------------------------------------------------
# AST 遍历：找到树中所有函数体
# --------------------------------------------------
def all_methods(root: Node, code: bytes) -> List[Tuple[str, Node]]:
    methods = []

    def walk(n: Node):
        if n.type == "method_declaration":
            name = n.child_by_field_name("name")
            sig = code[name.start_byte:name.end_byte].decode()
            body = n.child_by_field_name("body")
            if body:
                methods.append((sig, body))
        for c in n.children:
            walk(c)

    walk(root)
    return methods

# --------------------------------------------------
# 条件表达式收集（含短路处理）
# --------------------------------------------------
def collect_conditions_with_position(node: Node, code: bytes):
    """
    返回 (条件字符串, 起始字节, 结束字节)
    会递归进入 && / ||，找到所有原子条件
    """
    conds = []

    def walk(n: Node):
        if n.type in {"if_statement", "while_statement", "do_statement"}:
            cond = n.child_by_field_name("condition")
            if cond:
                conds.append((code[cond.start_byte:cond.end_byte].decode(),
                              cond.start_byte, cond.end_byte))
        elif n.type == "for_statement":
            cond = n.child_by_field_name("condition")
            if cond:
                conds.append((code[cond.start_byte:cond.end_byte].decode(),
                              cond.start_byte, cond.end_byte))
        elif n.type == "conditional_expression":
            cond = n.child_by_field_name("condition")
            if cond:
                conds.append((code[cond.start_byte:cond.end_byte].decode(),
                              cond.start_byte, cond.end_byte))
        elif n.type in {"binary_expression", "parenthesized_expression"}:
            # 继续深入找 &&/||
            for c in n.children:
                walk(c)
        for c in n.children:
            walk(c)

    walk(node)
    return conds

# --------------------------------------------------
# CFG 节点定义
# --------------------------------------------------
class CFGNode:
    _id = 0

    def __init__(self, label: str = "", cond: str = "", parent = None):
        self.id   = CFGNode._id; CFGNode._id += 1
        self.label = label
        self.cond  = cond
        self.succ  : List[Tuple[str, CFGNode]] = []   # (edge_label, node)
        self.mcdc_inputs : List[Dict[str, bool]] = []
        self.parent = parent
    
    @property
    def children(self):
        return [n for _, n in self.succ]

    def add_succ(self, label: str, node: "CFGNode"):
        self.succ.append((label, node))

    def to_dot(self):
        lines = [f'{self.id} [label="{self.label}\\n{self.cond}"]']
        for lab, nxt in self.succ:
            lines.append(f'{self.id} -> {nxt.id} [label="{lab}"]')
        return lines

# --------------------------------------------------
# 把 Java 条件转成 Z3 布尔表达式 + 原子，原子用于MCDC 求解
# --------------------------------------------------


# 把 AST 节点还原成源码片段（去掉多余空格）
def _node_src(expr: str, node) -> str:
    if node.position is None:
        return str(node)
    start, end = node.position
    return expr[start:end].strip()

# --------------------------------------------------
# 把 Java 条件表达式 →  Z3 布尔表达式
# 返回值:
#   z3_expr : z3.BoolRef        例如 Or(AT0, AT1, AT2)
#   atoms   : List[str]         例如 ['point.getLatitude()==Double.NaN', ...]
#   z3_vars : Dict[str, Bool]   例如 {'AT0': Bool('AT0'), 'AT1': ...}
# --------------------------------------------------
def to_z3(expr: str) -> Tuple[z3.BoolRef, List[str], Dict[str, z3.BoolRef]]:
    # 1. 先收集所有需要独立成原子的布尔子式
    def collect_atoms(node) -> List[str]:
        atoms = []
        if isinstance(node, tree.BinaryOperation) and node.operator in {"==", "!=", "<", "<=", ">", ">="}:
            atoms.append(_node_src(expr, node))
        # elif isinstance(node, tree.UnaryExpression) and node.operator == "!":
        #     atoms.extend(collect_atoms(node.operand))
        elif isinstance(node, tree.BinaryOperation) and node.operator in {"&&", "||"}:
            atoms.extend(collect_atoms(node.operandl))
            atoms.extend(collect_atoms(node.operandr))
        elif isinstance(node, tree.TernaryExpression):
            atoms.extend(collect_atoms(node.expression))
        else:
            # 其它表达式整体当成一个原子
            atoms.append(_node_src(expr, node))
        return atoms

    try:
        ast = javalang.parse.parse_expression(expr)
    except Exception:
        # 容错：解析失败就把整个表达式当成一个原子
        atoms = [expr.strip()]
    else:
        # 去重并保持出现顺序
        atoms = list(dict.fromkeys(collect_atoms(ast)))

    # 2. 建立变量映射 AT0, AT1, ...
    z3_vars = {f"AT{i}": z3.Bool(f"AT{i}") for i in range(len(atoms))}
    atom2z3 = {atom: z3_vars[f"AT{i}"] for i, atom in enumerate(atoms)}

    # 3. 递归生成 Z3 表达式
    def walk(node) -> z3.BoolRef:
        if isinstance(node, tree.BinaryOperation):
            if node.operator in {"&&", "||"}:
                left, right = walk(node.operandl), walk(node.operandr)
                return z3.And(left, right) if node.operator == "&&" else z3.Or(left, right)
            elif node.operator in {"==", "!=", "<", "<=", ">", ">="}:
                return atom2z3[_node_src(expr, node)]
        # if isinstance(node, tree.UnaryOperation) and node.operator == "!":
        #     return z3.Not(walk(node.operand))
        if isinstance(node, tree.TernaryExpression):
            return walk(node.expression)
        # 其它节点 → 原子
        return atom2z3[_node_src(expr, node)]

    # 如果解析失败直接返回单个原子
    if not atoms:
        atoms = [expr.strip()]
        z3_vars = {"AT0": z3.Bool("AT0")}
        return z3_vars["AT0"], atoms, z3_vars

    try:
        z3_expr = walk(ast)
    except Exception:
        # 兜底：把整个表达式当成一个原子
        z3_expr = z3_vars["AT0"]

    print(f"[debug] to_z3 called, expr={expr},\n atoms={atoms},\n z3_vars={z3_vars}")
    return z3_expr, atoms, z3_vars




# --------------------------------------------------
# 在 CFG 上枚举 MCDC
# --------------------------------------------------

def mcdc_on_cfg(root: CFGNode) -> Dict[int, List[Dict[str, bool]]]:
    result = {}
    visited = set()

    def dfs(n: CFGNode):
        if n in visited or not n.cond:
            return
        visited.add(n)
        result[n.id] = mcdc_full(n.cond)
        for _, nxt in n.succ:
            dfs(nxt)

    # 从 root 开始 DFS，但 root 可能是 entry，所以需要遍历所有节点
    nodes_to_visit = [root]
    seen_nodes = set()
    while nodes_to_visit:
        cur = nodes_to_visit.pop()
        if cur in seen_nodes:
            continue
        seen_nodes.add(cur)
        if cur.cond:                       # 只在有 cond 的节点上计算
            result[cur.id] = mcdc_full(cur.cond)
        for _, child in cur.succ:
            if child not in seen_nodes:
                nodes_to_visit.append(child)
    return result

# --------------------------------------------------
# 单条布尔表达式的完整 MCDC 用例
# --------------------------------------------------
import itertools
def mcdc_full(expr: str) -> List[Dict[str, bool]]:
    z3_expr, atoms, z3_vars = to_z3(expr)
    var_names = list(z3_vars.keys())
    if not var_names:
        return []

    tests: List[Dict[str, bool]] = []

    # 对每个原子变量做独立影响对
    for a in var_names:
        others = [v for v in var_names if v != a]
        for mask_bits in itertools.product([False, True], repeat=len(others)):
            ctx_base = dict(zip(others, mask_bits))

            # 情景1：a = True
            ctx1 = {**ctx_base, a: True}
            s = z3.Solver()
            for k, v in ctx1.items():
                s.add(z3_vars[k] == v)
            if s.check() != z3.sat:
                continue
            val1 = z3.is_true(s.model().eval(z3_expr))

            # 情景2：a = False
            ctx2 = {**ctx_base, a: False}
            s.reset()
            for k, v in ctx2.items():
                s.add(z3_vars[k] == v)
            if s.check() != z3.sat:
                continue
            val2 = z3.is_true(s.model().eval(z3_expr))

            if val1 != val2:            # 现在都是 Python bool，可直接比较
                tests.append(ctx1)      # 保存两个情景的上下文
                tests.append(ctx2)      # 保存两个情景的上下文
                break                   # 找到一组即可

    # 去重
    seen = set(tuple(sorted(d.items())) for d in tests)
    return [dict(t) for t in seen]

# --------------------------------------------------
# 函数体 → CFG
# --------------------------------------------------
def build_cfg(body: Node, code: bytes) -> CFGNode:
    """
    CFG：每个语句/条件一个节点，遇到 if/while 产生分支
    仅演示思路，真正工业级需完整语义
    """
    CFGNode._id = 0
    entry = CFGNode("entry")
    exit_ = CFGNode("exit")

    # 收集所有条件
    conds = collect_conditions_with_position(body, code)
    print(f"[debug] build_cfg called, conds={conds}")

    # 为每个条件建节点
    prev = entry
    for expr, _, _ in conds:
        cond_node = CFGNode("cond", cond=expr)
        prev.add_succ("", cond_node)
        cond_node.add_succ("T", exit_)
        cond_node.add_succ("F", exit_)
        prev = cond_node

    prev.add_succ("", exit_)
    entry.succ.append(("", exit_))
    return entry

# --------------------------------------------------
# pipeline
# --------------------------------------------------
def main(java_file: Path):
    JAVA_LANG = Language(tsjava.language())
    java_name = java_file.stem
    OUT_JSON = Path(__file__).resolve().parent / "mcdc_output" / f"{java_name}_mcdc_cfg.json"
    OUT_DIR  = Path(__file__).resolve().parent / "mcdc_output"; 
    OUT_DIR.mkdir(exist_ok=True)
    code_bytes = java_file.read_bytes()
    parser = Parser()
    parser.language = JAVA_LANG
    tree = parser.parse(code_bytes)

    methods = all_methods(tree.root_node, code_bytes)
    summary = {}
    print(f"[debug] 找到 {len(methods)} 个方法：{[sig for sig, _ in methods]}")

    for sig, body in methods:
        cfg_root = build_cfg(body, code_bytes)
        # 输出 dot
        lines = ["digraph CFG {"]
        visited = set()

        def dot(n: CFGNode):
            if n in visited:
                return
            visited.add(n)
            lines.extend(n.to_dot())
            for _, nxt in n.succ:
                dot(nxt)

        dot(cfg_root)
        lines.append("}")
        dot_path = OUT_DIR / f"{sig}.dot"
        visited = set()
        lines = ["digraph CFG {"]

        def dot(n: CFGNode):
            if n.id in visited:
                return
            visited.add(n.id)
            safe_label = n.label.replace('"', r'\"')
            safe_cond = n.cond.replace('"', r'\"').replace('\n', r'\l')
            lines.append(f'{n.id} [label="{safe_label}\\n{safe_cond}"]')
            for lab, nxt in n.succ:
                if nxt.id not in visited:
                    dot(nxt)
                lines.append(f'{n.id} -> {nxt.id} [label="{lab}"]')

        dot(cfg_root)
        lines.append("}")
        dot_path.write_text("\n".join(lines), encoding="utf-8")


        # MCDC
        mcdc_map = mcdc_on_cfg(cfg_root)

        summary[sig] = {
            "dot": str(dot_path),
            "cfg_nodes": [
                {
                    "id": n.id,
                    "label": n.label,
                    "cond": n.cond,
                    "mcdc_inputs": mcdc_map.get(n.id, [])
                }
                for n in [cfg_root] + [n for n in PreOrderIter(cfg_root) if n != cfg_root]
            ]
        }

    Path(OUT_JSON).write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"[✓] CFG + MCDC 完成 → {OUT_JSON} 和 {OUT_DIR}")
    # 仅返回condintion、mcdc_inputs不为空的项目的condition和mcdc_inputs
    # filtered_summary = {}
    # for sig, data in summary.items():
    #     cfg_nodes = data["cfg_nodes"]
    #     for node in cfg_nodes:
    #         if node["cond"] and node["mcdc_inputs"]:
    #             if sig not in filtered_summary:
    #                 filtered_summary[sig] = []
    #             filtered_summary[sig].append({
    #                 "condition": node["cond"],
    #                 "mcdc_inputs": node["mcdc_inputs"]
    #             })
    # print(filtered_summary)
    filtered_summary = {
            "cases":[{"cond": n.cond,
            "mcdc_inputs": mcdc_map.get(n.id, [])
        }
            for n in [cfg_root] + [n for n in PreOrderIter(cfg_root) if n != cfg_root and n.cond and mcdc_map.get(n.id, [])]
    ]}
    print(filtered_summary)
    return filtered_summary


# --------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成 Java 函数的控制流图和 MCDC 测试用例")
    parser.add_argument("--java_file", type=Path, default=Path(__file__).resolve().parent.parent.parent / "java_project" / "src" / "main" / "java"/ "org" / "example" / "DataCleaner.java",  help="Java 源文件路径")
    args = parser.parse_args()
    main(args.java_file)
