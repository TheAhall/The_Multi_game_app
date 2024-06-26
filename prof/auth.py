#auth.py
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from prof.database import get_user, add_user,update_nickname ,update_profile, update_profile_pic, update_password, verify_password, get_highest_scores
import os
import re

class LoginScreen(Screen):
    def login(self, username, password):
        if not username or not password:
            self.ids.error.text = 'Username and password are empty'
            return
        
        print(f"Attempting to log in user: {username}")
        user = get_user(username)
        if user:
            print(f"User found: {user['username']}")
            if verify_password(password, user['password']):
                print(f"Password correct for user: {username}")
                app = App.get_running_app()
                app.current_user = user
                self.ids.error.text = ''
                self.manager.current = 'main'
            else:
                print("Incorrect password")
                self.ids.error.text = 'Invalid username or password'
        else:
            print("User not found")
            self.ids.error.text = 'Invalid username or password'

    def on_pre_leave(self):
        self.ids.username.text = ''
        self.ids.password.text = ''
        self.ids.error.text = ''

class SignUpScreen(Screen):
    def is_valid_email(self, email):
        email_regex = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
        return email_regex.match(email)
    
    def signup(self, nickname, username, password, confirm_password, email, confirm_email):
        if not username or not password or not email or not nickname:
            self.ids.error.text = 'All fields are required'
            return
        if ' ' in nickname or '\t' in nickname:
            self.ids.error.text = 'Nickname cannot contain spaces'
            return
        if ' ' in username or '\t' in username:
            self.ids.error.text = 'Username cannot contain spaces'
            return
        if password != confirm_password:
            self.ids.error.text = 'Passwords do not match'
            return
        
        if not self.is_valid_email(email):
            self.ids.error.text = 'Invalid email format'
            return
        
        if email != confirm_email:
            self.ids.error.text = 'Email do not match'
            return
        
        if add_user(nickname, username, password, email):
            App.get_running_app().screen_manager.current = 'login'
            self.ids.error.text = ''
        else:
            self.ids.error.text = 'Username already exists'

    def on_pre_leave(self):
        self.ids.nickname.text = ''
        self.ids.username.text = ''
        self.ids.email.text = ''
        self.ids.confirm_email.text = ''
        self.ids.password.text = ''
        self.ids.confirm_password.text = ''
        self.ids.error.text = ''

class ProfileScreen(Screen):
    def on_pre_enter(self):
        app = App.get_running_app()
        user = app.current_user
        if user:
            highest_scores = get_highest_scores(user['username'])
            self.ids.nickname.text = user['nickname']
            self.ids.email.text = user['email']
            self.ids.about.text = user.get('about', '') or ''
            self.ids.profile_pic.source = user.get('profile_pic') or 'default_profile.png'
            self.ids.highest_scores.text = '\n'.join([f'{game}: {score}' for game, score in highest_scores.items()])

            # Show logout button if user is logged in
            self.ids.logout_button.opacity = 1
            self.ids.logout_button.disabled = False
        else:
            self.manager.current = 'login'

    def logout(self):
        app = App.get_running_app()
        app.current_user = None
        self.manager.current = 'login'

    def on_leave(self):
        # Hide logout button when leaving profile screen
        self.ids.logout_button.opacity = 0
        self.ids.logout_button.disabled = True

class EditProfileScreen(Screen):
    def on_pre_enter(self):
        app = App.get_running_app()
        user = app.current_user

        if user:
            self.ids.nickname.text = user.get('nickname')
            self.ids.about.text = user.get('about', '') or ''
            self.ids.current_password.text = ''
            self.ids.new_password.text = ''
            self.ids.confirm_password.text = ''
            self.ids.profile_pic.source = user.get('profile_pic') or 'default_profile.png'
        else:
            print("No user is currently logged in")

    def save_profile(self, about, nickname, current_password, new_password, confirm_new_password, profile_pic_path):
        app = App.get_running_app()
        user = app.current_user
        username = user['username']

        if new_password:
            if not verify_password(current_password, app.current_user['password']):
                self.ids.error.text = 'Current password is incorrect'
                return
            if new_password != confirm_new_password:
                self.ids.error.text = 'Passwords do not match'
                return
            update_password(username, new_password)
            app.current_user['password'] = new_password

        if nickname:
            if ' ' in nickname or '\t' in nickname:
                self.ids.error.text = 'Nickname cannot contain spaces'
                return
            if update_nickname(username, nickname):
                app.current_user['nickname'] = nickname
            else:
                self.ids.error.text = 'Nickname already exists'
                return

        if profile_pic_path and profile_pic_path != 'default_profile.png':
            # Save the profile picture to a specific directory
            profile_pics_dir = 'profile_pics'
            os.makedirs(profile_pics_dir, exist_ok=True)
            profile_pic_filename = os.path.basename(profile_pic_path)
            new_profile_pic_path = os.path.join(profile_pics_dir, profile_pic_filename)
            with open(profile_pic_path, 'rb') as src_file:
                with open(new_profile_pic_path, 'wb') as dst_file:
                    dst_file.write(src_file.read())
            update_profile_pic(username, new_profile_pic_path)
            user['profile_pic'] = new_profile_pic_path

        if about:
            update_profile(username, about)
            user['about'] = about

        self.manager.current = 'profile'

    def on_pre_leave(self):
        self.ids.error.text = ''

    def choose_image(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        filechooser = FileChooserListView(path=os.path.expanduser('~'), filters=['*.png', '*.jpg', '*.jpeg', '*.gif'])
        content.add_widget(filechooser)

        def on_select(instance):
            selection = filechooser.selection
            if selection:
                selected_path = selection[0]
                if selected_path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    self.ids.profile_pic.source = selected_path
                    self.selected_image_path = selected_path  # Store the selected image path for later use
                else:
                    self.ids.error.text = 'Selected file is not a valid image'
            popup.dismiss()

        button_content = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), padding=3, spacing=2)
        choose_btn = Button(text='Choose', size_hint=(1, None), font_size=17, height=45, on_release=on_select)
        cancel_btn = Button(text='Cancel', size_hint=(1, None), font_size=17, height=45)
        button_content.add_widget(choose_btn)
        button_content.add_widget(cancel_btn)
        content.add_widget(button_content)

        popup = Popup(title='Choose Profile Picture', content=content, size_hint=(0.9, 0.9), background_color=(0.2, 0.6, 0.8, 0.8))
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()