import flet as ft
import math
import asyncio
import random


def main(page: ft.Page):
    page.title = "Генератор сигналов звуковой частоты"
    page.bgcolor = "#333333"
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # --- СОСТОЯНИЕ ---
    state = {
        "running": False,
        "left_freq": 1000,
        "right_freq": 1000,
        "left_vol": 20,
        "right_vol": 20,
        "knob_vals": [8, 4, 40, 60],
        "knob_angles": [0.0, 0.0, 0.0, 0.0],
        "channel_mode": "stereo",
        "wave_type": "sine"
    }

    # --- ЦВЕТА ---
    PANEL_BG = "#D4D0C8"  # Классический серый Windows
    PANEL_BORDER = "#808080"
    DARK_BG = "#111111"  # Фон для табло
    GREEN_LED = "#00FF00"
    YELLOW_LED = "#FFFF00"
    TEXT_COLOR = "#000000"

    # --- ЦИФРОВОЕ ТАБЛО ---
    def create_led(text, color=GREEN_LED):
        return ft.Container(
            content=ft.Text(text, size=20, color=color, weight=ft.FontWeight.BOLD, font_family="Consolas"),
            bgcolor=DARK_BG,
            border=ft.Border.all(2, PANEL_BORDER),
            padding=ft.Padding(10, 5, 10, 5),
            alignment=ft.Alignment.CENTER,
            width=180,
        )

    left_freq_disp = create_led("01000 Гц")
    right_freq_disp = create_led("01000 Гц")
    left_vol_disp = create_led("020 мВ", YELLOW_LED)
    right_vol_disp = create_led("020 мВ", YELLOW_LED)

    # --- ОБНОВЛЕНИЕ ---
    def update_ui():
        left_freq_disp.content.value = f"{int(state['left_freq']):05d} Гц"
        right_freq_disp.content.value = f"{int(state['right_freq']):05d} Гц"
        left_vol_disp.content.value = f"{int(state['left_vol']):03d} мВ"
        right_vol_disp.content.value = f"{int(state['right_vol']):03d} мВ"

        for i in range(4):
            knobs_txt[i].value = str(int(state["knob_vals"][i]))
            max_vals = [10, 100, 10, 100]
            ratio = state["knob_vals"][i] / max_vals[i]
            angle = -135 + ratio * 270
            knobs_ind[i].rotate = ft.Rotate(angle=math.radians(angle), alignment=ft.Alignment.BOTTOM_CENTER)

        page.update()

    # --- КНОПКИ ---
    def toggle_start(e):
        state["running"] = True
        update_ui()

    def stop_gen(e):
        state["running"] = False
        state["left_freq"] = 0
        state["right_freq"] = 0
        state["left_vol"] = 0
        state["right_vol"] = 0
        update_ui()

    def exit_app(e):
        page.window.close()

    # --- КРУТИЛКИ (Как на скрине - простые) ---
    knobs_ui = []
    knobs_ind = []
    knobs_txt = []

    for i in range(4):
        size = 80
        center = size / 2
        radius = size * 0.35

        # Фон
        bg = ft.Container(width=size, height=size, border_radius=size / 2, bgcolor="#888888",
                          border=ft.Border.all(2, "#444444"))

        # Указатель
        indicator = ft.Container(
            width=4, height=radius - 5, bgcolor="#FFFFFF", border_radius=2,
            left=center - 2, top=center - (radius - 5),
            rotate=ft.Rotate(angle=math.radians(-135), alignment=ft.Alignment.BOTTOM_CENTER)
        )
        knobs_ind.append(indicator)

        # Колпачок
        cap = ft.Container(width=16, height=16, bgcolor="#444444", border_radius=8, left=center - 8, top=center - 8)

        # Текст
        txt = ft.Text(str(state["knob_vals"][i]), size=12, color="#FFFFFF", weight=ft.FontWeight.BOLD)
        knobs_txt.append(txt)

        stack = ft.Stack([
            bg, indicator, cap,
            ft.Container(content=txt, width=size, height=size, alignment=ft.Alignment.BOTTOM_CENTER,
                         padding=ft.Padding(0, 0, 0, 5))
        ], width=size, height=size)
        knobs_ui.append(stack)

    # --- ПАНЕЛИ ---
    # Левая панель (Левый канал)
    left_panel = ft.Container(
        width=250, height=400,
        bgcolor=PANEL_BG, border=ft.Border.all(2, PANEL_BORDER),
        padding=10,
        content=ft.Column([
            ft.Text("Левый канал", size=12, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
            left_freq_disp,
            left_vol_disp,
            ft.Divider(height=10, color=PANEL_BORDER),
            ft.RadioGroup(content=ft.Column([
                ft.Radio(value="stereo", label="Левый/Правый", fill_color="#000080",
                         label_style=ft.TextStyle(color=TEXT_COLOR, size=12)),
                ft.Radio(value="left", label="Левый канал", fill_color="#000080",
                         label_style=ft.TextStyle(color=TEXT_COLOR, size=12)),
                ft.Radio(value="right", label="Правый канал", fill_color="#000080",
                         label_style=ft.TextStyle(color=TEXT_COLOR, size=12)),
            ], spacing=5), value="stereo"),
            ft.Container(height=10),
            ft.Text("Канал", size=10, color="#000080", weight=ft.FontWeight.BOLD),
        ], spacing=5)
    )

    # Центральная панель
    center_panel = ft.Container(
        width=180, height=400,
        bgcolor=PANEL_BG, border=ft.Border.all(2, PANEL_BORDER),
        padding=10,
        content=ft.Column([
            # Индикаторы
            ft.Row([ft.Text("1:1", color=TEXT_COLOR, size=10),
                    ft.Container(width=10, height=10, bgcolor="#333333", border_radius=5)]),
            ft.Row([ft.Text("1:12", color=TEXT_COLOR, size=10),
                    ft.Container(width=10, height=10, bgcolor="#333333", border_radius=5)]),
            ft.Row([ft.Text("Дискретность", color=TEXT_COLOR, size=10),
                    ft.Container(width=10, height=10, bgcolor="#333333", border_radius=5)]),
            ft.Divider(height=10, color=PANEL_BORDER),
            # Кнопки
            ft.Button(
                content=ft.Text("СТАРТ", color="#000000", weight=ft.FontWeight.BOLD, size=14),
                bgcolor=PANEL_BG, on_click=toggle_start,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=0))  # Квадратные кнопки
            ),
            ft.Button(
                content=ft.Text("СТОП", color="#000000", weight=ft.FontWeight.BOLD, size=14),
                bgcolor=PANEL_BG, on_click=stop_gen,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=0))
            ),
            ft.Button(
                content=ft.Text("ВЫХОД", color="#000000", weight=ft.FontWeight.BOLD, size=14),
                bgcolor=PANEL_BG, on_click=exit_app,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=0))
            ),
        ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
    )

    # Правая панель
    right_panel = ft.Container(
        width=250, height=400,
        bgcolor=PANEL_BG, border=ft.Border.all(2, PANEL_BORDER),
        padding=10,
        content=ft.Column([
            ft.Text("Правый канал", size=12, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
            right_freq_disp,
            right_vol_disp,
            ft.Divider(height=10, color=PANEL_BORDER),
            ft.RadioGroup(content=ft.Column([
                ft.Radio(value="sine", label="Синусоида", fill_color="#000080",
                         label_style=ft.TextStyle(color=TEXT_COLOR, size=12)),
                ft.Radio(value="saw", label="Пилообразный", fill_color="#000080",
                         label_style=ft.TextStyle(color=TEXT_COLOR, size=12)),
                ft.Radio(value="triangle", label="Треугольный", fill_color="#000080",
                         label_style=ft.TextStyle(color=TEXT_COLOR, size=12)),
            ], spacing=5), value="sine"),
            ft.Container(height=10),
            ft.Text("Вид сигнала", size=10, color="#000080", weight=ft.FontWeight.BOLD),
        ], spacing=5)
    )

    # Нижняя панель (Крутилки)
    bottom_panel = ft.Container(
        width=700, height=180,
        bgcolor=PANEL_BG, border=ft.Border.all(2, PANEL_BORDER),
        padding=10,
        content=ft.Column([
            ft.Row([
                ft.Column(
                    [knobs_ui[i], ft.Text(f"1-{['1 кГц', '100 Гц', '1 Гц', 'Ампл'][i]}", size=10, color=TEXT_COLOR)],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER) for i in range(4)
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
            ft.Container(height=5),
            ft.Text("ГСЧ-1-01", size=10, color="#555555", weight=ft.FontWeight.BOLD)
        ], spacing=5)
    )

    # --- АНИМАЦИЯ ---
    async def anim():
        while True:
            if state["running"]:
                state["left_freq"] = 800 + random.randint(-30, 30)
                state["right_freq"] = 800 + random.randint(-30, 30)
                state["left_vol"] = 15 + random.randint(-3, 3)
                state["right_vol"] = 15 + random.randint(-3, 3)
                for i in range(4):
                    state["knob_vals"][i] = max(0, min(100, state["knob_vals"][i] + random.uniform(-0.5, 0.5)))
                update_ui()
            await asyncio.sleep(0.1)

    page.run_task(anim)
    update_ui()

    # --- ГЛАВНЫЙ КОРПУС ---
    body = ft.Container(
        width=740, height=680,
        bgcolor=PANEL_BG,
        border=ft.Border.all(2, "#FFFFFF"),  # 3D эффект Windows
        padding=10,
        content=ft.Column([
            ft.Container(
                width=720, height=25,
                bgcolor="#000080",  # Синий заголовок Windows
                content=ft.Text("Генератор сигналов звуковой частоты", color="#FFFFFF", size=12),
                padding=ft.Padding(5, 0, 0, 0),
                alignment=ft.Alignment.CENTER_LEFT
            ),
            ft.Container(height=10),
            ft.Row([left_panel, center_panel, right_panel], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ft.Container(height=10),
            bottom_panel
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
    )

    page.add(body)


if __name__ == "__main__":
    ft.run(main)