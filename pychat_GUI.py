from tkinter import *
from tkinter import scrolledtext, messagebox
import threading, queue


class ChatGUI:
    def __init__(self, cl):
        self.root = Tk()
        self.root.title("pychat GUI")

        # Set client reference
        self.client = cl

        # Initialize chat window widgets
        self.init_chatwindow()

    def init_chatwindow(self):
        self.chatbox = scrolledtext.ScrolledText(self.root, width=60, height=10)
        self.chatbox.grid(row=0, column=0, padx=5, pady=2.5, columnspan=5, sticky="W")
        self.chatbox.config(state=DISABLED)

        self.chatinput = Entry(self.root, width=71)
        self.chatinput.grid(row=1, column=0, padx=5, pady=2.5, sticky="W")

        self.enterbutton = Button(self.root, text="Enter", width=7, command=self.send_input)
        self.enterbutton.grid(row=1, column=1, padx=2.5, pady=2.5, sticky="W")
        self.enterbutton.config(bg="lightblue")

    # Start GUI instance
    def start_GUI(self):
        self.start_msg_thread()
        self.root.mainloop()

    # Update chatbox with message from server
    def update_chatbox(self, msg):
        self.chatbox.config(state=NORMAL)
        self.chatbox.insert(END, msg + "\n")
        self.chatbox.see(END)
        self.chatbox.config(state=DISABLED)

    # Send user messages to server
    def send_input(self):
        self.client.send_message(self.chatinput.get())
        self.chatinput.delete(0, END)

    # Start thread for reading messages from server
    def start_msg_thread(self):
        self.thread_queue = queue.Queue()
        self.new_thread = threading.Thread(
            target=self.client.add_to_queue,
            kwargs={'thread_queue': self.thread_queue})
        self.new_thread.start()
        self.listen_for_result()

    # Loop for checking if there is message from server
    def listen_for_result(self):
        try:
            new = self.thread_queue.get(0)
            self.update_chatbox(new)
            self.root.after(100, self.listen_for_result)
        except queue.Empty:
            self.root.after(100, self.listen_for_result)