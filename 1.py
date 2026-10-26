import flet as ft
import math
import asyncio
import random


def main(page: ft.Page):
    page.title = "Аналоговые приборы с Коробкой Передач"
    page.bgcolor = "#2B2B2B"
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # --- Состояние автомобиля ---
    state = {
        "engine_on": False,  # Работает ли двигатель
        "gear": 0,  # Текущая передача (0 - нейтраль, 1-5)
        "speed": 0.0,  # Текущая скорость (км/ч)
        "target_speed": 0.0,  # Желаемая скорость
        "temp": 20.0  # Температура
    }

    # Максимальные скорости для передач (0 - нейтраль, 1-5)
    gear_max_speeds = {0: 0, 1: 40, 2: 70, 3: 95, 4: 115, 5: 120}

    def create_gauge(title, min_val, max_val, unit, initial_value, color_zones=None, size=280):
        center = size / 2
        ticks = []

        # Цветные сектора
        if color_zones:
            for start, end, color in color_zones:
                start_angle = 135 + ((start - min_val) / (max_val - min_val)) * 270
                end_angle = 135 + ((end - min_val) / (max_val - min_val)) * 270
                for a in range(int(start_angle), int(end_angle), 4):
                    rad = math.radians(a)
                    r = size * 0.42
                    x = center + r * math.cos(rad)
                    y = center + r * math.sin(rad)
                    ticks.append(
                        ft.Container(
                            width=5, height=5, bgcolor=color, border_radius=2.5,
                            left=x - 2.5, top=y - 2.5
                        )
                    )

        # Деления и цифры
        num_ticks = 10
        for i in range(num_ticks + 1):
            val = min_val + (max_val - min_val) * i / num_ticks
            angle_deg = 135 + (i / num_ticks) * 270

            r_text = size * 0.32
            x_text = center + r_text * math.cos(math.radians(angle_deg))
            y_text = center + r_text * math.sin(math.radians(angle_deg))
            ticks.append(
                ft.Container(
                    content=ft.Text(str(int(val)), size=11, color="#333333", weight=ft.FontWeight.BOLD),
                    left=x_text - 15, top=y_text - 10, width=30, alignment=ft.Alignment.CENTER
                )
            )

            if i < num_ticks:
                r_line = size * 0.38
                x_line = center + r_line * math.cos(math.radians(angle_deg))
                y_line = center + r_line * math.sin(math.radians(angle_deg))
                ticks.append(
                    ft.Container(
                        width=3, height=12, bgcolor="#333333",
                        border_radius=1,
                        left=x_line - 1.5, top=y_line - 6,
                        rotate=ft.Rotate(angle=math.radians(angle_deg + 90), alignment=ft.Alignment.CENTER)
                    )
                )

        # Стрелка
        needle = ft.Container(
            width=4, height=size * 0.35,
            bgcolor="#E53935",
            border_radius=4,
            left=center - 2,
            top=center - (size * 0.35),
            rotate=ft.Rotate(angle=math.radians(135), alignment=ft.Alignment.BOTTOM_CENTER)
        )

        # Цифровое табло
        display_text = ft.Text(f"{int(initial_value)} {unit}", size=16, color="#00E676", weight=ft.FontWeight.BOLD)
        display_box = ft.Container(
            content=display_text,
            bgcolor="#222222",
            padding=ft.Padding(10, 5, 10, 5),
            border_radius=5,
            left=center - 50, top=center + 45, width=100,
            alignment=ft.Alignment.CENTER
        )

        # Колпачок
        cap = ft.Container(
            width=24, height=24, bgcolor="#333333", border_radius=12,
            border=ft.Border.all(2, "#888888"),
            left=center - 12, top=center - 12
        )

        gauge_stack = ft.Stack(
            [
                ft.Container(
                    width=size, height=size, border_radius=size / 2,
                    bgcolor="#F5F5F5", border=ft.Border.all(6, "#BDBDBD"),
                    shadow=ft.BoxShadow(blur_radius=10, color="#00000030")
                ),
                *ticks,
                needle,
                cap,
                display_box,
                ft.Container(
                    content=ft.Text(title, size=12, color="#757575", weight=ft.FontWeight.BOLD),
                    left=center - 50, top=center - 30, width=100, alignment=ft.Alignment.CENTER
                )
            ],
            width=size, height=size
        )

        def update_visuals(val):
            val = max(min_val, min(max_val, val))
            ratio = (val - min_val) / (max_val - min_val)
            angle_rad = math.radians(135 + ratio * 270)
            needle.rotate = ft.Rotate(angle=angle_rad, alignment=ft.Alignment.BOTTOM_CENTER)
            display_text.value = f"{int(val)} {unit}"

        return gauge_stack, update_visuals

    # Создаём приборы
    temp_gauge, set_temp = create_gauge(
        "ТЕМПЕРАТУРА", -30, 50, "°C", 20,
        color_zones=[(-30, 0, "#42A5F5"), (0, 25, "#66BB6A"), (25, 50, "#EF5350")]
    )

    speed_gauge, set_speed = create_gauge(
        "СПИДОМЕТР", 0, 120, "км/ч", 0,
        color_zones=[(0, 50, "#66BB6A"), (50, 80, "#FFEE58"), (80, 120, "#EF5350")]
    )

    # --- UI Элементы управления ---
    gear_text = ft.Text("Передача: N", size=20, color="white", weight=ft.FontWeight.BOLD)

    def change_gear(e, gear_num):
        state["gear"] = gear_num
        if gear_num == 0:
            gear_text.value = "Передача: N (Нейтраль)"
        else:
            gear_text.value = f"Передача: {gear_num}"
        page.update()

    # Кнопка Нейтрали + Кнопки 1-5 передач
    gear_buttons = ft.Row(
        [
            ft.Button("N", on_click=lambda e: change_gear(e, 0),
                      style=ft.ButtonStyle(bgcolor="#FF9800", color="white",
                                           shape=ft.RoundedRectangleBorder(radius=6))),
            *[
                ft.Button(f"{i}", on_click=lambda e, i=i: change_gear(e, i),
                          style=ft.ButtonStyle(bgcolor="#424242", color="white",
                                               shape=ft.RoundedRectangleBorder(radius=6)))
                for i in range(1, 6)
            ]
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    # --- ГЛАВНЫЙ ЦИКЛ СИМУЛЯЦИИ ---
    async def run_loop():
        while True:
            if state["engine_on"]:
                # --- ДВИГАТЕЛЬ РАБОТАЕТ ---
                current_gear = state["gear"]
                state["target_speed"] = gear_max_speeds[current_gear]

                if current_gear == 0:
                    # На нейтрали машина катится накатом (плавно тормозит)
                    if state["speed"] > 0:
                        state["speed"] -= 1.0  # Накат медленнее, чем при торможении двигателем
                        if state["speed"] < 0:
                            state["speed"] = 0
                else:
                    # На передачах идет разгон или торможение двигателем
                    if state["speed"] > state["target_speed"]:
                        state["speed"] -= 2.0
                    else:
                        accel_rate = 1.5 if current_gear == 1 else (1.0 if current_gear == 2 else 0.6)
                        state["speed"] += accel_rate

                # Нагрев двигателя (плавно к 90°C)
                if state["temp"] < 90:
                    state["temp"] += 0.5
                state["temp"] += random.uniform(-0.2, 0.2)

            else:
                # --- ДВИГАТЕЛЬ ЗАГЛУШЕН ---
                # Скорость плавно падает до 0
                if state["speed"] > 0:
                    state["speed"] -= 1.5
                    if state["speed"] < 0:
                        state["speed"] = 0

                # Температура падает к комнатной (20°C)
                if state["temp"] > 20:
                    state["temp"] -= 0.2

            # Ограничители
            if state["speed"] > 120: state["speed"] = 120
            if state["speed"] < 0: state["speed"] = 0
            if state["temp"] < 20: state["temp"] = 20
            if state["temp"] > 100: state["temp"] = 100

            # Обновляем визуал
            set_speed(state["speed"])
            set_temp(state["temp"])
            page.update()

            await asyncio.sleep(0.05)

    # Запуск фонового цикла при старте страницы
    page.run_task(run_loop)

    # --- ОБРАБОТЧИКИ КНОПОК ---
    async def start_engine(e):
        state["engine_on"] = True
        start_btn.disabled = True
        stop_btn.disabled = False
        page.update()

    async def stop_engine(e):
        state["engine_on"] = False
        start_btn.disabled = False
        stop_btn.disabled = True
        page.update()

    start_btn = ft.Button(
        content=ft.Text("Запустить двигатель", color="white"),
        on_click=start_engine,
        bgcolor="#4CAF50",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )

    stop_btn = ft.Button(
        content=ft.Text("Заглушить", color="white"),
        on_click=stop_engine,
        bgcolor="#F44336",
        disabled=True,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )

    # Сборка интерфейса
    page.add(
        ft.Text("Приборная панель", size=24, weight=ft.FontWeight.BOLD, color="white"),
        ft.Row([temp_gauge, speed_gauge], alignment=ft.MainAxisAlignment.CENTER, spacing=40),
        ft.Container(height=10),
        gear_text,
        gear_buttons,
        ft.Container(height=10),
        ft.Row([start_btn, stop_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    )


if __name__ == "__main__":
    ft.run(main)