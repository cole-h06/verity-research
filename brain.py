from llm.extract_specs import process_product
from utils.normalization import *
from utils.constants import PILLARS
import re

def clean_price(p):
    if not p:
        return None
    p = str(p)
    p = re.sub(r"[^\d.]", "", p)
    try:
        return float(p)
    except Exception:
        return None

def get_pillar_count(structured, category):
    pillar_keys = PILLARS.get(category, [])
    return sum(1 for k, _ in structured if k in pillar_keys)