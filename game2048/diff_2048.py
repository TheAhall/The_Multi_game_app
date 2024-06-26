#difficulty_selection_screen.py
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

# Load the .kv file
Builder.load_file('game2048/diff_2048.kv')

class DiffGame2048(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def load_2x2(self, instance):
        self.manager.current = '2048_2x2'

    def load_3x3(self, instance):
        self.manager.current = '2048_3x3'
        
    def load_4x4(self, instance):
        self.manager.current = '2048_4x4'

    def load_5x5(self, instance):
        self.manager.current = '2048_5x5'

    def load_6x6(self, instance):
        self.manager.current = '2048_6x6'

    def load_main(self, instance):
        self.manager.current = 'main'