#difficulty_selection_screen.py
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

# Load the .kv file
Builder.load_file('fifteen_game/diff.kv')

class DifficultySelectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def load_easy_2x2(self, instance):
        self.manager.current = 'easy_2x2'

    def load_easy_3x3(self, instance):
        self.manager.current = 'easy_3x3'
        
    def load_medium(self, instance):
        self.manager.current = 'medium_4'

    def load_hard(self, instance):
        self.manager.current = 'hard_5'

    def load_hard_6(self, instance):
        self.manager.current = 'hard_6'

    def load_main(self, instance):
        self.manager.current = 'main'


