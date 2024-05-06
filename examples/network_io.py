'''
Demonstrates how to perform an I/O operation in asynckivy.
'''
import requests
from kivy.app import App
from kivy.uix.button import Button
import asynckivy as ak


class TestApp(App):

    def build(self):
        return Button(font_size='20sp')

    def on_start(self):
        ak.start(self.main())

    async def main(self):
        button = self.root
        button.text = 'start a http request'
        await ak.event(button, 'on_press')
        button.text = 'waiting for the server to respond...'
        res = await ak.run_in_thread(lambda: requests.get("https://httpbin.org/delay/2"), daemon=True)
        button.text = res.json()['headers']['User-Agent']


if __name__ == '__main__':
    TestApp().run()
