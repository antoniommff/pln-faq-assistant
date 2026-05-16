import re
import unidecode
import contractions
import spacy
from spellchecker import SpellChecker
from lingua import Language, LanguageDetectorBuilder

# ── Modelos ───────────────────────────────────────────────────────────────────
nlp_es = spacy.load('es_core_news_md')
nlp_en = spacy.load('en_core_web_md')

detector = LanguageDetectorBuilder.from_languages(Language.SPANISH, Language.ENGLISH).build()

spell_es = SpellChecker(language='es')
spell_en = SpellChecker(language='en')
spell_es.word_frequency.load_words(
    ['aove', 'thermomix', 'airfryer', 'umami', 'keto', 'dente',
     'pizza', 'sushi', 'wok', 'bowl', 'tupper', 'smoothie'])
spell_en.word_frequency.load_words(
    ['bbq', 'thermomix', 'airfryer', 'umami', 'keto', 'ramen'])

# ── Stopwords personalizadas ──────────────────────────────────────────────────
KEEP_ES = {'no', 'sin', 'excepto', 'nunca', 'cuando', 'como', 'cuanto',
           'antes', 'despues', 'hacer', 'estar', 'ser', 'buen', 'mal',
           'gluten', 'lactosa', 'proteina', 'vegano', 'vegana', 'keto', 'umami'}
KEEP_EN = {'no', 'not', 'without', 'never', 'free', 'when', 'how',
           'before', 'after', 'make', 'good', 'bad',
           'gluten', 'lactose', 'vegan', 'keto', 'umami', 'bbq'}

STOPWORDS_ES = {unidecode.unidecode(w).lower() for w in nlp_es.Defaults.stop_words} - KEEP_ES
STOPWORDS_EN = {unidecode.unidecode(w).lower() for w in nlp_en.Defaults.stop_words} - KEEP_EN

# ── Normalización de jerga ────────────────────────────────────────────────────
SLANG_ES = {
    'aser': 'hacer', 'kiero': 'quiero', 'q': 'que', 'xq': 'porque',
    'komo': 'como', 'weno': 'bueno', 'k': 'que', 'x': 'por',
}

# ── Excepciones al lematizador ────────────────────────────────────────────────
EXC_ES = {
    'gluten': 'gluten', 'proteina': 'proteina', 'lactosa': 'lactosa',
    'vegano': 'vegano', 'vegana': 'vegano', 'bizcocho': 'bizcocho',
    'aove': 'aove', 'pizza': 'pizza',
}
EXC_EN = {'gluten': 'gluten', 'ramen': 'ramen', 'vegan': 'vegan'}

# ── Sinónimos regionales ──────────────────────────────────────────────────────
SYN_ES = {
    'papa': 'patata', 'papas': 'patata', 'durazno': 'melocoton',
    'palta': 'aguacate', 'frutilla': 'fresa', 'choclo': 'maiz',
    'elote': 'maiz', 'anana': 'pina', 'jugo': 'zumo',
    'banana': 'platano', 'jitomate': 'tomate', 'batata': 'boniato',
    'camaron': 'gamba', 'mani': 'cacahuete', 'aji': 'chile',
}
SYN_EN = {
    'aubergine': 'eggplant', 'courgette': 'zucchini',
    'coriander': 'cilantro', 'rocket': 'arugula',
    'biscuit': 'cookie', 'yoghurt': 'yogurt',
    'beetroot': 'beet', 'prawn': 'shrimp',
}


def apply_synonyms(text: str, lang: str) -> str:
    synonyms = SYN_ES if lang == 'es' else SYN_EN
    return ' '.join(synonyms.get(w, w) for w in text.split())


def process_text(text: str, lang: str, is_predict: bool = False) -> str:
    if not isinstance(text, str) or not text.strip():
        return ''
    if lang == 'en':
        text = contractions.fix(text)
    if lang == 'es':
        for s, c in SLANG_ES.items():
            text = re.sub(rf'\b{s}\b', c, text, flags=re.IGNORECASE)
    nlp = nlp_es if lang == 'es' else nlp_en
    sw = STOPWORDS_ES if lang == 'es' else STOPWORDS_EN
    keep_set = KEEP_ES if lang == 'es' else KEEP_EN
    spell = spell_es if lang == 'es' else spell_en
    exc = EXC_ES if lang == 'es' else EXC_EN
    doc = nlp(text)
    tokens = []
    for tok in doc:
        if tok.is_space or tok.is_punct:
            continue
        no_accents = unidecode.unidecode(tok.text).lower()
        lemma = exc.get(no_accents, tok.lemma_.lower())
        if is_predict and spell.unknown([lemma]):
            corr = spell.correction(lemma)
            lemma = corr if corr else lemma
        norm = unidecode.unidecode(lemma)
        if norm in keep_set:
            tokens.append(norm)
        elif norm not in sw and len(norm) > 1:
            tokens.append(norm)
    return apply_synonyms(' '.join(tokens), lang)
