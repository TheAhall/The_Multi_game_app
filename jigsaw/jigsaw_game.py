#jigsaw_game.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.scatter import Scatter
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from random import choice
from PIL import Image as PILImage
import random
import os

# Load the .kv file
Builder.load_file('jigsaw/jigsaw_game.kv')

class JigsawPiece(Scatter):
    def __init__(self, texture, piece_pos, **kwargs):
        super().__init__(**kwargs)
        self.do_rotation = False
        self.do_scale = False
        self.image = Image(texture=texture)
        self.add_widget(self.image)
        self.piece_pos = piece_pos
        self.size_hint = (None, None)
        self.size = self.image.size

        # Bring piece to the top
        with self.canvas.before:
            Color(1, 1, 1, 0)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Bring to front
            parent = self.parent
            if parent:
                touch.grab(self)

            self._touch_pos = touch.pos
            return True
        return super().on_touch_down(touch)
    

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.center_x += touch.x - self._touch_pos[0]
            self.center_y += touch.y - self._touch_pos[1]
            self._touch_pos = touch.pos
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)

class GridCell(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.piece = None
        with self.canvas:
            Color(0.8, 0.8, 0.8, 1)  # Light grey color
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def add_piece(self, piece):
        self.piece = piece
        self.add_widget(piece)
        piece.center = self.center

    def remove_piece(self):
        if self.piece:
            self.remove_widget(self.piece)
            self.piece = None

class JigsawGame(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grid_size = 3  # Fixed grid size
        self.piece_size_x = 100  # Example size, should calculate based on image and grid
        self.piece_size_y = 65
        self.pieces = []
        self.grid_cells = []
        self.build_puzzle()

    def build_puzzle(self):
        self.clear_widgets()
        self.pieces = []
        self.grid_cells = []
        self.win_popup_shown = False  # Reset the flag when rebuilding the puzzle

        # Load and shuffle pieces
        image_path = ['asset/puzzle_image_1.jpg',
                      'asset/puzzle_image_2.jpg',
                      'asset/puzzle_image_3.jpg',
                      'asset/puzzle_image_4.jpg',
                      'asset/puzzle_image_5.jpg',
                      'asset/puzzle_image_6.jpg',
                      'asset/puzzle_image_7.jpg'
                    ] # Replace with the path to your image
        random_image_path = choice(image_path)
        self.load_and_shuffle_pieces(random_image_path)
        
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        
        # Create the title
        layout=BoxLayout(orientation='horizontal',size_hint=(1, 0.1), pos_hint={'center_x': 0.5})

        reset_button=Button(text='Reset',size_hint=(0.3, None), size=(50, 40), background_color=(0.2, 0.8, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        reset_button.bind(on_release= self.reset_game)
        layout.add_widget(reset_button)

        title_label = Label(text=f'Jigsaw Puzzle Game', font_size=32, size_hint=(1, 1))
        layout.add_widget(title_label)

        quit_button=Button(text='Quit',size_hint=(0.3, None), size=(50, 40), background_color=(0.8, 0.2, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        quit_button.bind(on_release=self.go_back_to_main)
        layout.add_widget(quit_button)

        main_layout.add_widget(layout)

        # Container layout for the puzzle
        puzzle_layout = GridLayout(cols= 2, padding=15, spacing=25, size_hint=(0.88, 0.65), pos_hint={'center_x': 0.5})
        with puzzle_layout.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0, 0, 0, 0.8)
            self.rect = RoundedRectangle(size=puzzle_layout.size, pos=puzzle_layout.pos, radius= [20,])
            puzzle_layout.bind(size=self._update_rect, pos=self._update_rect)

        # Left side layout for pieces
        self.piece_pack_layout = GridLayout(cols=self.grid_size, spacing=5, rows=self.grid_size, size_hint=(0.5, 1))
        for piece in self.pieces:
            self.piece_pack_layout.add_widget(piece)

        # Middle layout for the board grid

        self.board_grid = GridLayout(cols=self.grid_size, rows=self.grid_size, spacing=5, size_hint=(0.5, 1))
        
        for row in range(self.grid_size):
            row_cells = []
            for col in range(self.grid_size):
                cell = GridCell(size_hint=(None, None), size=(self.piece_size_x, self.piece_size_y))
                self.board_grid.add_widget(cell)
                row_cells.append(cell)
            self.grid_cells.append(row_cells)
        

        puzzle_layout.add_widget(self.board_grid)
        puzzle_layout.add_widget(self.piece_pack_layout)

        main_layout.add_widget(puzzle_layout)


        self.add_widget(main_layout)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos
    
    def load_and_shuffle_pieces(self, image_path):
        pil_image = PILImage.open(image_path)
        img_width, img_height = pil_image.size
        piece_width = img_width // self.grid_size
        piece_height = img_height // self.grid_size

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                left = col * piece_width
                top = row * piece_height
                right = left + piece_width
                bottom = top + piece_height

                piece_image = pil_image.crop((left, top, right, bottom))
                piece_image = piece_image.transpose(PILImage.FLIP_TOP_BOTTOM)
                piece_texture = self.pil_image_to_texture(piece_image)
                
                piece = JigsawPiece(
                    texture=piece_texture,
                    piece_pos=(col, row)
                )
                piece.bind(on_touch_up=self.on_piece_release)
                self.pieces.append(piece)

        random.shuffle(self.pieces)

    def pil_image_to_texture(self, pil_image):
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()

        texture = Texture.create(size=size, colorfmt='rgb')
        texture.blit_buffer(data, colorfmt='rgb', bufferfmt='ubyte')
        return texture

    def on_piece_release(self, piece, touch):
        if piece.collide_point(*touch.pos):
            # Check if piece is inside a grid cell
            placed_in_cell = False
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    cell = self.grid_cells[row][col]
                    if cell.collide_point(*touch.pos):
                        # Remove piece from current parent before adding to new cell
                        if piece.parent:
                            piece.parent.remove_widget(piece)
                        # Add piece to cell (replacing the existing one if present)
                        cell.add_piece(piece)
                        placed_in_cell = True
                        break
                if placed_in_cell:
                    break

            # If not placed in a grid cell, return to piece pack
            if not placed_in_cell:
                if piece.parent:
                    piece.parent.remove_widget(piece)
                self.piece_pack_layout.add_widget(piece)

            self.check_win()

    def check_win(self, *args):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell = self.grid_cells[row][col]
                if cell.piece is None or cell.piece.piece_pos != (col, row):
                    return
        self.show_win_popup()

    def show_win_popup(self):
        if self.win_popup_shown:
            return
        self.win_popup_shown = True
        
        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        win_label = Label(text='Congratulations! You solved the puzzle!', font_size=20, halign='center')
        
        buttons_layout = BoxLayout(orientation='vertical', spacing=10)
        
        buttons_1_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        reset_button = Button(text='Reset', size_hint=(1, None), font_size=17, height=45)
        reset_button.bind(on_release=self.reset_game)
        buttons_1_layout.add_widget(reset_button)

        back_button = Button(text='Back to Main', size_hint=(1, None), font_size=17, height=45)
        back_button.bind(on_release=self.go_back_to_main)
        buttons_1_layout.add_widget(back_button)
        
        buttons_layout.add_widget(buttons_1_layout)
        
        popup_content.add_widget(win_label)
        popup_content.add_widget(buttons_layout)
        
        self.win_popup = Popup(title='You Win!', content=popup_content, size = (400, 200), size_hint=(None, None), background_color=(0.2, 0.6, 0.8, 0.5), height=200, auto_dismiss=False)
        back_button.bind(on_release=self.win_popup.dismiss)
        self.win_popup.open()

    def go_back_to_main(self, instance):
        self.parent.go_to_main_menu()

    def reset_game(self, instance):
        self.win_popup.dismiss() if hasattr(self, 'win_popup') else None
        random.shuffle(self.pieces)
        self.build_puzzle()

class JigsawGameScreen(Screen):
    def on_enter(self, *args):
        self.game = JigsawGame()
        self.add_widget(self.game)
        self.game.build_puzzle()

    def go_to_main_menu(self, instance=None):
        self.manager.current = 'main'
        self.clear_widgets()
