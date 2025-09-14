import re
from typing import List

def norm_gloss_lower(s: str) -> str:
    # 基本清洗：去首尾空格，转小写
    return s.strip().lower()

def candidates_for_filename(gloss: str) -> list[str]:
    """
    生成一组候选文件名（不带 .mp4），用于匹配你库里现有的小写+标点风格。
    顺序很重要：先尽量“保留原样的小写”，再做替代。
    例子： "Double" -> ["double", "double", "double", ...]
          "early (i)" -> ["early (i)", "early-(i)", "early_(i)", "early-i", "early_i", "earlyi"]
    """
    g0 = norm_gloss_lower(gloss)

    # 1) 原样（保留空格与标点的小写）
    cands = [g0]

    # 2) 空格替换为 - 或 _
    cands += [g0.replace(" ", "-"), g0.replace(" ", "_")]

    # 3) 移除多余空白
    g1 = re.sub(r"\s+", " ", g0).strip()
    if g1 not in cands:
        cands.append(g1)

    # 4) 常见标点的等价替换：空格/破折/下划线互换
    repl_pairs = [
        (" - ", "-"), (" – ", "-"), (" — ", "-"),
        ("-", "_"), ("_", "-"),
    ]
    for a, b in repl_pairs:
        cand = g1.replace(a, b)
        if cand not in cands:
            cands.append(cand)

    # 5) 去除部分弱标点（逗号、分号、冒号），保留括号与连字符的版本也留一份
    g2 = re.sub(r"[,:;]+", "", g1)
    for form in {g2, g2.replace(" ", "-"), g2.replace(" ", "_")}:
        if form not in cands:
            cands.append(form)

    # 6) 纯字母数字兜底（供未来 alphabet 回退用）
    g3 = re.sub(r"[^a-z0-9]+", "", g1)
    if g3 and g3 not in cands:
        cands.append(g3)

    return cands

def tokenize_user_input(text: str) -> List[str]:
    rough = re.split(r"\s+", text.strip())
    toks = []
    for w in rough:
        w = re.sub(r"[^\w\-']+", "", w)
        g = norm_gloss(w)
        if g:
            toks.append(g)
    return toks
