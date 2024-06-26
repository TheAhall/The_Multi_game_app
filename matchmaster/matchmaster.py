#matchmaster.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import random

Builder.load_file('matchmaster/matchmaster.kv')

class Card(Button):
    def __init__(self, front_image, card_grid, **kwargs):
        super().__init__(**kwargs)
        self.front_image = front_image
        self.is_flipped = False
        self.is_matched = False
        self.card_grid = card_grid
        self.back_image = 'matchmaster/assets/card_back.png'
        self.background_normal = self.back_image
        self.bind(on_release=self.flip)

    def flip(self, *args):
        if not self.is_flipped and not self.is_matched:
            self.is_flipped = True
            self.background_normal = self.front_image
            self.card_grid.card_flipped(self)

    def hide(self):
        self.is_flipped = False
        self.background_normal = self.back_image

    def match(self):
        self.is_matched = True

class CardGrid(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.match_master = None

    def card_flipped(self, card):
        if self.match_master:
            self.match_master.card_flipped(card)

class MatchMaster(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.card_grid = self.ids.card_grid
        self.card_grid.match_master = self
        self.cards = []
        self.flipped_cards = []
        self.build_grid()

    def build_grid(self):
        self.cards = []
        self.card_grid.clear_widgets()
        images = [
            'matchmaster/assets/card_front_1.png', 'matchmaster/assets/card_front_2.png', 'matchmaster/assets/card_front_3.png', 'matchmaster/assets/card_front_4.png',
            'matchmaster/assets/card_front_5.jpg', 'matchmaster/assets/card_front_6.jpg',
        ]
        images *= 2  # Duplicate the images to create pairs
        random.shuffle(images)
        for img in images:
            card = Card(front_image=img, card_grid=self.card_grid)
            self.cards.append(card)
            self.card_grid.add_widget(card)

    def card_flipped(self, card):
        self.flipped_cards.append(card)
        if len(self.flipped_cards) == 2:
            if self.flipped_cards[0].front_image == self.flipped_cards[1].front_image:
                self.flipped_cards[0].match()
                self.flipped_cards[1].match()
                self.flipped_cards = []
                self.check_win()
            else:
                Clock.schedule_once(self.reset_flipped_cards, 1)  # Wait 1 second before flipping back

    def reset_flipped_cards(self, dt):
        for card in self.flipped_cards:
            card.hide()
        self.flipped_cards = []

    def check_win(self):
        if all(card.is_matched for card in self.cards):
            self.show_win_popup()

    def show_win_popup(self):
        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        win_label = Label(text='Congratulations! You won!', font_size=20, halign='center')
        
        buttons_layout = BoxLayout(orientation='vertical', spacing=10)
        buttons_1_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        
        reset_button = Button(text='Play Again', size_hint=(1, None), font_size=17, height=45)
        reset_button.bind(on_release=self.reset_game)
        buttons_1_layout.add_widget(reset_button)
        
        buttons_layout.add_widget(buttons_1_layout)
        
        popup_content.add_widget(win_label)
        popup_content.add_widget(buttons_layout)
        
        self.popup = Popup(title='You Win!', content=popup_content, size_hint=(0.6, 0.4), background_color=(0.2, 0.6, 0.8, 0.5), height=200, auto_dismiss=False)
        reset_button.bind(on_release=self.popup.dismiss)
        self.popup.open()

    def reset_game(self, instance=None):
        if hasattr(self, 'popup'):
            self.popup.dismiss()
        self.build_grid()

    def quit_game(self):
        self.parent.go_to_main_menu()

class MatchMasterScreen(Screen):
    def on_enter(self, *args):
        self.game = MatchMaster()
        self.add_widget(self.game)
        self.game.build_grid()

    def go_to_main_menu(self, instance=None):
        self.manager.current = 'main'
        self.clear_widgets()
