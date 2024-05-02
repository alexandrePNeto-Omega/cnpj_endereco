from tkinter import Button
from tkinter import DISABLED
from tkinter import Tk
from tkinter import *
from tkinter import filedialog

class WindowFile():
    def __init__(self):
        self.window = Tk()
        self.file_name = ""
        self.email_usuario = ""
        self.button_explore = None
        self.email_name = {}
        self.window.geometry("185x99")
        self.window.resizable(False, False)

    def show(self):
        # Titulo Janela
        self.window.title("Selecione a lista dos cnpj's")
        self.button_explore = Button(self.window, text = "Selecione o arquivo", command = self.browse_files)
        self.button_explore.grid(padx=15, pady=10)
        email_label = Label(self.window, text="Email")
        email_label.grid(padx=15, pady=0)
        self.email_name = Entry(self.window, width=25)
        self.email_name.grid(padx=15, pady=1)
        self.window.mainloop()

    def browse_files(self): 
        self.file_name = filedialog.askopenfilename(initialdir = "/", title = "Selecione a lista", filetypes=(("Excel2","*.csv*"),("all files", "*.*"))) or ""
        self.button_explore.configure(state=DISABLED)
        self.email_usuario = self.email_name.get() or ""
        self.window.destroy()

if __name__ == '__main__':
    W = WindowFile()
    W.show()