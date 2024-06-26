#tic_tac_toe.py
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

Builder.load_file('tictactoe/tic_tac_toe.kv')

class TicTacToeButton(Button):
    pass

class TicTacToe(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_player = 'X'
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.build_board()

    def build_board(self):
        self.clear_widgets()
        
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title_label = Label(text='Tic-Tac-Toe', font_size=32, size_hint=(1, 0.1))
        main_layout.add_widget(title_label)
        
        container_layout = BoxLayout(orientation='vertical', padding=5, spacing=10, size_hint=(0.6, 0.6), pos_hint={'center_x': 0.5})
        with container_layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.2, 0.2, 0.2, 1)
            self.rect = Rectangle(size=container_layout.size, pos=container_layout.pos)
            container_layout.bind(size=self._update_rect, pos=self._update_rect)

        self.grid = GridLayout(cols=3, spacing=5, size_hint=(1, 1))
        for i in range(3):
            for j in range(3):
                button = TicTacToeButton()
                button.row = i
                button.col = j
                button.bind(on_release=self.make_move)
                self.grid.add_widget(button)
        container_layout.add_widget(self.grid)
        main_layout.add_widget(container_layout)

        button_layout = BoxLayout(spacing=1, size_hint=(0.6, 0.065), pos_hint={'center_x': 0.5})
        reset_button = Button(text='Reset', font_size=20, background_color=(0.2, 0.8, 0.2, 1), color=(1, 1, 1, 1))
        reset_button.bind(on_release=self.reset_game)
        button_layout.add_widget(reset_button)
        back_button = Button(text='Quit', font_size=20, background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        back_button.bind(on_release=self.quit_game)
        button_layout.add_widget(back_button)
        main_layout.add_widget(button_layout)

        self.add_widget(main_layout)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def make_move(self, button):
        row, col = button.row, button.col
        if self.board[row][col] == '':
            self.board[row][col] = self.current_player
            button.text = self.current_player
            if self.check_winner():
                self.show_winner_popup(f'Player {self.current_player} wins!')
            elif all(cell != '' for row in self.board for cell in row):
                self.show_winner_popup('It\'s a tie!')
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'

    def check_winner(self):
        for row in self.board:
            if row[0] == row[1] == row[2] != '':
                return True
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != '':
                return True
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '' or self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            return True
        return False

    def show_winner_popup(self, message):
        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        win_label = Label(text=message, font_size=20, halign='center')
        
        buttons_layout = BoxLayout(orientation='vertical', spacing=10)
        buttons_1_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        
        reset_button = Button(text='Play Again', size_hint=(1, None), font_size=17, height=45)
        reset_button.bind(on_release=self.reset_game)
        
        buttons_1_layout.add_widget(reset_button)
        
        
        buttons_layout.add_widget(buttons_1_layout)
        
        popup_content.add_widget(win_label)
        popup_content.add_widget(buttons_layout)
        
        self.popup = Popup(title='Game Over', content=popup_content, size_hint=(0.6, 0.4), height=200, background_color=(0.2, 0.6, 0.8, 0.5), auto_dismiss=False)
        reset_button.bind(on_release=self.popup.dismiss)
        self.popup.open()

    def quit_game(self, instance):
        self.parent.go_to_main_menu()

    def reset_game(self, instance):
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.build_board()

    
class TicTacToeScreen(Screen):
    def on_enter(self, *args):
        self.game = TicTacToe()
        self.add_widget(self.game)
        self.game.build_board()

    def go_to_main_menu(self, instance=None):
        self.manager.current = 'main'
        self.clear_widgets()
