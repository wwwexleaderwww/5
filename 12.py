import flet as ft
import math
import asyncio
import random


def main(page: ft.Page):
    page.title = "Современный Медиа-Плеер"
    page.bgcolor = "#0F0F11"  # Глубокий темный фон
    page.padding = 0

    # --- ГЛОБАЛЬНОЕ СОСТОЯНИЕ ---
    state = {
        "playing": False,
        "angle": 0.0,
        "current_track_idx": 0,
        "current_time_sec": 0,
        "volume": 65,
        "windows": {
            "deck": True,
            "playlist": True,
            "eq": True,
            "mini": True,
            "props": True
        }
    }

    tracks = [
        {"title": "Dark Side of the Moon", "artist": "Pink Floyd", "duration_sec": 43 * 60},
        {"title": "Abbey Road", "artist": "The Beatles", "duration_sec": 47 * 60},
        {"title": "Thriller", "artist": "Michael Jackson", "duration_sec": 42 * 60},
        {"title": "Back in Black", "artist": "AC/DC", "duration_sec": 42 * 60},
        {"title": "Nevermind", "artist": "Nirvana", "duration_sec": 49 * 60},
    ]

    def format_time(seconds):
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m:02d}:{s:02d}"

    # =====================================================================
    # КОМПОНЕНТ: ОКНО (Современный стиль)
    # =====================================================================
    def create_window(title, content, width, height, window_id):
        def close_window(e):
            state["windows"][window_id] = False
            refresh_desktop()

        title_bar = ft.Container(
            width=width, height=40,
            bgcolor="#1A1A1E",  # Темный заголовок
            border_radius=ft.BorderRadius(12, 12, 0, 0),
            content=ft.Row([
                ft.Text(title, size=14, color="#FFFFFF", weight=ft.FontWeight.W_600),
                ft.Container(expand=True),
                ft.IconButton(ft.Icons.CLOSE, icon_size=16, icon_color="#888888", on_click=close_window,
                              tooltip="Закрыть"),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.Padding(15, 0, 5, 0),
        )

        return ft.Container(
            width=width, height=height,
            bgcolor="#242429",  # Темный фон окна
            border_radius=12,
            border=ft.Border.all(1, "#333333"),
            shadow=ft.BoxShadow(blur_radius=20, color="#00000080"),
            content=ft.Column([
                title_bar,
                ft.Container(content=content, padding=15, expand=True)
            ], spacing=0)
        )

    # =====================================================================
    # ЭЛЕМЕНТЫ УПРАВЛЕНИЯ
    # =====================================================================
    def create_reel(size=60):
        center = size / 2
        outer = ft.Container(width=size, height=size, border_radius=size / 2, bgcolor="#111111",
                             border=ft.Border.all(2, "#333333"))
        holes = []
        for i in range(6):
            angle = math.radians(i * 60)
            hx = center + (size * 0.25) * math.cos(angle) - 4
            hy = center + (size * 0.25) * math.sin(angle) - 4
            holes.append(ft.Container(width=8, height=8, bgcolor="#000000", border_radius=4, left=hx, top=hy))
        inner = ft.Container(width=size * 0.5, height=size * 0.5, bgcolor="#E53935", border_radius=size * 0.25,
                             left=center - size * 0.25, top=center - size * 0.25)
        shaft = ft.Container(width=12, height=12, bgcolor="#444444", border_radius=6, left=center - 6, top=center - 6)
        return ft.Stack([outer, *holes, inner, shaft], width=size, height=size)

    reel_l_container = ft.Container(content=create_reel(60))
    reel_r_container = ft.Container(content=create_reel(60))

    # Тексты
    track_title = ft.Text(tracks[0]["title"], size=16, color="#FFFFFF", weight=ft.FontWeight.BOLD,
                          text_align=ft.TextAlign.CENTER, width=260)
    track_artist = ft.Text(tracks[0]["artist"], size=12, color="#AAAAAA", text_align=ft.TextAlign.CENTER)
    time_current = ft.Text("00:00", size=12, color="#4CAF50", weight=ft.FontWeight.BOLD, width=45,
                           text_align=ft.TextAlign.CENTER)
    time_total = ft.Text("00:00", size=12, color="#666666", width=45, text_align=ft.TextAlign.CENTER)

    # Визуализация
    vu_bars = [ft.Container(width=8, height=10, bgcolor="#333333", border_radius=2) for _ in range(15)]
    vu_row = ft.Row(vu_bars, spacing=3, alignment=ft.MainAxisAlignment.CENTER)

    eq_bars = [ft.Container(width=12, height=10, bgcolor="#2196F3", border_radius=3) for _ in range(12)]
    eq_row = ft.Row(eq_bars, spacing=5, alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.END)

    # Прогресс-бар
    seek_fill = ft.Container(width=0, height=6, bgcolor="#4CAF50", border_radius=3)
    seek_bar_bg = ft.Container(
        width=200, height=6, bgcolor="#333333", border_radius=3,
        on_click=lambda e: on_seek(e),
        content=seek_fill
    )

    def on_seek(e):
        new_percent = e.local_x / 200
        duration = tracks[state["current_track_idx"]]["duration_sec"]
        state["current_time_sec"] = new_percent * duration
        update_ui_time()

    # Кнопки плеера (Стильные)
    def toggle_play(e):
        state["playing"] = not state["playing"]
        btn_play.content = ft.Icon(ft.Icons.PAUSE if state["playing"] else ft.Icons.PLAY_ARROW, color="white", size=32)
        btn_play.bgcolor = "#FF5252" if state["playing"] else "#4CAF50"
        page.update()

    def stop_play(e):
        state["playing"] = False
        state["current_time_sec"] = 0
        btn_play.content = ft.Icon(ft.Icons.PLAY_ARROW, color="white", size=32)
        btn_play.bgcolor = "#4CAF50"
        update_ui_time()

    def next_track(e):
        state["current_track_idx"] = (state["current_track_idx"] + 1) % len(tracks)
        state["current_time_sec"] = 0
        update_track_info()
        update_ui_time()

    def prev_track(e):
        state["current_track_idx"] = (state["current_track_idx"] - 1) % len(tracks)
        state["current_time_sec"] = 0
        update_track_info()
        update_ui_time()

    def update_track_info():
        data = tracks[state["current_track_idx"]]
        track_title.value = data["title"]
        track_artist.value = data["artist"]

    def update_ui_time():
        duration = tracks[state["current_track_idx"]]["duration_sec"]
        time_current.value = format_time(state["current_time_sec"])
        time_total.value = format_time(duration)
        if duration > 0:
            seek_fill.width = 200 * (state["current_time_sec"] / duration)

    # Кнопка Play (стильная)
    btn_play = ft.Button(
        content=ft.Icon(ft.Icons.PLAY_ARROW, color="white", size=32),
        on_click=toggle_play,
        bgcolor="#4CAF50",
        width=64, height=64,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=32),
            overlay_color="#FFFFFF20",
        ),
        elevation=5
    )

    # --- ОКНО 1: МАГНИТОФОН ---
    deck_content = ft.Column([
        ft.Container(
            width=260, height=100, bgcolor="#1A1A1E", border_radius=10, border=ft.Border.all(1, "#333333"),
            content=ft.Stack([
                ft.Container(width=180, height=40, bgcolor="#111111", border_radius=8, left=40, top=30,
                             border=ft.Border.all(1, "#444444")),
                ft.Container(content=reel_l_container, left=50, top=20),
                ft.Container(content=reel_r_container, left=150, top=20),
            ])
        ),
        ft.Container(height=10),
        ft.Column([track_title, track_artist], alignment=ft.MainAxisAlignment.CENTER,
                  horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Container(height=10),
        ft.Row([time_current, seek_bar_bg, time_total], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        ft.Container(height=10),
        vu_row,
        ft.Container(height=15),
        ft.Row([
            ft.IconButton(ft.Icons.SKIP_PREVIOUS, icon_color="#FFFFFF", on_click=prev_track, width=40, height=40,
                          style=ft.ButtonStyle(bgcolor="#333333", shape=ft.RoundedRectangleBorder(radius=20))),
            btn_play,
            ft.IconButton(ft.Icons.STOP, icon_color="#FFFFFF", on_click=stop_play, width=40, height=40,
                          style=ft.ButtonStyle(bgcolor="#333333", shape=ft.RoundedRectangleBorder(radius=20))),
            ft.IconButton(ft.Icons.SKIP_NEXT, icon_color="#FFFFFF", on_click=next_track, width=40, height=40,
                          style=ft.ButtonStyle(bgcolor="#333333", shape=ft.RoundedRectangleBorder(radius=20))),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=15)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)

    window1 = create_window("Магнитофон", deck_content, 320, 400, "deck")

    # --- ОКНО 2: ПЛЕЙЛИСТ ---
    playlist_items = []
    for i, t in enumerate(tracks):
        playlist_items.append(
            ft.Container(
                content=ft.Row([
                    ft.Text(f"{i + 1}.", size=12, color="#888888", width=20),
                    ft.Column([ft.Text(t["title"], size=12, color="#FFFFFF", weight=ft.FontWeight.W_500),
                               ft.Text(t["artist"], size=10, color="#AAAAAA")], spacing=0, expand=True),
                    ft.Text(format_time(t["duration_sec"]), size=10, color="#666666")
                ]),
                padding=ft.Padding(10, 8, 10, 8),
                bgcolor="#1A1A1E" if i % 2 == 0 else "#242429",  # Чересстрочный фон
                border_radius=5,
                on_click=lambda e, idx=i: select_track(idx)
            )
        )

    def select_track(idx):
        state["current_track_idx"] = idx
        state["current_time_sec"] = 0
        update_track_info()
        update_ui_time()

    playlist_content = ft.Column(playlist_items, spacing=5, scroll=ft.ScrollMode.AUTO)
    window2 = create_window("Плейлист", playlist_content, 300, 400, "playlist")

    # --- ОКНО 3: ЭКВАЛАЙЗЕР ---
    eq_content = ft.Column([
        ft.Text("Визуализация звука", size=14, color="#AAAAAA", weight=ft.FontWeight.BOLD),
        ft.Container(content=eq_row, height=150, alignment=ft.Alignment.BOTTOM_CENTER)
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
    window3 = create_window("Эквалайзер", eq_content, 300, 300, "eq")

    # --- ОКНО 4: МИНИ-ПЛЕЕР ---
    mini_seek = ft.Container(width=180, height=6, bgcolor="#333333", border_radius=3,
                             content=ft.Container(width=0, height=6, bgcolor="#2196F3", border_radius=3))

    mini_content = ft.Column([
        ft.Row([ft.Icon(ft.Icons.MUSIC_NOTE, color="#2196F3", size=16),
                ft.Text("Now Playing", size=12, color="#AAAAAA", weight=ft.FontWeight.W_500)],
               alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(height=10),
        mini_seek,
        ft.Container(height=10),
        ft.Row([
            ft.IconButton(ft.Icons.SKIP_PREVIOUS, icon_color="#FFFFFF", on_click=prev_track, width=40, height=40),
            ft.IconButton(ft.Icons.PLAY_CIRCLE_FILLED, icon_color="#4CAF50", icon_size=36, on_click=toggle_play,
                          width=50, height=50),
            ft.IconButton(ft.Icons.SKIP_NEXT, icon_color="#FFFFFF", on_click=next_track, width=40, height=40)
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=15)
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    window4 = create_window("Мини-плеер", mini_content, 240, 180, "mini")

    # --- ОКНО 5: СВОЙСТВА ---
    def volume_change(e):
        state["volume"] = e.control.value

    settings_content = ft.Column([
        ft.Text("Свойства трека", size=14, color="#FFFFFF", weight=ft.FontWeight.BOLD),
        ft.Divider(height=1, color="#333333"),
        ft.Text("Формат: Digital", size=12, color="#AAAAAA"),
        ft.Text("Битрейт: 320 kbps", size=12, color="#AAAAAA"),
        ft.Text("Год: 1973", size=12, color="#AAAAAA"),
        ft.Divider(height=1, color="#333333"),
        ft.Row([ft.Text("Громкость:", size=12, color="#AAAAAA"),
                ft.Slider(min=0, max=100, value=65, width=120, active_color="#4CAF50", on_change=volume_change)]),
        ft.Button(content=ft.Text("ОК", color="white"), bgcolor="#2196F3",
                  style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))
    ], spacing=10)
    window5 = create_window("Свойства", settings_content, 260, 280, "props")

    # =====================================================================
    # ПАНЕЛЬ ЗАДАЧ (Современная)
    # =====================================================================
    taskbar_buttons = {}
    window_names = {
        "deck": "Магнитофон",
        "playlist": "Плейлист",
        "eq": "Эквалайзер",
        "mini": "Мини-плеер",
        "props": "Свойства"
    }

    def toggle_window(window_id):
        state["windows"][window_id] = not state["windows"][window_id]
        refresh_desktop()

    for key, name in window_names.items():
        taskbar_buttons[key] = ft.Button(
            content=ft.Text(name, size=12, color="white", weight=ft.FontWeight.W_500),
            bgcolor="#4CAF50" if state["windows"][key] else "#1A1A1E",
            on_click=lambda e, k=key: toggle_window(k),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                overlay_color="#FFFFFF10",
            )
        )

    def refresh_taskbar():
        for key, btn in taskbar_buttons.items():
            btn.bgcolor = "#4CAF50" if state["windows"][key] else "#1A1A1E"

    taskbar = ft.Container(
        width=1000, height=60,
        bgcolor="#1A1A1E",
        border_radius=15,
        content=ft.Row(list(taskbar_buttons.values()), spacing=10, alignment=ft.MainAxisAlignment.CENTER),
        padding=10,
        shadow=ft.BoxShadow(blur_radius=15, color="#00000080")
    )

    # =====================================================================
    # СБОРКА
    # =====================================================================
    def build_desktop():
        row1 = []
        row2 = []

        if state["windows"]["deck"]: row1.append(window1)
        if state["windows"]["playlist"]: row1.append(window2)
        if state["windows"]["eq"]: row1.append(window3)

        if state["windows"]["mini"]: row2.append(window4)
        if state["windows"]["props"]: row2.append(window5)

        desktop_rows = []
        if row1: desktop_rows.append(ft.Row(row1, alignment=ft.MainAxisAlignment.CENTER, spacing=20, wrap=True))
        if row2: desktop_rows.append(ft.Row(row2, alignment=ft.MainAxisAlignment.CENTER, spacing=20, wrap=True))

        if not desktop_rows:
            desktop_rows.append(ft.Text("Все окна закрыты", color="#555555", size=20))

        return ft.Column(desktop_rows, alignment=ft.MainAxisAlignment.CENTER,
                         horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)

    desktop_ui = ft.Container(content=build_desktop(), alignment=ft.Alignment.CENTER, padding=20, expand=True)

    def refresh_desktop():
        desktop_ui.content = build_desktop()
        refresh_taskbar()
        page.update()

    # --- АНИМАЦИЯ ---
    async def animate_loop():
        while True:
            if state["playing"]:
                state["current_time_sec"] += 0.1
                duration = tracks[state["current_track_idx"]]["duration_sec"]

                if state["current_time_sec"] >= duration:
                    state["current_time_sec"] = 0
                    state["current_track_idx"] = (state["current_track_idx"] + 1) % len(tracks)
                    update_track_info()

                state["angle"] += 8
                reel_l_container.rotate = ft.Rotate(angle=math.radians(state["angle"]), alignment=ft.Alignment.CENTER)
                reel_r_container.rotate = ft.Rotate(angle=math.radians(state["angle"]), alignment=ft.Alignment.CENTER)

                vol_factor = state["volume"] / 100.0
                for bar in vu_bars:
                    bar.height = random.randint(5, 25) * vol_factor
                    bar.bgcolor = "#F44336" if bar.height > 18 else ("#FFEB3B" if bar.height > 12 else "#4CAF50")

                for bar in eq_bars:
                    bar.height = random.randint(10, 140) * vol_factor
                    bar.bgcolor = "#F44336" if bar.height > 90 else ("#FFEB3B" if bar.height > 50 else "#2196F3")

                update_ui_time()
                page.update()

            await asyncio.sleep(0.1)

    page.run_task(animate_loop)
    update_ui_time()

    page.add(
        ft.Column([
            desktop_ui,
            taskbar
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, expand=True)
    )


if __name__ == "__main__":
    ft.run(main)