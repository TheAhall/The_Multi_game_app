from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.app import App  # Import the App class from kivy.app

class SudokuDifficultyPopup(Popup):
    def __init__(self, **kwargs):
        super(SudokuDifficultyPopup, self).__init__(**kwargs)
        self.title = 'Select Sudoku Difficulty'
        self.size_hint = (None, None)
        self.size = (400, 300)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        with layout.canvas.before:
            Color(0.2, 0.2, 0.2, 1)  # Background color
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
            layout.bind(size=self._update_rect, pos=self._update_rect)

        label = Label(text='Choose Difficulty Level', font_size=30, size_hint=(1, None), height=50, color=(1, 1, 1, 1))
        layout.add_widget(label)

        button_layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 0.1), height=150)

        button_colors = (0.2, 0.6, 0.8, 1)
        text_color = (1, 1, 1, 1)

        easy_button = Button(text='Easy', background_color=button_colors, color=text_color, size_hint_y=0.2, height=50)
        easy_button.bind(on_release=lambda x: self.select_difficulty('easy'))
        button_layout.add_widget(easy_button)

        medium_button = Button(text='Medium', background_color=button_colors, color=text_color, size_hint_y=0.2, height=50)
        medium_button.bind(on_release=lambda x: self.select_difficulty('medium'))
        button_layout.add_widget(medium_button)

        hard_button = Button(text='Hard', background_color=button_colors, color=text_color, size_hint_y=0.2, height=50)
        hard_button.bind(on_release=lambda x: self.select_difficulty('hard'))
        button_layout.add_widget(hard_button)

        layout.add_widget(button_layout)
        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def select_difficulty(self, difficulty):
        self.dismiss()
        app = App.get_running_app()
        app.start_sudoku_game(difficulty)
