#colormatch.py
import random
import sqlite3
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from prof.database import update_highest_score, game_highest_score

Builder.load_file('color_match/color_match.kv')

class ColorGame(Screen):
    current_color = StringProperty("")
    score = NumericProperty(0)
    highest_score = NumericProperty(0)
    time_left = NumericProperty(30)
    game_name = 'Color Match'

    def __init__(self, **kwargs):
        super(ColorGame, self).__init__(**kwargs)
        self.colors = ["Red", "Green", "Blue", "Yellow", "Purple", "Orange"]
        self.correct_color = ""
        self.score = 0
        self.highest_score = 0
        self.grid_layout = None
        self.timer_event = None
        self.show_highest_score()

    def start_game(self, instance=None):
        self.score = 0
        self.highest_score = 0
        self.time_left = 30
        self.grid_layout = self.ids.color_grid
        self.grid_layout.clear_widgets()
        self.create_color_buttons()
        self.update_color()
        self.timer_event = Clock.schedule_interval(self.update_time, 1)

    def end_game(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.show_game_over_popup()

    def show_game_over_popup(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=5)
        message = Label(text=f"Time is up!\nYour score: {self.score}", font_size=24)
        content.add_widget(message)
        buttons = BoxLayout(orientation='horizontal', padding=5, spacing=10)
        restart_button = Button(text="Restart", size_hint=(1, 0.7))
        restart_button.bind(on_release=self.restart_game)
        buttons.add_widget(restart_button)
        quit_button = Button(text="quit", size_hint=(1, 0.7))
        quit_button.bind(on_release=self.quit_game)
        buttons.add_widget(quit_button)
        content.add_widget(buttons)
        popup = Popup(title='Game Over', content=content, size_hint=(None, None), size=(400, 200), background_color=(0.2, 0.6, 0.8, 0.5), auto_dismiss=False)
        restart_button.bind(on_release=popup.dismiss)
        quit_button.bind(on_release=popup.dismiss)
        popup.open()

    def restart_game(self, instance):
        self.start_game()

    def create_color_buttons(self):
        for i in range(3):
            for j in range(3):
                button = Button(on_release=self.check_color)
                self.grid_layout.add_widget(button)

    def update_color(self):
        buttons = self.grid_layout.children
        for button in buttons:
            button.color_name = random.choice(self.colors)
            button.background_color = self.get_color_from_name(button.color_name)

        self.correct_color = random.choice(buttons).color_name
        self.current_color = self.correct_color

    def get_color_from_name(self, color_name):
        color_map = {
            "Red": (1, 0, 0, 1),
            "Green": (0, 1, 0, 1),
            "Blue": (0, 0,1, 1),
            "Yellow": (1, 1, 0, 1),
            "Purple": (0.5, 0, 0.5, 1),
            "Orange": (1, 0.5, 0, 1),
        }
        return color_map.get(color_name, (1, 1, 1, 1))

    def check_color(self, instance):
        app = App.get_running_app()
        if instance.color_name == self.correct_color:
            self.score += 10
            if app.current_user:
                username = app.current_user['username']
                update_highest_score(username, self.game_name, self.score)
                self.show_highest_score()
            self.update_color()

    def show_highest_score(self):
        app = App.get_running_app()
        if app.current_user:
            username = app.current_user['username']
            highest_score=game_highest_score(username, self.game_name)
            self.ids.highest_score.text = f'Highest score: {highest_score}'
        else:
            if self.score > self.highest_score:
                self.highest_score = self.score
            self.ids.highest_score.text = f'Highest score: {self.highest_score}'

    def update_time(self, dt):
        if self.time_left > 0:
            self.time_left -= 1
        else:
            self.end_game()

    def quit_game(self, instance=None):
        if self.timer_event:
            self.timer_event.cancel()
        self.parent.go_to_main_menu()

class ColorGameScreen(Screen):
    def on_enter(self, *args):
        self.game = ColorGame()
        self.add_widget(self.game)

    def go_to_main_menu(self, instance=None):
        self.manager.current = 'main'
        self.clear_widgets()


