#game_2048.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.animation import Animation
from kivy.lang import Builder
import random
import sqlite3
import json

Builder.load_file('game2048/game_2048.kv')

class Game2048(Screen):
    def __init__(self, grid_size, **kwargs):
        super().__init__(**kwargs)
        self.grid_size = grid_size
        self.score = 0
        self.last_score = 0
        self.high_score = 0
        self.cells = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.create_scores_table()
        self.load_scores()
        self.build_ui()
        self.start_game()

    def create_scores_table(self):
        with sqlite3.connect('game2048/2048game.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS scores (
                                grid_size INTEGER,
                                high_score INTEGER DEFAULT 0,
                                last_score INTEGER DEFAULT 0,
                                PRIMARY KEY (grid_size)
                              )''')

    def load_scores(self):
        with sqlite3.connect('game2048/2048game.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT high_score, last_score FROM scores WHERE grid_size = ?', (self.grid_size,))
            result = cursor.fetchone()
            if result:
                self.high_score, self.last_score = result
            else:
                cursor.execute('INSERT INTO scores (grid_size) VALUES (?)', (self.grid_size,))
                conn.commit()
                self.high_score, self.last_score = 0, 0

    def save_last_score(self):
        with sqlite3.connect('game2048/2048game.db') as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE scores SET last_score = ? WHERE grid_size = ?', (self.score, self.grid_size))
            if self.score > self.high_score:
                self.high_score = self.score
                cursor.execute('UPDATE scores SET high_score = ? WHERE grid_size = ?', (self.high_score, self.grid_size))
            conn.commit()

    def build_ui(self):
        self.clear_widgets()
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)


        # Title label
        title_label = Label(text='2048', font_size=32, size_hint=(1, 0.1))
        main_layout.add_widget(title_label)

        score_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        
        # High Score label
        self.high_score_label = Label(text=f'High Score: {self.high_score}', font_size=20, size_hint=(1, 1))
        score_layout.add_widget(self.high_score_label)

        # Score label
        self.score_label = Label(text='Score: 0', font_size=25, size_hint=(1, 1))
        score_layout.add_widget(self.score_label)

        # Last Score label
        self.last_score_label = Label(text=f'Last Score: {self.last_score}', font_size=15, size_hint=(1, 1))
        score_layout.add_widget(self.last_score_label)

        main_layout.add_widget(score_layout)

        # Container layout for the puzzle with background color
        container_layout = BoxLayout(orientation='vertical', padding=5, spacing=10, size_hint=(0.6, 0.6), pos_hint={'center_x': 0.5})
        with container_layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.2, 0.2, 0.2, 1)  # Dark grey background
            self.rect = Rectangle(size=container_layout.size, pos=container_layout.pos)
            container_layout.bind(size=self._update_rect, pos=self._update_rect)

        # Grid layout for the puzzle
        self.grid = GridLayout(cols=self.grid_size, spacing=5, size_hint=(1, 1))
        self.cell_buttons = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                btn = Button(text='', font_size=24, background_normal='', background_color=(0.7, 0.7, 0.7, 1))
                self.grid.add_widget(btn)
                self.cell_buttons[row][col] = btn

        container_layout.add_widget(self.grid)
        main_layout.add_widget(container_layout)

        # Create buttons for reset and back to difficulty outside the container layout
        button_layout = BoxLayout(spacing=10, size_hint=(0.6, 0.1), pos_hint={'center_x': 0.5})
        reset_button = Button(text='Reset', font_size=20, background_color=(0.2, 0.8, 0.2, 1), color=(1, 1, 1, 1))
        reset_button.bind(on_release=lambda x: self.start_game())
        button_layout.add_widget(reset_button)
        back_button = Button(text='Back', font_size=20, background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        back_button.bind(on_release=self.go_to_main_menu)
        button_layout.add_widget(back_button)
        main_layout.add_widget(button_layout)

        self.add_widget(main_layout)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def start_game(self, instance=None):
        self.last_score = self.score
        self.save_last_score()
        self.cells = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.score = 0
        self.add_random_tile()
        self.add_random_tile()
        self.update_ui()

    def add_random_tile(self):
        empty_cells = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size) if self.cells[r][c] == 0]
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.cells[r][c] = 2 if random.random() < 0.9 else 4

    def animate_tile(self, button, value):
        animation = Animation(background_color=self.get_color(value), duration=0.2)
        animation.start(button)

    def get_color(self, value):
        color_map = {
            0: (1, 1, 1, 1),    # Empty cells
            2: (0.4, 0.4, 0.4, 1),    # Background color for 2
            4: (0.8, 0.8, 0.6, 1),    # Background color for 4
            8: (0.9, 0.6, 0.4, 1),    # Background color for 8
            16: (0.9, 0.5, 0.3, 1),   # Background color for 16
            32: (0.9, 0.4, 0.3, 1),   # Background color for 32
            64: (0.9, 0.3, 0.3, 1),   # Background color for 64
            128: (0.9, 0.8, 0.4, 1),  # Background color for 128
            256: (0.9, 0.8, 0.3, 1),  # Background color for 256
            512: (0.9, 0.8, 0.2, 1),  # Background color for 512
            1024: (0.9, 0.8, 0.1, 1), # Background color for 1024
            2048: (0.9, 0.8, 0.0, 1), # Background color for 2048
        }
        return color_map.get(value, (0.7, 0.7, 0.7, 1)) # Default color

    def update_ui(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                value = self.cells[row][col]
                btn = self.cell_buttons[row][col]
                btn.text = str(value) if value else ''
                self.animate_tile(btn, value)
        self.score_label.text = f"Score: {self.score}"
        self.high_score_label.text = f"High Score: {self.high_score}"
        self.last_score_label.text = f"Last Score: {self.last_score}"

    def merge(self, row, row_idx):
        for i in range(len(row) - 1):
            if row[i] == row[i + 1] and row[i] != 0:
                row[i] *= 2
                self.score += row[i]
                row[i + 1] = 0
                self.animate_tile(self.cell_buttons[row_idx][i], row[i])  # Animate the merged tile
        self.compact(row)

    def compact(self, row):
        new_row = [i for i in row if i != 0]
        new_row += [0] * (len(row) - len(new_row))
        for i in range(len(row)):
            row[i] = new_row[i]

    def check_game_over(self):
        if any(0 in row for row in self.cells):
            return False
        for row in self.cells:
            for col in range(self.grid_size - 1):
                if row[col] == row[col + 1]:
                    return False
        for col in range(self.grid_size):
            for row in range(self.grid_size - 1):
                if self.cells[row][col] == self.cells[row + 1][col]:
                    return False
        return True

    def move(self, direction):
        moved = False
        if direction == 'up':
            for col in range(self.grid_size):
                column = [self.cells[row][col] for row in range(self.grid_size)]
                original_column = list(column)
                self.compact(column)
                self.merge(column, col)  # Pass column index
                for row in range(self.grid_size):
                    self.cells[row][col] = column[row]
                if column != original_column:
                    moved = True

        elif direction == 'down':
            for col in range(self.grid_size):
                column = [self.cells[row][col] for row in range(self.grid_size)]
                original_column = list(column)
                column.reverse()
                self.compact(column)
                self.merge(column, col)  # Pass column index
                column.reverse()
                for row in range(self.grid_size):
                    self.cells[row][col] = column[row]
                if column != original_column:
                    moved = True

        elif direction == 'left':
            for row in range(self.grid_size):
                original_row = list(self.cells[row])
                self.compact(self.cells[row])
                self.merge(self.cells[row], row)  # Pass row index
                if self.cells[row] != original_row:
                    moved = True

        elif direction == 'right':
            for row in range(self.grid_size):
                original_row = list(self.cells[row])
                self.cells[row].reverse()
                self.compact(self.cells[row])
                self.merge(self.cells[row], row)  # Pass row index
                self.cells[row].reverse()
                if self.cells[row] != original_row:
                    moved = True

        if moved:
            self.add_random_tile()
            self.update_ui()
            if self.check_game_over():
                self.show_game_over_popup()


    def show_win_popup(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f'Congratulations!\nYou reached 2048!', font_size=24))
        
        button_layout = BoxLayout(orientation='horizontal', spacing=10)

        reset_button = Button(text='Reset', size_hint=(1, None), font_size=17, height=45)
        reset_button.bind(on_release=self.start_game)
        button_layout.add_widget(reset_button)

        back_button = Button(text='Back', size_hint=(1, None), font_size=17, height=45)
        back_button.bind(on_release=self.go_to_main_menu)
        button_layout.add_widget(back_button)

        content.add_widget(button_layout)
        
        popup = Popup(title='You Win!', content=content, size_hint=(0.6, 0.4), background_color=(0.2, 0.6, 0.8, 0.5), auto_dismiss=False)
        reset_button.bind(on_release=popup.dismiss)
        back_button.bind(on_release=popup.dismiss)
        popup.open()

    def show_game_over_popup(self):
        if self.score > self.high_score:
            self.high_score = self.score
        self.save_last_score()
        
        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Game Over label
        game_over_label = Label(text='Game Over!', font_size=24, halign='center')
        popup_content.add_widget(game_over_label)
        
        # Score label
        score_label = Label(text=f'Your Score: {self.score}', font_size=20, halign='center')
        popup_content.add_widget(score_label)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10)
        
        # Restart button
        restart_button = Button(text='Restart', size_hint=(1, None), font_size=17, height=45)
        restart_button.bind(on_release=self.start_game)
        buttons_layout.add_widget(restart_button)
        
        # Main Menu button
        main_menu_button = Button(text='Main Menu', size_hint=(1, None), font_size=17, height=45)
        main_menu_button.bind(on_release=self.go_to_main_menu)
        buttons_layout.add_widget(main_menu_button)
        
        popup_content.add_widget(buttons_layout)
        
        popup = Popup(title='Game Over', content=popup_content, size_hint=(0.6, 0.4), background_color=(0.2, 0.6, 0.8, 0.5), auto_dismiss=False)
        restart_button.bind(on_release=popup.dismiss)
        main_menu_button.bind(on_release=popup.dismiss)
        popup.open()

    def go_to_main_menu(self, instance):
        self.start_game()
        self.manager.current = 'game_2048'

    def on_touch_up(self, touch):
        if abs(touch.dx) > abs(touch.dy):
            if touch.dx > 0:
                self.move('right')
            else:
                self.move('left')
        else:
            if touch.dy > 0:
                self.move('up')
            else:
                self.move('down')
        return super().on_touch_up(touch)

    
