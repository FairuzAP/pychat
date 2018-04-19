from tkinter import *


class ECCParam:
    def __init__(self):
        self.root = Tk()
        self.root.title("ECC Parameters")

        # Set variable for checking if parameters have been entered
        self.param_set = False

        # Initialize parameters
        self.a_val = -1
        self.b_val = 188
        self.p_val = 7919
        self.pt_x = 224
        self.pt_y = 503
        self.k_val = 20

        # Initialize ECC parameter window widgets
        self.init_eccwindow()

        self.root.mainloop()

    def init_eccwindow(self):
        self.a_text = Label(self.root, text="a")
        self.a_text.grid(row=0, column=0, padx=10, pady=2.5)

        self.b_text = Label(self.root, text="b")
        self.b_text.grid(row=1, column=0, padx=10, pady=2.5)

        self.p_text = Label(self.root, text="p")
        self.p_text.grid(row=2, column=0, padx=10, pady=2.5)

        self.pt_text = Label(self.root, text="Point")
        self.pt_text.grid(row=3, column=0, padx=10, pady=2.5)

        self.k_text = Label(self.root, text="k")
        self.k_text.grid(row=4, column=0, padx=10, pady=2.5)

        self.a_field = Entry(self.root, width=10)
        self.a_field.grid(row=0, column=1, padx=5, pady=2.5, sticky="W")
        self.a_field.insert(END, self.a_val)

        self.b_field = Entry(self.root, width=10)
        self.b_field.grid(row=1, column=1, padx=5, pady=2.5, sticky="W")
        self.b_field.insert(END, self.b_val)

        self.p_field = Entry(self.root, width=10)
        self.p_field.grid(row=2, column=1, padx=5, pady=2.5, sticky="W")
        self.p_field.insert(END, self.p_val)

        self.pt_frame = Frame(self.root)
        self.pt_frame.grid(row=3, column=1,padx=5, pady=2.5, sticky="W")

        self.ptx_field = Entry(self.pt_frame, width=10)
        self.ptx_field.pack(padx=(0,5), pady=2.5, side=LEFT)
        self.ptx_field.insert(END, self.pt_x)

        self.pty_field = Entry(self.pt_frame, width=10)
        self.pty_field.pack(padx=5, pady=2.5, side=LEFT)
        self.pty_field.insert(END, self.pt_y)

        self.k_field = Entry(self.root, width=10)
        self.k_field.grid(row=4, column=1, padx=5, pady=2.5, sticky="W")
        self.k_field.insert(END, self.k_val)

        self.b_frame = Frame(self.root)
        self.b_frame.grid(row=5, column=0, padx=5, pady=2.5, columnspan=2)

        self.input_button = Button(self.b_frame, width=15, text="Set Parameter", command=self.setValues)
        self.input_button.pack(padx=5, pady=2.5)

    # Set ECC parameter values based on input
    def setValues(self):
        self.a_val = int(self.a_field.get())
        self.b_val = int(self.b_field.get())
        self.p_val = int(self.p_field.get())
        self.pt_x = int(self.ptx_field.get())
        self.pt_y = int(self.pty_field.get())
        self.k_val = int(self.k_field.get())
        self.root.destroy()
        self.param_set = True