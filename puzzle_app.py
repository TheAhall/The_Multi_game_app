#puzzle_app.py
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from sudoku.difficulty.difficulty import SudokuDifficultyPopup
from kivy.lang import Builder

Builder.load_file('puzzle_app.kv')

class FifteenG(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self):
        app = App.get_running_app()
        if app.current_user:
            self.ids.logout.opacity = 1
            self.ids.logout.disabled = False
            self.ids.profile.text = 'Profile'
            self.ids.profile.on_release = self.load_profile
        else:
            self.ids.logout.opacity = 0
            self.ids.logout.disabled = True
            self.ids.profile.text = 'Login'
            self.ids.profile.on_release = self.load_login

    def load_the_game(self):
        self.manager.current = 'select'

    def load_pong_game(self):
        self.manager.current = 'pong'

    def load_tic_tac_toe_game(self):
        self.manager.current = 'tic_tac_toe'

    def load_jigsaw_game(self):
        self.manager.current = 'jigsaw'

    def load_space_game(self):
        self.manager.current = 'space_game'

    def load_match_game(self):
        self.manager.current = 'match'

    def load_game_2048(self):
        self.manager.current = 'game_2048'

    def load_brick_game(self):
        app = App.get_running_app()
        if app.current_user:
            self.manager.current = 'break_out'
        else:
            self.popup()

    def load_color_memory(self):
        self.manager.current = 'color_memory'

    def load_color_match(self):
        self.manager.current = 'color_match'

    def load_sudoku_game(self):
        self.show_sudoku_difficulty_popup()

    def show_sudoku_difficulty_popup(self):
        popup = SudokuDifficultyPopup()
        popup.open()

    def load_profile(self):
        self.manager.current = 'profile'

    def load_login(self, instance=None):
        self.manager.current = 'login'

    def load_info(self, instance=None):
        self.show_welcome_popup()

    def logout(self):
        app = App.get_running_app()
        app.current_user = None
        self.manager.current = 'login'

    def popup(self):
        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        login_label = Label(text='You are not logged in!', font_size=20, halign='center', color=(1, 1, 1, 1))
        
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10)
        
        login_button = Button(text='Login', size_hint=(1, None), font_size=17, height=45, background_color=(0.2, 0.8, 0.2, 1), color=(1, 1, 1, 1))
        login_button.bind(on_release=self.load_login)
        buttons_layout.add_widget(login_button)
        
        
        popup_content.add_widget(login_label)
        popup_content.add_widget(buttons_layout)
        
        popup = Popup(title='Login to play!', content=popup_content, size = (400, 200), size_hint=(None, None), background_color=(0.2, 0.6, 0.8, 0.5))
        # Dismiss popup when any button is clicked
        login_button.bind(on_release=popup.dismiss)
        popup.open()
    
    def show_welcome_popup(self):
        try:
            with open('README.txt', 'r') as file:
                welcome_text = file.read()
        except FileNotFoundError:
            welcome_text = "Welcome to the Multi-Game App!"

        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Create a ScrollView
        scroll_view = ScrollView(size_hint=(1, 1))

        # Create a Label with the welcome text
        message_label = Label(text=welcome_text, font_size=20, size_hint_y=None)
        message_label.bind(texture_size=message_label.setter('size'))

        # Update text_size when ScrollView's width changes
        def update_text_size(instance, value):
            message_label.text_size = (instance.width, None)
            message_label.texture_update()  # Force texture update

        scroll_view.bind(width=update_text_size)
        
        # Initial update for text_size
        update_text_size(scroll_view, scroll_view.width)

        # Add the Label to the ScrollView
        scroll_view.add_widget(message_label)

        ok_button = Button(text='OK', size_hint=(1, None), height=50, background_color=(0.2, 0.6, 0.8, 1), color=(1, 1, 1, 1))
        ok_button.bind(on_release=lambda x: popup.dismiss())

        popup_content.add_widget(scroll_view)
        popup_content.add_widget(ok_button)

        popup = Popup(title='Games Rules!', content=popup_content, size_hint=(0.8, 0.8))
        popup.open()
