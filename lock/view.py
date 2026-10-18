import tkinter as tk  


from config import BG,BUTTON,BUTTON_ACTIVE,DIM,TEXT,WATER


def draw_glass(canvas,fraction):
    canvas.delete("all")
    top_1,top_r,bot_l,bot_r=40,180,65,155

    top_y,bot_y=20,220

    fraction=max(0.0,min(fraction,1.0))

    level=bot_y-(bot_y-top_y)*fraction

    def edge(y,a,b):
        return a+(b-a)*(y-top_y)/(bot_y-top_y)


        