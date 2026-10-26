import flet as ft
import math
import datetime
import asyncio
import random


def main(page: ft.Page):
    page.title = "Приборы: Манометр и Часы"
    page.bgcolor = "#E0E0E0"
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # ==========================================
    # 1. МАНОМЕТР
    # ==========================================
    def create_manometer(size=280):
        center = size / 2
        ticks = []
        min_val, max_val = 0, 120

        # Цветные сектора (Зеленый, Желтый, Красный)
        # Зеленый: 0-60, Желтый: 60-90, Красный: 90-120
        zones = [(0, 60, "#4CAF50"), (60, 90, "#FFEB3B"), (90, 120, "#F44336")]
        for start, end, color in zones:
            start_angle = 135 + ((start - min_val) / (max_val - min_val)) * 270
            end_angle = 135 + ((end - min_val) / (max_val - min_val)) * 270
            for a in range(int(start_angle), int(end_angle), 3):
                rad = math.radians(a)
                r = size * 0.42
                x = center + r * math.cos(rad)
                y = center + r * math.sin(rad)
                ticks.append(
                    ft.Container(width=6, height=6, bgcolor=color, border_radius=3, left=x - 3, top=y - 3)
                )

        # Деления и цифры
        for i in range(9):  # 0, 15, 30... 120
            val = i * 15
            angle_deg = 135 + (val / max_val) * 270

            # Цифры
            r_text = size * 0.3
            x_text = center + r_text * math.cos(math.radians(angle_deg))
            y_text = center + r_text * math.sin(math.radians(angle_deg))
            ticks.append(
                ft.Container(
                    content=ft.Text(str(val), size=11, color="#333333", weight=ft.FontWeight.BOLD),
                    left=x_text - 15, top=y_text - 10, width=30, alignment=ft.Alignment.CENTER
                )
            )

            # Палочки
            r_line = size * 0.36
            x_line = center + r_line * math.cos(math.radians(angle_deg))
            y_line = center + r_line * math.sin(math.radians(angle_deg))
            ticks.append(
                ft.Container(
                    width=2, height=12, bgcolor="#333333",
                    left=x_line - 1, top=y_line - 6,
                    rotate=ft.Rotate(angle=math.radians(angle_deg + 90), alignment=ft.Alignment.CENTER)
                )
            )

        # Стрелка
        needle = ft.Container(
            width=4, height=size * 0.35, bgcolor="#333333", border_radius=4,
            left=center - 2, top=center - (size * 0.35),
            rotate=ft.Rotate(angle=0, alignment=ft.Alignment.BOTTOM_CENTER)
        )
        # Хвост стрелки (противовес)
        tail = ft.Container(
            width=4, height=30, bgcolor="#333333", border_radius=4,
            left=center - 2, top=center,
            rotate=ft.Rotate(angle=0, alignment=ft.Alignment.TOP_CENTER)
        )

        # Цифровое табло
        display_text = ft.Text("29 [bar]", size=16, color="#333333", weight=ft.FontWeight.BOLD)
        display_box = ft.Container(
            content=display_text, bgcolor="#EEEEEE", padding=ft.Padding(10, 2, 10, 2),
            border_radius=2, left=center - 45, top=center + 40, width=90, alignment=ft.Alignment.CENTER
        )

        # Колпачок
        cap = ft.Container(
            width=20, height=20, bgcolor="#222222", border_radius=10,
            left=center - 10, top=center - 10
        )

        # Корпус
        body = ft.Container(
            width=size, height=size, border_radius=size / 2,
            bgcolor="#F0F0F0", border=ft.Border.all(8, "#555555"),
            shadow=ft.BoxShadow(blur_radius=10, color="#00000030")
        )

        stack = ft.Stack([
            body, *ticks, needle, tail, cap, display_box
        ], width=size, height=size)

        def set_value(val):
            ratio = val / max_val
            angle_rad = math.radians(135 + ratio * 270)
            needle.rotate = ft.Rotate(angle=angle_rad, alignment=ft.Alignment.BOTTOM_CENTER)
            tail.rotate = ft.Rotate(angle=angle_rad, alignment=ft.Alignment.TOP_CENTER)
            display_text.value = f"{int(val)} [bar]"

        return stack, set_value

    # ==========================================
    # 2. ЧАСЫ
    # ==========================================
    def create_clock(size=280):
        center = size / 2
        ticks = []

        # Циферблат
        body = ft.Container(
            width=size, height=size, border_radius=size / 2,
            bgcolor="#FFFFFF", border=ft.Border.all(8, "#E53935"),  # Красный ободок
            shadow=ft.BoxShadow(blur_radius=10, color="#00000030")
        )

        # Цифры 1-12
        for i in range(1, 13):
            angle = math.radians(i * 30 - 90)  # 12 часов сверху
            r_text = size * 0.38
            x = center + r_text * math.cos(angle)
            y = center + r_text * math.sin(angle)
            ticks.append(
                ft.Container(
                    content=ft.Text(str(i), size=16, color="#333333", weight=ft.FontWeight.BOLD),
                    left=x - 10, top=y - 10, width=20, alignment=ft.Alignment.CENTER
                )
            )
            # Минутные деления
            for j in range(1, 5):
                sub_angle = math.radians(i * 30 + j * 6 - 90)
                r_line = size * 0.44
                x_l = center + r_line * math.cos(sub_angle)
                y_l = center + r_line * math.sin(sub_angle)
                ticks.append(
                    ft.Container(width=2, height=6, bgcolor="#999999", left=x_l - 1, top=y_l - 3)
                )

        # Стрелки (Часовая, Минутная, Секундная)
        # Часовая (короткая, широкая)
        hour_needle = ft.Container(
            width=6, height=size * 0.22, bgcolor="#333333", border_radius=3,
            left=center - 3, top=center - (size * 0.22),
            rotate=ft.Rotate(angle=0, alignment=ft.Alignment.BOTTOM_CENTER)
        )
        # Минутная (длинная, тонкая)
        minute_needle = ft.Container(
            width=4, height=size * 0.32, bgcolor="#333333", border_radius=2,
            left=center - 2, top=center - (size * 0.32),
            rotate=ft.Rotate(angle=0, alignment=ft.Alignment.BOTTOM_CENTER)
        )
        # Секундная (красная, самая тонкая)
        second_needle = ft.Container(
            width=2, height=size * 0.36, bgcolor="#E53935", border_radius=1,
            left=center - 1, top=center - (size * 0.36),
            rotate=ft.Rotate(angle=0, alignment=ft.Alignment.BOTTOM_CENTER)
        )

        # Хвосты стрелок (противовесы)
        hour_tail = ft.Container(width=6, height=20, bgcolor="#333333", border_radius=3, left=center - 3, top=center,
                                 rotate=ft.Rotate(angle=0, alignment=ft.Alignment.TOP_CENTER))
        minute_tail = ft.Container(width=4, height=30, bgcolor="#333333", border_radius=2, left=center - 2, top=center,
                                   rotate=ft.Rotate(angle=0, alignment=ft.Alignment.TOP_CENTER))
        second_tail = ft.Container(width=2, height=40, bgcolor="#E53935", border_radius=1, left=center - 1, top=center,
                                   rotate=ft.Rotate(angle=0, alignment=ft.Alignment.TOP_CENTER))

        # Колпачок
        cap = ft.Container(
            width=16, height=16, bgcolor="#E53935", border_radius=8,
            left=center - 8, top=center - 8
        )

        stack = ft.Stack([
            body, *ticks, hour_needle, minute_needle, second_needle,
            hour_tail, minute_tail, second_tail, cap
        ], width=size, height=size)

        def update_time(now):
            # Часы: 360 градусов = 12 часов, значит 30 градусов в час
            # Плюс плавный ход от минут
            hour_angle = (now.hour % 12) * 30 + now.minute * 0.5
            # Минуты: 360 градусов = 60 минут, 6 градусов в минуту
            minute_angle = now.minute * 6 + now.second * 0.1
            # Секунды: 6 градусов в секунду
            second_angle = now.second * 6 + now.microsecond * 0.000006

            hour_needle.rotate = ft.Rotate(angle=math.radians(hour_angle - 90), alignment=ft.Alignment.BOTTOM_CENTER)
            hour_tail.rotate = ft.Rotate(angle=math.radians(hour_angle - 90), alignment=ft.Alignment.TOP_CENTER)

            minute_needle.rotate = ft.Rotate(angle=math.radians(minute_angle - 90),
                                             alignment=ft.Alignment.BOTTOM_CENTER)
            minute_tail.rotate = ft.Rotate(angle=math.radians(minute_angle - 90), alignment=ft.Alignment.TOP_CENTER)

            second_needle.rotate = ft.Rotate(angle=math.radians(second_angle - 90),
                                             alignment=ft.Alignment.BOTTOM_CENTER)
            second_tail.rotate = ft.Rotate(angle=math.radians(second_angle - 90), alignment=ft.Alignment.TOP_CENTER)

        return stack, update_time

    # --- Создаем приборы ---
    manometer_ui, set_pressure = create_manometer(280)
    clock_ui, update_clock = create_clock(280)

    # Текущее время для отрисовки при запуске
    update_clock(datetime.datetime.now())
    set_pressure(29)

    # --- ГЛАВНЫЙ ЦИКЛ ---
    async def main_loop():
        pressure = 29.0
        target_pressure = 29.0
        time_counter = 0

        while True:
            # 1. Обновление часов каждые 50 мс (для плавности секундной стрелки)
            now = datetime.datetime.now()
            update_clock(now)

            # 2. Симуляция манометра (плавное изменение давления)
            time_counter += 1
            if time_counter > 40:  # Раз в 2 секунды меняем цель
                target_pressure = random.uniform(10, 110)
                time_counter = 0

            # Плавно движемся к цели
            if pressure < target_pressure:
                pressure += 0.5
            elif pressure > target_pressure:
                pressure -= 0.5

            set_pressure(pressure)

            page.update()
            await asyncio.sleep(0.05)  # 20 FPS

    page.run_task(main_loop)

    # Добавляем на страницу
    page.add(
        ft.Text("Аналоговые приборы", size=24, weight=ft.FontWeight.BOLD, color="#333333"),
        ft.Container(height=10),
        ft.Row(
            [manometer_ui, clock_ui],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=40
        )
    )


if __name__ == "__main__":
    ft.run(main)