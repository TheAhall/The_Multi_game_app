#sudoku.py
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle
import sqlite3
import random

Builder.load_file('sudoku/sudoku.kv')

class GridEntry(Button):
    def __init__(self, **kwargs):
        super(GridEntry, self).__init__(**kwargs)
        self.font_size = 20
        self.multiline = False
        self.original_background_color = (1, 1, 1, 1)
        self.is_initial = False

class SudokuGrid(GridLayout):
    def __init__(self, game_screen, **kwargs):
        super(SudokuGrid, self).__init__(**kwargs)
        self.cols = 9
        self.rows = 9
        self.spacing = 1
        self.size_hint = (1, 1)
        self.cells = []
        self.game_screen = game_screen
        self.block_colors = [
            (1, 0.9, 0.9, 1),  # Light Red
            (0.9, 1, 0.9, 1),  # Light Green
            (1, 0.9, 0.9, 1),  # Light Blue
            (0.9, 1, 0.9, 1),    # Light Yellow
            (1, 0.9, 0.9, 1),    # Light Pink
            (0.9, 1, 0.9, 1),    # Light Cyan
            (1, 0.9, 0.9, 1),      # White
            (0.9, 1, 0.9, 1),# Light Gray
            (1, 0.9, 0.9, 1) # Very Light Gray
        ]
        self.create_grid()

    def create_grid(self):
        for i in range(81):
            cell = GridEntry(text='')
            cell.bind(on_release=lambda cell=cell: self.cell_selected(cell))
            
            row, col = divmod(i, 9)
            block_index = (row // 3) * 3 + (col // 3)
            cell.background_color = self.block_colors[block_index]
            cell.original_background_color = self.block_colors[block_index]
            
            self.add_widget(cell)
            self.cells.append(cell)

    def cell_selected(self, cell):
        self.game_screen.highlight_cell(cell)
        self.game_screen.selected_cell = cell

    def fill_board(self, puzzle):
        for i in range(81):
            row, col = divmod(i, 9)
            number = puzzle[row][col]
            cell = self.cells[i]
            if number != 0:
                cell.text = str(number)
                cell.is_initial = True  # Mark the cell as part of the initial puzzle
                cell.color = (0, 1, 1, 1)
                cell.readonly = True  # Make the initial cells readonly
            else:
                cell.text = ''
                cell.is_initial = False  # Mark the cell as not part of the initial puzzle
                cell.color = (1, 1, 1, 1)
                cell.readonly = False  # Make the editable cells writable

    def clear_board(self):
        for cell in self.cells:
            cell.text = ''
            cell.background_color = cell.original_background_color
            

class NumberButton(Button):
    def __init__(self, number, game_screen, **kwargs):
        super(NumberButton, self).__init__(**kwargs)
        self.number = number
        self.text = str(number)
        self.font_size = 20
        self.size_hint = (1, 0.01)
        self.height = 10
        self.background_color = (0.2, 0.1, 0.8, 1)
        self.color = (1, 1, 1, 1)
        self.game_screen = game_screen
        self.bind(on_release=self.on_release_action)

    def on_release_action(self, instance=None):
        self.game_screen.number_selected(self.text)

class NumberSelection(GridLayout):
    def __init__(self, game_screen, **kwargs):
        super(NumberSelection, self).__init__(**kwargs)
        self.cols = 9
        self.size_hint = (1, 0.1)
        self.spacing = 2
        self.game_screen = game_screen
        self.create_buttons()

    def create_buttons(self):
        for i in range(1, 10):
            self.add_widget(NumberButton(i, game_screen=self.game_screen))

class SudokuGameScreen(Screen):
    def __init__(self, **kwargs):
        super(SudokuGameScreen, self).__init__(**kwargs)
        
        self.selected_cell = None
        self.db_conn = sqlite3.connect('sudoku/sudoku.db')
        self.initial_puzzle = None
        self.create_table()
        self.build_board()
    
    def build_board(self):    
        self.start_time = 0
        self.mistakes = 0
        self.difficulty = 'easy'
        
        root_layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        
        title_label = Label(text='Sudoku', font_size=32, size_hint=(1, 0.1), color=(1, 1, 1, 1))
        root_layout.add_widget(title_label)
        
        info_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.05), pos_hint={'center_x': 0.5})

        self.difficulty_label = Label(text=f'Difficulty: {self.difficulty}', size_hint=(0.25, 1))
        info_layout.add_widget(self.difficulty_label)
        
        self.timer_label = Label(text='Time: 0', size_hint=(0.25, 1))
        info_layout.add_widget(self.timer_label)
        
        self.mistakes_label = Label(text=f'Mistakes: {self.mistakes}/5', size_hint=(0.25, 1))
        info_layout.add_widget(self.mistakes_label)
        
        root_layout.add_widget(info_layout)
        
        container_layout = BoxLayout(orientation='vertical', padding=2, spacing=10, size_hint=(0.4, 0.6), pos_hint={'center_x': 0.5})
        with container_layout.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.rect = Rectangle(size=container_layout.size, pos=container_layout.pos)
            container_layout.bind(size=self._update_rect, pos=self._update_rect)

        self.sudoku_grid = SudokuGrid(game_screen=self)  # Pass reference to self
        container_layout.add_widget(self.sudoku_grid)
        root_layout.add_widget(container_layout)
        
        button_layout = BoxLayout(size_hint=(0.7, 0.07), pos_hint={'center_x': 0.5})
        save_button = Button(text="Save Game", on_release=self.save_game)
        load_button = Button(text="Load Game", on_release=self.load_progress)
        reset_button = Button(text="Reset Game", on_release=self.reset_game)
        difficulty_button = Button(text="Difficulty", on_release=self.show_difficulty_popup)
        clear_button = Button(text="Clear Cell", on_release=self.clear_cell)  # New clear cell button
        
        button_layout.add_widget(save_button)
        button_layout.add_widget(load_button)
        button_layout.add_widget(reset_button)
        button_layout.add_widget(difficulty_button)
        button_layout.add_widget(clear_button)  # Add the clear cell button
        
        root_layout.add_widget(button_layout)
        
        back_button = Button(text="Quit", size_hint=(0.15, 0.07), pos_hint={'center_x': 0.5}, background_color=(1, 0.8, 0.2, 1))
        back_button.bind(on_release=self.show_worning_popup)
        root_layout.add_widget(back_button)
        
        number_selection = NumberSelection(game_screen=self)
        root_layout.add_widget(number_selection)
        
        self.add_widget(root_layout)
        
        self.generate_puzzle('easy')
        self.load_progress()
        
        Clock.schedule_interval(self.update_timer, 1)

    def clear_cell(self, instance=None):
        if self.selected_cell:
            if self.selected_cell.is_initial:  # Prevent clearing initial cells
                return
            cell_index = self.sudoku_grid.cells.index(self.selected_cell)
            row, col = divmod(cell_index, 9)

            # Check if the cell was part of the initial puzzle
            if self.initial_puzzle[row][col] == 0:
                self.selected_cell.text = ''
                self.selected_cell.background_color = self.selected_cell.original_background_color
                self.save_game(self.selected_cell)
                self.highlight_cell(self.selected_cell)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos
    
    def create_table(self):
        cursor = self.db_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cell_index INTEGER UNIQUE,
                number INTEGER,
                is_initial INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        self.db_conn.commit()

    def show_difficulty_popup(self, instance):
        content = BoxLayout(orientation='vertical', padding=(10, 10, 10, 20), spacing=10)
        content.add_widget(Label(size_hint_y=None, height=50))
        
        difficulty_levels = ['easy', 'medium', 'hard']
        popup = Popup(title='Select Difficulty', title_size=28, title_align='center', content=content, size_hint=(0.6, 0.5), background_color=(0.2, 0.6, 0.8, 0.5))

        for level in difficulty_levels:
            button = Button(text=level.capitalize(), size_hint_y=None, height=50, font_size=20, background_color=(0.2, 0.6, 0.8, 1), color=(1, 1, 1, 1))
            button.bind(on_release=lambda btn, lvl=level: self.set_difficulty(lvl))
            button.bind(on_release=popup.dismiss)
            button.bind(on_release=self.reset_game)
            content.add_widget(button)
        
        popup.open()
        self.difficulty_popup = popup

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.difficulty_label.text = f'Difficulty: {self.difficulty}'
        self.generate_puzzle(difficulty)

    def generate_puzzle(self, difficulty):
        self.initial_puzzle = self.create_puzzle(difficulty)  # Store the initial puzzle
        self.sudoku_grid.clear_board()
        self.sudoku_grid.fill_board(self.initial_puzzle)

    def create_puzzle(self, difficulty):
        base = 3
        side = base * base
        def pattern(r, c): return (base * (r % base) + r // base + c) % side
        def shuffle(s): return random.sample(s, len(s))
        r_base = range(base)
        rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
        cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
        nums = shuffle(range(1, base * base + 1))
        board = [[nums[pattern(r, c)] for c in cols] for r in rows]
        squares = side * side
        no_of_clues = squares * {'easy': 0.5, 'medium': 0.36, 'hard': 0.28}[difficulty]
        for p in random.sample(range(squares), int(squares - no_of_clues)):
            board[p // side][p % side] = 0
        return board

    def update_timer(self, dt):
        self.start_time += 1
        minutes, seconds = divmod(self.start_time, 60)
        self.timer_label.text = f'Time: {minutes}:{seconds:02d}'

    def number_selected(self, number):
        if self.selected_cell:
            if self.selected_cell.is_initial:  # Prevent changing initial cells
                return
            if self.selected_cell.text == number:
                return
            cell_index = self.sudoku_grid.cells.index(self.selected_cell)
            row, col = divmod(cell_index, 9)
            # Clear any previous highlighting
            for c in self.sudoku_grid.cells:
                c.background_color = c.original_background_color

            if self.is_valid_move(row, col, int(number)):
                self.selected_cell.text = number
                self.selected_cell.background_color = (1, 1, 1, 1)  # Reset color on valid move
                self.save_game(self.selected_cell)
                self.highlight_cell(self.selected_cell)
                if self.check_win_condition():
                    self.show_win_popup()
            else:
                self.selected_cell.background_color = (1, 0, 0, 1)  # Highlight invalid move
                self.mistakes += 1
                self.mistakes_label.text = f'Mistakes: {self.mistakes}/5'
                if self.mistakes >= 5:
                    self.game_over()

    def is_valid_move(self, row, col, number):
        # Check the row
        for c in range(9):
            if self.sudoku_grid.cells[row * 9 + c].text == str(number):
                return False

        # Check the column
        for r in range(9):
            if self.sudoku_grid.cells[r * 9 + col].text == str(number):
                return False

        # Check the 3x3 grid
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(start_row, start_row + 3):
            for c in range(start_col, start_col + 3):
                if self.sudoku_grid.cells[r * 9 + c].text == str(number):
                    return False
        return True

    def highlight_cell(self, cell):
        for c in self.sudoku_grid.cells:
            c.background_color = c.original_background_color  # Reset all cells to their original color

        cell_index = self.sudoku_grid.cells.index(cell)
        row, col = divmod(cell_index, 9)

        # Highlight row
        for i in range(9):
            self.sudoku_grid.cells[row * 9 + i].background_color = (0.7, 0.7, 0.8, 1)

        # Highlight column
        for i in range(9):
            self.sudoku_grid.cells[i * 9 + col].background_color = (0.7, 0.7, 0.8, 1)

        # Highlight box
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                self.sudoku_grid.cells[(start_row + i) * 9 + (start_col + j)].background_color = (0.7, 0.7, 0.8, 1)

        cell.background_color = (0.8, 0.7, 0.1, 1)  # Highlight selected cell

        # Highlight identical numbers
        number = cell.text
        if number:
            for c in self.sudoku_grid.cells:
                if c.text == number:
                    c.background_color = (0.8, 0.7, 0.1, 1)

    def check_win_condition(self):
        for row in range(9):
            for col in range(9):
                cell = self.sudoku_grid.cells[row * 9 + col]
                if cell.text == '':
                    return False
                original_text = cell.text
                cell.text = ''
                if not self.is_valid_move(row, col, int(original_text)):
                    cell.text = original_text
                    return False
                cell.text = original_text
        return True

    def show_win_popup(self):
        content = BoxLayout(orientation='vertical', padding=(10, 10, 10, 20), spacing=10)
        message_label = Label(size_hint_y=None, height=50)
        content.add_widget(message_label)
        
        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        quit_button = Button(text='Quit', size_hint_y=None, height=50, font_size=20, background_color=(0.2, 0.6, 0.8, 1), color=(1, 1, 1, 1))
        quit_button.bind(on_release=lambda x: self.go_to_main_menu(x))
        
        reset_button = Button(text='Reset', size_hint_y=None, height=50, font_size=20, background_color=(0.2, 0.6, 0.8, 1), color=(1, 1, 1, 1))
        reset_button.bind(on_release=lambda x: (self.reset_game(), popup.dismiss()))
        
        button_layout.add_widget(quit_button)
        button_layout.add_widget(reset_button)
        
        content.add_widget(button_layout)
        
        popup = Popup(title='Congratulations! You have won the game!', title_size=28, title_align='center', content=content, size_hint=(0.6, 0.5), background_color=(0.2, 0.6, 0.8, 0.5))
        reset_button.bind(on_release=popup.dismiss)
        quit_button.bind(on_release=popup.dismiss)
        popup.open()
        self.win_popup = popup

    def show_worning_popup(self, instance):
        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Game Over label
        game_over_label = Label(text='Are you sure?\nEvery unsaved data will be lost!', font_size=20, halign='center')
        popup_content.add_widget(game_over_label)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10)
        # Restart button
        restart_button = Button(text='Keep playing', size_hint=(1, 0.5), font_size=17, height=45, background_color= (0.2, 0.8, 0.2))
        buttons_layout.add_widget(restart_button)
        # Main Menu button
        main_menu_button = Button(text='Quit', size_hint=(1, 0.5), font_size=17, height=45, background_color= (0.8, 0.2, 0.2))
        main_menu_button.bind(on_release=self.go_to_main_menu)
        buttons_layout.add_widget(main_menu_button)
        
        popup_content.add_widget(buttons_layout)
        
        popup = Popup(title='You are leaving!!', content=popup_content, size = (400, 250), size_hint=(None, None), background_color=(0.2, 0.6, 0.8, 0.5), auto_dismiss=False)
        restart_button.bind(on_release=popup.dismiss)
        main_menu_button.bind(on_release=popup.dismiss)
        popup.open()

    def game_over(self):
        popup = Popup(title='Game Over', content=Label(text='Too many mistakes!'), size_hint=(0.5, 0.5), background_color=(0.2, 0.6, 0.8, 0.5))
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)
        self.reset_game()

    def save_game(self, instance):
        cursor = self.db_conn.cursor()
        cursor.execute('DELETE FROM progress')
        for i, cell in enumerate(self.sudoku_grid.cells):
            number = int(cell.text) if cell.text else 0
            is_initial = 1 if cell.is_initial else 0
            cursor.execute('INSERT OR REPLACE INTO progress (cell_index, number, is_initial) VALUES (?, ?, ?)', (i, number, is_initial))
        cursor.execute('INSERT OR REPLACE INTO game_state (key, value) VALUES (?, ?)', ('difficulty', self.difficulty))
        cursor.execute('INSERT OR REPLACE INTO game_state (key, value) VALUES (?, ?)', ('start_time', self.start_time))
        cursor.execute('INSERT OR REPLACE INTO game_state (key, value) VALUES (?, ?)', ('mistakes', self.mistakes))
        self.db_conn.commit()

    def load_progress(self, instance=None):
        cursor = self.db_conn.cursor()
        cursor.execute('SELECT cell_index, number, is_initial FROM progress')
        progress = cursor.fetchall()
        for cell_index, number, is_initial in progress:
            cell = self.sudoku_grid.cells[cell_index]
            cell.text = str(number) if number != 0 else ''
            cell.is_initial = bool(is_initial)
            if cell.is_initial:
                cell.color = (0, 1, 1, 1)
            else:
                cell.color = (1, 1, 1, 1)
        cursor.execute('SELECT key, value FROM game_state')
        state = cursor.fetchall()
        for key, value in state:
            if key == 'difficulty':
                self.difficulty = value
                self.difficulty_label.text = f'Difficulty: {self.difficulty}'
            elif key == 'start_time':
                self.start_time = int(value)
            elif key == 'mistakes':
                self.mistakes = int(value)
                self.mistakes_label.text = f'Mistakes: {self.mistakes}/5'

    def reset_game(self, instance=None):
        self.sudoku_grid.clear_board()
        self.start_time = 0
        self.mistakes = 0
        self.mistakes_label.text = f'Mistakes: {self.mistakes}/5'
        self.timer_label.text = 'Time: 0'
        self.generate_puzzle(self.difficulty)

    def on_pre_enter(self):
        self.reset_game()

    def go_to_main_menu(self, instance):
        self.manager.current = 'main'