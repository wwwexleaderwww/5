import flet as ft
import math


def main(page: ft.Page):
    page.title = "Индикаторы направления"
    page.bgcolor = "#E0E0E0"  # Светлый фон (шахматка на фото)
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Состояние для спидометра
    current_speed = 0.0
    speed_text_ref = None
    needle_ref = None

    # =====================================================================
    # 1. СПИДОМЕТР (Слева)
    # =====================================================================
    def create_speedometer(size=200):
        nonlocal speed_text_ref, needle_ref
        center = size / 2
        radius = size * 0.4

        # Фон
        bg = ft.Container(width=size, height=size, border_radius=size / 2, bgcolor="#2C2C2C",
                          border=ft.Border.all(8, "#333333"))

        # Цветная шкала (дуга из точек)
        arc_dots = []
        for i in range(0, 101, 2):
            angle_deg = 135 + (i / 100) * 270
            rad = math.radians(angle_deg)
            x = center + radius * math.cos(rad)
            y = center + radius * math.sin(rad)

            # Цвет: зеленый -> желтый -> красный
            if i < 50:
                color = "#00E676"
            elif i < 80:
                color = "#FFEB3B"
            else:
                color = "#F44336"

            arc_dots.append(ft.Container(width=4, height=4, bgcolor=color, border_radius=2, left=x - 2, top=y - 2))

        # Деления и цифры
        for i in range(0, 101, 10):
            angle_deg = 135 + (i / 100) * 270
            rad = math.radians(angle_deg)

            # Цифры
            tx = center + (radius - 25) * math.cos(rad)
            ty = center + (radius - 25) * math.sin(rad)
            arc_dots.append(
                ft.Container(content=ft.Text(str(i), size=10, color="#FFFFFF"), left=tx - 10, top=ty - 7, width=20,
                             alignment=ft.Alignment.CENTER)
            )

        # Стрелка
        needle = ft.Container(
            width=6, height=radius - 10, bgcolor="#FF5252", border_radius=3,
            left=center - 3, top=center - (radius - 10),
            rotate=ft.Rotate(angle=math.radians(135), alignment=ft.Alignment.BOTTOM_CENTER)
        )
        needle_ref = needle

        cap = ft.Container(width=20, height=20, bgcolor="#FF5252", border_radius=10, left=center - 10, top=center - 10)

        # Текст скорости
        speed_txt = ft.Text("0", size=28, color="#FFFFFF", weight=ft.FontWeight.BOLD)
        speed_text_ref = speed_txt

        stack = ft.Stack([
            bg, *arc_dots, needle, cap,
            ft.Container(content=speed_txt, width=size, height=size, alignment=ft.Alignment.BOTTOM_CENTER,
                         padding=ft.Padding(0, 0, 0, 30))
        ], width=size, height=size)

        return stack

    # =====================================================================
    # 2. ДЖОЙСТИКИ (Справа)
    # =====================================================================
    def create_joystick(theme_color, bg_color, size=150):
        center = size / 2

        # Кнопка в центре (обновить)
        center_btn = ft.Container(
            width=40, height=40, border_radius=20,
            border=ft.Border.all(2, theme_color),
            alignment=ft.Alignment.CENTER,
            content=ft.Icon(ft.Icons.REFRESH, color=theme_color, size=20)
        )

        # Создаем 4 стрелки (треугольники)
        # Для простоты используем иконки стрелок
        arrow_up = ft.Icon(ft.Icons.ARROW_DROP_UP, color=theme_color, size=24)
        arrow_down = ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=theme_color, size=24)
        arrow_left = ft.Icon(ft.Icons.ARROW_LEFT, color=theme_color, size=24)
        arrow_right = ft.Icon(ft.Icons.ARROW_RIGHT, color=theme_color, size=24)

        # Позиции
        pad = 15

        def on_press(direction):
            nonlocal current_speed
            if direction == "UP":
                current_speed += 10
            elif direction == "DOWN":
                current_speed -= 10
            elif direction == "LEFT":
                current_speed -= 5
            elif direction == "RIGHT":
                current_speed += 5
            elif direction == "CENTER":
                current_speed = 0  # Сброс

            # Ограничиваем скорость
            if current_speed > 100: current_speed = 100
            if current_speed < 0: current_speed = 0

            # Обновляем спидометр
            speed_text_ref.value = str(int(current_speed))
            angle = math.radians(135 + (current_speed / 100) * 270)
            needle_ref.rotate = ft.Rotate(angle=angle, alignment=ft.Alignment.BOTTOM_CENTER)
            page.update()

        # Оборачиваем иконки в GestureDetector для кликов
        up_btn = ft.GestureDetector(on_tap=lambda e: on_press("UP"), content=ft.Container(content=arrow_up, padding=5))
        down_btn = ft.GestureDetector(on_tap=lambda e: on_press("DOWN"),
                                      content=ft.Container(content=arrow_down, padding=5))
        left_btn = ft.GestureDetector(on_tap=lambda e: on_press("LEFT"),
                                      content=ft.Container(content=arrow_left, padding=5))
        right_btn = ft.GestureDetector(on_tap=lambda e: on_press("RIGHT"),
                                       content=ft.Container(content=arrow_right, padding=5))
        center_btn_action = ft.GestureDetector(on_tap=lambda e: on_press("CENTER"), content=center_btn)

        # Сборка в Stack
        stack = ft.Stack([
            ft.Container(width=size, height=size, border_radius=size / 2, bgcolor=bg_color,
                         border=ft.Border.all(4, theme_color)),
            ft.Container(content=up_btn, left=center - 20, top=pad),
            ft.Container(content=down_btn, left=center - 20, top=size - pad - 30),
            ft.Container(content=left_btn, left=pad, top=center - 20),
            ft.Container(content=right_btn, left=size - pad - 30, top=center - 20),
            ft.Container(content=center_btn_action, left=center - 20, top=center - 20)
        ], width=size, height=size)

        return stack

    # =====================================================================
    # СОЗДАЕМ ЭЛЕМЕНТЫ
    # =====================================================================
    gauge_ui = create_speedometer(200)

    # 4 джойстика с разными темами (как на фото)
    joy_dark = create_joystick("#00BCD4", "#2C2C2C")  # Темный
    joy_light = create_joystick("#FF9800", "#F5F5F5")  # Светлый (оранжевый)
    joy_blue = create_joystick("#00BCD4", "#1565C0")  # Синий
    joy_purple = create_joystick("#9C27B0", "#283593")  # Фиолетовый

    # =====================================================================
    # СБОРКА СТРАНИЦЫ
    # =====================================================================
    page.add(
        ft.Text("Индикаторы направления", size=24, weight=ft.FontWeight.BOLD, color="#333333"),
        ft.Container(height=20),
        ft.Row(
            [
                gauge_ui,
                joy_dark,
                joy_light,
                joy_blue,
                joy_purple
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
            wrap=True
        ),
        ft.Container(height=20),
        ft.Text("Нажимай на стрелки джойстиков, чтобы изменить скорость", color="#666666")
    )


if __name__ == "__main__":
    ft.run(main)