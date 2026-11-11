from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.core.audio import SoundLoader
from kivy.core.clipboard import Clipboard
from kivy.animation import Animation
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Ellipse, Line

import ast
import operator
import math
import wave
import struct
import tempfile
import os
import json


Window.clearcolor = (0.025, 0.035, 0.09, 1)


# ==================================
# SOUND GENERATOR
# ==================================

def create_sound(name, frequencies, duration):
    path = os.path.join(tempfile.gettempdir(), name)
    rate = 44100

    with wave.open(path, "w") as wav:
        wav.setparams((1, 2, rate, 0, "NONE", "NONE"))
        frames = bytearray()
        total = int(rate * duration)

        for i in range(total):
            t = i / rate
            section = min(
                int(t / (duration / len(frequencies))),
                len(frequencies) - 1
            )
            freq = frequencies[section]
            envelope = min(1, t * 50) * max(0, 1 - t / duration)
            value = int(
                10000 * envelope *
                math.sin(2 * math.pi * freq * t)
            )
            frames.extend(struct.pack("<h", value))

        wav.writeframes(frames)

    return path


# ==================================
# HANGING ALIEN
# ==================================

class HangingAlien(Widget):
    swing = NumericProperty(0)
    jump = NumericProperty(0)
    expression = StringProperty("happy")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bind(
            pos=self.draw,
            size=self.draw,
            swing=self.draw,
            jump=self.draw,
            expression=self.draw
        )

        Clock.schedule_once(lambda dt: self.idle_animation(), 0)
        Clock.schedule_interval(self.auto_blink, 3)

    def idle_animation(self):
        anim = (
            Animation(swing=dp(7), duration=1.1) +
            Animation(swing=-dp(7), duration=1.1)
        )
        anim.repeat = True
        anim.start(self)

    def auto_blink(self, dt):
        if self.expression == "happy":
            self.expression = "blink"
            Clock.schedule_once(
                lambda t: self.set_expression("happy"), 0.18
            )

    def set_expression(self, value):
        self.expression = value

    def react(self, mood):
        self.expression = mood
        Animation.cancel_all(self, "jump")

        if mood == "dance":
            anim = (
                Animation(jump=dp(18), duration=0.18) +
                Animation(jump=0, duration=0.18) +
                Animation(jump=dp(18), duration=0.18) +
                Animation(jump=0, duration=0.18)
            )
            anim.start(self)
            Clock.schedule_once(
                lambda dt: self.reset_reaction(), 0.8
            )
        else:
            Animation(jump=dp(7), duration=0.15).start(self)
            Clock.schedule_once(
                lambda dt: self.reset_reaction(), 0.8
            )

    def reset_reaction(self):
        self.expression = "happy"
        Animation(jump=0, duration=0.2).start(self)

    def draw(self, *args):
        self.canvas.clear()
        x = self.center_x + self.swing
        y = self.y + self.jump

        with self.canvas:
            # Rope
            Color(0.75, 0.7, 1, 1)
            Line(
                points=[
                    self.center_x, self.y + self.height,
                    x, y + dp(125)
                ],
                width=dp(2)
            )

            # Antenna
            Color(0.2, 1, 0.6, 1)
            Line(
                points=[x, y + dp(109), x, y + dp(120)],
                width=dp(2)
            )
            Ellipse(
                pos=(x - dp(4), y + dp(117)),
                size=(dp(8), dp(8))
            )

            # Head
            Color(0.25, 0.95, 0.5, 1)
            Ellipse(
                pos=(x - dp(24), y + dp(68)),
                size=(dp(48), dp(45))
            )

            # Eyes
            Color(0.02, 0.04, 0.10, 1)

            if self.expression == "blink":
                Line(
                    points=[x-dp(15), y+dp(90), x-dp(4), y+dp(90)],
                    width=dp(2)
                )
                Line(
                    points=[x+dp(4), y+dp(90), x+dp(15), y+dp(90)],
                    width=dp(2)
                )
            elif self.expression == "surprised":
                Ellipse(
                    pos=(x-dp(14), y+dp(82)),
                    size=(dp(10), dp(14))
                )
                Ellipse(
                    pos=(x+dp(4), y+dp(82)),
                    size=(dp(10), dp(14))
                )
            else:
                eye_size = dp(5) if self.expression == "sad" else dp(12)
                Ellipse(
                    pos=(x-dp(15), y+dp(83)),
                    size=(eye_size, eye_size+dp(5))
                )
                Ellipse(
                    pos=(x+dp(3), y+dp(83)),
                    size=(eye_size, eye_size+dp(5))
                )

            # Eye shine
            Color(1, 1, 1, 1)
            if self.expression not in ("blink", "sad"):
                Ellipse(
                    pos=(x-dp(12), y+dp(94)),
                    size=(dp(4), dp(4))
                )
                Ellipse(
                    pos=(x+dp(6), y+dp(94)),
                    size=(dp(4), dp(4))
                )

            # Mouth
            Color(0, 0.25, 0.12, 1)
            if self.expression == "surprised":
                Ellipse(
                    pos=(x-dp(4), y+dp(72)),
                    size=(dp(8), dp(9))
                )
            elif self.expression == "sad":
                Line(
                    points=[
                        x-dp(6), y+dp(73),
                        x, y+dp(77),
                        x+dp(6), y+dp(73)
                    ],
                    width=dp(2)
                )
            else:
                Line(
                    points=[
                        x-dp(6), y+dp(78),
                        x, y+dp(74),
                        x+dp(6), y+dp(78)
                    ],
                    width=dp(2)
                )

            # Body
            Color(0.15, 0.8, 0.4, 1)
            Ellipse(
                pos=(x-dp(14), y+dp(43)),
                size=(dp(28), dp(29))
            )

            # Arms and legs
            Color(0.15, 0.8, 0.4, 1)
            Line(
                points=[x-dp(10), y+dp(60), x-dp(24), y+dp(76)],
                width=dp(3)
            )
            Line(
                points=[x+dp(10), y+dp(60), x+dp(24), y+dp(76)],
                width=dp(3)
            )
            Line(
                points=[x-dp(6), y+dp(45), x-dp(11), y+dp(33)],
                width=dp(3)
            )
            Line(
                points=[x+dp(6), y+dp(45), x+dp(11), y+dp(33)],
                width=dp(3)
            )


# ==================================
# ROUND BUTTON
# ==================================

class RoundButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.font_size = sp(21)
        self.bold = True
        self.base_rgba = (0.12, 0.16, 0.30, 1)

        with self.canvas.before:
            self.bg_color = Color(0.12, 0.16, 0.30, 1)
            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(15)]
            )

        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def on_press(self):
        Animation(
            rgba=(0.25, 0.85, 1, 1), duration=0.08
        ).start(self.bg_color)

    def on_release(self):
        Animation(
            rgba=self.base_rgba, duration=0.15
        ).start(self.bg_color)


# ==================================
# MAIN CALCULATOR
# ==================================

class AnkitCalculator(App):
    def build(self):
        self.expression = ""
        self.last_result = False
        self.history = []
        self.history_file = os.path.join(self.user_data_dir, "ankit_history.json")
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as file:
                    saved = json.load(file)
                    if isinstance(saved, list):
                        self.history = saved[-100:]
        except Exception:
            self.history = []

        # Load sounds safely
        self.click_sound = None
        self.success_sound = None
        self.error_sound = None

        try:
            self.click_sound = SoundLoader.load(
                create_sound("ankit_click.wav", [700, 900], 0.12)
            )
            self.success_sound = SoundLoader.load(
                create_sound("ankit_success.wav", [600, 800, 1100], 0.35)
            )
            self.error_sound = SoundLoader.load(
                create_sound("ankit_error.wav", [250, 180], 0.25)
            )
        except Exception:
            pass

        self.dark_theme = True
        self.calc_buttons = []
        self.utility_buttons = []

        main = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(7)
        )
        self.main_layout = main

        heading = Label(
            text="[b]ANKIT PRO[/b]  [color=00E5FF]6.0[/color]",
            markup=True,
            font_size=sp(27),
            size_hint_y=0.085
        )
        self.heading = heading
        main.add_widget(heading)

        alien_box = BoxLayout(
            orientation="vertical",
            size_hint_y=0.18
        )
        self.alien = HangingAlien()
        alien_box.add_widget(self.alien)
        main.add_widget(alien_box)

        self.message = Label(
            text="Hello! Let's calculate",
            font_size=sp(14),
            color=(0.4, 1, 0.8, 1),
            size_hint_y=0.05
        )
        main.add_widget(self.message)

        self.display = Label(
            text="0",
            font_size=sp(35),
            bold=True,
            color=(1, 1, 1, 1),
            halign="right",
            valign="middle",
            size_hint_y=0.15
        )
        self.display.bind(
            size=lambda obj, val: setattr(obj, "text_size", val)
        )
        main.add_widget(self.display)

        grid = GridLayout(
            cols=4,
            spacing=dp(7),
            size_hint_y=0.43
        )

        buttons = [
            ("AC", "AC"), ("⌫", "DEL"), ("%", "%"), ("÷", "/"),
            ("7", "7"), ("8", "8"), ("9", "9"), ("×", "*"),
            ("4", "4"), ("5", "5"), ("6", "6"), ("−", "-"),
            ("1", "1"), ("2", "2"), ("3", "3"), ("+", "+"),
            ("00", "00"), ("0", "0"), (".", "."), ("=", "=")
        ]

        for title, value in buttons:
            btn = RoundButton(text=title, font_size=sp(21))

            if value == "=":
                btn.bg_color.rgba = (0.0, 0.65, 0.85, 1)
            elif value in ("+", "-", "*", "/", "%"):
                btn.bg_color.rgba = (0.35, 0.20, 0.55, 1)
            elif value in ("AC", "DEL"):
                btn.bg_color.rgba = (0.65, 0.16, 0.28, 1)

            btn.base_rgba = btn.bg_color.rgba
            btn.bind(
                on_release=lambda instance, v=value: self.press(v)
            )
            self.calc_buttons.append((btn, value))
            grid.add_widget(btn)

        main.add_widget(grid)

        utility_row = BoxLayout(size_hint_y=0.065, spacing=dp(8))
        history_btn = Button(
            text="HISTORY",
            background_normal="",
            background_color=(0.08, 0.48, 0.62, 1),
            font_size=sp(14), bold=True
        )
        history_btn.bind(on_release=self.show_history)
        premium = Button(
            text="PREMIUM MATHS TOOLS",
            background_normal="",
            background_color=(0.35, 0.16, 0.65, 1),
            font_size=sp(14), bold=True
        )
        premium.bind(on_release=self.show_premium)
        utility_row.add_widget(history_btn)
        utility_row.add_widget(premium)
        self.utility_buttons.extend([history_btn, premium])
        main.add_widget(utility_row)

        extra_row = BoxLayout(size_hint_y=0.065, spacing=dp(8))
        copy_btn = Button(
            text="COPY RESULT",
            background_normal="",
            background_color=(0.08, 0.48, 0.42, 1),
            font_size=sp(13), bold=True
        )
        copy_btn.bind(on_release=self.copy_result)
        self.theme_btn = Button(
            text="☀ LIGHT MODE",
            background_normal="",
            background_color=(0.35, 0.32, 0.16, 1),
            font_size=sp(13), bold=True
        )
        self.theme_btn.bind(on_release=self.toggle_theme)
        extra_row.add_widget(copy_btn)
        extra_row.add_widget(self.theme_btn)
        self.utility_buttons.extend([copy_btn, self.theme_btn])
        main.add_widget(extra_row)

        footer = Label(
            text="[color=00E5FF]MADE BY ANKIT (dhantola) 🚀[/color]",
            markup=True,
            font_size=sp(12),
            size_hint_y=0.04
        )
        main.add_widget(footer)

        return main

    # ==================================
    # EXTRA FEATURES: COPY + THEME
    # ==================================

    def copy_result(self, instance):
        value = self.display.text.strip()
        if not value or value == "0" or value == "Error":
            self.message.text = "Nothing to copy yet!"
            self.alien.react("surprised")
            return
        try:
            Clipboard.copy(value)
            self.message.text = "Result copied to clipboard!"
            self.alien.react("dance")
            if self.success_sound:
                self.success_sound.play()
        except Exception:
            self.message.text = "Copy is not available on this device."

    def toggle_theme(self, instance):
        self.dark_theme = not self.dark_theme
        if self.dark_theme:
            Window.clearcolor = (0.025, 0.035, 0.09, 1)
            self.heading.color = (1, 1, 1, 1)
            self.display.color = (1, 1, 1, 1)
            self.message.color = (0.4, 1, 0.8, 1)
            self.theme_btn.text = "☀ LIGHT MODE"
            for btn, value in self.calc_buttons:
                if value == "=":
                    btn.base_rgba = (0.0, 0.65, 0.85, 1)
                    btn.bg_color.rgba = btn.base_rgba
                elif value in ("+", "-", "*", "/", "%"):
                    btn.base_rgba = (0.35, 0.20, 0.55, 1)
                    btn.bg_color.rgba = btn.base_rgba
                elif value in ("AC", "DEL"):
                    btn.base_rgba = (0.65, 0.16, 0.28, 1)
                    btn.bg_color.rgba = btn.base_rgba
                else:
                    btn.base_rgba = (0.12, 0.16, 0.30, 1)
                    btn.bg_color.rgba = btn.base_rgba
            self.utility_buttons[0].background_color = (0.08, 0.48, 0.62, 1)
            self.utility_buttons[1].background_color = (0.35, 0.16, 0.65, 1)
            self.utility_buttons[2].background_color = (0.08, 0.48, 0.42, 1)
            self.utility_buttons[3].background_color = (0.35, 0.32, 0.16, 1)
        else:
            Window.clearcolor = (0.91, 0.94, 0.98, 1)
            self.heading.color = (0.08, 0.12, 0.22, 1)
            self.display.color = (0.08, 0.12, 0.22, 1)
            self.message.color = (0.02, 0.42, 0.38, 1)
            self.theme_btn.text = "🌙 DARK MODE"
            for btn, value in self.calc_buttons:
                if value == "=":
                    btn.base_rgba = (0.0, 0.48, 0.68, 1)
                    btn.bg_color.rgba = btn.base_rgba
                elif value in ("+", "-", "*", "/", "%"):
                    btn.base_rgba = (0.48, 0.36, 0.70, 1)
                    btn.bg_color.rgba = btn.base_rgba
                elif value in ("AC", "DEL"):
                    btn.base_rgba = (0.78, 0.28, 0.36, 1)
                    btn.bg_color.rgba = btn.base_rgba
                else:
                    btn.base_rgba = (0.70, 0.77, 0.88, 1)
                    btn.bg_color.rgba = btn.base_rgba
                btn.color = (0.05, 0.08, 0.16, 1)
            self.utility_buttons[0].background_color = (0.10, 0.55, 0.68, 1)
            self.utility_buttons[1].background_color = (0.48, 0.34, 0.72, 1)
            self.utility_buttons[2].background_color = (0.12, 0.58, 0.48, 1)
            self.utility_buttons[3].background_color = (0.62, 0.55, 0.25, 1)
        self.message.text = "Theme changed! Looking fresh."
        self.alien.react("dance")

    # ==================================
    # BUTTON PRESS
    # ==================================

    def press(self, value):
        if self.click_sound:
            self.click_sound.play()

        if value == "AC":
            self.expression = ""
            self.display.text = "0"
            self.message.text = "Fresh start!"
            self.alien.react("dance")
            self.last_result = False
            return

        if value == "DEL":
            self.expression = self.expression[:-1]
            self.display.text = self.expression or "0"
            self.alien.react("sad")
            self.last_result = False
            return

        if value == "=":
            self.calculate()
            return

        if self.last_result:
            if value in "0123456789.":
                self.expression = ""
            self.last_result = False

        self.expression += value
        self.display.text = self.expression
        self.message.text = "Keep calculating!"
        self.alien.react("happy")

    # ==================================
    # CALCULATE
    # ==================================

    def calculate(self):
        try:
            if not self.expression:
                return

            original_expression = self.expression
            result = self.safe_calculate(self.expression)

            if isinstance(result, float):
                if not math.isfinite(result):
                    raise ValueError("Invalid result")
                if result.is_integer():
                    result = int(result)

            self.expression = str(result)
            self.display.text = str(result)
            self.add_history(original_expression, result)
            self.message.text = "Wow! Perfect answer!"
            self.alien.react("dance")

            if self.success_sound:
                self.success_sound.play()

            self.last_result = True

        except Exception:
            self.display.text = "Error"
            self.message.text = "Oops! Try again."
            self.alien.react("surprised")

            if self.error_sound:
                self.error_sound.play()

            self.expression = ""
            self.last_result = False

    # ==================================
    # CALCULATION HISTORY
    # ==================================

    def add_history(self, expression, result):
        self.history.append({"expression": str(expression), "result": str(result)})
        self.history = self.history[-100:]
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            with open(self.history_file, "w", encoding="utf-8") as file:
                json.dump(self.history, file, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def show_history(self, instance):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        title = Label(
            text="[b]CALCULATION HISTORY[/b]",
            markup=True, size_hint_y=None, height=dp(38), font_size=sp(18)
        )
        content.add_widget(title)

        if self.history:
            rows = []
            for item in reversed(self.history[-30:]):
                rows.append(f"{item.get('expression', '?')}  =  {item.get('result', '?')}")
            history_text = "\n".join(rows)
        else:
            history_text = "No calculations yet.\nYour results will appear here."

        history_label = Label(
            text=history_text, halign="left", valign="top",
            font_size=sp(15), color=(0.88, 0.94, 1, 1)
        )
        history_label.bind(size=lambda obj, val: setattr(obj, "text_size", val))
        content.add_widget(history_label)

        buttons = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        clear_btn = Button(text="CLEAR HISTORY", background_normal="", background_color=(0.65, 0.16, 0.28, 1))
        close_btn = Button(text="CLOSE", background_normal="", background_color=(0.08, 0.48, 0.62, 1))
        buttons.add_widget(clear_btn)
        buttons.add_widget(close_btn)
        content.add_widget(buttons)

        popup = Popup(title="ANKIT PRO", content=content, size_hint=(0.90, 0.72))

        def clear_history(*args):
            self.history = []
            try:
                if os.path.exists(self.history_file):
                    os.remove(self.history_file)
            except Exception:
                pass
            history_label.text = "No calculations yet.\nYour results will appear here."
            self.message.text = "History cleared!"
            self.alien.react("happy")

        clear_btn.bind(on_release=clear_history)
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    # ==================================
    # SAFE MATH ENGINE
    # ==================================

    def safe_calculate(self, expression):
        allowed_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Mod: operator.mod,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos
        }

        def evaluate(node):
            if isinstance(node, ast.Expression):
                return evaluate(node.body)

            if isinstance(node, ast.Constant):
                if type(node.value) in (int, float):
                    return node.value
                raise ValueError("Invalid number")

            if isinstance(node, ast.BinOp):
                op_type = type(node.op)
                if op_type not in allowed_operators:
                    raise ValueError("Invalid operator")
                left = evaluate(node.left)
                right = evaluate(node.right)
                return allowed_operators[op_type](left, right)

            if isinstance(node, ast.UnaryOp):
                op_type = type(node.op)
                if op_type not in allowed_operators:
                    raise ValueError("Invalid operator")
                return allowed_operators[op_type](
                    evaluate(node.operand)
                )

            raise ValueError("Invalid expression")

        tree = ast.parse(expression, mode="eval")
        return evaluate(tree)

    # ==================================
    # PREMIUM MATHS TOOLS - NOW WORKING
    # ==================================

    def show_premium(self, instance):
        content = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(12)
        )

        title = Label(
            text="[b]ANKIT PRO MATHS TOOLS[/b]",
            markup=True,
            font_size=sp(19),
            size_hint_y=None,
            height=dp(42)
        )
        content.add_widget(title)

        tools = [
            "Percentage (%)",
            "Square (x²)",
            "Square Root (√)",
            "Cube (x³)",
            "Cube Root (∛)",
            "LCM",
            "HCF",
            "Power (xʸ)"
        ]

        for tool in tools:
            btn = Button(
                text="OPEN  |  " + tool,
                size_hint_y=None,
                height=dp(40),
                background_normal="",
                background_color=(0.15, 0.20, 0.40, 1),
                font_size=sp(14)
            )
            btn.bind(
                on_release=lambda instance, t=tool: self.open_math_tool(t)
            )
            content.add_widget(btn)

        close_btn = Button(
            text="CLOSE",
            size_hint_y=None,
            height=dp(42),
            background_normal="",
            background_color=(0.1, 0.6, 0.75, 1)
        )
        content.add_widget(close_btn)

        popup = Popup(
            title="ANKIT PRO",
            content=content,
            size_hint=(0.90, 0.88)
        )
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def open_math_tool(self, tool):
        two_inputs = tool in ("Percentage (%)", "LCM", "HCF", "Power (xʸ)")

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(14)
        )

        if tool == "Percentage (%)":
            hint = "Enter percentage and total value"
            first_hint, second_hint = "Percentage (%)", "Total value"
        elif tool in ("LCM", "HCF"):
            hint = "Enter two whole numbers"
            first_hint, second_hint = "First number", "Second number"
        elif tool == "Power (xʸ)":
            hint = "Enter base and exponent"
            first_hint, second_hint = "Base (x)", "Power (y)"
        else:
            hint = "Enter one number"
            first_hint, second_hint = "Number", ""

        content.add_widget(Label(
            text="[b]" + tool + "[/b]\n" + hint,
            markup=True,
            size_hint_y=None,
            height=dp(55),
            font_size=sp(16)
        ))

        first_input = TextInput(
            hint_text=first_hint,
            multiline=False,
            input_filter="int" if tool in ("LCM", "HCF") else None,
            size_hint_y=None,
            height=dp(48),
            font_size=sp(18),
            halign="center"
        )
        content.add_widget(first_input)

        second_input = None
        if two_inputs:
            second_input = TextInput(
                hint_text=second_hint,
                multiline=False,
                input_filter="int" if tool in ("LCM", "HCF") else None,
                size_hint_y=None,
                height=dp(48),
                font_size=sp(18),
                halign="center"
            )
            content.add_widget(second_input)

        result_label = Label(
            text="Result will appear here",
            size_hint_y=None,
            height=dp(42),
            color=(0.4, 1, 0.8, 1),
            font_size=sp(16)
        )
        content.add_widget(result_label)

        actions = BoxLayout(
            size_hint_y=None,
            height=dp(46),
            spacing=dp(8)
        )
        calculate_btn = Button(
            text="CALCULATE",
            background_normal="",
            background_color=(0.0, 0.55, 0.75, 1)
        )
        close_btn = Button(
            text="CLOSE",
            background_normal="",
            background_color=(0.35, 0.20, 0.45, 1)
        )
        actions.add_widget(calculate_btn)
        actions.add_widget(close_btn)
        content.add_widget(actions)

        popup = Popup(
            title="MATHS TOOL",
            content=content,
            size_hint=(0.88, 0.62 if two_inputs else 0.55)
        )

        def calculate_tool(*args):
            try:
                a = float(first_input.text.strip())
                b = float(second_input.text.strip()) if second_input else None

                if not math.isfinite(a) or (b is not None and not math.isfinite(b)):
                    raise ValueError("Please enter valid finite numbers")

                if tool == "Percentage (%)":
                    result = (a / 100) * b
                elif tool == "Square (x²)":
                    result = a ** 2
                elif tool == "Square Root (√)":
                    if a < 0:
                        raise ValueError("Negative number ka real square root nahi hota")
                    result = math.sqrt(a)
                elif tool == "Cube (x³)":
                    result = a ** 3
                elif tool == "Cube Root (∛)":
                    result = math.copysign(abs(a) ** (1 / 3), a)
                elif tool == "LCM":
                    result = math.lcm(int(a), int(b))
                elif tool == "HCF":
                    result = math.gcd(int(a), int(b))
                elif tool == "Power (xʸ)":
                    result = a ** b
                else:
                    raise ValueError("Unknown tool")

                if isinstance(result, float):
                    if not math.isfinite(result):
                        raise ValueError("Result is too large")
                    if abs(result) < 1e15 and result.is_integer():
                        result = int(result)

                result_label.text = "Result: " + str(result)
                self.message.text = tool + " completed!"
                self.alien.react("dance")
                if self.success_sound:
                    self.success_sound.play()

            except ZeroDivisionError:
                result_label.text = "Error: Cannot divide by zero"
                self.alien.react("surprised")
                if self.error_sound:
                    self.error_sound.play()
            except Exception as error:
                result_label.text = "Error: " + str(error)
                self.alien.react("surprised")
                if self.error_sound:
                    self.error_sound.play()

        calculate_btn.bind(on_release=calculate_tool)
        close_btn.bind(on_release=popup.dismiss)
        popup.open()


# ==================================
# START APPLICATION
# ==================================

if __name__ == "__main__":
    AnkitCalculator().run()
