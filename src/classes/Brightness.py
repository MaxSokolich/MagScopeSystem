"""
Module containing the Brightness class

**( EXPERIMENTAL )
**( CURRENTLY NON-IMPLEMENTED )

@authors: Max Sokolich, Brennan Gallamoza, Luke Halko, Trea Holley,
          Alexis Mainiero, Cameron Thacker, Zoe Valladares
"""

import tkinter


def find(obj):
    name = f"{type(obj).__name__}:n    "
    try:
        return name + "n    ".join([f"{x} = '{obj.cget(x)}'" for x in obj.keys()])
    except:
        return f"'{obj}' has no keys attribute"


class Brightness:
    """
    Brightness class for handling brightness/contrast adjustment to the OpenCV
    Tracker feed.
    """

    def __init__(self):
        self.master = tkinter.Tk()
        self.master.update_idletasks()
        self.color = 15790320  # #f0f0f0 = SystemButtonFace
        self.var = tkinter.IntVar(self.master, value=self.color)
        self.flexx(self.master)

        self.label = tkinter.LabelFrame(
            self.master, labelanchor="n", text=self.master["background"]
        )
        self.label.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.flexx(self.label, r=None)
        self.flexx(self.label, r=None, c=1)

        self.scroll = tkinter.Scale(
            self.label,
            orient="horizontal",
            resolution=65793,
            label="Brightness Control",
            from_=0,
            to=16777215,
            variable=self.var,
            command=self.control,
        )
        self.scroll.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.master.geometry("200x200")
        self.master.minsize(334, 113)

    def flexx(self, o, r=0, c=0, rw=1, cw=1):
        if r != None:
            o.rowconfigure(r, weight=rw)
        if c != None:
            o.columnconfigure(c, weight=cw)

    def convert(self):
        col = "#" + ("000000" + hex(self.color)[2:])[~5:]
        self.var.set(self.color)
        self.label["text"] = col
        self.master.tk_setPalette(col)

    def control_up(self):
        self.color += 65793
        if self.color > 16777215:
            self.color = 15790320
        col = self.convert()

    def control_down(self):
        self.color -= 65793
        if self.color < 0:  # 15790320:
            self.color = 16777215
        col = self.convert()

    def control(self, n):
        self.color = int(n)
        col = self.convert()


if __name__ == "__main__":

    bright = Brightness()
    tkinter.mainloop()
