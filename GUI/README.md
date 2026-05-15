# Guía de uso e isntalación de la interfáz
Clona el repositorio y entra en la carpeta.
```
git clone https://github.com/usuario/repositorio
cd pln-faq-assistant
```

## Instalación

Para utilizar la GUI sin hacer uso de los ejecutables proporcionados. Instalando los paquetes necesarios. Se hace uso de `pyenv+virtualenv` pero cualquier gestor de paquetes es válido.

```
pyenv virtualenv 3.12 FAQ
pyenv activate FAQ
```
Instalamos las dependencias de build (son las mismas que para la interfáz).

```
python -m pip install --upgrade pip
pip install -R requirements-build.txt
python -m spacy download es_core_news_md
python -m spacy download en_core_web_md
```
Finalemte podemos lanzar la interfáz mediante el comando

```
python GUI/GUI.py
```

## Compilación
Para compilar seguimos los mismos pasos que en la sección anterior. Además nos aseguramos de tener el sistema actualizado, en caso de ser **linux** se recomienda tener las versiones actualizadas de  `libgtk-3-dev`, `libgstreamer1.0-dev`, `libgstreamer-plugins-base1.0-dev` y `libmpv-dev`.

### Instalando dependencias

#### Linux (Arch)

```
sudo pacman -Syu --needed base-devel gtk3 gstreamer gst-plugins-base mpv
```

#### Linux (Ubuntu/Debian)

```
sudo apt update && sudo apt install -y libgtk-3-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-good1.0-dev libmpv-dev
```

#### Windows/Mac
No hay dependencias adicionales para compilar.

**Nota** No hay build de MacOS de momento pues no tenemos firma de desarrollador (o algo así no tengo Mac)

### Empaquetando
Se utilizar la libreria `pyinstaller` (está en `requirements-build.txt` no hay que instalar por separado).

**Para Windows/Linux**
```
pyinstaller --noconsole --onefile --name "FAQ" --icon="icon.ico" --hidden-import="es_core_news_md" --hidden-import="en_core_web_md" --collect-all="spacy" --collect-all="es_core_news_md" --collect-all="en_core_web_md" --collect-all="flet" --exclude-module="matplotlib" --exclude-module="scipy" GUI/GUI.py
```
Tras unos segundos (o minutos) se creará el ejecutable que contiene todo lo necesarios para usar la app.
## Uso
