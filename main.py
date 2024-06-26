#main.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, WipeTransition
from fifteen_game.difficulty_selection_screen import DifficultySelectionScreen
from fifteen_game.puzzle_game import PuzzleGame
from puzzle_app import FifteenG
from pong_game.pong import PongScreen
from tictactoe.tic_tac_toe import TicTacToeScreen
from jigsaw.jigsaw_game import JigsawGameScreen
from matchmaster.matchmaster import MatchMasterScreen
from sudoku.sudoku import SudokuGameScreen  # Import the Sudoku screen
from game2048.game_2048 import Game2048
from game2048.diff_2048 import DiffGame2048
from breakout.breakout import BreakoutScreen
from color.color_memory import ColorMemoryScreen
from color_match.color_match import ColorGameScreen
from space_game.space_adventure import SpaceAdventure
from kivy.core.window import Window
from kivy.lang import Builder
from prof.auth import LoginScreen, SignUpScreen, ProfileScreen, EditProfileScreen
from prof.database import create_tables  # Import the create_tables function

# Load the .kv files
Builder.load_file('prof/profile.kv')  # Load the profile .kv file
Builder.load_file('prof/login.kv')


class PuzzleApp(App):
    current_user = None  # Define the current_user attribute

    def build(self):
        Window.set_orientation=('landscape')
        Window.size=(800, 450)
        create_tables()  # Ensure tables are created at startup
        
        self.title = 'Multi-Game'
        self.screen_manager = ScreenManager(transition=WipeTransition())

        self.screen_manager.add_widget(FifteenG(name='main'))
        self.screen_manager.add_widget(DifficultySelectionScreen(name='select'))
        self.screen_manager.add_widget(PuzzleGame(name='easy_2x2', grid_size=2))
        self.screen_manager.add_widget(PuzzleGame(name='easy_3x3', grid_size=3))
        self.screen_manager.add_widget(PuzzleGame(name='medium_4', grid_size=4))
        self.screen_manager.add_widget(PuzzleGame(name='hard_5', grid_size=5))
        self.screen_manager.add_widget(PuzzleGame(name='hard_6', grid_size=6))
        self.screen_manager.add_widget(PongScreen(name='pong'))
        self.screen_manager.add_widget(DiffGame2048(name='game_2048'))
        self.screen_manager.add_widget(Game2048(name='2048_2x2', grid_size=2))
        self.screen_manager.add_widget(Game2048(name='2048_3x3', grid_size=3))
        self.screen_manager.add_widget(Game2048(name='2048_4x4', grid_size=4))
        self.screen_manager.add_widget(Game2048(name='2048_5x5', grid_size=5))
        self.screen_manager.add_widget(Game2048(name='2048_6x6', grid_size=6))
        self.screen_manager.add_widget(TicTacToeScreen(name='tic_tac_toe'))
        self.screen_manager.add_widget(ColorMemoryScreen(name='color_memory'))
        self.screen_manager.add_widget(JigsawGameScreen(name='jigsaw'))
        self.screen_manager.add_widget(MatchMasterScreen(name='match'))
        self.screen_manager.add_widget(SudokuGameScreen(name='sudoku_game'))
        self.screen_manager.add_widget(BreakoutScreen(name='break_out'))
        self.screen_manager.add_widget(ColorGameScreen(name='color_match'))
        self.screen_manager.add_widget(SpaceAdventure(name='space_game'))
        
        # Add new screens for profile system
        self.screen_manager.add_widget(LoginScreen(name='login'))
        self.screen_manager.add_widget(SignUpScreen(name='signup'))
        self.screen_manager.add_widget(ProfileScreen(name='profile'))
        self.screen_manager.add_widget(EditProfileScreen(name='edit_profile'))

        return self.screen_manager
    
    def start_sudoku_game(self, difficulty):
        # Implement logic to start the Sudoku game with the selected difficulty
        self.screen_manager.current = 'sudoku_game'
        sudoku_screen = self.screen_manager.get_screen('sudoku_game')
        sudoku_screen.set_difficulty(difficulty)

if __name__ == '__main__':
    PuzzleApp().run()
