import re
from typing import List

def norm_gloss(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^A-Z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s

def tokenize_user_input(text: str) -> List[str]:
    rough = re.split(r"\s+", text.strip())
    toks = []
    for w in rough:
        w = re.sub(r"[^\w\-']+", "", w)
        g = norm_gloss(w)
        if g:
            toks.append(g)
    return toks
