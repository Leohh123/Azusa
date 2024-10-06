import tkinter
import tkinter.filedialog as fd
import tkinter.messagebox as mb


def open_file():
    '''Create a Tk file dialog and cleanup when finished'''
    top = tkinter.Tk()
    top.withdraw()  # hide window
    file_name = fd.askopenfilename(parent=top)
    top.destroy()
    return file_name


def info(msg):
    '''Create a info message box'''
    mb.showinfo('Message', msg)


def dashboard():
    top = tkinter.Tk()
    top.mainloop()
