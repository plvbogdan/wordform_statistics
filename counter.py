from collections import defaultdict
import string 
import numpy as np
from utils import get_lemma

async def count_words(content: bytes, lang: str, progress_callback=None):

    total_lines = content.count(b'\n') + 1
    text = content.decode('utf-8')
    
    punct = string.punctuation + '—–…«»“”'
    stats = defaultdict(lambda: {'total': 0, 'per_line': np.zeros(total_lines, dtype=np.uint16)})
    cache = {}
    
    for line_num, line in enumerate(text.splitlines()):
        for word in line.strip().split():
            word = word.strip(punct).lower()
            if not word:
                continue
            
            if word in cache:
                lemma = cache[word]
            else:
                lemma = get_lemma(word, lang)
                cache[word] = lemma
            
            stats[lemma]['total'] += 1
            stats[lemma]['per_line'][line_num] += 1
        
        if progress_callback and line_num % 100 == 0:
            await progress_callback(int(line_num / total_lines * 100))
    
    return dict(stats)

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)