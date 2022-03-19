__author__ = 'bunkus'
import threading
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.settings import Settings
from kivy.config import ConfigParser
from kivy.uix.actionbar import ActionBar, ActionButton, ActionGroup, ActionView
from kivy.graphics.texture import Texture
import cv2

from mefamo.mefamo import Mefamo 

class MediapipeFaceGUI(App):

    def build(self):

        layout = GridLayout(cols=1)

        self.img1 = Image()
        button = ActionButton(text="Settings")
        button.bind(on_release=self.open_settings)

        self.settings = Settings()

        action_bar = ActionBar()
        action_view = ActionView()
        action_group = ActionGroup()
        action_group.add_widget(button)
        action_view.add_widget(action_group)
        action_bar.add_widget(action_view)

        # layout.add_widget(action_bar)
        layout.add_widget(self.img1)

        self.mdpf = Mefamo() 
        mdpf_thread = threading.Thread(target=self.mdpf.start, daemon=True)
        mdpf_thread.start()

        Clock.schedule_interval(self.update, 1.0/60.0)
        return layout

    def build_config(self, config):
        return super().build_config(config)

    def button_callback(self, instance):
        print('The button %s state is <%s>' % (instance, instance.state))

    def update(self, dt):
        if self.mdpf.image is not None:
            buf1 = cv2.flip(self.mdpf.image, 0)
            buf = buf1.tostring()
            texture1 = Texture.create(size=(self.mdpf.image.shape[1], self.mdpf.image.shape[0]), colorfmt='bgr') 
            #if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer. 
            texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.img1.texture = texture1
                
        
        # display image from cam in opencv window
        # ret, frame = self.capture.read()
        # cv2.imshow("CV2 Image", frame)
        # # convert it to texture
        # buf1 = cv2.flip(frame, 0)
        # buf = buf1.tostring()
        # texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
        # #if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer. 
        # texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # # display image from the texture
        # self.img1.texture = texture1

if __name__ == '__main__':
    MediapipeFaceGUI().run()
    cv2.destroyAllWindows()