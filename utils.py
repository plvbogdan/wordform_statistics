import pymorphy3
import simplemma
from openpyxl import Workbook

morph_ru = pymorphy3.MorphAnalyzer()

def get_lemma(word: str, lang: str) -> str:
    if lang == 'ru':
        return morph_ru.parse(word)[0].normal_form
    return simplemma.lemmatize(word, lang=lang)

def save_to_excel(stats: dict, filename: str):
    wb = Workbook()
    ws = wb.active
    ws.append(["Словоформа", "Всего", "По строкам"])

    for word, data in sorted(stats.items(), key=lambda x: -x[1]['total']):
        per_line = per_line = ','.join(map(str, data['per_line']))
        ws.append([word, data['total'], per_line])
    
    wb.save(filename)