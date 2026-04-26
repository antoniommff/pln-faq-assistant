import warnings
import spacy
import es_core_news_md
import en_core_web_md

class EntityExtractor:
    """Extractor de entidades mediante similitud del coseno con spaCy."""

    VECTORS = {
        "es": {
            "comida_base":     "cocina gastronomía receta comida",
            "origen_cultura":  "italiana mexicano japonés país cultura tradicional",
            "tipo_dieta":      "vegano vegetariano celíaco saludable ligero",
            "ingrediente":     "ingredientes lácteo carne pescado verdura tubérculo fruta",
            "utensilios":      "sartén cacerola batidora cubiertos olla",
            "electrodomestico": "vitrocerámica nevera congelador horno freidora tostadora",
        },
        "en": {
            "comida_base":     "cooking gastronomy recipe food",
            "origen_cultura":  "Italian Mexican Japanese country culture traditional",
            "tipo_dieta":      "vegan vegetarian celiac healthy light",
            "ingrediente":     "ingredients dairy meat fish vegetable tuber fruit",
            "utensilios":      "frying pan saucepan blender cutlery pot",
            "electrodomestico": "ceramic hob fridge freezer oven frier toaster",
        },
    }

    NEG_AND_SUST = {
        "es": {
            "negaciones_pegadas": ["no", "sin", "ningún", "cero"],
            "negaciones":         ["no", "nunca", "jamás", "tampoco"],
            "verbos_cambio":      ["sustituir", "cambiar", "reemplazar", "quitar"],
        },
        "en": {
            "negaciones_pegadas": ["no", "without", "none", "zero"],
            "negaciones":         ["no", "never", "ever", "neither"],
            "verbos_cambio":      ["replace", "change", "substitute", "remove"],
        },
    }

    def __init__(self, langs={"en" : en_core_web_md, "es": es_core_news_md}):
        self.nlp = {lang: langs[lang].load() for lang in langs}
        self.vectors = {}
        self.neg_and_sust = {}

    def add_vectors(self, vectors=VECTORS, neg_and_sust=NEG_AND_SUST):
        self.vectors = {
            lang: {cat: self.nlp[lang](vectors[lang][cat]) for cat in vectors[lang]}
            for lang in self.nlp
        }
        self.neg_and_sust = {
            lang: {cat: neg_and_sust[lang][cat] for cat in neg_and_sust[lang]}
            for lang in neg_and_sust
        }

    def _check_negation_and_sustitution(self, doc, word, lang="es"):
        if word.i > 0 and doc[word.i - 1].text.lower() in self.neg_and_sust[lang]["negaciones_pegadas"]:
            return True
        for ancestor in word.ancestors:
            for child in ancestor.children:
                if child.text.lower() in self.neg_and_sust[lang]["negaciones"]:
                    return True
        if word.head.lemma_ in self.neg_and_sust[lang]["verbos_cambio"] and word.dep_ == "obj":
            return True
        return False

    def extract(self, clean_text, threshold=0.4, neg=False, lang="es", print_warn=False):
        with warnings.catch_warnings(record=True) as w:
            doc = self.nlp[lang](clean_text)
            result = {cat: [] for cat in self.vectors[lang]}

            for word in doc:
                if word.pos_ in ["NOUN", "VERB", "ADJ", "PROPN"] and not word.is_stop:
                    best_category, best_mark = None, 0
                    for cat, anchor in self.vectors[lang].items():
                        sim = word.similarity(anchor)
                        if sim >= threshold and sim > best_mark:
                            best_mark = sim
                            best_category = cat
                    if best_category:
                        is_neg = self._check_negation_and_sustitution(doc, word, lang=lang) and neg
                        result[best_category].append(f"NO_{word.lemma_}" if is_neg else word.lemma_)

            items = [v for vals in result.values() for v in vals]
            if w and print_warn:
                print("\n--- Hay errores no críticos ---")
                for wi in w:
                    if issubclass(wi.category, UserWarning) and "[W008]" in str(wi.message):
                        print(f"Hay palabras no reconocidas en el texto: {wi.message}")
        return items, result

    def pretty_print(self, items, entities, text="Desglose de entidades:", lang="es", print_all=True):
        """print_all controla si se muestran todas las categorías o solo la lista plana."""
        print(f'\n[{lang.upper()}] {text}')
        if entities:
            for cat, vals in entities.items():
                if print_all:
                    print(f'  {cat:17s}: {vals}')
            print(f"  Entidades: {items}")
        else:
            print('  (sin entidades detectadas)')
