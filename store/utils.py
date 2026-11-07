"""Транслітерація для slug — щоб посилання були латиницею, а не кирилицею."""
from django.utils.text import slugify

TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e', 'є': 'ie',
    'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'i', 'й': 'i', 'к': 'k', 'л': 'l',
    'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ь': '',
    'ю': 'iu', 'я': 'ia', 'ы': 'y', 'э': 'e', 'ё': 'e', 'ъ': '',
}

def uk_slugify(text: str) -> str:
    """'Навушники VOLT Air' -> 'navushnyky-volt-air'"""
    transliterated = ''.join(TRANSLIT.get(ch, ch) for ch in text.lower())
    return slugify(transliterated)
