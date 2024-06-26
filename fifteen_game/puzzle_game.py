#puzzle_game.py
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
import random

# Load the .kv files
Builder.load_file('fifteen_game/puzzle_game.kv')

class PuzzleGame(Screen):
    def __init__(self, grid_size, **kwargs):
        super().__init__(**kwargs)
        self.grid_size = grid_size
        self.build_puzzle()

    def build_puzzle(self):
        self.clear_widgets()
        
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Create the title
        title_label = Label(text=f'{self.grid_size}x{self.grid_size}', font_size=32, size_hint=(1, 0.1), color=(1, 1, 1, 1), bold=True)
        main_layout.add_widget(title_label)

        # Container layout for the puzzle with background color
        container_layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint=(0.5, 0.8), pos_hint={'center_x': 0.5})
        with container_layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0, 0, 0, 0.5)  # Semi-transparent background
            self.rect = Rectangle(size=container_layout.size, pos=container_layout.pos)
            container_layout.bind(size=self._update_rect, pos=self._update_rect)

        # Create the grid layout for the puzzle
        self.grid = GridLayout(cols=self.grid_size, spacing=5, size_hint=(1, 1))
        self.tiles = list(range(1, self.grid_size**2)) + [None]
        random.shuffle(self.tiles)

        self.buttons = []
        for tile in self.tiles:
            if tile:
                btn = Button(text=str(tile), font_size=24, background_normal='', background_color=(0.1, 0.5, 0.8, 1), color=(1, 1, 1, 1))
                btn.bind(on_release=self.move_tile)
            else:
                btn = Button(background_normal='', background_color=(0.7, 0.7, 0.7, 1))  # Grey button for the empty space
            self.buttons.append(btn)
            self.grid.add_widget(btn)
        
        container_layout.add_widget(self.grid)
        main_layout.add_widget(container_layout)

        # Create buttons for reset and back to difficulty outside the container layout
        button_layout = BoxLayout(spacing=5, size_hint=(0.5, 0.1), pos_hint={'center_x': 0.5})
        reset_button = Button(text='Reset', font_size=20, background_color=(0.2, 0.8, 0.2, 1), color=(1, 1, 1, 1))
        reset_button.bind(on_release=self.reset_game)
        button_layout.add_widget(reset_button)
        back_button = Button(text='Back to Difficulty', font_size=20, background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        back_button.bind(on_release=self.go_back_to_difficulty)
        button_layout.add_widget(back_button)
        main_layout.add_widget(button_layout)

        self.add_widget(main_layout)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def move_tile(self, instance):
        index = self.buttons.index(instance)
        empty_index = self.get_empty_index()
        
        if self.can_move(index, empty_index):
            self.grid.clear_widgets()
            self.buttons[empty_index], self.buttons[index] = self.buttons[index], self.buttons[empty_index]

            for btn in self.buttons:
                self.grid.add_widget(btn)

            if self.check_win():
                self.show_win_popup()

    def get_empty_index(self):
        for i, btn in enumerate(self.buttons):
            if not btn.text:
                return i

    def can_move(self, index, empty_index):
        index_row, index_col = divmod(index, self.grid_size)
        empty_row, empty_col = divmod(empty_index, self.grid_size)
        
        return (index_row == empty_row and abs(index_col - empty_col) == 1) or (index_col == empty_col and abs(index_row - empty_row) == 1)

    def check_win(self):
        current_order = [btn.text for btn in self.buttons if btn.text]
        return current_order == [str(i) for i in range(1, self.grid_size**2)]

    def show_win_popup(self):
        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        win_label = Label(text='Congratulations! You solved the puzzle!', font_size=20, halign='center', color=(1, 1, 1, 1))
        
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10)
        
        reset_button = Button(text='Reset', size_hint=(1, None), font_size=17, height=45, background_color=(0.2, 0.8, 0.2, 1), color=(1, 1, 1, 1))
        reset_button.bind(on_release=self.reset_game)
        buttons_layout.add_widget(reset_button)

        back_button = Button(text='Back to Difficulty', size_hint=(1, None), font_size=17, height=45, background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        back_button.bind(on_release=self.go_back_to_difficulty)
        buttons_layout.add_widget(back_button)
        
        
        popup_content.add_widget(win_label)
        popup_content.add_widget(buttons_layout)
        
        popup = Popup(title='You Win!', content=popup_content, size_hint=(0.8, 0.4), background_color=(0.2, 0.6, 0.8, 0.5), auto_dismiss=False)
        # Dismiss popup when any button is clicked
        reset_button.bind(on_release=popup.dismiss)
        back_button.bind(on_release=popup.dismiss)
        popup.open()

    def go_back_to_difficulty(self, instance):
        self.manager.current = 'select'

    def reset_game(self, instance):
        random.shuffle(self.tiles)
        self.grid.clear_widgets()
        self.buttons = []

        for tile in self.tiles:
            if tile:
                btn = Button(text=str(tile), font_size=24, background_normal='', background_color=(0.1, 0.5, 0.8, 1), color=(1, 1, 1, 1))
                btn.bind(on_release=self.move_tile)
            else:
                btn = Button(background_normal='', background_color=(0.9, 0.9, 0.9, 1))
            self.buttons.append(btn)
            self.grid.add_widget(btn)
