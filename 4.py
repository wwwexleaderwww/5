import flet as ft
import math
import random
import asyncio


def main(page: ft.Page):
    page.title = "Индикатор уровня"
    page.bgcolor = "#121212"
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # --- Размеры ---
    W, H = 450, 300
    center_x = W / 2
    center_y = 220  # Точка вращения
    radius = 150

    # --- 1. Дуга ---
    arc_elements = []
    for a in range(180, -1, -2):
        rad = math.radians(a)
        x = center_x + radius * math.cos(rad)
        y = center_y - radius * math.sin(rad)

        if a >= 120:
            color = "#00E676"
        elif a >= 60:
            color = "#FFEB3B"
        else:
            color = "#F44336"

        arc_elements.append(
            ft.Container(
                width=8, height=8, bgcolor=color, border_radius=4,
                left=x - 4, top=y - 4,
                shadow=ft.BoxShadow(blur_radius=10, color=color)
            )
        )

    # --- 2. Стрелка (ФИКС) ---
    # Длина стрелки
    n_len = radius - 20

    # Контейнер стрелки. Мы делаем его высотой n_len и шириной 6.
    # Ставим его так, чтобы нижний край был ровно в центре (center_x, center_y).
    needle = ft.Container(
        width=6, height=n_len, bgcolor="#FFFFFF", border_radius=3,
        left=center_x - 3,
        top=center_y - n_len,  # Верх стрелки
        # Вращаем вокруг НИЖНЕГО ЦЕНТРА (BOTTOM_CENTER)
        rotate=ft.Rotate(angle=math.radians(180), alignment=ft.Alignment.BOTTOM_CENTER),
    )

    # Хвост стрелки (противовес)
    needle_tail = ft.Container(
        width=6, height=35, bgcolor="#FFFFFF", border_radius=3,
        left=center_x - 3,
        top=center_y,  # Низ стрелки
        rotate=ft.Rotate(angle=math.radians(180), alignment=ft.Alignment.TOP_CENTER),
    )

    # --- 3. Ось ---
    cap = ft.Container(
        width=26, height=26, bgcolor="#333333", border_radius=13,
        border=ft.Border.all(3, "#757575"),
        left=center_x - 13, top=center_y - 13,
    )

    # --- 4. Батарейка ---
    batt_segments = []
    for i in range(5):
        batt_segments.append(
            ft.Container(
                width=14, height=24, bgcolor="#FFFFFF", border_radius=2,
                left=W - 110 + (i * 18), top=H - 45, opacity=0.1
            )
        )
    batt_terminal = ft.Container(
        width=5, height=10, bgcolor="#FFFFFF", border_radius=ft.BorderRadius(2, 0, 0, 2),
        left=W - 115, top=H - 38,
    )

    # --- 5. Корпус ---
    body = ft.Container(
        width=W, height=H, bgcolor="#222222", border_radius=15,
        border=ft.Border.all(4, "#444444"),
    )
    inner_bg = ft.Container(
        width=W - 20, height=H - 20, bgcolor="#1A1A1A", border_radius=10,
        left=10, top=10,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT,
            colors=["#2A2A2A", "#111111"]
        )
    )

    # --- 6. Сборка ---
    gauge_ui = ft.Stack(
        [
            body, inner_bg, *arc_elements, batt_terminal, *batt_segments,
            needle, needle_tail, cap,
        ],
        width=W, height=H
    )

    # --- 7. Обновление ---
    def update_indicator(val):
        val = max(0, min(100, val))

        # Логика вращения:
        # При 0% стрелка смотрит влево (180 градусов по Flet).
        # При 100% стрелка смотрит вправо (0 градусов).
        # Формула: от 180 отнимаем долю от 180.
        angle_deg = 180 - (val / 100) * 180
        rad = math.radians(angle_deg)

        needle.rotate = ft.Rotate(angle=rad, alignment=ft.Alignment.BOTTOM_CENTER)
        needle_tail.rotate = ft.Rotate(angle=rad, alignment=ft.Alignment.TOP_CENTER)

        # Батарейка
        lit = int(val / 20)
        for i, seg in enumerate(batt_segments):
            seg.opacity = 1.0 if i < lit else 0.1

    # --- 8. Симуляция ---
    async def auto_loop():
        current = 0.0
        target = 50.0
        while True:
            if random.random() < 0.02:
                target = random.uniform(5, 100)

            if current < target:
                current += 1.0
            elif current > target:
                current -= 1.0

            update_indicator(current)
            page.update()
            await asyncio.sleep(0.03)

    page.run_task(auto_loop)

    page.add(
        ft.Text("Индикатор уровня", size=26, weight=ft.FontWeight.BOLD, color="white"),
        ft.Container(height=20),
        gauge_ui
    )


if __name__ == "__main__":
    ft.run(main)