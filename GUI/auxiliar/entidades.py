import warnings


class EntityExtractor:
    """Extractor de entidades mediante similitud del coseno con spaCy."""

    VECTORS = {
        "es": {
            "food_base":      "cocina gastronomía receta comida",
            "culture_origin": "italiana mexicano japonés país cultura tradicional",
            "diet_type":      "vegano vegetariano celíaco saludable ligero",
            "ingredient":     "ingredientes lácteo carne pescado verdura tubérculo fruta",
            "utensil":        "sartén cacerola batidora cubiertos olla",
            "appliance":      "vitrocerámica nevera congelador horno freidora tostadora",
        },
        "en": {
            "food_base":      "cooking gastronomy recipe food",
            "culture_origin": "Italian Mexican Japanese country culture traditional",
            "diet_type":      "vegan vegetarian celiac healthy light",
            "ingredient":     "ingredients dairy meat fish vegetable tuber fruit",
            "utensil":        "frying pan saucepan blender cutlery pot",
            "appliance":      "ceramic hob fridge freezer oven frier toaster",
        },
    }

    NEG_AND_SUST = {
        "es": {
            "attached_negations": ["no", "sin", "ningún", "cero"],
            "negations":          ["no", "nunca", "jamás", "tampoco"],
            "change_verbs":       ["sustituir", "cambiar", "reemplazar", "quitar"],
        },
        "en": {
            "attached_negations": ["no", "without", "none", "zero"],
            "negations":          ["no", "never", "ever", "neither"],
            "change_verbs":       ["replace", "change", "substitute", "remove"],
        },
    }

    def __init__(self, nlp):
        self.nlp = nlp
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

    def _check_negation_and_substitution(self, doc, word, lang="es"):
        if word.i > 0 and doc[word.i - 1].text.lower() in self.neg_and_sust[lang]["attached_negations"]:
            return True
        for ancestor in word.ancestors:
            for child in ancestor.children:
                if child.text.lower() in self.neg_and_sust[lang]["negations"]:
                    return True
        if word.head.lemma_ in self.neg_and_sust[lang]["change_verbs"] and word.dep_ == "obj":
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
                        is_neg = self._check_negation_and_substitution(doc, word, lang=lang) and neg
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
