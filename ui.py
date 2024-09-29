import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import time


class Paint:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.root = tk.Tk()

        self.canvas = tk.Canvas(
            self.root, width=self.width, height=self.height)
        self.canvas.grid(row=0)

        self.image = Image.new('RGB', (self.width, self.height), 'white')
        self.draw = ImageDraw.Draw(self.image)
        self.image_id = None
        self.update()

        self.root.mainloop()

    def update(self):
        print(f'update: {time.time()}')
        new_image = Image.eval(self.image, lambda x: (x + 1) % 255)
        self.image = new_image
        self.imageTk = ImageTk.PhotoImage(self.image)
        if self.image_id is not None:
            self.canvas.delete(self.image_id)
        self.image_id = self.canvas.create_image(
            self.width,
            self.height,
            image=self.imageTk,
            state='normal',
            anchor='se',
        )
        self.canvas.after(10, self.update)


if __name__ == '__main__':
    Paint()
