import flet as ft
import math
import asyncio


def main(page: ft.Page):
    page.title = "Компас"
    page.bgcolor = "#E0E0E0"
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Настройки
    SIZE = 300
    CENTER = SIZE / 2
    RADIUS = 130

    # Цвета
    RED_RIM = "#C62828"
    DARK_BLUE = "#1A237E"
    LIGHT_BLUE = "#3949AB"
    NEEDLE_RED = "#E53935"
    NEEDLE_BLUE = "#29B6F6"

    # --- 1. Корпус и фон ---
    # Внешний красный ободок
    rim = ft.Container(
        width=SIZE, height=SIZE, border_radius=SIZE / 2, bgcolor=RED_RIM,
        shadow=ft.BoxShadow(blur_radius=10, color="#00000080")
    )
    # Внутренний темно-синий круг
    dial_bg = ft.Container(
        width=SIZE - 24, height=SIZE - 24, border_radius=(SIZE - 24) / 2,
        bgcolor=DARK_BLUE,
        # Легкий градиент для объема
        gradient=ft.RadialGradient(colors=[LIGHT_BLUE, DARK_BLUE], radius=0.9)
    )

    # --- 2. Буквы и тики ---
    elements = []

    # Буквы N, E, S, W
    directions = [
        ("N", 0, "#FFFFFF"),
        ("E", 90, "#FFFFFF"),
        ("S", 180, "#FFFFFF"),
        ("W", 270, "#FFFFFF")
    ]

    for label, angle_deg, color in directions:
        rad = math.radians(angle_deg - 90)  # -90, чтобы N был сверху
        r_text = RADIUS - 25
        x = CENTER + r_text * math.cos(rad)
        y = CENTER + r_text * math.sin(rad)

        elements.append(
            ft.Container(
                content=ft.Text(label, size=20, color=color, weight=ft.FontWeight.BOLD),
                left=x - 15, top=y - 15, width=30, alignment=ft.Alignment.CENTER
            )
        )

    # Белые тики (деления)
    # 4 основных тика (N, E, S, W) и 4 промежуточных (NE, SE, SW, NW)
    for i in range(8):
        angle_deg = i * 45
        rad = math.radians(angle_deg - 90)

        # Основные тики длиннее
        is_major = (i % 2 == 0)
        tick_len = 16 if is_major else 8
        tick_width = 4 if is_major else 2

        # Координаты тика
        r_outer = RADIUS
        r_inner = RADIUS - tick_len

        x_o = CENTER + r_outer * math.cos(rad)
        y_o = CENTER + r_outer * math.sin(rad)
        x_i = CENTER + r_inner * math.cos(rad)
        y_i = CENTER + r_inner * math.sin(rad)

        mid_x = (x_o + x_i) / 2
        mid_y = (y_o + y_i) / 2

        elements.append(
            ft.Container(
                width=tick_width, height=tick_len, bgcolor="#FFFFFF",
                left=mid_x - tick_width / 2, top=mid_y - tick_len / 2,
                rotate=ft.Rotate(angle=rad + math.pi / 2, alignment=ft.Alignment.CENTER)
            )
        )

    # --- 3. Стрелка (Двухцветная) ---
    # Контейнер для всей стрелки (вращается целиком)
    needle_container = ft.Container(width=SIZE, height=SIZE)

    # Красная часть (Север)
    needle_north = ft.Container(
        width=10, height=RADIUS - 30,
        bgcolor=NEEDLE_RED,
        border_radius=ft.BorderRadius(5, 5, 0, 0),  # Острый кончик сверху
        left=CENTER - 5, top=CENTER - (RADIUS - 30),
        gradient=ft.LinearGradient(begin=ft.Alignment.TOP_CENTER, end=ft.Alignment.BOTTOM_CENTER,
                                   colors=[NEEDLE_RED, "#B71C1C"])
    )

    # Синяя часть (Юг)
    needle_south = ft.Container(
        width=10, height=RADIUS - 50,
        bgcolor=NEEDLE_BLUE,
        border_radius=ft.BorderRadius(0, 0, 5, 5),  # Острый кончик снизу
        left=CENTER - 5, top=CENTER,
        gradient=ft.LinearGradient(begin=ft.Alignment.TOP_CENTER, end=ft.Alignment.BOTTOM_CENTER,
                                   colors=["#0288D1", NEEDLE_BLUE])
    )

    # Ось (Белый круг)
    axis = ft.Container(
        width=24, height=24, bgcolor="#FFFFFF", border_radius=12,
        left=CENTER - 12, top=CENTER - 12,
        shadow=ft.BoxShadow(blur_radius=4, color="#00000080")
    )
    axis_inner = ft.Container(
        width=8, height=8, bgcolor="#CCCCCC", border_radius=4,
        left=CENTER - 4, top=CENTER - 4
    )

    # Сборка стрелки
    needle_ui = ft.Stack(
        [needle_north, needle_south, axis, axis_inner],
        width=SIZE, height=SIZE
    )

    # --- 4. Главный Stack ---
    # Накладываем слои: ободок -> фон -> элементы (буквы, тики) -> стрелка
    compass_ui = ft.Stack(
        [
            rim,
            ft.Container(content=dial_bg, width=SIZE, height=SIZE, alignment=ft.Alignment.CENTER),
            *elements,
            needle_ui
        ],
        width=SIZE, height=SIZE
    )

    # --- ЛОГИКА ВРАЩЕНИЯ ---
    # Начальный угол (0 - Север)
    current_angle = 0.0

    def update_compass(angle):
        # Поворачиваем весь слой стрелки
        needle_ui.rotate = ft.Rotate(angle=math.radians(angle), alignment=ft.Alignment.CENTER)
        page.update()

    # Ползунок для ручного управления
    slider = ft.Slider(min=0, max=360, value=0, divisions=360, label="{value}°", width=400)

    def on_slider_change(e):
        nonlocal is_auto
        is_auto = False
        update_compass(slider.value)

    slider.on_change = on_slider_change

    # Кнопка "Автопилот"
    is_auto = True

    async def auto_rotate():
        nonlocal current_angle, is_auto
        while True:
            if is_auto:
                current_angle = (current_angle + 0.5) % 360
                slider.value = current_angle
                update_compass(current_angle)
            await asyncio.sleep(0.03)

    page.run_task(auto_rotate)

    # Кнопка включения/выключения автопилота
    def toggle_auto(e):
        nonlocal is_auto
        is_auto = not is_auto
        auto_btn.text = "Остановить" if is_auto else "Включить автопилот"
        auto_btn.bgcolor = "#F44336" if is_auto else "#4CAF50"
        page.update()

    auto_btn = ft.Button(
        content=ft.Text("Остановить", color="white"),
        bgcolor="#F44336",
        on_click=toggle_auto,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
    )

    # --- ВЫВОД ---
    page.add(
        ft.Text("Компас", size=28, weight=ft.FontWeight.BOLD, color="#333333"),
        ft.Container(height=20),
        compass_ui,
        ft.Container(height=20),
        ft.Text("Управление направлением:", size=14, color="#666666"),
        slider,
        ft.Container(height=10),
        auto_btn
    )


if __name__ == "__main__":
    ft.run(main)