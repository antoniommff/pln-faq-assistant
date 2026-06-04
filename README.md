<p align="center">
    <img src="memoria/images/LogoPLN.jpg" align="center" height="80">
</p>
<p align="center"><h1 align="center">Asistente de Preguntas Frecuentes</h1></p>
<p align="center">
    <em>Proyecto de diseño de sistemas PLN - Máster Universitario en Lógica, Ciencias de la Computación e Inteligencia Artificial - Universidad de Sevilla</em>
</p>
<p align="center">
    <img src="https://img.shields.io/badge/Python-3776AB.svg?style=default&logo=Python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Jupyter-F37626.svg?style=default&logo=Jupyter&logoColor=white" alt="Jupyter">
    <img src="https://img.shields.io/badge/spaCy-09A3D5.svg?style=default&logo=spaCy&logoColor=white" alt="spaCy">
    <img src="https://img.shields.io/badge/scikit--learn-F7931E.svg?style=default&logo=scikitlearn&logoColor=white" alt="scikit-learn">
    <img src="https://img.shields.io/badge/Flet-2979FF.svg?style=default&logo=flutter&logoColor=white" alt="Flet">
</p>
<br>

## Índice

- [Índice](#índice)
- [Visión general](#visión-general)
- [Tareas de PLN](#tareas-de-pln)
  - [T1 · Identificación de idioma](#t1--identificación-de-idioma)
  - [T2 · Clasificación de intención](#t2--clasificación-de-intención)
  - [T3 · Extracción de entidades](#t3--extracción-de-entidades)
  - [T4 · Recuperación de FAQs](#t4--recuperación-de-faqs)
  - [Resultados obtenidos](#resultados-obtenidos)
- [Arquitectura del sistema](#arquitectura-del-sistema)
- [_Dataset_](#dataset)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Primeros pasos](#primeros-pasos)
  - [Requisitos previos](#requisitos-previos)
  - [Instalación del entorno](#instalación-del-entorno)
  - [Ejecutar los _notebooks_](#ejecutar-los-notebooks)
    - [_Notebook_ 1 - Análisis de datos y preprocesamiento](#notebook-1---análisis-de-datos-y-preprocesamiento)
    - [_Notebook_ 2 - Prueba de concepto (PoC)](#notebook-2---prueba-de-concepto-poc)
  - [Ejecutar la GUI](#ejecutar-la-gui)
    - [Opción A — Descargar el ejecutable (Recomendado)](#opción-a--descargar-el-ejecutable-recomendado)
    - [Opción B — Desde el código fuente](#opción-b--desde-el-código-fuente)
    - [Opción C — Compilar un ejecutable _standalone_](#opción-c--compilar-un-ejecutable-standalone)
    - [Uso de la GUI](#uso-de-la-gui)
- [Licencia](#licencia)
- [Autores](#autores)

---

## Visión general

Este proyecto diseña e implementa un **asistente automático de preguntas frecuentes (FAQ)** orientado al dominio de la cocina, con detección de idiomas para **español e inglés**. Dada una consulta en lenguaje natural, determina su idioma, clasifica su intención y extrae las entidades culinarias relevantes, para finalmente recuperar la respuesta más adecuada de una base de FAQs estructurada.

El uso de un _dataset_ de cocina presenta una **variabilidad lingüística inherentemente alta** (*slang*, regionalismos, lenguaje figurado, elipsis), lo que lo convierte en un banco de pruebas adecuado para técnicas de PLN. Más allá del interés académico del manejo de téncicas de PLN, el asistente resuelve una necesidad real: las pequeñas empresas carecen de recursos para mantener _chatbots_ sofisticados, pero sí pueden beneficiarse de un sistema ligero que automatice la respuesta a consultas recurrentes.

El proyecto se desarrolló de forma longitudinal en tres entregas.

| Entrega | Contenido principal |
|---------|---------------------|
| **Entrega 1** | Justificación del dominio, caracterización lingüística, descomposición en tareas PLN, restricciones no técnicas e hipótesis de diseño inicial |
| **Entrega 2** | Revisión de hipótesis, decisiones de representación y modelado, protocolo de evaluación y arquitectura final |
| **Entrega 3** | Prueba de concepto (PoC): implementación, evaluación cuantitativa (T1/T2) y exploración empírica (T3/T4), análisis de errores y reflexión crítica |

La memoria completa del proyecto se encuentra en [`memoria/Tarea2_PLN.pdf`](memoria/Tarea2_PLN.pdf).

---

## Tareas de PLN

### T1 · Identificación de idioma

**Objetivo:** Detectar si la consulta está en español o inglés antes de activar cualquier modelo posterior.

**Enfoque:** Modelo estadístico de **$n$-gramas de caracteres** (longitud 1–5) implementado mediante la librería `lingua`. El detector aplica primero un filtro por reglas (alfabeto, caracteres exclusivos) y luego un clasificador Naive Bayes sobre los $n$-gramas residuales. Esta representación es robusta ante errores ortográficos, préstamos lingüísticos y *code-switching* (p. ej., `"¿A qué temperatura pongo la _airfryer_?"`), ya que la distribución de caracteres a nivel de frase sigue siendo discriminativa aunque el vocabulario sea mixto.

### T2 · Clasificación de intención

**Objetivo:** Asignar a la consulta una de las 8 intenciones culinarias del sistema.

**Intenciones disponibles:** `recipe`, `cook_time`, `ingredient_substitution`, `nutrition_info`, `calories`, `food_last`, `ingredients_list`, `meal_suggestion`.

**Enfoque:** _Pipeline_ **TF-IDF + LinearSVC**, con un vectorizador y clasificador independientes por idioma. El preprocesamiento que precede a la vectorización incluye:
1. Expansión de contracciones (EN) y normalización de *slang* (ES: `kiero -> quiero`, `q -> que`).
2. Tokenización, lematización con excepciones culinarias (`gluten`, `aove`, `pizza`) y conversión a minúsculas.
3. Eliminación de tildes y filtrado de *stopwords*, preservando negaciones semánticamente relevantes (`no`, `sin`, `without`).
4. Unificación de regionalismos (`papa -> patata`, `prawn -> shrimp`).

Este enfoque fue preferido sobre arquitecturas Transformer por su bajo coste computacional en inferencia y su adecuación al volumen del corpus disponible.

### T3 · Extracción de entidades

**Objetivo:** Identificar los conceptos culinarios clave de la consulta (ingredientes, técnicas, utensilios, dietas, países, platos) para contextualizar la intención detectada en T2.

**Dos enfoques implementados y comparados:**

- **Vía léxica (diccionarios controlados):** Intersección entre los _tokens_ normalizados de la consulta y vocabularios culinarios organizados por categoría. Es determinista y muy rápida, pero falla ante sinónimos no contemplados.

- **Vía semántica (spaCy + similitud del coseno):** Los _tokens_ de la consulta se comparan vectorialmente con palabras ancla del dominio usando los *embeddings* estáticos del modelo mediano de spaCy (`es_core_news_md` / `en_core_web_md`, 300 dimensiones). Al no depender de un listado cerrado, recupera entidades fuera del diccionario a costa de introducir ocasionalmente falsos positivos.

### T4 · Recuperación de FAQs

**Objetivo:** Dada la tupla `[Idioma, Intención, Entidades]`, localizar la FAQ más relevante en la base de datos.

**Dos enfoques implementados y comparados:**

- **Whoosh + BM25:** Motor de búsqueda indexada. Rápido y sin dependencias de inferencia, pero sufre dependencia léxica: falla si el vocabulario de la consulta no coincide con el de la FAQ.

- ***Embeddings* + similitud del coseno:** Los vectores de las FAQs se precalculan y se almacenan en memoria. En tiempo de consulta, la entrada se codifica y se filtra primero por idioma e intención; después se puntúa por similitud del coseno, bonificando las FAQs cuyos _tokens_ coincidan con las entidades de T3. Más robusto ante reformulaciones.

> **Nota:** La evaluación de T4 es exploratoria. Al no disponer de una base de datos real de FAQs de cocina, las pruebas se realizan sobre un corpus de demostración de 12 ejemplos (`utils/faqs_demo.py`).

### Resultados obtenidos

Evaluación sobre el conjunto de test de CLINC150 (240 ejemplos por idioma, 8 clases balanceadas). El *baseline* de referencia es un clasificador uniforme (*dummy*): **50 %** para T1 (2 clases) y **12.5 %** para T2 (8 clases).

| Tarea | Modelo | *Accuracy* EN | *Accuracy* ES | F1 macro (EN / ES) |
|-------|--------|-------------|-------------|---------------------|
| **T1** | lingua ($n$-gramas de caracteres) | **100 %** | **100 %** | - |
| **T2** | TF-IDF + LinearSVC (*C* = 0.5) | **92.5 %** | **94.2 %** | **0.925 / 0.942** |
| _Baseline_ (_dummy_) | - | 12.5 % | 12.5 % | - |

---

## Arquitectura del sistema

```
Consulta (texto libre)
        │
        ▼
  ┌────────────┐
  │     C1     │  lingua (n-gramas de caracteres)
  │   Idioma   │  -> Idioma detectado (ES / EN)
  └──────┬─────┘
         │
   ┌─────┴─────┐
   ▼           ▼
┌──────┐   ┌──────┐
│  C2  │   │  C3  │  Diccionarios o
│Intent│   │Entid.│  embeddings
└──┬───┘   └───┬──┘
   │           │  
   └─────┬─────┘
         ▼
   ┌───────────┐
   │     C4    │  Whoosh+BM25 o  
   │    FAQs   │  embeddings+coseno
   └─────┬─────┘
         ▼
  FAQ más relevante
```


---

## *Dataset*

Se utiliza el corpus **CLINC150** (Larson et al., 2019) en su configuración `plus`, disponible en Hugging Face Datasets. CLINC150 es un estándar de la industria para clasificación de intenciones en múltiples dominios.

Para este proyecto, se ha aplicado un **filtrado al subdominio culinario**, reduciendo el problema a **8 intenciones**. Dado que CLINC150 es nativo en inglés, las particiones se tradujeron automáticamente al español mediante `deep_translator` para generar el corpus bilingüe.

Los datos en crudo y preprocesados se encuentran en la carpeta [`data/`](data/).

---

## Estructura del proyecto

```
pln-faq-assistant/
│
├── Analisis_Datos_PLN.ipynb      # Notebook 1: EDA, traducción y preprocesamiento
│  
├── PoC_PLN.ipynb                 # Notebook 2: Modelado y evaluación (T1–T4)
│  
├── requirements.txt              # Dependencias para ejecutar los notebooks
│  
├── requirements-build.txt        # Dependencias para ejecutar/compilar la GUI
│  
├── data/
│   ├── data_train.csv            # CLINC150 filtrado - entrenamiento (EN)
│   ├── data_test.csv             # CLINC150 filtrado - prueba (EN)
│   ├── clean_data_train_en.csv   # Datos preprocesados - entrenamiento (EN)
│   ├── clean_data_test_en.csv    # Datos preprocesados - prueba (EN)
│   ├── clean_data_train_es.csv   # Datos preprocesados - entrenamiento (ES)
│   └── clean_data_test_es.csv    # Datos preprocesados - prueba (ES)
│  
├── models/
│   ├── vectorizer_en.pkl         # Vectorizador TF-IDF entrenado (inglés)
│   ├── vectorizer_es.pkl         # Vectorizador TF-IDF entrenado (español)
│   ├── model_en.pkl              # Clasificador LinearSVC entrenado (inglés)
│   └── model_es.pkl              # Clasificador LinearSVC entrenado (español)
│  
├── utils/
│   ├── __init__.py
│   ├── preprocesamiento.py       # Pipeline de normalización de texto (T1/T2/T3)
│   ├── entidades.py              # Extracción de entidades: diccionarios + spaCy (T3)
│   └── faqs_demo.py              # Base de FAQs de demostración y esquema Whoosh (T4)
│  
├── GUI/
│   ├── GUI.py                    # Aplicación de escritorio (Flet)
│   └── auxiliar/
│       ├── entidades.py          # EntityExtractor adaptado para la GUI
│       ├── preprocesamiento.py   # Pipeline de normalización para la GUI
│       └── utils.py              # Carga de modelos y detección de idioma para la GUI
│  
├── memoria/
│   ├── Tarea2_PLN.tex            # Memoria completa en LaTeX
│   ├── Tarea2_PLN.pdf            # Memoria compilada (PDF)
│   └── images/                   # Imágenes y figuras de la memoria
│  
├── docs/                         # Enunciado oficial de la tarea y documento de ejemplo 
│  
└── .github/                      # Pipeline CI/CD para compilar el ejecutable de la GUI
```

---

## Primeros pasos

### Requisitos previos

- **Python 3.10+** (recomendado 3.12)
- **pip** o cualquier gestor de entornos compatible (`pyenv`, `conda`, `venv`)
- Conexión a internet en la primera ejecución (descarga de modelos de spaCy y *dataset* de Hugging Face)

### Instalación del entorno

1. Clona el repositorio:
    ```sh
    git clone https://github.com/antoniommff/pln-faq-assistant.git
    cd pln-faq-assistant
    ```

2. Crea un entorno virtual e instala las dependencias:
    ```sh
    python -m venv .venv
    source .venv/bin/activate        # En Windows: venv\Scripts\activate
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

3. Descarga los modelos de lenguaje de spaCy:
    ```sh
    python -m spacy download es_core_news_md
    python -m spacy download en_core_web_md
    ```

### Ejecutar los *notebooks*

Se recomienda seguir los *notebooks* **en orden**, ya que el segundo depende de los datos exportados por el primero.

#### *Notebook* 1 - Análisis de datos y preprocesamiento

```sh
jupyter notebook Analisis_Datos_PLN.ipynb
```

Este *notebook* carga el corpus CLINC150, realiza el análisis exploratorio, genera la traducción al español y ejecuta el *pipeline* de preprocesamiento completo. Al finalizar, exporta los ficheros `clean_data_*.csv` a `data/`.

> Si los ficheros `data/clean_data_*.csv` ya existen en el repositorio, este *notebook* no es necesario para ejecutar el segundo.

#### *Notebook* 2 - Prueba de concepto (PoC)

```sh
jupyter notebook PoC_PLN.ipynb
```

Este es el *notebook* principal del proyecto. Evalúa las cuatro tareas del sistema (T1–T4), entrena los modelos de intención y los guarda en `models/`. Puede ejecutarse de forma completa (`Kernel > Restart & Run All`) o celda a celda para explorar cada tarea de forma independiente.

> Los modelos ya entrenados están incluidos en `models/`, por lo que las celdas de evaluación y demostración de T3/T4 pueden ejecutarse directamente sin reentrenar.

### Ejecutar la GUI

La interfaz gráfica integra el identificador de idioma (C1), el clasificador de intención (C2) y el extractor de entidades semántico (C3) en una aplicación de escritorio.

> **Aviso sobre macOS:** Al tratarse de una Prueba de Concepto (PoC) académica/de proyecto, el alcance se ha mantenido simple y el soporte se limita de forma exclusiva a Linux y Windows. No se dispone de un entorno Mac para realizar pruebas, la configuración de dependencias en dicho sistema es más compleja y desconocemos los pasos exactos para garantizar un despliegue exitoso. Por ello, macOS queda fuera de esta PoC.

#### Opción A — Descargar el ejecutable (Recomendado)

Si solo quieres probar la aplicación sin tener que instalar Python ni compilar código, puedes usar la versión ya empaquetada:

1. Ve a la sección _Releases_ en este repositorio de GitHub (en el panel derecho).

2. Descarga el ejecutable correspondiente a tu sistema operativo (por ejemplo, el archivo .exe para Windows).

3. Haz doble clic en el archivo para ejecutar la GUI. (Nota: En Windows, es posible que SmartScreen te lance una advertencia de seguridad al no estar firmado digitalmente; simplemente pulsa en "Más información" y "Ejecutar de todas formas").

#### Opción B — Desde el código fuente
_(Solo Linux/Windows)_ 

1. Instala las dependencias de la GUI (incluye `flet` y sus dependencias de escritorio). Se puede usar cualquier gestor de entornos; aquí se muestra con `pyenv+virtualenv`:
    ```sh
    pyenv virtualenv 3.12 FAQ
    pyenv activate FAQ
    python -m pip install --upgrade pip
    pip install -r requirements-build.txt
    python -m spacy download es_core_news_md
    python -m spacy download en_core_web_md
    ```

2. Lanza la aplicación:
    ```sh
    python GUI/GUI.py
    ```

    La aplicación cargará los modelos de spaCy en segundo plano (puede tardar unos segundos) y mostrará `"Modelo cargado correctamente."` cuando esté lista para recibir consultas.

#### Opción C — Compilar un ejecutable *standalone*

Si has realizado pequeños cambios en el código y quieres empaquetar tu propia versión de la GUI como un único ejecutable que no requiere Python instalado, puedes usar `pyinstaller` (incluido en `requirements-build.txt`).

Antes de empaquetar, en **Linux** es necesario tener las dependencias del sistema actualizadas:

```sh
# Arch Linux
sudo pacman -Syu --needed base-devel gtk3 gstreamer gst-plugins-base mpv

# Ubuntu / Debian
sudo apt update && sudo apt install -y libgtk-3-dev libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev libgstreamer-plugins-good1.0-dev libmpv-dev
```

En **Windows** no hay dependencias adicionales del sistema.

Una vez instaladas las dependencias, ejecuta desde la raíz del repositorio:

```sh
# Linux
pyinstaller --onefile --name "FAQ" --noconsole --icon="GUI/icon.ico" \
    --hidden-import="es_core_news_md" \
    --hidden-import="en_core_web_md" \
    --hidden-import="sklearn" \
    --hidden-import="unidecode" \
    --collect-all="spacy" \
    --collect-all="es_core_news_md" \
    --collect-all="en_core_web_md" \
    --collect-all="flet" \
    --collect-all="sklearn" \
    --collect-all="lingua" \
    --collect-all="spellchecker" \
    --collect-all="contractions" \
    --add-data "models:models" \
    --add-data "GUI/icon.ico:." \
    --exclude-module="matplotlib" \
    GUI/GUI.py

# Windows (cmd)
pyinstaller --onefile --name "FAQ" --noconsole --icon="GUI/icon.ico" ^
    --hidden-import="es_core_news_md" ^
    --hidden-import="en_core_web_md" ^
    --hidden-import="sklearn" ^
    --hidden-import="unidecode" ^
    --collect-all="spacy" ^
    --collect-all="es_core_news_md" ^
    --collect-all="en_core_web_md" ^
    --collect-all="flet" ^
    --collect-all="sklearn" ^
    --collect-all="lingua" ^
    --collect-all="spellchecker" ^
    --collect-all="contractions" ^
    --add-data "models;models" ^
    --add-data "GUI/icon.ico;." ^
    --exclude-module="matplotlib" ^
    GUI/GUI.py

# Windows (PowerShell)
pyinstaller --onefile --name "FAQ" --noconsole --icon="GUI/icon.ico" `
    --hidden-import="es_core_news_md" `
    --hidden-import="en_core_web_md" `
    --hidden-import="sklearn" `
    --hidden-import="unidecode" `
    --collect-all="spacy" `
    --collect-all="es_core_news_md" `
    --collect-all="en_core_web_md" `
    --collect-all="flet" `
    --collect-all="sklearn" `
    --collect-all="lingua" `
    --collect-all="spellchecker" `
    --collect-all="contractions" `
    --add-data "models;models" `
    --add-data "GUI/icon.ico;." `
    --exclude-module="matplotlib" `
    GUI/GUI.py
```

Tras unos minutos se generará el ejecutable en `dist/FAQ` (Linux) o `dist/FAQ.exe` (Windows), listo para distribuir sin dependencias adicionales.

#### Uso de la GUI

1. Escribe una consulta culinaria en el campo de texto (en español o inglés).  
   *Ejemplos: `"¿Cómo hago pollo al horno sin gluten?"`, `"How long to boil rice?"`*
2. Pulsa **Enviar** o la tecla `Enter`.
3. La respuesta mostrará:
   - El **idioma detectado** (ES / EN).
   - La **intención** clasificada.
   - Las **entidades extraídas** semánticamente, opcionalmente agrupadas por categoría.
4. El botón superior alterna entre la vista de entidades por **categorías** (desglosado) o como **lista plana**.

> La GUI implementa T1, T2 y T3. La recuperación de FAQs (T4) se explora exclusivamente en `PoC_PLN.ipynb`.

---

## Licencia

Este proyecto está protegido bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## Autores

Proyecto realizado por:

- **Antonio Macías Ferrera** - <a href="https://github.com/antoniommff">@antoniommff</a>
- **Elsa Domínguez González** - <a href="https://github.com/elsdomgon">@elsdomgon</a>
- **Óscar Niño Robles** - <a href="https://github.com/oscninrob">@oscninrob</a>
- **Nicolás Rodríguez Ruiz** - <a href="https://github.com/nicolasrodriguezruiz">@nicolasrodriguezruiz</a>
