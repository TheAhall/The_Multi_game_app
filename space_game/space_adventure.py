#space_adventure.py
from kivy.uix.filechooser import Screen
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty, StringProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.vector import Vector
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.animation import Animation
from random import randint
from prof.database import update_highest_score, game_highest_score
import random
from kivy.lang import Builder

Builder.load_file('space_game/space_adventure.kv')

class Spaceship(Widget):
    def move_left(self):
        if self.x > 0:
            self.pos = Vector(-3, 0) + self.pos

    def move_right(self):
        if self.right < self.parent.width:
            self.pos = Vector(3, 0) + self.pos

    def move_up(self):
        if self.top < self.parent.height:
            self.pos = Vector(0, 3) + self.pos

    def move_down(self):
        if self.y > 0:
            self.pos = Vector(0, -3) + self.pos

    def on_touch_move(self, touch):
        self.center_x = touch.x
        if self.center_x < self.width / 2:
            self.center_x = self.width / 2
        if self.center_x > Window.width - self.width / 2:
            self.center_x = Window.width - self.width / 2
        self.center_y = touch.y
        if self.center_y < self.height / 2:
            self.center_y = self.height / 2
        if self.center_y > Window.height - self.height / 2:
            self.center_y = Window.height - self.height / 2

class Asteroid(Widget):
    pass

class Star(Widget):
    pass

class PowerUp(Widget):
    pass

class Magnetic(Widget):
    pass

class Bullet(Widget):
    pass

class SpaceGame(Widget):
    spaceship = ObjectProperty(None)
    score = NumericProperty(0)
    highest_score = NumericProperty(0)
    game_over_flag = BooleanProperty(False)  # Add a flag to track game over state
    speed_multiplier = NumericProperty(0.5)  # Start with a lower speed
    invincible = BooleanProperty(False)  # Add a flag for invincibility
    magnetic_active = BooleanProperty(False)
    powerup_timer_text = StringProperty('')  # Add a property for the power-up timer text
    game_name = 'Space Adventure'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
        self.keys_pressed = set()

        self.asteroids = []
        self.stars = []
        self.power_ups = []
        self.magnetics = []
        self.bullets = []
        
        self.powerup_time_left = ''
        self.magnetic_time_left = ''

        Clock.schedule_once(self.set_spaceship_position)
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        Clock.schedule_interval(self.generate_asteroid, 1.0)
        Clock.schedule_interval(self.generate_star, 2.0)
        Clock.schedule_interval(self.generate_power_up, 10.0)
        Clock.schedule_interval(self.generate_magnetic, 15.0)

    def generate_power_up(self, dt):
        power_up = PowerUp()
        power_up.size = (30, 30)
        power_up.x = random.randint(0, self.width - power_up.width)
        power_up.y = self.height
        self.add_widget(power_up)
        self.power_ups.append(power_up)

    def generate_magnetic(self, dt):
        magnetic = Magnetic()
        magnetic.size = (30, 30)
        magnetic.x = random.randint(0, self.width - magnetic.width)
        magnetic.y = self.height
        self.add_widget(magnetic)
        self.magnetics.append(magnetic)

    def set_spaceship_position(self, dt):
        self.spaceship.pos = (self.width / 2 - self.spaceship.width / 2, self.height * 0.1)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        self.keys_pressed.add(keycode[1])

    def _on_key_up(self, keyboard, keycode):
        self.keys_pressed.discard(keycode[1])

    def generate_asteroid(self, dt):
        asteroid = Asteroid()
        asteroid.size = (50, 50)
        asteroid.pos = (randint(2, self.width - asteroid.width), self.height)
        self.add_widget(asteroid)
        self.asteroids.append(asteroid)

    def generate_star(self, dt):
        star = Star()
        star.size = (30, 30)
        star.pos = (randint(0, self.width - star.width), self.height)
        self.add_widget(star)
        self.stars.append(star)
        if not self.game_over_flag:
            if self.magnetic_active:
                anim = Animation(center=self.spaceship.center, duration=1)
                anim.start(star)
        else:
            return

    def update(self, dt):
        if self.game_over_flag:
            return  # Skip update if the game is over

        # Update spaceship position
        if 'left' in self.keys_pressed:
            self.spaceship.move_left()
        if 'right' in self.keys_pressed:
            self.spaceship.move_right()
        if 'up' in self.keys_pressed:
            self.spaceship.move_up()
        if 'down' in self.keys_pressed:
            self.spaceship.move_down()

        # Move asteroids and check for collisions
        for asteroid in self.asteroids:
            asteroid.y -= 4 * self.speed_multiplier
            if asteroid.y < 0:
                self.remove_widget(asteroid)
                self.asteroids.remove(asteroid)
            if not self.invincible and self.spaceship.collide_widget(asteroid):
                self.game_over()

        # Move stars and check for collection
        for star in self.stars:
            star.y -= 2.5 * self.speed_multiplier
            if star.y < 0:
                self.remove_widget(star)
                self.stars.remove(star)
            if self.spaceship.collide_widget(star):
                if self.invincible:
                    self.score += 10 * 2
                else:
                    self.score += 10
                self.remove_widget(star)
                self.stars.remove(star)
                
        app = App.get_running_app()
        if app.current_user:
            username = app.current_user['username']
            update_highest_score(username, self.game_name, self.score)
        else:
            if self.score > self.highest_score:
                self.highest_score = self.score

        # Move power-ups and check for collection
        for power_up in self.power_ups:
            power_up.y -= 2 * self.speed_multiplier
            if power_up.y < 0:
                self.remove_widget(power_up)
                self.power_ups.remove(power_up)
            if self.spaceship.collide_widget(power_up):
                self.activate_power_up()
                self.remove_widget(power_up)
                self.power_ups.remove(power_up)

        # Move power-ups and check for collection
        for magnetic in self.magnetics:
            magnetic.y -= 2 * self.speed_multiplier
            if magnetic.y < 0:
                self.remove_widget(magnetic)
                self.magnetics.remove(magnetic)
            if self.spaceship.collide_widget(magnetic):
                self.activate_magnetic()
                self.remove_widget(magnetic)
                self.magnetics.remove(magnetic)

        for bullet in self.bullets[:]:  # Use a copy of the list to avoid modification during iteration
            bullet.y += 10
            if bullet.top > self.height:
                self.remove_widget(bullet)
                if bullet in self.bullets:  # Check if the bullet is still in the list before removing
                    self.bullets.remove(bullet)
            for asteroid in self.asteroids:
                if bullet.collide_widget(asteroid):
                    self.score += 5
                    self.remove_widget(asteroid)
                    self.remove_widget(bullet)
                    if asteroid in self.asteroids:  # Check if the asteroid is still in the list before removing
                        self.asteroids.remove(asteroid)
                    if bullet in self.bullets:  # Check if the bullet is still in the list before removing
                        self.bullets.remove(bullet)
                    break

        # Increase speed over time, but very slowly
        self.speed_multiplier += 0.00001

    
    def shoot_bullet(self, dt):
        if self.game_over_flag:
            return
        # Left bullet
        left_bullet = Bullet()
        left_bullet.size = (10, 30)
        left_bullet.pos = (self.spaceship.x, self.spaceship.center_y - left_bullet.height / 2)
        self.add_widget(left_bullet)
        self.bullets.append(left_bullet)

        # Right bullet
        right_bullet = Bullet()
        right_bullet.size = (10, 30)
        right_bullet.pos = (self.spaceship.right - right_bullet.width, self.spaceship.center_y - right_bullet.height / 2)
        self.add_widget(right_bullet)
        self.bullets.append(right_bullet)

        # Top bullet
        top_bullet = Bullet()
        top_bullet.size = (10, 30)
        top_bullet.pos = (self.spaceship.center_x - top_bullet.width / 2, self.spaceship.top)
        self.add_widget(top_bullet)
        self.bullets.append(top_bullet)

    def animate_powerup(self, widget, *args):
        animate = Animation(size = (100, 120), duration= 1)
        animate.start(widget)

    def animate_powerup_down(self, widget, *args):
        animate = Animation(size = (70, 80), duration= 1)
        animate.start(widget)

    def activate_power_up(self):
        self.invincible = True
        self.powerup_time_left = 5  # Set the power-up duration to 5 seconds
        Clock.schedule_interval(self.update_powerup_timer, 1)  # Update the timer every second
        self.animate_powerup(self.spaceship)
        Clock.schedule_once(self.deactivate_power_up, 5)  # Power-up lasts for 5 seconds
        
    def activate_magnetic(self):
        if self.game_over_flag:
            return
        self.magnetic_active = True
        self.magnetic_time_left = 10  # Set the power-up timer text to 10
        Clock.schedule_interval(self.update_magnetic_timer, 1)
        Clock.schedule_once(self.deactivate_magnetic, 10)
        Clock.schedule_interval(self.shoot_bullet, 0.4)
        
    def update_powerup_timer(self, dt):
        self.powerup_time_left -= 1
        if self.powerup_time_left == 0:
            return False  # Stop the timer
        
    def update_magnetic_timer(self, dt):
        self.magnetic_time_left -= 1
        if self.game_over_flag:
            self.magnetic_time_left = 0
        if self.magnetic_time_left == 0:
            return False  # Stop the timer

    def deactivate_magnetic(self, dt):
        self.magnetic_active = False
        Clock.unschedule(self.shoot_bullet)


    def deactivate_power_up(self, dt):
        self.animate_powerup_down(self.spaceship)
        self.invincible = False

    def game_over(self):
        if self.game_over_flag:
            return  # Prevent multiple game over triggers
        self.game_over_flag = True
        self.show_game_over_popup()

    def show_game_over_popup(self):
        box = BoxLayout(orientation='vertical')
        box.add_widget(Label(text='Game Over!', font_size='40sp'))
        box.add_widget(Label(text=f'Final Score: {self.score}', font_size='25sp'))
        button_layout = BoxLayout(orientation='horizontal', spacing= 5)
        reset_button = Button(text='Reset', size_hint_y=0.5, background_color=(0.2, 0.8, 0.2), height=50)
        reset_button.bind(on_release=self.reset_game)
        button_layout.add_widget(reset_button)

        quit_button = Button(text='Quit', size_hint_y=0.5, background_color=(0.8, 0.2, 0.2), height=50)
        quit_button.bind(on_release=self.go_to_main_menu)
        button_layout.add_widget(quit_button)

        box.add_widget(button_layout)

        self.popup = Popup(title='Game Over', content=box, size_hint=(None, None), size=(400, 300), background_color=(0.2, 0.6, 0.8, 0.5), auto_dismiss=False)
        reset_button.bind(on_release=self.popup.dismiss)
        quit_button.bind(on_release=self.popup.dismiss)
        self.popup.open()

    def reset_game(self, instance):
        self.clear_game_state()  # Clear the game state

        # Reset game state variables
        self.score = 0
        self.game_over_flag = False
        self.speed_multiplier = 0.5
        self.invincible = False
        self.magnetic_active = False
        self.powerup_time_left = ''
        self.magnetic_time_left = ''

        # Set spaceship position again
        self.set_spaceship_position(None)

        # Unschedule existing intervals
        Clock.unschedule(self.update)
        Clock.unschedule(self.generate_asteroid)
        Clock.unschedule(self.generate_star)
        Clock.unschedule(self.generate_power_up)
        Clock.unschedule(self.generate_magnetic)
        Clock.unschedule(self.shoot_bullet)

        # Schedule intervals again
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        Clock.schedule_interval(self.generate_asteroid, 1.0)
        Clock.schedule_interval(self.generate_star, 2.0)
        Clock.schedule_interval(self.generate_power_up, 10.0)
        Clock.schedule_interval(self.generate_magnetic, 15.0)

    def clear_game_state(self):
        # Remove asteroids, stars, and power-ups from the game
        for asteroid in self.asteroids:
            self.remove_widget(asteroid)
        for star in self.stars:
            self.remove_widget(star)
        for power_up in self.power_ups:
            self.remove_widget(power_up)
        for magnetic in self.magnetics:
            self.remove_widget(magnetic)
        for bullet in self.bullets:
            self.remove_widget(bullet)

        self.asteroids = []
        self.stars = []
        self.power_ups = []
        self.magnetics = []
        self.bullets = []

    def go_to_main_menu(self, instance=None):
        self.parent.go_to_main_menu()

class SpaceAdventure(Screen):
    def on_pre_enter(self, *args):
        self.game = SpaceGame()
        self.add_widget(self.game)
        self.game.reset_game(None)

        main_layout = BoxLayout(orientation='vertical', padding=[5, 20], spacing=5, size_hint=(1, 0.4), pos_hint={'top': 1})
        layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), pos_hint={'center_x': 0.5})

        self.highest_score_label = Label(size_hint=(1, 1), font_size=20)
        layout.add_widget(self.highest_score_label)

        self.score_label = Label(text=f"Score: {self.game.score}", size_hint=(1, 1), font_size=20)
        layout.add_widget(self.score_label)

        back_button = Button(text='X', bold=True, size_hint=(None, None), background_color=(0.8, 0.2, 0.2), size=(40, 40), pos_hint={'right': 1, 'top': 1})
        back_button.bind(on_release=self.go_to_main_menu)
        layout.add_widget(back_button)

        main_layout.add_widget(layout)

        self.powerup_timer = Label(bold=True, size_hint=(1, 0.5), font_size=35)
        main_layout.add_widget(self.powerup_timer)
        self.magnetic_timer = Label(bold=True, size_hint=(1, 0.5), font_size=35)
        main_layout.add_widget(self.magnetic_timer)

        self.add_widget(main_layout)

        self.game.reset_game(None)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def update(self, dt):
        self.game.update(dt)
        self.score_label.text = f"Score: {self.game.score}"
        if self.game.invincible:
            self.powerup_timer.text = f"x2/invincible {self.game.powerup_time_left}"
        else:
            self.powerup_timer.text = ''
        if self.game.magnetic_active :
            self.magnetic_timer.text = f"Magnatic/Shots {self.game.magnetic_time_left}"
        else :
            self.magnetic_timer.text = ''
        if self.game.game_over_flag :
            self.magnetic_timer.text = ''
        app = App.get_running_app()
        if app.current_user:
            username = app.current_user['username']
            highest_score = game_highest_score(username, self.game.game_name)
            self.highest_score_label.text = f'Highest score: {highest_score}'
        else:
            self.highest_score_label.text = f'Highest score: {self.game.highest_score}'

    def go_to_main_menu(self, instance=None):
        Clock.unschedule(self.update)
        self.game.game_over_flag = True
        self.manager.current = 'main'
        self.clear_widgets()