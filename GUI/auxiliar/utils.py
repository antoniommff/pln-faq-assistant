from lingua import Language, LanguageDetectorBuilder
from auxiliar.entidades import EntityExtractor
from auxiliar.preprocesamiento import Preprocessing
import es_core_news_md
import en_core_web_md
import joblib

import os
import sys


REV_INTENT = {1: 'meal_suggestion', 2: 'recipe', 3: 'ingredients_list', 4: 'ingredient_substitution', 5: 'nutrition_info', 6: 'calories', 7: 'cook_time', 8: 'food_last'}



def load():
    # Comprobamos si estamos dentro del ejecutable de PyInstaller
    if hasattr(sys, '_MEIPASS'):
        models_dir = os.path.join(sys._MEIPASS, "models")
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "models"))

    intention_models = {'es': joblib.load(f"{models_dir}/model_es.pkl"), 'en': joblib.load(f"{models_dir}/model_en.pkl") }
    vectorizers = {'es': joblib.load(f"{models_dir}/vectorizer_es.pkl"), 'en': joblib.load(f"{models_dir}/vectorizer_en.pkl") }

    nlp = {'es': es_core_news_md.load(), 'en': en_core_web_md.load()}

    detector = LanguageDetectorBuilder.from_languages(Language.SPANISH, Language.ENGLISH).build()

    preprocesor = Preprocessing(nlp=nlp)

    extractor = EntityExtractor(nlp=nlp)
    extractor.add_vectors()

    return extractor, detector, preprocesor, vectorizers ,intention_models


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
