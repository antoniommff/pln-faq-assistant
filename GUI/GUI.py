import flet as ft
import asyncio
from auxiliar.utils import predict_language, load, prettify, REV_INTENT
import os
import random


async def main(page: ft.Page):

    extractor = None
    detector = None

    # Configuración
    page.title = "FAQs"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 450
    page.window_height = 400
    page.window.icon = os.path.abspath("icon.ico")
    page.window_resizable = False
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 40
    page.update()

    # Lógica de la app
    async def ir_a_github(e):
        await page.launch_url("https://github.com/antoniommff/pln-faq-assistant")

    async def enviar_click(e):
        nonlocal extractor
        nonlocal detector
        nonlocal preprocesor
        nonlocal vectorizers
        nonlocal intention_models

        if extractor is None or detector is None or preprocesor is None:
            texto_salida.value = "El modelo sigue cargando..."
            texto_salida.color = ft.Colors.ORANGE_400

        elif not campo_entrada.value:
            texto_salida.value = "Escribe algo primero."
            texto_salida.color = ft.Colors.RED_400

        else:
            text = campo_entrada.value.rstrip("\r\n")
            lang = predict_language(text, detector)

            clean_text = preprocesor.process_text(text=text, lang=lang, is_predict=True)

            items, entities = extractor.extract(
                clean_text=clean_text,
                lang=lang,
            )
            vector = vectorizers[lang].transform([clean_text])
            intent_num = int(intention_models[lang].predict(vector)[0])
            intent_name = REV_INTENT.get(intent_num, 'unknown')

            display = "\n" + prettify(entities) if boton_superior.content == "Categorías" else items
            texto_salida.value = f"Idioma (T1): {lang.upper()}\n\nIntención (T2): {intent_name}\n\nEntidades (T3): {display}"
            texto_salida.color = ft.Colors.GREEN_400

        page.update()

    async def cambiar_texto_boton(e):
        boton_superior.content = "Lista" if boton_superior.content == "Categorías" else "Categorías"
        page.update()

    async def rotar_titulo():
        nuevo_idx = idx_mensaje
        while nuevo_idx == idx_mensaje:
            nuevo_idx = random.randint(0, len(mensajes) - 1)

        if random.randint(0, 1000) == 17:
            titulo_texto.value = "¡Literalmente 1 entre 1000!"

        titulo_texto.value = mensajes[nuevo_idx]
        titulo_animado.content = ft.Text(
            titulo_texto.value,
            size=30,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_200,
        )
        page.update()

    boton_superior = ft.Button(
        content="Lista",
        on_click=cambiar_texto_boton,
    )

    # Elementos de la app

    # Lista de mensajes para el ciclo
    mensajes = [
        "Bienvenido", "Welcome", "Ask anything!", "Consulta tus dudas",
        "FAQ's", "¡Escribe algo!", "Comida comida comida", "Now with 20% less cyanide",
        "Condimentando tus dudas", "Sin grumos en la información",
        "¿Se te quemó el 'arro'? ¡Pregunta!", "El ingrediente secreto es el FAQ",
        "La receta del éxito (y del flan)", "From (data) farm to screen",
        "Don't let your soup get cold!", "Gordon-Ramsay-approved (maybe)",
    ]
    idx_mensaje = 0

    titulo_texto = ft.Text(
        mensajes[idx_mensaje],
        size=30,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_200,
    )

    # Componente que gestiona la animación de deslizamiento
    titulo_animado = ft.AnimatedSwitcher(
        titulo_texto,
        transition=ft.AnimatedSwitcherTransition.FADE,  # Desliza hacia la derecha
        duration=500,  # Duración de la animación en ms
        reverse_duration=500,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
    )

    campo_entrada = ft.TextField(
        label="Como hacer pollo al horno",
        width=300,
        border_radius=15,
    )
    campo_entrada.on_submit = enviar_click

    texto_salida = ft.Text(
        value="Cargando motor IA...",
        color=ft.Colors.ORANGE_400,
    )

    boton = ft.Button(
        "Enviar",
        on_click=enviar_click,
    )

    # Construcción de la app
    page.add(
        # Fila superior para el botón izquierdo
        ft.Row(
            controls=[
                boton_superior,
                ft.IconButton(
                    icon=ft.Icons.CODE,
                    tooltip="Ver en GitHub",
                    on_click=ir_a_github,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        # Contenedor central para el resto de elementos
        ft.Column(
            controls=[
                titulo_animado,
                campo_entrada,
                boton,
                texto_salida,
                ft.Container(expand=True),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,  # Asegura que el contenido se mantenga centrado
        ),
    )

    page.update()

    # =========================
    # CARGA EN SEGUNDO PLANO
    # =========================

    extractor, detector, preprocesor, vectorizers, intention_models = await asyncio.to_thread(load)

    texto_salida.value = "Modelo cargado correctamente."
    texto_salida.color = ft.Colors.GREEN_400

    page.update()

    # Bucle infinito para la rotación cada 15 segundos
    while True:
        await asyncio.sleep(15)
        await rotar_titulo()


if __name__ == "__main__":
    ft.run(main)
