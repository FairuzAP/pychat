from tkinter import *


class ServerInput:
    def __init__(self):
        self.root = Tk()
        self.root.title("ECC Parameters")

        # Initialize address variable and check variable
        self.address = ""
        self.server_set = False

        # Initialize server address window widgets
        self.init_serverwindow()

        self.root.mainloop()

    def init_serverwindow(self):
        self.s_label = Label(self.root, text="Please insert server address:")
        self.s_label.grid(row=0, column=0, pady=5)

        self.s_field = Entry(self.root, width=30)
        self.s_field.grid(row=1, column=0, padx=10, pady=5)

        self.s_button = Button(self.root, width=15, text="Submit Adress", command=self.set_server)
        self.s_button.grid(row=2, column=0, pady=5)

    # Set server address
    def set_server(self):
        self.address = self.s_field.get()
        self.server_set = True
        self.root.destroy()