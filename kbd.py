__author__ = 'VWGX1YO'
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.vkeyboard import VKeyboard

class Bab2Keyboard(VKeyboard):
    # on_key_up 은 필요 없다.

    # 일반 글자 처리
    def on_textinput(self, it):
        print("text input " + it)

    # 백스페이스, 엔터, 시프트, 캡스록, 이스케이프 등 처리
    def on_key_down(self, b_keycode, internal, b_modifiers):
        print("key down " + b_keycode + "," + str(internal) + "," + str(b_modifiers))

class LoginScreen(GridLayout):

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.vk = Bab2Keyboard(layout='qwerty')
        self.cols = 2
        self.add_widget(Label(text='User Name'))
        self.username = TextInput(multiline=False)
        self.add_widget(self.username)
        self.add_widget(Label(text='password'))
        self.password = TextInput(password=True, multiline=False)
        self.add_widget(self.password)
        self.add_widget(self.vk)

    # def focused(self):
    #     if self.password.focus == True:
    #         self.vk.on_key_down(self)
    #     elif self.username.focus == True:
    #         self.vk.on_key_down(self)

class MyApp(App):
    def build(self):
        return LoginScreen()


if __name__ == '__main__':
    MyApp().run()
