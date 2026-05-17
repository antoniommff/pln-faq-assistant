import re
import unidecode
import contractions
from spellchecker import SpellChecker

class Preprocessing():
	def __init__(self, nlp):
		self.spell = {'es': SpellChecker(language='es'),  'en': SpellChecker(language='en')}

		self.nlp = nlp

		self.spell['es'].word_frequency.load_words(
		    ['aove', 'thermomix', 'airfryer', 'umami', 'keto', 'dente',
		     'pizza', 'sushi', 'wok', 'bowl', 'tupper', 'smoothie'])
		self.spell['en'].word_frequency.load_words(
		    ['bbq', 'thermomix', 'airfryer', 'umami', 'keto', 'ramen'])

		# ── Stopwords personalizadas ──────────────────────────────────────────────────
		self.KEEP = {'es':
				{'no', 'sin', 'excepto', 'nunca', 'cuando', 'como', 'cuanto',
				'antes', 'despues', 'hacer', 'estar', 'ser', 'buen', 'mal',
				'gluten', 'lactosa', 'proteina', 'vegano', 'vegana', 'keto', 'umami'},
			     'en':
				{'no', 'not', 'without', 'never', 'free', 'when', 'how',
				'before', 'after', 'make', 'good', 'bad',
				'gluten', 'lactose', 'vegan', 'keto', 'umami', 'bbq'}
				}

		self.STOPWORDS = {'es': {unidecode.unidecode(w).lower() for w in nlp['es'].Defaults.stop_words} - self.KEEP['es'],
				  'en': {unidecode.unidecode(w).lower() for w in nlp['en'].Defaults.stop_words} - self.KEEP['en']
			         }

		# ── Normalización de jerga ────────────────────────────────────────────────────
		self.SLANG_ES = {
		    'aser': 'hacer', 'kiero': 'quiero', 'q': 'que', 'xq': 'porque',
		    'komo': 'como', 'weno': 'bueno', 'k': 'que', 'x': 'por',
		}

		# ── Excepciones lematizador ───────────────────────────────────────────────────
		self.EXC = {'es':
			      {'gluten': 'gluten', 'proteina': 'proteina', 'lactosa': 'lactosa',
			       'vegano': 'vegano', 'vegana': 'vegano', 'bizcocho': 'bizcocho',
			       'aove': 'aove', 'pizza': 'pizza',},
		            'en':
			      {'gluten': 'gluten', 'ramen': 'ramen', 'vegan': 'vegan'}
			      }

		# ── Sinónimos regionales ──────────────────────────────────────────────────────
		self.SYN = { 'es':
				  {'papa': 'patata', 'papas': 'patata', 'durazno': 'melocoton',
				   'palta': 'aguacate', 'frutilla': 'fresa', 'choclo': 'maiz',
				   'elote': 'maiz', 'anana': 'pina', 'jugo': 'zumo',
				   'banana': 'platano', 'jitomate': 'tomate', 'batata': 'boniato',
				   'camaron': 'gamba', 'mani': 'cacahuete', 'aji': 'chile',},
				'en':
				  {'aubergine': 'eggplant', 'courgette': 'zucchini',
		                   'coriander': 'cilantro', 'rocket': 'arugula',
			           'biscuit': 'cookie', 'yoghurt': 'yogurt',
			           'beetroot': 'beet', 'prawn': 'shrimp',}
				}


	def apply_synonyms(self, text: str, lang: str) -> str:
	    synonyms = self.SYN[lang]
	    return ' '.join(synonyms.get(w, w) for w in text.split())


	def process_text(self, text: str, lang: str, is_predict: bool = False) -> str:
	    if not isinstance(text, str) or not text.strip():
	        return ''
	    if lang == 'en':
	        text = contractions.fix(text)
	    if lang == 'es':
	        for s, c in self.SLANG_ES.items():
	            text = re.sub(rf'\b{s}\b', c, text, flags=re.IGNORECASE)


	    nlp = self.nlp[lang]
	    sw = self.STOPWORDS[lang]
	    keep_set = self.KEEP[lang]
	    spell = self.spell[lang]
	    exc = self.EXC[lang]

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
	    return self.apply_synonyms(' '.join(tokens), lang)
