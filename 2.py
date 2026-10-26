import flet as ft


def main(page: ft.Page):
    page.title = "Термометр"
    page.bgcolor = "#E0E0E0"
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Диапазон температур
    MIN_TEMP = 0
    MAX_TEMP = 120

    # Размеры термометра
    TUBE_W = 16
    TUBE_H = 350
    BULB_R = 25
    OFFSET_Y = 40  # Отступ сверху, чтобы 120 не обрезалось

    LIQUID_COLOR = "#1565C0"

    # --- 1. Жидкость и трубка ---
    # Внутренняя жидкость
    liquid_tube = ft.Container(
        width=TUBE_W - 4,
        height=0,
        bgcolor=LIQUID_COLOR,
        border_radius=ft.BorderRadius(8, 8, 0, 0),
        alignment=ft.Alignment.BOTTOM_CENTER,
        animate=ft.Animation(duration=400, curve=ft.AnimationCurve.EASE_OUT)  # Плавность
    )

    # Сама трубка (стекло)
    tube = ft.Container(
        width=TUBE_W,
        height=TUBE_H,
        bgcolor="#E0E0E0",
        border=ft.Border.all(2, "#BDBDBD"),
        border_radius=ft.BorderRadius(8, 8, 0, 0),
        alignment=ft.Alignment.BOTTOM_CENTER,
        content=liquid_tube,
        shadow=ft.BoxShadow(blur_radius=4, color="#00000020"),
    )

    # Колба
    bulb = ft.Container(
        width=BULB_R * 2,
        height=BULB_R * 2,
        bgcolor=LIQUID_COLOR,
        border_radius=BULB_R,
        border=ft.Border.all(2, "#BDBDBD"),
        shadow=ft.BoxShadow(blur_radius=4, color="#00000030"),
    )

    # --- 2. Шкала (деления и цифры) ---
    scale_elements = []
    steps = [0, 15, 30, 45, 60, 75, 90, 105, 120]

    for val in steps:
        ratio = val / MAX_TEMP
        # Позиция Y для конкретного значения (с учетом отступа OFFSET_Y)
        y_pos = OFFSET_Y + TUBE_H - (ratio * TUBE_H)

        # Деление (палочка)
        scale_elements.append(
            ft.Container(
                width=8, height=2, bgcolor="#333333",
                left=BULB_R + 8, top=y_pos - 1,
            )
        )

        # Цифра
        scale_elements.append(
            ft.Container(
                content=ft.Text(str(val), size=11, color="#333333", weight=ft.FontWeight.BOLD),
                left=BULB_R + 20, top=y_pos - 10, width=30
            )
        )

    # --- 3. Цифровое табло ---
    display_text = ft.Text("0 °C", size=18, color="#333333", weight=ft.FontWeight.BOLD)
    display_box = ft.Container(
        content=display_text,
        width=80, alignment=ft.Alignment.CENTER,
        bgcolor="#FFFFFF", border=ft.Border.all(1, "#BDBDBD"),
        padding=ft.Padding(5, 5, 5, 5), border_radius=4,
        margin=ft.Margin(0, 20, 0, 0)  # Отступ сверху
    )

    # --- 4. Логика обновления ---
    def update_thermometer(e):
        val = slider.value
        # Обновляем высоту жидкости
        liquid_tube.height = (val / MAX_TEMP) * TUBE_H
        # Обновляем текст
        display_text.value = f"{int(val)} °C"
        page.update()

    init_temp = 29
    liquid_tube.height = (init_temp / MAX_TEMP) * TUBE_H
    display_text.value = f"{init_temp} °C"

    slider = ft.Slider(
        min=MIN_TEMP, max=MAX_TEMP, divisions=120,
        value=init_temp, on_change=update_thermometer,
        width=200, active_color=LIQUID_COLOR,
    )

    # --- 5. Сборка ---
    # Используем Stack для позиционирования трубки, колбы и шкалы
    main_stack = ft.Stack(
        [
            # Трубка (сдвинута вниз на OFFSET_Y)
            ft.Container(content=tube, left=BULB_R - (TUBE_W / 2), top=OFFSET_Y),
            # Колба (внизу трубки)
            ft.Container(content=bulb, left=0, top=OFFSET_Y + TUBE_H - BULB_R),
            # Шкала
            *scale_elements
        ],
        width=BULB_R * 2 + 60,
        height=OFFSET_Y + TUBE_H + BULB_R + 10,  # Высота с запасом
    )

    page.add(
        ft.Text("Термометр", size=28, weight=ft.FontWeight.BOLD, color="#333333"),
        ft.Container(height=10),
        ft.Row([main_stack], alignment=ft.MainAxisAlignment.CENTER),
        display_box,
        ft.Container(height=10),
        slider,
    )


if __name__ == "__main__":
    ft.run(main)