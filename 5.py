import flet as ft
import math
import asyncio
from dataclasses import dataclass


# ==============================================================================
# МОДУЛЬ 1: КОНСТАНТЫ И НАСТРОЙКИ
# ==============================================================================
class GameConfig:
    WINDOW_WIDTH = 850
    WINDOW_HEIGHT = 650
    BG_COLOR = "#0D1117"
    GAUGE_SIZE = 450
    MAX_SPEED = 120

    BASE_ACCEL = 2.0
    BRAKE_FORCE = 2.5
    ENGINE_BRAKE = 0.5

    MAX_RPM = 8000
    IDLE_RPM = 800
    REDLINE_RPM = 7000
    BLOW_UP_TEMP = 120.0
    TICK_RATE = 0.016


# ==============================================================================
# МОДУЛЬ 2: СОСТОЯНИЕ АВТОМОБИЛЯ
# ==============================================================================
@dataclass
class CarState:
    speed: float = 0.0
    rpm: float = 800.0
    gear: int = 1
    temperature: float = 20.0
    is_engine_on: bool = False
    is_engine_blown: bool = False
    is_accelerating: bool = False
    is_braking: bool = False
    max_speed_reached: float = 0.0

    def reset(self):
        self.speed = 0.0
        self.rpm = 800.0
        self.gear = 1
        self.temperature = 20.0
        self.is_engine_on = False
        self.is_engine_blown = False
        self.is_accelerating = False
        self.is_braking = False


# ==============================================================================
# МОДУЛЬ 3: ФИЗИЧЕСКИЙ ДВИЖОК
# ==============================================================================
class PhysicsEngine:
    GEAR_MAX_SPEEDS = {1: 40, 2: 70, 3: 95, 4: 115, 5: 130}

    @staticmethod
    def update(state: CarState, delta_time: float, config: GameConfig):
        if state.is_engine_blown:
            if state.speed > 0:
                state.speed -= 1.5 * delta_time * 60
                if state.speed < 0: state.speed = 0
            PhysicsEngine._update_temp(state, delta_time, config)
            return

        if state.is_engine_on:
            if state.is_accelerating and not state.is_braking:
                max_gear_speed = PhysicsEngine.GEAR_MAX_SPEEDS[state.gear]
                if state.speed < max_gear_speed:
                    accel = config.BASE_ACCEL * (1.0 - (state.gear - 1) * 0.15)
                    state.speed += accel * delta_time * 60
                state.rpm = config.IDLE_RPM + (state.speed / max_gear_speed) * (config.REDLINE_RPM - config.IDLE_RPM)
            elif state.is_braking:
                state.speed -= config.BRAKE_FORCE * delta_time * 60
                if state.speed < 0: state.speed = 0
                state.rpm = max(config.IDLE_RPM, state.rpm - 2000 * delta_time * 60)
            else:
                state.speed -= config.ENGINE_BRAKE * delta_time * 60
                if state.speed < 0: state.speed = 0
                state.rpm = max(config.IDLE_RPM, state.rpm - 1000 * delta_time)
        else:
            if state.speed > 0:
                state.speed -= 0.5 * delta_time * 60
                if state.speed < 0: state.speed = 0
            state.rpm = max(0, state.rpm - 3000 * delta_time)

        if state.speed > config.MAX_SPEED: state.speed = config.MAX_SPEED
        if state.speed < 0: state.speed = 0
        if state.speed > state.max_speed_reached: state.max_speed_reached = state.speed

        PhysicsEngine._update_temp(state, delta_time, config)

    @staticmethod
    def _update_temp(state: CarState, delta_time: float, config: GameConfig):
        if state.rpm > 5000:
            state.temperature += 0.8 * delta_time * 60 * (state.rpm / config.MAX_RPM)
        elif state.rpm < 2000:
            state.temperature -= 0.3 * delta_time * 60

        if state.temperature > config.BLOW_UP_TEMP:
            state.is_engine_blown = True
            state.is_engine_on = False
            state.speed = 0
            state.rpm = 0


# ==============================================================================
# МОДУЛЬ 4: РЕНДЕРИНГ ГРАФИКИ (СПИДОМЕТР)
# ==============================================================================
class GaugeRenderer:
    def __init__(self, size: int, max_speed: int):
        self.size = size
        self.center = size / 2
        self.max_speed = max_speed
        self.radius = size * 0.4
        self.elements = []
        self._build_components()

    def _build_components(self):
        self.elements.append(
            ft.Container(width=self.size, height=self.size, border_radius=self.size / 2, bgcolor="#1A1A1A",
                         border=ft.Border.all(15, "#333333"), shadow=ft.BoxShadow(blur_radius=20, color="#000000"))
        )
        for i in range(0, self.max_speed + 1, 5):
            angle_deg = 135 + (i / self.max_speed) * 270
            rad = math.radians(angle_deg)
            is_major = (i % 10 == 0)
            tick_len = 20 if is_major else 10
            tick_width = 4 if is_major else 2

            r_outer, r_inner = self.radius, self.radius - tick_len
            x_o, y_o = self.center + r_outer * math.cos(rad), self.center + r_outer * math.sin(rad)
            x_i, y_i = self.center + r_inner * math.cos(rad), self.center + r_inner * math.sin(rad)
            mid_x, mid_y = (x_o + x_i) / 2, (y_o + y_i) / 2

            self.elements.append(
                ft.Container(width=tick_width, height=tick_len, bgcolor="#FFFFFF", left=mid_x - tick_width / 2,
                             top=mid_y - tick_len / 2,
                             rotate=ft.Rotate(angle=rad + math.pi / 2, alignment=ft.Alignment.CENTER))
            )
            if is_major:
                r_text = self.radius - 50
                tx, ty = self.center + r_text * math.cos(rad), self.center + r_text * math.sin(rad)
                self.elements.append(
                    ft.Container(content=ft.Text(str(i), size=16, color="#FFFFFF", weight=ft.FontWeight.BOLD),
                                 left=tx - 20, top=ty - 12, width=40, alignment=ft.Alignment.CENTER)
                )

        needle_len = self.radius - 20
        self.needle = ft.Container(width=8, height=needle_len, bgcolor="#FF1744", border_radius=4, left=self.center - 4,
                                   top=self.center - needle_len,
                                   rotate=ft.Rotate(angle=math.radians(135), alignment=ft.Alignment.BOTTOM_CENTER),
                                   shadow=ft.BoxShadow(blur_radius=15, color="#FF1744", spread_radius=4))
        self.tail = ft.Container(width=8, height=40, bgcolor="#FF1744", border_radius=4, left=self.center - 4,
                                 top=self.center,
                                 rotate=ft.Rotate(angle=math.radians(135), alignment=ft.Alignment.TOP_CENTER))
        self.cap = ft.Container(width=36, height=36, bgcolor="#111111", border_radius=18, left=self.center - 18,
                                top=self.center - 18, border=ft.Border.all(3, "#FF1744"))

        self.elements.extend([self.needle, self.tail, self.cap])

    def get_stack(self):
        return ft.Stack(self.elements, width=self.size, height=self.size)

    def update_needle(self, speed):
        rad = math.radians(135 + (speed / self.max_speed) * 270)
        self.needle.rotate = ft.Rotate(angle=rad, alignment=ft.Alignment.BOTTOM_CENTER)
        self.tail.rotate = ft.Rotate(angle=rad, alignment=ft.Alignment.TOP_CENTER)


# ==============================================================================
# МОДУЛЬ 5: ГЛАВНЫЙ КОНТРОЛЛЕР
# ==============================================================================
class DragRacingGame:
    def __init__(self, page: ft.Page):
        self.page = page
        self.config = GameConfig()
        self.state = CarState()
        self.gauge = GaugeRenderer(self.config.GAUGE_SIZE, self.config.MAX_SPEED)

        self.speed_text = ft.Text("0", size=52, color="#FF1744", weight=ft.FontWeight.BOLD)
        self.rpm_text = ft.Text("800", size=16, color="#FFFFFF")
        self.temp_text = ft.Text("20°C", size=16, color="#FFFFFF")
        self.gear_text = ft.Text("1", size=56, color="#FF1744", weight=ft.FontWeight.BOLD)
        self.record_text = ft.Text("Рекорд: 0 км/ч", size=14, color="#888888")
        self.status_msg = ft.Text("Нажми и удерживай ГАЗ", size=16, color="#00E676")

        self.rpm_bar = ft.Container(width=20, height=10, bgcolor="#00E676", border_radius=5,
                                    animate=ft.Animation(100, ft.AnimationCurve.EASE_OUT))
        self.temp_bar = ft.Container(width=20, height=10, bgcolor="#42A5F5", border_radius=5,
                                     animate=ft.Animation(100, ft.AnimationCurve.EASE_OUT))

        self._build_ui()
        self.page.run_task(self._game_loop)

    def _build_ui(self):
        self.gas_btn = ft.GestureDetector(
            on_tap_down=self._start_accel, on_tap_up=self._stop_accel,
            content=ft.Container(content=ft.Text("ГАЗ", size=24, weight=ft.FontWeight.BOLD, color="white"), width=180,
                                 height=70, bgcolor="#4CAF50", border_radius=15, alignment=ft.Alignment.CENTER)
        )
        self.brake_btn = ft.GestureDetector(
            on_tap_down=self._start_brake, on_tap_up=self._stop_brake,
            content=ft.Container(content=ft.Text("ТОРМОЗ", size=20, weight=ft.FontWeight.BOLD, color="white"),
                                 width=140, height=70, bgcolor="#F44336", border_radius=15,
                                 alignment=ft.Alignment.CENTER)
        )

        self.restart_btn = ft.Button(
            content=ft.Text("СБРОС", color="white", weight=ft.FontWeight.BOLD),
            on_click=self._on_restart,
            bgcolor="#2196F3",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        )

        self.gear_buttons = []
        for g in range(1, 6):
            btn = ft.Container(content=ft.Text(str(g), size=20, color="white", weight=ft.FontWeight.BOLD), width=50,
                               height=50, bgcolor="#333333", border_radius=10, alignment=ft.Alignment.CENTER,
                               on_click=lambda e, gear=g: self._change_gear(gear))
            self.gear_buttons.append(btn)

        self.page.add(
            ft.Container(
                content=ft.Column(
                    [
                        # Верхняя панель (Заголовок, Рекорд, Сброс)
                        ft.Row([
                            ft.Text("DRAG RACING", size=24, weight=ft.FontWeight.BOLD, color="#FF1744"),
                            ft.Row([self.record_text, self.restart_btn], spacing=20)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=800),

                        # Центральная панель (Приборы)
                        ft.Row([
                            ft.Column([
                                ft.Text("ТАХОМЕТР", size=12, color="#FFFFFF"), self.rpm_text,
                                ft.Container(content=self.rpm_bar, width=200, height=10, bgcolor="#222222",
                                             border_radius=5),
                                ft.Divider(color="#333"),
                                ft.Text("ТЕМПЕРАТУРА", size=12, color="#FFFFFF"), self.temp_text,
                                ft.Container(content=self.temp_bar, width=200, height=10, bgcolor="#222222",
                                             border_radius=5),
                            ], alignment=ft.MainAxisAlignment.CENTER, width=220),

                            self.gauge.get_stack(),

                            ft.Column([
                                ft.Text("ПЕРЕДАЧА", size=12, color="#FFFFFF"), self.gear_text,
                                ft.Divider(color="#333"),
                                ft.Text("СКОРОСТЬ", size=12, color="#FFFFFF"), self.speed_text,
                                ft.Text("КМ/Ч", size=12, color="#888888"),
                            ], alignment=ft.MainAxisAlignment.CENTER, width=200)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=850),

                        # Нижняя панель (Управление)
                        ft.Row([self.gas_btn, ft.Column(
                            [ft.Row(self.gear_buttons), ft.Text("КОРОБКА ПЕРЕДАЧ", size=10, color="#555")]),
                                self.brake_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=40),

                        self.status_msg
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                ),
                width=self.config.WINDOW_WIDTH, height=self.config.WINDOW_HEIGHT, bgcolor=self.config.BG_COLOR,
                padding=20, border_radius=20
            )
        )

    async def _game_loop(self):
        while True:
            PhysicsEngine.update(self.state, self.config.TICK_RATE, self.config)
            self._update_ui()
            await asyncio.sleep(self.config.TICK_RATE)

    def _update_ui(self):
        self.gauge.update_needle(self.state.speed)
        self.speed_text.value = str(int(self.state.speed))
        self.rpm_text.value = f"{int(self.state.rpm)}"
        self.temp_text.value = f"{int(self.state.temperature)}°C"
        self.gear_text.value = str(self.state.gear)
        self.record_text.value = f"Рекорд: {int(self.state.max_speed_reached)} км/ч"

        self.rpm_bar.width = 200 * min(1.0, self.state.rpm / self.config.MAX_RPM)
        self.rpm_bar.bgcolor = "#F44336" if self.state.rpm > self.config.REDLINE_RPM else "#00E676"

        self.temp_bar.width = 200 * min(1.0, self.state.temperature / self.config.BLOW_UP_TEMP)
        self.temp_bar.bgcolor = "#F44336" if self.state.temperature > 80 else "#42A5F5"

        # Логика блокировки и статусов
        if self.state.is_engine_blown:
            self.status_msg.value = "💥 ДВИГАТЕЛЬ ВЗОРВАН! НАЖМИ СБРОС"
            self.status_msg.color = "#F44336"
            self.gas_btn.content.bgcolor = "#555555"  # Блокируем визуально
            self.brake_btn.content.bgcolor = "#555555"
        else:
            self.gas_btn.content.bgcolor = "#4CAF50"
            self.brake_btn.content.bgcolor = "#F44336"

            if self.state.is_braking:
                self.status_msg.value = "ТОРМОЖЕНИЕ"
                self.status_msg.color = "#F44336"
            elif self.state.is_accelerating:
                self.status_msg.value = "УСКОРЕНИЕ..."
                self.status_msg.color = "#FFEB3B"
            else:
                self.status_msg.value = "Нажми и удерживай ГАЗ"
                self.status_msg.color = "#00E676"

        for i, btn in enumerate(self.gear_buttons):
            btn.bgcolor = "#FF1744" if (i + 1) == self.state.gear else "#333333"

        self.page.update()

    def _start_accel(self, e):
        if not self.state.is_engine_blown:
            self.state.is_engine_on = True
            self.state.is_accelerating = True
            self.state.is_braking = False

    def _stop_accel(self, e):
        self.state.is_accelerating = False

    def _start_brake(self, e):
        if not self.state.is_engine_blown:
            self.state.is_braking = True
            self.state.is_accelerating = False

    def _stop_brake(self, e):
        self.state.is_braking = False

    def _change_gear(self, gear: int):
        if not self.state.is_engine_blown:
            self.state.gear = gear

    def _on_restart(self, e):
        self.state.reset()


# ==============================================================================
# МОДУЛЬ 6: ЗАПУСК
# ==============================================================================
def main(page: ft.Page):
    page.title = "Drag Racing Ultimate"
    page.bgcolor = "#000000"
    page.padding = 0
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    game = DragRacingGame(page)


if __name__ == "__main__":
    ft.run(main)