import random
import string
from flask import session

def gen_flag(qid):
    random.seed(session.get('flag_seed', 'default') + str(qid))
    rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"flag{{q{qid}_{rand_str}}}" 