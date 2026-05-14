from lingua import Language, LanguageDetectorBuilder
from auxiliar.entidades import EntityExtractor

def load():
    detector = LanguageDetectorBuilder.from_languages(Language.SPANISH, Language.ENGLISH).build()
    extractor = EntityExtractor()
    extractor.add_vectors()
    return extractor, detector

def predecir_idioma(texto, detector):
   lang = detector.detect_language_of(texto)
   return 'es' if lang == Language.SPANISH else 'en'

def prettify(category : dict()) -> str:
	texto = ""

	for c in category:
		if category[c] == []:
			continue
		else:
			texto += f"\t\t\t⋅ {c} -> {", ".join(category[c])}\n"

	return texto
