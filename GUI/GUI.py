import flet as ft
import asyncio
from auxiliar.utils import predict_language, load, prettify, REV_INTENT
import os
import random
import sys

async def main(page: ft.Page):

    extractor = None
    detector = None

    # Configuración
    page.title = "FAQs"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 450
    page.window_height = 400
    # Para no estroperar rutas al compilar
    if hasattr(sys, '_MEIPASS'):
        page.window.icon = os.path.join(sys._MEIPASS, "icon.ico")
    else:
        page.window.icon = os.path.abspath("icon.ico")
    page.window_resizable = False
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 40
    page.update()

    # Lógica de la app
    async def go_to_github(e):
        await page.launch_url("https://github.com/antoniommff/pln-faq-assistant")

    async def enviar_click(e):
        nonlocal extractor
        nonlocal detector
        nonlocal preprocesor
        nonlocal vectorizers
        nonlocal intention_models

        if extractor is None or detector is None or preprocesor is None:
            output_text.value = "El modelo sigue cargando..."
            output_text.color = ft.Colors.ORANGE_400

        elif not input_field.value:
            output_text.value = "Escribe algo primero."
            output_text.color = ft.Colors.RED_400

        else:
            text = input_field.value.rstrip("\r\n")
            lang = predict_language(text, detector)

            clean_text = preprocesor.process_text(text=text, lang=lang, is_predict=False)

            items, entities = extractor.extract(
                clean_text=clean_text,
                lang=lang,
            )

            vector = vectorizers[lang].transform([clean_text])
            intent_num = int(intention_models[lang].predict(vector)[0])
            intent_name = REV_INTENT.get(intent_num, 'unknown')

            display = "\n" + prettify(entities) if upper_button.content == "Categorías" else items
            output_text.value = f"Idioma (T1): {lang.upper()}\n\nIntención (T2): {intent_name}\n\nEntidades (T3): {display}"
            output_text.color = ft.Colors.GREEN_400

        page.update()

    async def change_text_button(e):
        upper_button.content = "Lista" if upper_button.content == "Categorías" else "Categorías"
        page.update()

    async def rotate_title():
        new_idx = idx_message
        while new_idx == idx_message:
            new_idx = random.randint(0, len(messages) - 1)

        if random.randint(0, 1000) == 17:
            title_text.value = "¡Literalmente 1 entre 1000!"

        title_text.value = messages[new_idx]
        animated_title.content = ft.Text(
            title_text.value,
            size=30,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_200,
        )
        page.update()

    async def chage_theme(e):
        theme_switch.thumb_icon = (
            ft.Icons.DARK_MODE if theme_switch.value else ft.Icons.LIGHT_MODE
        )

        if theme_switch.value:
            page.theme_mode = ft.ThemeMode.LIGHT
        else:
            page.theme_mode = ft.ThemeMode.DARK

        page.update()


    # Elementos de la app

    upper_button = ft.Button(
        content="Lista",
        on_click=change_text_button,
    )

    theme_switch = ft.Switch(
        value=False,
        thumb_icon=ft.Icons.LIGHT_MODE,
        on_change=chage_theme
    )

    # Lista de mensajes para el ciclo
    messages = [
        "Bienvenido", "Welcome", "Ask anything!", "Consulta tus dudas",
        "FAQ's", "¡Escribe algo!", "Comida comida comida", "Now with 20% less cyanide",
        "Condimentando tus dudas", "Sin grumos en la información",
        "¿Se te quemó el 'arro'? ¡Pregunta!", "El ingrediente secreto es el FAQ",
        "La receta del éxito (y del flan)", "From (data) farm to screen",
        "Don't let your soup get cold!", "Gordon-Ramsay-approved (maybe)",
    ]
    idx_message = 0

    title_text = ft.Text(
        messages[idx_message],
        size=30,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_200,
    )

    # Componente que gestiona la animación de deslizamiento
    animated_title = ft.AnimatedSwitcher(
        title_text,
        transition=ft.AnimatedSwitcherTransition.FADE,  # Desliza hacia la derecha
        duration=500,  # Duración de la animación en ms
        reverse_duration=500,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
    )

    input_field = ft.TextField(
        label="Como hacer pollo al horno",
        width=400,
        border_radius=15,
    )
    input_field.on_submit = enviar_click

    output_text = ft.Text(
        value="Cargando motor IA...",
        color=ft.Colors.ORANGE_400,
    )

    button = ft.Button(
        "Enviar",
        on_click=enviar_click,
    )

    # Construcción de la app
    page.add(
        ft.Stack(
            expand=True,
            controls=[
                # =========================
                # CONTENIDO PRINCIPAL
                # =========================
                ft.Column(
                    controls=[
                        # Fila superior
                        ft.Row(
                            controls=[
                                upper_button,
                                ft.IconButton(
                                    icon=ft.Icons.CODE,
                                    tooltip="Ver en GitHub",
                                    on_click=go_to_github,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),

                        # Contenido central
                        ft.Column(
                            controls=[
                                animated_title,
                                ft.Container(height=20),
                                input_field,
                                button,
                                output_text,
                                ft.Container(expand=True),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.CENTER,
                            expand=True,
                        ),
                    ],
                    expand=True,
                ),

                # =========================
                # SWITCH ABAJO DERECHA
                # =========================
                ft.Container(
                    content=theme_switch,
                    alignment=ft.Alignment(1, 1),
                    padding=20,
                ),
            ],
        )
    )

    page.update()

    # =========================
    # CARGA EN SEGUNDO PLANO
    # =========================

    extractor, detector, preprocesor, vectorizers, intention_models = await asyncio.to_thread(load)

    output_text.value = "Modelo cargado correctamente."
    output_text.color = ft.Colors.GREEN_400

    page.update()

    # Bucle infinito para la rotación cada 15 segundos
    while True:
        await asyncio.sleep(15)
        await rotate_title()


if __name__ == "__main__":
    ft.run(main)
