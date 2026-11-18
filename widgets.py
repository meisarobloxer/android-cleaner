import random
import tkinter as tk

from config import CURRENT_OS, CLR_BG, CLR_GREEN, CLR_CYAN, VERSION

class MatrixBanner(tk.Canvas):
    def __init__(self, master, width=940, height=85, **kwargs):
        super().__init__(master, width=width, height=height, bg=CLR_BG, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.fontsize = 12
        self.columns = max(1, width // self.fontsize)
        self.drops = [random.randint(-20, 0) for _ in range(self.columns)]
        self.chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%&*#<>[]"
        self.running = True
        self.animate()

    def animate(self):
        if not self.running:
            return
        self.delete("all")
        self.create_rectangle(0, 0, self.width, self.height, fill=CLR_BG, outline="")

        for i in range(len(self.drops)):
            char = random.choice(self.chars)
            x = i * self.fontsize + 4
            y = self.drops[i] * self.fontsize

            self.create_text(x, y, text=char, fill="#E0FFED", font=("Consolas", self.fontsize, "bold"))
            if y - self.fontsize > 0:
                self.create_text(x, y - self.fontsize, text=random.choice(self.chars), fill=CLR_GREEN, font=("Consolas", self.fontsize))
            if y - (self.fontsize * 2) > 0:
                self.create_text(x, y - (self.fontsize * 2), text=random.choice(self.chars), fill="#005522", font=("Consolas", self.fontsize))

            if y > self.height and random.random() > 0.93:
                self.drops[i] = 0
            else:
                self.drops[i] += 1

        os_label = "macOS" if CURRENT_OS == "Darwin" else CURRENT_OS.upper()
        self.create_text(self.width // 2, self.height // 2 - 12,
                         text=f"⚡ ANDROID CLEANER & DIAGNOSTICS ULTRA {VERSION} ⚡",
                         fill=CLR_GREEN, font=("Arial", 16, "bold"))
        self.create_text(self.width // 2, self.height // 2 + 12,
                         text=f"PLATFORM: [{os_label}] • GAME TURBO • DEBLOATER • LOGCAT • SCREEN TOOLS",
                         fill=CLR_CYAN, font=("Consolas", 10, "bold"))

        self.after(45, self.animate)

    def destroy(self):
        self.running = False
        super().destroy()
