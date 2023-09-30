import os
import tkinter as tk
from itertools import cycle
from PIL import Image, ImageTk

class AnimatedGif(tk.Label):
    def __init__(self, master, path, fps=30):
        self.frames = []
        img = Image.open(path)

        for frame in range(0, img.n_frames):
            photo = ImageTk.PhotoImage(img.copy().convert("RGBA"))
            self.frames.append(photo)
            img.seek(frame)

        self.iterator = cycle(self.frames)
        self.image = next(self.iterator)
        
        super().__init__(master, image=self.image)
        self.tick(fps)

    def tick(self, fps):
        self.image = next(self.iterator)
        self.config(image=self.image)
        self.after(int(1000 / fps), self.tick, fps)

def center_window(root, width=None, height=None):
    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # If width and height are not provided, use the root's current size
    width = width or root.winfo_width()
    height = height or root.winfo_height()
    
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

def display_animated_gif():
    root = tk.Tk()
    root.title("Animated GIF Display")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gif_path = os.path.join(base_dir, "assets", "griddy.gif")
    label = AnimatedGif(root, gif_path, fps=15)
    label.pack()
    
    # Center the window after the mainloop starts
    root.update_idletasks()
    center_window(root)

    root.mainloop()


display_animated_gif()
