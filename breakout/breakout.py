#breakout.py
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.lang import Builder
from prof.database import update_highest_score
import random

# Load the KV file explicitly
Builder.load_file('breakout/breakout.kv')

class Paddle(Widget):
    pass

class Brick(Widget):
    hits = NumericProperty(0)
    colors = ListProperty([(1, 0, 0, 1), (1, 0.5, 0, 1), (1, 1, 0, 1)])  # Colors change on each hit

    def change_color(self):
        if self.hits < len(self.colors):
            self.canvas.before.clear()
            with self.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(rgba=self.colors[self.hits])
                Rectangle(pos=self.pos, size=(self.size))

class Ball(Widget):
    velocity_x = NumericProperty(4)
    velocity_y = NumericProperty(4)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class BrickGame(Widget):
    game_name = 'Breakout'
    ball = ObjectProperty(None)
    paddle = ObjectProperty(None)
    bricks = []
    state = 'start'
    score = NumericProperty(0)
    lives = NumericProperty(3)
    number = 5

    def build_bricks(self):
        # Remove existing bricks
        for brick in self.bricks:
            self.remove_widget(brick)
        self.bricks = []

        # Brick dimensions
        brick_width = self.width / (self.number * 1.4)
        brick_height = self.height / 20

        # Calculate starting x position to center the bricks
        total_bricks_width = (brick_width + 10) * self.number - 10
        start_x = (self.width - total_bricks_width) / 2

        for x in range(self.number):
            for y in range(4):
                brick = Brick()
                brick.size = (brick_width, brick_height)
                brick.pos = (
                    start_x + x * (brick_width + 10),
                    self.height - (y * (brick_height + 10) + 100)
                )
                brick.change_color()
                self.bricks.append(brick)
                self.add_widget(brick)

    def serve_ball(self):
        self.ball.center = self.center
        while True:
            angle = random.uniform(210, 300)
            if not (260 < angle < 290):  # Exclude angles close to vertical
                break
        speed = 5
        self.ball.velocity = Vector(speed, 0).rotate(angle)

    def update(self, dt):
        if self.state == 'play':
            self.ball.move()

            if self.ball.collide_widget(self.paddle):
                vx, vy = self.ball.velocity
                offset = (self.ball.center_x - self.paddle.center_x) / (self.paddle.width / 5)
                bounced = Vector(vx, vy * -1)  # Adjust angle based on collision point
                vel = bounced * 1.03
                self.ball.velocity = vel.x + offset, vel.y

                if self.ball.y < self.paddle.top:
                    self.ball.y = self.paddle.top

            if self.ball.top > self.top:
                self.ball.velocity_y *= -1
            if self.ball.x < self.x or self.ball.right > self.width:
                self.ball.velocity_x *= -1

            if self.ball.y < self.y:
                self.lives -= 1
                if self.lives == 0:
                    self.show_game_over()
                else:
                    self.serve_ball()

            for brick in self.bricks[:]:
                if self.ball.collide_widget(brick):
                    self.handle_brick_collision(brick)
                    break

    def handle_brick_collision(self, brick):
        ball_center_x = self.ball.center_x
        ball_center_y = self.ball.center_y

        brick_left = brick.x
        brick_right = brick.right
        brick_top = brick.top
        brick_bottom = brick.y

        # Determine if collision is more horizontal or vertical
        if abs(self.ball.velocity_x) > abs(self.ball.velocity_y):  # More horizontal movement
            if ball_center_x < brick_left:  # Hit left side
                self.ball.velocity_x *= -1
            elif ball_center_x > brick_right:  # Hit right side
                self.ball.velocity_x *= -1
            else:  # Hit top or bottom
                self.ball.velocity_y *= -1
        else:  # More vertical movement
            if ball_center_y > brick_top:  # Hit top side
                self.ball.velocity_y *= -1
            elif ball_center_y < brick_bottom:  # Hit bottom side
                self.ball.velocity_y *= -1
            else:  # Hit left or right
                self.ball.velocity_x *= -1

        brick.hits += 1
        self.score += 10

        if brick.hits < 3:
            brick.change_color()
        else:
            self.bricks.remove(brick)
            self.remove_widget(brick)
            if not self.bricks:
                self.number += 1
                self.show_win_popup()

    def on_touch_move(self, touch):
        if touch.y < self.height / 3:
            self.paddle.center_x = touch.x

    def start_game(self):
        self.state = 'play'
        self.lives = 3
        self.serve_ball()
        self.build_bricks()

    def reset_game(self, instance):
        self.state = 'start'
        self.score = 0
        self.lives = 3
        self.number = 5
        self.serve_ball()
        self.build_bricks()

    def continue_game(self, instance):
        self.state = 'start'
        self.lives = 3
        self.serve_ball()
        self.build_bricks()

    def on_touch_down(self, touch):
        if self.state == 'start':
            self.start_game()

    def show_game_over(self):
        app = App.get_running_app()
        if app.current_user:
            username = app.current_user['username']
            update_highest_score(username, self.game_name, self.score)
        self.state = 'gameover'
        popup = Popup(title='Game Over',
                      content=Label(text='You have lost all your lives!'),
                      size_hint=(None, None), size=(400, 200))
        popup.bind(on_dismiss=self.reset_game)
        popup.open()

    def show_win_popup(self):
        self.state = 'win'
        popup = Popup(title='Congratulations!',
                      content=Label(text='Next level!'),
                      size_hint=(None, None), size=(400, 200))
        popup.bind(on_dismiss=self.continue_game)
        popup.open()

    def go_to_main_menu(self, instance):
        self.parent.go_to_main_menu()
        self.popup.dismiss()

class BreakoutScreen(Screen):
    def on_enter(self, *args):
        self.game = BrickGame()
        self.add_widget(self.game)

        # Create a layout for the score and lives
        layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, pos_hint={'right': 1, 'top': 1})
        self.score_label = Label(text=f"Score: {self.game.score}", size_hint=(0.5, 1))
        self.lives_label = Label(text=f"Lives: {self.game.lives}", size_hint=(0.5, 1))

        # Add the back button
        back_button = Button(size_hint=(None, None), size=(50, 50), pos_hint={'right': 1, 'top': 1})
        back_button.background_normal = 'breakout/back.png'  # Set the path to your icon
        back_button.bind(on_release=self.go_to_main_menu)
        layout.add_widget(back_button)
        layout.add_widget(self.score_label)
        layout.add_widget(self.lives_label)
        
        self.add_widget(layout)

        self.game.reset_game(None)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def update(self, dt):
        self.game.update(dt)
        self.score_label.text = f"Score: {self.game.score}"
        self.lives_label.text = f"Lives: {self.game.lives}"

    def go_to_main_menu(self, instance=None):
        Clock.unschedule(self.update)
        self.manager.current = 'main'
        self.clear_widgets()
