import flet as ft
import math


def main(page: ft.Page):
    page.title = "Приборная панель (4 стиля)"
    page.bgcolor = "#1E1E1E"  # Темный фон для контраста
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # =====================================================================
    # 1. ПРИБОР №1: МИНИМАЛИСТИЧНЫЙ ПРОГРЕСС (Слева)
    # =====================================================================
    def create_minimal_progress(size=200):
        center = size / 2
        radius = size * 0.4

        # Текст внутри
        percent_text = ft.Text("0%", size=32, color="#00BFA5", weight=ft.FontWeight.BOLD)
        task_text = ft.Text("выполнено", size=10, color="#00BFA5")

        # Стрелка-указатель (точка на конце дуги)
        dot = ft.Container(
            width=10, height=10, bgcolor="#00BFA5", border_radius=5,
            left=center + radius * math.cos(math.radians(135)) - 5,
            top=center + radius * math.sin(math.radians(135)) - 5
        )

        # Фон дуги (серый)
        arc_bg = ft.ProgressRing(
            width=size * 0.8, height=size * 0.8, stroke_width=6, value=1.0,
            color="#333333", bgcolor="transparent"
        )

        # Наша заливка (будем менять value)
        arc_fill = ft.ProgressRing(
            width=size * 0.8, height=size * 0.8, stroke_width=6, value=0.0,
            color="#00BFA5", bgcolor="transparent"
        )

        # Сборка
        stack = ft.Stack([
            ft.Container(width=size, height=size, bgcolor="transparent"),
            ft.Container(content=arc_bg, left=center - size * 0.4, top=center - size * 0.4),
            ft.Container(content=arc_fill, left=center - size * 0.4, top=center - size * 0.4),
            ft.Container(content=ft.Column([percent_text, task_text], alignment=ft.MainAxisAlignment.CENTER,
                                           horizontal_alignment=ft.CrossAxisAlignment.CENTER), width=size, height=size,
                         alignment=ft.Alignment.CENTER),
            dot
        ], width=size, height=size)

        def update(val):
            # Для простоты используем ProgressRing, но двигаем точку
            arc_fill.value = val / 100.0
            percent_text.value = f"{int(val)}%"
            # Двигаем точку по дуге от 135 до 45 градусов (или 90, тут условно)
            angle = math.radians(90 + (val / 100) * 180)
            dot.left = center + radius * math.cos(angle) - 5
            dot.top = center + radius * math.sin(angle) - 5

        return stack, update

    # =====================================================================
    # 2. ПРИБОР №2: СПИДОМЕТР С ЗОНАМИ (Второй слева)
    # =====================================================================
    def create_zone_speedometer(size=200):
        center = size / 2
        radius = size * 0.4

        # Фон
        bg = ft.Container(width=size, height=size, border_radius=size / 2, bgcolor="#2C2C2C",
                          border=ft.Border.all(6, "#444444"))

        # Деления
        ticks = []
        for i in range(0, 101, 10):
            angle = math.radians(135 + (i / 100) * 270)
            # Внутренняя точка
            x1 = center + (radius - 10) * math.cos(angle)
            y1 = center + (radius - 10) * math.sin(angle)
            # Внешняя точка
            x2 = center + radius * math.cos(angle)
            y2 = center + radius * math.sin(angle)

            # Рисуем как маленький повернутый контейнер
            ticks.append(
                ft.Container(
                    width=2, height=10, bgcolor="#AAAAAA",
                    left=(x1 + x2) / 2 - 1, top=(y1 + y2) / 2 - 5,
                    rotate=ft.Rotate(angle=angle + math.pi / 2, alignment=ft.Alignment.CENTER)
                )
            )

        # Цифровое табло
        display = ft.Text("0", size=24, color="#FF5252", weight=ft.FontWeight.BOLD)

        # Стрелка
        needle = ft.Container(
            width=4, height=radius - 10, bgcolor="#FF5252", border_radius=2,
            left=center - 2, top=center - (radius - 10),
            rotate=ft.Rotate(angle=math.radians(135), alignment=ft.Alignment.BOTTOM_CENTER)
        )
        # Ось
        cap = ft.Container(width=16, height=16, bgcolor="#111111", border_radius=8, left=center - 8, top=center - 8,
                           border=ft.Border.all(2, "#555555"))

        stack = ft.Stack([bg, *ticks, needle, cap,
                          ft.Container(content=display, width=size, height=size, alignment=ft.Alignment.CENTER)],
                         width=size, height=size)

        def update(val):
            display.value = str(int(val))
            rad = math.radians(135 + (val / 100) * 270)
            needle.rotate = ft.Rotate(angle=rad, alignment=ft.Alignment.BOTTOM_CENTER)

        return stack, update

    # =====================================================================
    # 3. ПРИБОР №3: ТЕМНЫЙ МИНИМАЛИЗМ С ТИКАМИ (Третий слева)
    # =====================================================================
    def create_dark_dial(size=200):
        center = size / 2
        radius = size * 0.35

        bg = ft.Container(width=size, height=size, border_radius=size / 2, bgcolor="#121212")

        # Тики вокруг
        ticks = []
        for i in range(24):
            angle = math.radians(i * 15)
            # Длина тика зависит от позиции
            tick_len = 15 if i % 2 == 0 else 8
            x = center + (radius + 10) * math.cos(angle)
            y = center + (radius + 10) * math.sin(angle)

            ticks.append(
                ft.Container(
                    width=4, height=tick_len, bgcolor="#AAAAAA", border_radius=2,
                    left=x - 2, top=y - tick_len / 2,
                    rotate=ft.Rotate(angle=angle + math.pi / 2, alignment=ft.Alignment.CENTER)
                )
            )

        # Стрелка (синяя)
        needle = ft.Container(
            width=8, height=radius - 10, bgcolor="#00B0FF", border_radius=4,
            left=center - 4, top=center - (radius - 10),
            rotate=ft.Rotate(angle=math.radians(0), alignment=ft.Alignment.BOTTOM_CENTER)
        )
        cap = ft.Container(width=16, height=16, bgcolor="#00B0FF", border_radius=8, left=center - 8, top=center - 8)

        stack = ft.Stack([bg, *ticks, needle, cap], width=size, height=size)

        def update(val):
            # Стрелка ходит по кругу (360 градусов)
            angle = math.radians((val / 100) * 360)
            needle.rotate = ft.Rotate(angle=angle, alignment=ft.Alignment.BOTTOM_CENTER)

        return stack, update

    # =====================================================================
    # 4. ПРИБОР №4: АВИАГОРИЗОНТ / КОМПАС (Справа)
    # =====================================================================
    def create_horizon(size=220):
        center = size / 2

        # Мы будем использовать Stack с маской (через Container с border_radius)
        # Имитируем небо и землю, двигая их вверх/вниз

        # Фон неба
        sky = ft.Container(width=size, height=size, bgcolor="#2196F3", border_radius=size / 2)
        # Земля (внизу)
        ground = ft.Container(width=size, height=size * 0.5, bgcolor="#8D6E63",
                              border_radius=ft.BorderRadius(0, 0, size / 2, size / 2), top=size / 2)

        # Обертка для неба и земли, которую мы будем двигать
        moving_bg = ft.Container(
            width=size, height=size * 1.5,
            content=ft.Stack([sky, ground]),
            top=-size * 0.25  # Начальное положение
        )

        # Линии на земле
        horizon_lines = ft.Container(
            width=size, height=20,
            bgcolor="transparent",
            content=ft.Text("---", color="#FFFFFF", size=20),
            alignment=ft.Alignment.CENTER,
            top=center - 10
        )

        # Стрелка/Самолетик
        plane = ft.Container(
            width=60, height=10, bgcolor="#FFEB3B", border_radius=5,
            left=center - 30, top=center - 5,
        )

        # Рамка прибора
        frame = ft.Container(width=size, height=size, border_radius=size / 2, border=ft.Border.all(8, "#757575"),
                             bgcolor="transparent")

        # Маска, чтобы небо/земля не вылезали за пределы круга
        # В Flet 1.0 нет clip_behavior, поэтому просто наложим рамку сверху (она закроет края)

        stack = ft.Stack([
            ft.Container(width=size, height=size, border_radius=size / 2, bgcolor="#000000"),  # Темный фон за приборами
            moving_bg,
            horizon_lines,
            plane,
            frame  # Рамка сверху
        ], width=size, height=size)

        def update(val):
            # val 0-100. 50 - ровный горизонт. 0 - нос вверх. 100 - нос вниз.
            # Двигаем фон
            offset = (val - 50) * 1.5  # Смещение фона
            moving_bg.top = -size * 0.25 + offset

        return stack, update

    # =====================================================================
    # СОЗДАЕМ ВСЕ ПРИБОРЫ
    # =====================================================================
    p1_stack, update_p1 = create_minimal_progress(200)
    p2_stack, update_p2 = create_zone_speedometer(200)
    p3_stack, update_p3 = create_dark_dial(200)
    p4_stack, update_p4 = create_horizon(200)

    # Главный ползунок для управления всеми приборами
    main_slider = ft.Slider(min=0, max=100, value=50, divisions=100, label="Значение: {value}%")

    def on_slider_change(e):
        val = main_slider.value
        update_p1(val)
        update_p2(val)
        update_p3(val)
        update_p4(val)
        page.update()

    main_slider.on_change = on_slider_change

    # Инициализация
    on_slider_change(None)

    # =====================================================================
    # СБОРКА СТРАНИЦЫ
    # =====================================================================
    page.add(
        ft.Text("4 Стиля Приборов", size=28, weight=ft.FontWeight.BOLD, color="white"),
        ft.Container(height=20),
        ft.Row(
            [
                ft.Column([p1_stack, ft.Text("Прогресс", color="#AAAAAA")],
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Column([p2_stack, ft.Text("Спидометр", color="#AAAAAA")],
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Column([p3_stack, ft.Text("Компас", color="#AAAAAA")],
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Column([p4_stack, ft.Text("Авиагоризонт", color="#AAAAAA")],
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=30,
            wrap=True
        ),
        ft.Container(height=30),
        ft.Text("Управление всеми приборами:", color="white"),
        main_slider
    )


if __name__ == "__main__":
    ft.run(main)