import flet as ft
import math
import asyncio


def main(page: ft.Page):
    page.title = "Liquid UI Interface"
    page.bgcolor = "#121212"
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # --- Цвета ---
    ACCENT_CYAN = "#00E5FF"
    ACCENT_GREEN = "#00E676"
    ACCENT_RED = "#FF1744"
    ACCENT_PURPLE = "#E040FB"
    TEXT_COLOR = "#FFFFFF"
    BG_PANEL = "#1E1E1E"

    current_value = 65.0
    is_auto_playing = True

    # =====================================================================
    # Универсальная функция создания колбы с жидкостью
    # =====================================================================
    def create_flask(theme_color, bg_color, is_glass=False, size=150):
        # Основной фон колбы (круг)
        bg = ft.Container(
            width=size, height=size, border_radius=size / 2,
            bgcolor=bg_color,
            border=ft.Border.all(4, "#333333" if not is_glass else "#E0E0E0"),
            shadow=ft.BoxShadow(blur_radius=10, color="#00000080") if not is_glass else None
        )

        # Жидкость (прямоугольник, который мы будем двигать снизу вверх)
        liquid = ft.Container(
            width=size - 8, height=0,
            bgcolor=theme_color,
            border_radius=ft.BorderRadius(0, 0, (size - 8) / 2, (size - 8) / 2),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER, end=ft.Alignment.BOTTOM_CENTER,
                colors=[theme_color, "#1A1A1A"]  # Легкий градиент для объема
            )
        )

        # Текст (всегда по центру)
        text = ft.Text("65%", size=28, color="#FFFFFF" if not is_glass else "#333333", weight=ft.FontWeight.BOLD)

        # Контейнер, который обрезает жидкость (имитация стекла)
        # В Flet 1.0 для этого лучше всего подходит Container с border_radius
        # и выравниванием по низу (чтобы жидкость росла вверх)
        liquid_wrapper = ft.Container(
            width=size - 8, height=size - 8,
            border_radius=(size - 8) / 2,
            alignment=ft.Alignment.BOTTOM_CENTER,
            content=liquid,
            # Обрезаем всё, что выходит за пределы
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS
        )

        # Блик (для красоты)
        glare = ft.Container(
            width=size * 0.3, height=size * 0.3,
            bgcolor="#FFFFFF10",
            border_radius=size * 0.15,
            left=size * 0.15, top=size * 0.15,
            rotate=ft.Rotate(angle=math.radians(-20))
        )

        # Собираем
        stack = ft.Stack([
            bg,
            # Жидкость центрируем внутри колбы с отступом 4px (рамка)
            ft.Container(content=liquid_wrapper, left=4, top=4),
            glare,
            # Текст поверх всего
            ft.Container(content=text, width=size, height=size, alignment=ft.Alignment.CENTER)
        ], width=size, height=size)

        def update(val):
            # Высота жидкости внутри контейнера
            # Максимальная высота = size - 8
            h = (val / 100.0) * (size - 8)
            liquid.height = h
            text.value = f"{int(val)}%"

        return stack, update

    # =====================================================================
    # 1. НЕОНОВАЯ ДУГА (Отдельный вид, без жидкости)
    # =====================================================================
    def create_neon_arc(size=150):
        center = size / 2
        radius = size * 0.42

        bg = ft.Container(width=size, height=size, border_radius=size / 2, bgcolor="#0A0A0A",
                          border=ft.Border.all(2, "#333333"))
        arc = ft.ProgressRing(width=radius * 2, height=radius * 2, stroke_width=8, value=0.65, color=ACCENT_CYAN)
        text = ft.Text("65%", size=26, color=TEXT_COLOR, weight=ft.FontWeight.BOLD)

        def update(val):
            arc.value = val / 100.0
            text.value = f"{int(val)}%"

        stack = ft.Stack([
            bg,
            ft.Container(content=arc, width=size, height=size, alignment=ft.Alignment.CENTER),
            ft.Container(content=text, width=size, height=size, alignment=ft.Alignment.CENTER)
        ], width=size, height=size)
        return stack, update

    # =====================================================================
    # СОЗДАЕМ ВСЕ ПРИБОРЫ
    # =====================================================================
    # 1. Неоновая дуга
    w1, u1 = create_neon_arc(150)

    # 2. Зеленая жидкость (темный фон)
    w2, u2 = create_flask(ACCENT_GREEN, "#222222", is_glass=False, size=150)

    # 3. Красная жидкость (светлое стекло)
    w3, u3 = create_flask(ACCENT_RED, "#F5F5F5", is_glass=True, size=150)

    # 4. Фиолетовая жидкость (темный фон)
    w4, u4 = create_flask(ACCENT_PURPLE, "#1A1A1A", is_glass=False, size=150)

    # 5. Оранжевая жидкость (стекло с ободком)
    w5, u5 = create_flask("#FF9800", "#E0E0E0", is_glass=True, size=150)

    def update_all(val):
        u1(val)
        u2(val)
        u3(val)
        u4(val)
        u5(val)

    # --- ПОЛЗУНОК ---
    slider_text = ft.Text("УРОВЕНЬ: 65%", size=16, color="#AAAAAA", weight=ft.FontWeight.BOLD)

    def on_slider_change(e):
        nonlocal is_auto_playing
        is_auto_playing = False
        val = e.control.value
        slider_text.value = f"УРОВЕНЬ: {int(val)}%"
        update_all(val)
        page.update()

    slider = ft.Slider(min=0, max=100, value=65, divisions=100, active_color=ACCENT_CYAN, thumb_color=ACCENT_CYAN,
                       on_change=on_slider_change)

    # --- ФОНОВАЯ АНИМАЦИЯ ---
    async def auto_animate():
        nonlocal current_value, is_auto_playing
        direction = 1
        while True:
            if is_auto_playing:
                current_value += 1.0 * direction
                if current_value >= 100:
                    current_value = 100
                    direction = -1
                elif current_value <= 0:
                    current_value = 0
                    direction = 1

                slider.value = current_value
                slider_text.value = f"УРОВЕНЬ: {int(current_value)}%"
                update_all(current_value)
                page.update()

            await asyncio.sleep(0.03)

    page.run_task(auto_animate)
    update_all(current_value)

    # --- СБОРКА ---
    page.add(
        ft.Text("Liquid UI Interface", size=32, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
        ft.Text("Интерактивные датчики уровня", size=14, color="#888888"),
        ft.Container(height=30),
        ft.Container(
            content=ft.Row([w1, w2, w3, w4, w5], alignment=ft.MainAxisAlignment.CENTER, spacing=20, wrap=True),
            bgcolor=BG_PANEL, padding=20, border_radius=15
        ),
        ft.Container(height=30),
        slider_text,
        ft.Container(content=slider, width=600)
    )


if __name__ == "__main__":
    ft.run(main)