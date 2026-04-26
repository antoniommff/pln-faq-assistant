import flet as ft
from auxiliar.entidades import EntityExtractor



def main(page: ft.Page):
    extractor = None
    # 1. Configuración de la página (Ventana)
    page.title = "FAQs"
    page.theme_mode = ft.ThemeMode.DARK # Modo oscuro automático
    page.window_width = 450
    page.window_height = 400
    page.window_resizable = False
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 40

    # 2. Lógica de la aplicación
    def enviar_click(e):
        if extractor is None:
            texto_salida.value = "El modelo aún se está cargando..." # MUY IMPROBABLE QUE PASE LOL
            texto_salida.color = ft.Colors.ORANGE_400
            return
        if not campo_entrada.value:
            texto_salida.value = "Por favor, escribe algo primero."
            texto_salida.color = ft.Colors.RED_400
        else:
            items, _ = extractor.extract(campo_entrada.value.rstrip("\r").rstrip("\n"))
            texto_salida.value = f"Se han extraido las siguientes entidades: {items}"
            texto_salida.color = ft.Colors.GREEN_400

        page.update() # Refresca la interfaz para mostrar los cambios

    # 3. Componentes de la interfaz (Widgets)
    titulo = ft.Text(
        "Bienvenido",
        size=30,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_200
    )

    campo_entrada = ft.TextField(
        label="Escribe algo aquí...",
        border_radius=15,
        border_color=ft.Colors.BLUE_700,
        focused_border_color=ft.Colors.BLUE_400,
        width=300,
        text_align=ft.TextAlign.LEFT,
    )

    boton_enviar = ft.Button(
        content=ft.Text("Enviar datos"),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        on_click=enviar_click
    )

    texto_salida = ft.Text(
        value="Esperando entrada...",
        size=16,
        italic=True,
        color=ft.Colors.GREY_500
    )

    # 4. Agregar componentes a la página
    page.add(
        titulo,
        ft.Divider(height=20, color="transparent"),
        campo_entrada,
        ft.Divider(height=10, color="transparent"),
        boton_enviar,
        ft.Divider(height=30, color="transparent"),
        texto_salida
    )

    # Muestra un mensajito mientras carga # No funciona, quizas un poco de multithreading molaria
    texto_salida.value = "Cargando motor de IA..."
    page.update()

    # Carga el modelo
    extractor = EntityExtractor()
    extractor.add_vectors()

    # Avisa que ya terminó
    texto_salida.value = "Esperando entrada..."
    page.update()


if __name__ == "__main__":
    ft.run(main)

