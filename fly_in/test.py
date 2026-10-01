import arcade


WIDTH = 1280
HEIGHT = 720
TITLE = "TEST"


class Window(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, TITLE)
        # self.backgrount_color = arcade.color.AMAZON

    def on_draw(self):
        self.clear()

    def on_key_press(self, key, key_modifiers):
        print("KEY PRESSED")
        print("symbol:", key)
        print("type:", type(key))
        print()
        print("mod:", key_modifiers)
        print("type:", type(key_modifiers))



def main():
    window = Window()
    arcade.run()

if __name__ == "__main__":
    main()
