#color_memory.py
import random
import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from prof.database import update_highest_score, game_highest_score
from kivy.clock import Clock
from kivy.lang import Builder

Builder.load_file('color/color_memory.kv')

class ColorMemoryGame(BoxLayout):
    game_name = 'Color Memory'
    def __init__(self, **kwargs):
        super(ColorMemoryGame, self).__init__(**kwargs)
        self.colors = ["red", "green", "blue", "yellow", "purple", "orange", "cyan", "magenta", "lime"]
        self.sequence = []
        self.user_sequence = []
        self.current_level = 1
        self.score = 0
        self.highest_score = 0
        self.show_highest_score()

        # Get references to UI elements
        self.score_label = self.ids.score_label

        self.grid_layout = self.ids.grid_layout

        # Create buttons for the colors
        self.color_buttons = {}
        for color in self.colors:
            btn = Button(background_color=self.get_color(color))
            btn.bind(on_press=self.on_color_button_press)
            btn.color_name = color  # Store color name in the button
            btn.ignore_input = False  # Flag to ignore input
            self.color_buttons[color] = btn
            self.grid_layout.add_widget(btn)

    def get_color(self, color_name):
        color_dict = {
            "red": [1, 0, 0, 1],
            "green": [0, 1, 0, 1],
            "blue": [0, 0, 1, 1],
            "yellow": [1, 1, 0, 1],
            "purple": [0.5, 0, 0.5, 1],
            "orange": [1, 0.5, 0, 1],
            "cyan": [0, 1, 1, 1],
            "magenta": [1, 0, 1, 1],
            "lime": [0.75, 1, 0, 1]
        }
        return color_dict.get(color_name, [1, 1, 1, 1])

    def start_game(self, instance=None):
        self.sequence = []
        self.user_sequence = []
        self.current_level = 1
        self.score = 0
        self.score_label.text = "Score: 0"
        self.show_prepare_message()

    def show_prepare_message(self):
        popup = Popup(title='Get Ready!',
                      content=Label(text='Prepare yourself! The sequence is about to start.'),
                      size_hint=(0.6, 0.4),
                      background_color=(0.2, 0.6, 0.8, 0.5),
                      auto_dismiss=True)
        popup.open()
        Clock.schedule_once(lambda dt: (popup.dismiss(), self.next_level()), 2)  # 2-second delay before starting the game

    def next_level(self):
        self.user_sequence = []
        self.sequence = [random.choice(self.colors) for _ in range(self.current_level)]  # Generate new sequence
        self.current_level += 1
        self.show_sequence()

    def show_sequence(self):
        self.disable_buttons()
        self.showing_sequence = True
        for i, color in enumerate(self.sequence):
            Clock.schedule_once(lambda dt, c=color: self.highlight_button(c), i + 1)  # Ensure a 1-second delay between highlights
        Clock.schedule_once(lambda dt: self.end_sequence_showing(), len(self.sequence) + 1)  # End sequence showing after the full sequence

    def highlight_button(self, color):
        btn = self.color_buttons[color]
        original_color = btn.background_color
        btn.background_color = self.get_color(color)
        btn.disabled = False  # Enable the button being highlighted
        btn.ignore_input = True  # Ignore input during highlight
        Clock.schedule_once(lambda dt: self.reset_button_color(btn, original_color), 0.5)

    def reset_button_color(self, btn, original_color):
        btn.background_color = original_color
        btn.disabled = True  # Disable the button after highlight
        btn.ignore_input = False

    def end_sequence_showing(self):
        self.showing_sequence = False
        self.enable_buttons()  # Enable all buttons after the sequence is shown

    def on_color_button_press(self, instance):
        if instance.ignore_input:
            return  # Ignore input if button is in highlight state

        if self.showing_sequence:
            return  # Ignore inputs if the sequence is being shown

        color = instance.color_name
        self.user_sequence.append(color)
        if self.user_sequence == self.sequence[:len(self.user_sequence)]:
            if len(self.user_sequence) == len(self.sequence):
                self.score += 10
                self.score_label.text = f"Score: {self.score}"
                app = App.get_running_app()
                if app.current_user:
                    username = app.current_user['username']
                    update_highest_score(username, self.game_name, self.score)
                self.show_highest_score()
                Clock.schedule_once(lambda dt: self.next_level(), 1)
        else:
            self.show_game_over()

    def disable_buttons(self):
        for btn in self.color_buttons.values():
            btn.disabled = True

    def enable_buttons(self):
        for btn in self.color_buttons.values():
            btn.disabled = False

    def show_game_over(self):
        self.disable_buttons()

        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Game Over label
        game_over_label = Label(text='Game Over!', font_size=24, halign='center')
        popup_content.add_widget(game_over_label)
        
        # Score label
        score_label = Label(text=f'Your Score: {self.score}', font_size=20, halign='center')
        popup_content.add_widget(score_label)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10)
        
        # Restart button
        restart_button = Button(text='Play again', size_hint=(1, None), font_size=17, height=45)
        restart_button.bind(on_release=self.start_game)
        buttons_layout.add_widget(restart_button)
        
        # Main Menu button
        main_menu_button = Button(text='Main Menu', size_hint=(1, None), font_size=17, height=45)
        main_menu_button.bind(on_release=self.go_to_main_menu)
        buttons_layout.add_widget(main_menu_button)
        
        popup_content.add_widget(buttons_layout)
        
        popup = Popup(title='Game Over', content=popup_content, size = (400, 250), size_hint=(None, None), background_color=(0.2, 0.6, 0.8, 0.5), auto_dismiss=False)
        restart_button.bind(on_release=popup.dismiss)
        main_menu_button.bind(on_release=popup.dismiss)
        popup.open()

    def show_highest_score(self):
        app = App.get_running_app()
        if app.current_user:
            username = app.current_user['username']
            highest_score=game_highest_score(username, self.game_name)
            self.ids.highest_score_label.text = f'Highest score: {highest_score}'
        else:
            if self.score > self.highest_score:
                self.highest_score = self.score
            self.ids.highest_score_label.text = f'Highest score: {self.highest_score}'

    def go_to_main_menu(self, instance=None):
        self.parent.go_to_main_menu()

class ColorMemoryScreen(Screen):
    def on_enter(self, *args):
        self.game = ColorMemoryGame()
        self.add_widget(self.game)

    def go_to_main_menu(self, instance=None):
        self.manager.current = 'main'
        self.clear_widgets()