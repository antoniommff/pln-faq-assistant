import warnings
import spacy


# ===================
# VÍA 1: DICCIONARIOS
# ===================

ENTITIES = {
    'ingredientes': {
        'es': {
            # Proteínas animales y Alternativas
            'pollo', 'ternera', 'cerdo', 'cordero', 'salmon', 'atun', 'gambas',
            'merluza', 'bacalao', 'pavo', 'pato', 'tofu', 'seitan', 'tempeh',
            # Lácteos y Huevos
            'huevo', 'leche', 'queso', 'mantequilla', 'nata', 'yogur', 'kefir', 'cuajada',
            # Verduras y Hortalizas
            'tomate', 'cebolla', 'ajo', 'patata', 'zanahoria', 'pimiento', 'calabacin',
            'espinaca', 'lechuga', 'brocoli', 'coliflor', 'berenjena', 'champiñon',
            'puerro', 'esparrago', 'alcachofa', 'calabaza', 'remolacha', 'apio',
            # Legumbres y Cereales
            'arroz', 'pasta', 'harina', 'pan', 'lentejas', 'garbanzos', 'judias',
            'quinoa', 'cuscus', 'avena', 'maiz', 'soja',
            # Grasas y Condimentos
            'sal', 'pimienta', 'aceite', 'vinagre', 'azucar', 'miel', 'limon', 'lima',
            'oregano', 'tomillo', 'pimenton', 'comino', 'canela', 'perejil', 'albahaca',
            'laurel', 'curcuma', 'jengibre', 'mostaza', 'soja', 'miso',
            # Frutos secos
            'nuez', 'almendra', 'avellana', 'piñon', 'cacahuete', 'sesamo'
        },
        'en': {
            'chicken', 'beef', 'pork', 'lamb', 'salmon', 'tuna', 'shrimp',
            'hake', 'cod', 'turkey', 'duck', 'tofu', 'seitan', 'tempeh',
            'egg', 'milk', 'cheese', 'butter', 'cream', 'yogurt', 'kefir', 'curd',
            'tomato', 'onion', 'garlic', 'potato', 'carrot', 'pepper', 'zucchini',
            'spinach', 'lettuce', 'broccoli', 'cauliflower', 'eggplant', 'mushroom',
            'leek', 'asparagus', 'artichoke', 'pumpkin', 'beetroot', 'celery',
            'rice', 'pasta', 'flour', 'bread', 'lentil', 'chickpea', 'bean',
            'quinoa', 'couscous', 'oats', 'corn', 'soy',
            'salt', 'pepper', 'oil', 'vinegar', 'sugar', 'honey', 'lemon', 'lime',
            'oregano', 'thyme', 'paprika', 'cumin', 'cinnamon', 'parsley', 'basil',
            'bay leaf', 'turmeric', 'ginger', 'mustard', 'soy sauce', 'miso',
            'walnut', 'almond', 'hazelnut', 'pine nut', 'peanut', 'sesame'
        },
    },
    'tecnicas': {
        'es': {
            # Calor seco
            'freir', 'hornear', 'asar', 'saltear', 'gratinar', 'tostar', 'sofreir',
            # Calor húmedo
            'hervir', 'cocer', 'escaldar', 'pochar', 'vapor', 'guisar', 'estofar',
            # Mecánicas
            'mezclar', 'batir', 'amasar', 'cortar', 'picar', 'triturar', 'moler',
            'rallar', 'laminar', 'emulsionar', 'tamizar',
            # Químicas / Otras
            'marinar', 'caramelizar', 'fundir', 'reducir', 'glasear', 'macerar',
            'fermentar', 'deshidratar', 'ahumar', 'confitar', 'escabechar'
        },
        'en': {
            'fry', 'bake', 'roast', 'saute', 'grill', 'toast', 'stir-fry',
            'boil', 'simmer', 'blanch', 'poach', 'steam', 'stew', 'braise',
            'mix', 'beat', 'knead', 'cut', 'chop', 'blend', 'grind',
            'grate', 'slice', 'emulsify', 'sift',
            'marinate', 'caramelize', 'melt', 'reduce', 'glaze', 'macerate',
            'ferment', 'dehydrate', 'smoke', 'confit', 'pickle'
        },
    },
    'utensilios': {
        'es': {
            'sarten', 'olla', 'cazuela', 'horno', 'freidora de aire', 'thermomix',
            'batidora', 'licuadora', 'molde', 'colador', 'rallador', 'cuchillo',
            'wok', 'plancha', 'microondas', 'freidora', 'bowl', 'tupper',
            'espátula', 'rodillo', 'bascula', 'manga pastelera', 'mortero',
            'vaporera', 'mandolina', 'pelador', 'varillas'
        },
        'en': {
            'pan', 'pot', 'saucepan', 'oven', 'airfryer', 'thermomix',
            'blender', 'mixer', 'mold', 'colander', 'grater', 'knife',
            'wok', 'grill', 'microwave', 'fryer', 'bowl', 'container',
            'spatula', 'rolling pin', 'scale', 'piping bag', 'mortar',
            'steamer', 'mandoline', 'peeler', 'whisk'
        },
    },
    'dietas': {
        'es': {
            'vegano', 'vegetariano', 'omnivoro', 'paleo', 'keto', 'cetogenica',
            'sin gluten', 'celiaco', 'sin lactosa', 'low carb', 'mediterranea',
            'ayuno intermitente', 'detox', 'kosher', 'halal'
        },
        'en': {
            'vegan', 'vegetarian', 'omnivore', 'paleo', 'keto', 'ketogenic',
            'gluten-free', 'celiac', 'lactose-free', 'low carb', 'mediterranean',
            'intermittent fasting', 'detox', 'kosher', 'halal'
        },
    },
    'paises': {
        'es': {
            'españa', 'mejico', 'italia', 'francia', 'japon', 'china', 'india',
            'tailandia', 'grecia', 'marruecos', 'peru', 'argentina', 'eeuu',
            'corea', 'turquia', 'vietnam', 'brasil', 'libano'
        },
        'en': {
            'spain', 'mexico', 'italy', 'france', 'japan', 'china', 'india',
            'thailand', 'greece', 'morocco', 'peru', 'argentina', 'usa',
            'korea', 'turkey', 'vietnam', 'brazil', 'lebanon'
        },
    },
    'gentilicios': {
        'es': {
            'español', 'mejicano', 'italiano', 'frances', 'japones', 'chino', 'indio',
            'tailandes', 'griego', 'marroqui', 'peruano', 'argentino', 'estadounidense',
            'coreano', 'turco', 'vietnamita', 'brasileño', 'libanes'
        },
        'en': {
            'spanish', 'mexican', 'italian', 'french', 'japanese', 'chinese', 'indian',
            'thai', 'greek', 'moroccan', 'peruvian', 'argentinian', 'american',
            'korean', 'turkish', 'vietnamese', 'brazilian', 'lebanese'
        },
    },
    'platos_completos': {
        'es': {
            # Cocina española
            'paella', 'tortilla de patatas', 'gazpacho', 'salmorejo', 'cocido',
            'fabada', 'pulpo a la gallega', 'pan con tomate', 'pisto',
            'croquetas', 'empanada', 'migas', 'rabo de toro',
            # Internacionales comunes
            'piza', 'hamburguesa', 'perrito', 'sushi', 'ramen', 'udon',
            'tacos', 'burritos', 'enchiladas', 'lasagna', 'carbonara',
            'risotto', 'curry', 'pad thai', 'poke bowl', 'falafel',
            'kebab', 'shawarma', 'chili con carne', 'fried chicken',
            # Platos de cuchara / hogar
            'lentejas guisadas', 'garbanzos estofados', 'sopa de pollo',
            'estofado de ternera', 'potaje de verduras'
        },
        'en': {
            'paella', 'spanish omelette', 'gazpacho', 'salmorejo', 'stew',
            'fabada', 'octopus galician style', 'tomato bread', 'ratatouille',
            'croquettes', 'empanada', 'breadcrumbs stew', 'oxtail stew',
            'pizza', 'burger', 'hot dog', 'sushi', 'ramen', 'udon',
            'tacos', 'burritos', 'enchiladas', 'lasagna', 'carbonara',
            'risotto', 'curry', 'pad thai', 'poke bowl', 'falafel',
            'kebab', 'shawarma', 'chili con carne', 'fried chicken',
            'lentil stew', 'chickpea stew', 'chicken soup',
            'beef stew', 'vegetable stew'
        },
    },
}

def extract_entities(clean_text: str, lang: str) -> dict:
    """Extrae entidades culinarias por coincidencia de tokens normalizados."""
    tokens = set(clean_text.lower().split())
    return {
        cat: sorted(tokens & dic.get(lang, set()))
        for cat, dic in ENTITIES.items()
        if tokens & dic.get(lang, set())
    }


# =================
# VÍA 2: EMBEDDINGS
# =================

class EntityExtractor:
    """Extractor de entidades mediante similitud del coseno con spaCy."""
    VECTORS = {
        "es": {
            "comida_base":      "cocina gastronomía receta comida",
            "origen_cultura":   "italiana mexicano japonés país cultura tradicional",
            "tipo_dieta":       "vegano vegetariano celíaco saludable ligero",
            "ingrediente":      "ingredientes lácteo carne pescado verdura tubérculo fruta",
            "utensilio":        "sartén cacerola batidora cubiertos olla",
            "electrodomestico": "vitrocerámica nevera congelador horno freidora tostadora",
        },
        "en": {
            "comida_base":      "cooking gastronomy recipe food",
            "origen_cultura":   "Italian Mexican Japanese country culture traditional",
            "tipo_dieta":       "vegan vegetarian celiac healthy light",
            "ingrediente":      "ingredients dairy meat fish vegetable tuber fruit",
            "utensilio":        "frying pan saucepan blender cutlery pot",
            "electrodomestico": "ceramic hob fridge freezer oven frier toaster",
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

    def __init__(self, langs={"en": "en_core_web_md", "es": "es_core_news_md"}):
        self.nlp = {v: spacy.load(langs[v]) for v in langs}
        self.vectors = {}
        self.neg_and_sust = {}

    def add_vectors(self, vectors=VECTORS, neg_and_sust=NEG_AND_SUST):
        self.vectors = {
            lang: {cat: self.nlp[lang](vectors[lang][cat]) for cat in vectors[lang]}
            for lang in vectors
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
