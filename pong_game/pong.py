#pong.py
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
import random

# Load the KV file explicitly
Builder.load_file('pong_game/pong.kv')

class PongPaddle(Widget):
    score = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset

class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    def serve_ball(self):
        self.ball.center = self.center
        # Set a random direction for the ball, excluding vertical directions
        while True:
            angle = random.uniform(0, 360)
            if not (60 < angle < 120 or 240 < angle < 300):  # Exclude angles close to 90 and 270 degrees
                break
        speed = 4
        velocity = Vector(speed, 0).rotate(angle)
        self.ball.velocity = velocity

    def update(self, dt):
        self.ball.move()

        # bounce off paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        # bounce ball off bottom or top
        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1

        # went off to a side to score point?
        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball()
            self.check_winner()
        if self.ball.right > self.width:
            self.player1.score += 1
            self.serve_ball()
            self.check_winner()

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y

    def check_winner(self):
        if self.player1.score >= 2:
            self.show_winner_popup("Player 1")
        elif self.player2.score >= 2:
            self.show_winner_popup("Player 2")

    def show_winner_popup(self, winner):
        Clock.unschedule(self.update)
        self.ball.velocity = (0, 0)  # Stop the ball in the middle
        self.ball.center = self.center  # Reset the ball to the center
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f"{winner} wins!", font_size=24))

        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        
        reset_button = Button(text="Reset", size_hint_y=None, height=45)
        reset_button.bind(on_release=self.reset_game)
        button_layout.add_widget(reset_button)
        
        main_menu_button = Button(text="Main Menu", size_hint_y=None, height=45)
        main_menu_button.bind(on_release=self.go_to_main_menu)
        button_layout.add_widget(main_menu_button)
        
        content.add_widget(button_layout)
        
        self.popup = Popup(title="Game Over", content=content, background_color=(0.2, 0.6, 0.8, 0.5), size_hint=(0.6, 0.4), auto_dismiss=False)
        self.popup.open()

    def reset_game(self, instance):
        self.player1.score = 0
        self.player2.score = 0
        self.serve_ball()
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        self.popup.dismiss()

    def go_to_main_menu(self, instance):
        self.parent.go_to_main_menu()
        self.popup.dismiss()

class PongScreen(Screen):
    def on_enter(self, *args):
        self.game = PongGame()
        self.add_widget(self.game)
        self.game.serve_ball()
        Clock.schedule_interval(self.game.update, 1.0 / 60.0)

    def go_to_main_menu(self, instance=None):
        Clock.unschedule(self.game.update)
        self.manager.current = 'main'
        self.clear_widgets()
