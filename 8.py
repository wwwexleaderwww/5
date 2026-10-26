import flet as ft
import math


def main(page: ft.Page):
    page.title = "Приборная панель (5 стилей)"
    page.bgcolor = "#E0E0E0"  # Светлый фон, как на шахматке
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # --- Цвета ---
    COLOR_BLUE = "#42A5F5"
    COLOR_GREEN = "#00E676"
    COLOR_RED = "#FF5252"
    COLOR_DARK = "#222222"
    COLOR_GRAY = "#888888"

    # =====================================================================
    # 1. ПРИБОР №1: "ПИНГ-ПОНГ" (Крайний слева)
    # =====================================================================
    def create_ping_pong(size=160):
        center = size / 2
        radius = size * 0.42

        # Фон круга
        bg = ft.Container(width=size, height=size, border_radius=size / 2, bgcolor=COLOR_DARK)

        # Дуга (толстая)
        arc = ft.ProgressRing(
            width=radius * 2, height=radius * 2, stroke_width=8,
            value=0.5, color=COLOR_BLUE, bgcolor="transparent"
        )
        # Центрируем дугу
        arc_container = ft.Container(content=arc, width=size, height=size, alignment=ft.Alignment.CENTER)

        # Кружок (бегунок), который будет бегать по дуге
        dot = ft.Container(width=20, height=20, bgcolor=COLOR_BLUE, border_radius=10)

        def update(val):
            # Бегунок движется по кругу (от 0 до 360)
            angle = math.radians((val / 100) * 360 - 90)  # -90 чтобы начать сверху
            x = center + radius * math.cos(angle) - 10
            y = center + radius * math.sin(angle) - 10
            dot.left = x
            dot.top = y

            # Сама дуга заливается
            arc.value = val / 100.0

        stack = ft.Stack([bg, arc_container, dot], width=size, height=size)
        return stack, update

    # =====================================================================
    # 2. ПРИБОР №2: "ПРОГРЕСС-БАР" (Второй слева)
    # =====================================================================
    def create_progress_ring(size=160):
        center = size / 2
        radius = size * 0.42

        # Фон
        bg = ft.Container(width=size, height=size, border_radius=size / 2, bgcolor="#EEEEEE")

        # Кольцо (будет расти)
        ring = ft.ProgressRing(
            width=radius * 2, height=radius * 2, stroke_width=10,
            value=0.0, color=COLOR_GREEN, bgcolor="transparent"
        )

        # Деления (тики по внешнему краю)
        ticks = []
        for i in range(36):  # Каждые 10 градусов
            angle = math.radians(i * 10)
            x = center + (radius + 10) * math.cos(angle)
            y = center + (radius + 10) * math.sin(angle)
            ticks.append(
                ft.Container(
                    width=2, height=8, bgcolor=COLOR_BLUE,
                    left=x - 1, top=y - 4,
                    rotate=ft.Rotate(angle=angle + math.pi / 2, alignment=ft.Alignment.CENTER)
                )
            )

        # Текст по центру
        text = ft.Text("0", size=28, color=COLOR_GREEN, weight=ft.FontWeight.BOLD)

        def update(val):
            ring.value = val / 100.0
            text.value = str(int(val))

        stack = ft.Stack(
            [bg, *ticks, ft.Container(content=ring, width=size, height=size, alignment=ft.Alignment.CENTER),
             ft.Container(content=text, width=size, height=size, alignment=ft.Alignment.CENTER)], width=size,
            height=size)
        return stack, update

    # =====================================================================
    # 3. ПРИБОР №3: "МИНИМАЛИЗМ" (Третий, по центру)
    # =====================================================================
    def create_minimal(size=160):
        center = size / 2
        radius = size * 0.42

        # Просто серый круг с точками
        bg = ft.Container(width=size, height=size, border_radius=size / 2, bgcolor="#F0F0F0")

        # Тонкие тики по кругу
        ticks = []
        for i in range(40):
            angle = math.radians(i * 9)
            length = 6 if i % 5 == 0 else 3
            x = center + (radius + 5) * math.cos(angle)
            y = center + (radius + 5) * math.sin(angle)
            ticks.append(
                ft.Container(
                    width=1, height=length, bgcolor=COLOR_DARK,
                    left=x - 0.5, top=y - length / 2,
                    rotate=ft.Rotate(angle=angle + math.pi / 2, alignment=ft.Alignment.CENTER)
                )
            )

        # Огромная цифра
        text = ft.Text("0", size=40, color=COLOR_DARK, weight=ft.FontWeight.BOLD)

        def update(val):
            text.value = str(int(val))

        stack = ft.Stack(
            [bg, *ticks, ft.Container(content=text, width=size, height=size, alignment=ft.Alignment.CENTER)],
            width=size, height=size)
        return stack, update

    # =====================================================================
    # 4. ПРИБОР №4: "КЛАССИЧЕСКИЙ СПИДОМЕТР" (Четвертый)
    # =====================================================================
    def create_speedometer(size=160):
        center = size / 2
        radius = size * 0.38

        # Фон
        bg = ft.Container(width=size, height=size, border_radius=size / 2, bgcolor="#F5F5F5",
                          border=ft.Border.all(4, COLOR_BLUE))

        # Шкала (деления)
        ticks = []
        for i in range(0, 101, 10):
            angle = math.radians(135 + (i / 100) * 270)
            x1 = center + (radius - 5) * math.cos(angle)
            y1 = center + (radius - 5) * math.sin(angle)
            x2 = center + radius * math.cos(angle)
            y2 = center + radius * math.sin(angle)

            ticks.append(
                ft.Container(
                    width=2, height=8, bgcolor=COLOR_DARK,
                    left=(x1 + x2) / 2 - 1, top=(y1 + y2) / 2 - 4,
                    rotate=ft.Rotate(angle=angle + math.pi / 2, alignment=ft.Alignment.CENTER)
                )
            )

        # Красная стрелка
        needle = ft.Container(
            width=3, height=radius - 5, bgcolor=COLOR_RED, border_radius=1.5,
            left=center - 1.5, top=center - (radius - 5),
            rotate=ft.Rotate(angle=math.radians(135), alignment=ft.Alignment.BOTTOM_CENTER)
        )

        # Центральный колпачок (полупрозрачный красный)
        cap = ft.Container(width=24, height=24, bgcolor="#FFCDD2", border_radius=12, left=center - 12, top=center - 12,
                           border=ft.Border.all(2, COLOR_RED))

        # Текст
        text = ft.Text("0", size=20, color=COLOR_RED, weight=ft.FontWeight.BOLD)

        def update(val):
            rad = math.radians(135 + (val / 100) * 270)
            needle.rotate = ft.Rotate(angle=rad, alignment=ft.Alignment.BOTTOM_CENTER)
            text.value = str(int(val))

        stack = ft.Stack([bg, *ticks, needle, cap,
                          ft.Container(content=text, width=size, height=size, alignment=ft.Alignment.BOTTOM_CENTER,
                                       padding=ft.Padding(0, 0, 0, 30))], width=size, height=size)
        return stack, update

    # =====================================================================
    # 5. ПРИБОР №5: "МНОГОЦВЕТНЫЙ ДАТЧИК" (Крайний справа)
    # =====================================================================
    def create_multi_color(size=160):
        center = size / 2
        radius = size * 0.42

        bg = ft.Container(width=size, height=size, border_radius=size / 2, bgcolor="#FFFFFF")

        # Синяя стрелка
        needle = ft.Container(
            width=4, height=radius - 10, bgcolor=COLOR_BLUE, border_radius=2,
            left=center - 2, top=center - (radius - 10),
            rotate=ft.Rotate(angle=math.radians(135), alignment=ft.Alignment.BOTTOM_CENTER)
        )
        cap = ft.Container(width=12, height=12, bgcolor=COLOR_DARK, border_radius=6, left=center - 6, top=center - 6)

        # Динамическая цветная дуга (рисуем кусочки, которые будем менять)
        arc_pieces = []
        num_pieces = 30
        for i in range(num_pieces):
            angle = math.radians(135 + (i / (num_pieces - 1)) * 270)
            x = center + radius * math.cos(angle)
            y = center + radius * math.sin(angle)
            # По умолчанию серые
            piece = ft.Container(width=6, height=6, bgcolor="#DDDDDD", border_radius=3, left=x - 3, top=y - 3)
            arc_pieces.append(piece)

        def update(val):
            # Двигаем стрелку
            rad = math.radians(135 + (val / 100) * 270)
            needle.rotate = ft.Rotate(angle=rad, alignment=ft.Alignment.BOTTOM_CENTER)

            # Закрашиваем кусочки дуги
            active_pieces = int((val / 100) * num_pieces)
            for i, piece in enumerate(arc_pieces):
                if i < active_pieces:
                    # Красим в зависимости от прогресса: Зеленый -> Желтый -> Розовый
                    ratio = i / num_pieces
                    if ratio < 0.5:
                        piece.bgcolor = COLOR_GREEN
                    elif ratio < 0.8:
                        piece.bgcolor = "#FFEB3B"  # Желтый
                    else:
                        piece.bgcolor = "#FF4081"  # Розовый
                else:
                    piece.bgcolor = "#DDDDDD"

        stack = ft.Stack([bg, *arc_pieces, needle, cap], width=size, height=size)
        return stack, update

    # =====================================================================
    # СОЗДАЕМ И СБИРАЕМ
    # =====================================================================
    p1, u1 = create_ping_pong(180)
    p2, u2 = create_progress_ring(180)
    p3, u3 = create_minimal(180)
    p4, u4 = create_speedometer(180)
    p5, u5 = create_multi_color(180)

    # Ползунок для управления
    slider = ft.Slider(min=0, max=100, value=50, divisions=100, label="Значение: {value}")

    def on_slider(e):
        val = slider.value
        u1(val);
        u2(val);
        u3(val);
        u4(val);
        u5(val)
        page.update()

    slider.on_change = on_slider
    on_slider(None)  # Инициализация

    # Добавляем на страницу
    page.add(
        ft.Text("5 стилей приборов", size=24, weight=ft.FontWeight.BOLD, color=COLOR_DARK),
        ft.Container(height=20),
        ft.Row(
            [p1, p2, p3, p4, p5],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
            wrap=True
        ),
        ft.Container(height=30),
        slider
    )


if __name__ == "__main__":
    ft.run(main)