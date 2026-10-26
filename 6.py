import flet as ft


def main(page: ft.Page):
    page.title = "LED VU-Метр (Индикатор звука)"
    page.bgcolor = "#1E1E1E"
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # --- Настройки прибора ---
    NUM_SEGMENTS = 40  # Количество сегментов в одном канале
    SEG_WIDTH = 6  # Ширина сегмента
    SEG_HEIGHT = 24  # Высота сегмента
    SEG_SPACING = 2  # Расстояние между сегментами

    # Цвета (из фото: голубой переходит в фиолетовый)
    COLOR_CYAN = "#00BFFF"  # Голубой (начало шкалы)
    COLOR_PURPLE = "#8A2BE2"  # Фиолетовый (середина)
    COLOR_PINK = "#FF1493"  # Розовый (пик)

    # --- Создаем сегменты для L и R ---
    # Мы будем хранить ссылки на них в списках, чтобы потом менять цвет
    l_segments = []
    r_segments = []

    for i in range(NUM_SEGMENTS):
        # Вычисляем цвет в зависимости от позиции (0 - слева, 39 - справа)
        ratio = i / (NUM_SEGMENTS - 1)
        if ratio < 0.5:
            # Плавный переход от голубого к фиолетовому
            color = COLOR_CYAN
        elif ratio < 0.8:
            color = COLOR_PURPLE
        else:
            color = COLOR_PINK

        # Создаем сегмент для левого канала
        l_seg = ft.Container(
            width=SEG_WIDTH, height=SEG_HEIGHT,
            bgcolor="#222222",  # Изначально выключен (темный)
            border_radius=1,
            # Сохраняем цвет, которым он должен гореть
            data={"active_color": color}
        )
        l_segments.append(l_seg)

        # Создаем сегмент для правого канала
        r_seg = ft.Container(
            width=SEG_WIDTH, height=SEG_HEIGHT,
            bgcolor="#222222",
            border_radius=1,
            data={"active_color": color}
        )
        r_segments.append(r_seg)

    # --- Сборка рядов ---
    # Обернем сегменты в Row с минимальным отступом
    l_row = ft.Row(controls=l_segments, spacing=SEG_SPACING, alignment=ft.MainAxisAlignment.CENTER)
    r_row = ft.Row(controls=r_segments, spacing=SEG_SPACING, alignment=ft.MainAxisAlignment.CENTER)

    # --- Шкала дБ (посередине) ---
    # Значения от -20 до +6. Выравниваем их по центру, чтобы они примерно совпадали с сегментами
    db_labels = ["-20", "-15", "-10", "-6", "-3", "0", "+3", "+6"]
    db_row = ft.Row(
        controls=[
            ft.Container(content=ft.Text(val, size=10, color="#777777", weight=ft.FontWeight.BOLD),
                         width=(NUM_SEGMENTS * (SEG_WIDTH + SEG_SPACING)) / len(db_labels))
            for val in db_labels
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        width=NUM_SEGMENTS * (SEG_WIDTH + SEG_SPACING)
    )

    # --- Корпус прибора ---
    # Черный фон с легким градиентом для объема
    panel_bg = ft.Container(
        width=NUM_SEGMENTS * (SEG_WIDTH + SEG_SPACING) + 100,
        height=130,
        bgcolor="#111111",
        border=ft.Border.all(3, "#333333"),
        border_radius=8,
        shadow=ft.BoxShadow(blur_radius=15, color="#000000"),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("L", size=14, color="#AAAAAA", weight=ft.FontWeight.BOLD, width=20),
                        l_row
                    ],
                    alignment=ft.MainAxisAlignment.START
                ),
                ft.Container(height=5),
                db_row,
                ft.Container(height=5),
                ft.Row(
                    [
                        ft.Text("R", size=14, color="#AAAAAA", weight=ft.FontWeight.BOLD, width=20),
                        r_row
                    ],
                    alignment=ft.MainAxisAlignment.START
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=ft.Padding(10, 10, 10, 10)
    )

    # --- Функция обновления (имитация звука) ---
    def update_vu_level(left_val, right_val):
        # left_val и right_val от 0 до 100 (проценты)

        # Обновляем левый канал
        active_l = int((left_val / 100) * NUM_SEGMENTS)
        for i, seg in enumerate(l_segments):
            if i < active_l:
                seg.bgcolor = seg.data["active_color"]
                # Добавляем свечение (эффект неона)
                seg.shadow = ft.BoxShadow(blur_radius=8, color=seg.data["active_color"], spread_radius=1)
            else:
                seg.bgcolor = "#222222"
                seg.shadow = None

        # Обновляем правый канал
        active_r = int((right_val / 100) * NUM_SEGMENTS)
        for i, seg in enumerate(r_segments):
            if i < active_r:
                seg.bgcolor = seg.data["active_color"]
                seg.shadow = ft.BoxShadow(blur_radius=8, color=seg.data["active_color"], spread_radius=1)
            else:
                seg.bgcolor = "#222222"
                seg.shadow = None

        page.update()

    # --- Ползунки для ручного управления (чтобы можно было проверить) ---
    left_slider = ft.Slider(min=0, max=100, value=40, label="L: {value}%", active_color=COLOR_CYAN, width=400)
    right_slider = ft.Slider(min=0, max=100, value=45, label="R: {value}%", active_color=COLOR_PURPLE, width=400)

    def on_slider_change(e):
        update_vu_level(left_slider.value, right_slider.value)

    left_slider.on_change = on_slider_change
    right_slider.on_change = on_slider_change

    # Инициализация начального состояния
    update_vu_level(left_slider.value, right_slider.value)

    # --- Вывод на страницу ---
    page.add(
        ft.Text("Аудио-индикатор (VU Meter)", size=24, weight=ft.FontWeight.BOLD, color="white"),
        ft.Container(height=10),
        panel_bg,
        ft.Container(height=30),
        ft.Text("Регулировка уровня:", color="#AAAAAA"),
        left_slider,
        right_slider
    )


if __name__ == "__main__":
    ft.run(main)