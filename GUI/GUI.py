import flet as ft
import asyncio
from auxiliar.entidades import EntityExtractor
import os

def load():
    extractor = EntityExtractor()
    extractor.add_vectors()
    return extractor


async def main(page: ft.Page):

    extractor = None

    # Configuración
    page.title = "FAQs"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 450
    page.window_height = 400
    page.window.icon = os.path.abspath("icon.ico") # "logo.ico" # o "logo.png"
    page.window_resizable = False
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 40
    page.update()
    # Logica de la app
    async def enviar_click(e):
        nonlocal extractor

        if extractor is None:
            texto_salida.value = "El modelo sigue cargando..."
            texto_salida.color = ft.Colors.ORANGE_400

        elif not campo_entrada.value:
            texto_salida.value = "Escribe algo primero."
            texto_salida.color = ft.Colors.RED_400

        else:
            items, _ = extractor.extract(
                campo_entrada.value.rstrip("\r\n")
            )

            texto_salida.value = f"Entidades:\n{items}"
            texto_salida.color = ft.Colors.GREEN_400

        page.update()

    # Elementos de la app
    titulo = ft.Text(
        "Bienvenido",
        size=30,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_200
    )

    campo_entrada = ft.TextField(
        label="Escribe algo aquí...",
        width=300,
        border_radius=15,
    )
    campo_entrada.on_submit = enviar_click
    
    texto_salida = ft.Text(
        value="Cargando motor IA...",
        color=ft.Colors.ORANGE_400
    )
    
    boton = ft.ElevatedButton(
        "Enviar",
        on_click=enviar_click
    )
    # Construccion de la app
    page.add(
        titulo,
        campo_entrada,
        boton,
        texto_salida
    )

    page.update()

    # =========================
    # CARGA EN SEGUNDO PLANO
    # =========================

    extractor = await asyncio.to_thread(load)

    texto_salida.value = "Modelo cargado correctamente."
    texto_salida.color = ft.Colors.GREEN_400

    page.update()


if __name__ == "__main__":
    ft.run(main)

