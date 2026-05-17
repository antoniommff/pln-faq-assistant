from lingua import Language, LanguageDetectorBuilder
from auxiliar.entidades import EntityExtractor
from auxiliar.preprocesamiento import Preprocessing
import es_core_news_md
import en_core_web_md

def load():
    nlp = {'es': es_core_news_md.load(), 'en': en_core_web_md.load()}

    detector = LanguageDetectorBuilder.from_languages(Language.SPANISH, Language.ENGLISH).build()

    preprocesor = Preprocessing(nlp=nlp)

    extractor = EntityExtractor(nlp=nlp)
    extractor.add_vectors()

    return extractor, detector, preprocesor


def predict_language(text, detector):
    lang = detector.detect_language_of(text)
    return 'es' if lang == Language.SPANISH else 'en'


def prettify(category: dict) -> str:
    text = ""
    for c in category:
        if category[c] == []:
            continue
        else:
            text += f"\t\t\t⋅ {c} -> {', '.join(category[c])}\n"
    return text
