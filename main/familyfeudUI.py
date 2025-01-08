from time import sleep
from groq import Groq
from gameLogicHandlers import steal, decide_turn, handle_turn, print_board
from questiongenerators import questions_from_AI, questions_from_file, questions_from_topic
from tkinter import*

window = Tk()         
window.state('zoomed') 
window.title("Currency Converter")
bg = PhotoImage(file = "background.gif")
w= window.winfo_screenwidth()               
h= window.winfo_screenheight()   
label1 = Label(window, image = bg, height=h, width=w)
label1.place(x = 0,y = 0)

window.mainloop()