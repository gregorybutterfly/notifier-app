"""
Simple app created with TKinter. Create/Edit/Delete reminders by date.

If today's date == reminders date, an email with written message will be sent to the recipient.

Messages are saved in: messages.json

To use gmail you have to enable 'Allow less secure apps' on your google account:
https://myaccount.google.com/u/1/security?rapt=https://www.google.com/settings/security/lesssecureapps#connectedapps

To use this script edit:
- username
- password
- recipient
"""

from tkinter import Tk, Frame, Label, Text, Listbox, Button, END, Entry, StringVar, RIGHT, messagebox
import json
from collections import defaultdict
import smtplib
from os import path
from datetime import date
import re
from threading import Thread

# Today's date
TODAY = date.today().strftime('%d/%m/%Y')

# Name of the application
APP_NAME = 'Notifier App'
# Standard font size
APP_FONT = ('Helvetica', '12')
# Widget title font size
WIDGET_FONT_TITLE = ('Helvetica', '15')

# Your email credentials
username = ''
password = ''
recipient = ''

JSON_FILE = path.isfile(path.join(path.abspath('.'), 'messages.json'))


def send_email(username, password, recipient, body, time):
    """Go through the list of reminders found in messages.json file and check if there is any email to be sent.
    """
    FROM = username
    TO = recipient
    SUBJECT = 'Reminder'
    TEXT = body
    MESSAGE = 'Subject: {}\n\nTime of reminder:\n{}\nMessage:\n{}\n'.format(SUBJECT, time, TEXT)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(FROM, TO, MESSAGE)
    server.close()
    print('Success')


class Gui(Tk):

    """Gui window mostly built with grid layout.
    #####TOP#####
    #LEFT##RIGHT#
    ###BOTTOM####
    """

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.geometry('700x510+50+50')
        self.title('Notifier Beta')

        # Main Window container
        self.container = Frame(self, bg='white', width=660, height=460)
        self.container.grid(row=0, column=0, padx=20, pady=20, sticky='nesw')
        self.messages = defaultdict(dict)
        self.read_reminders()

        # LAYOUT WIDGET GRID
        self.window_top()
        self.window_left()
        self.window_right()
        self.window_bottom()

        # SEND EMAILS if any date matches TODAY
        if username is not '':
            notifier = DateChecker(self.messages)
            notifier.run()

    def create_json(self):
        """Create json file: messages.json
        """

        with open('messages.json', 'w') as f:
            json.dump(self.messages, f, indent=4, sort_keys=True)

    def write_reminders(self, mydate, mytime, mymessage):
        """Grab the data from data_entry_var, time_entry_var, message_box and save them in messages.json.
        Update listbox with new reminders
        """

        if mydate != 'DD/MM/YYYY' and mytime != 'HH:MM' and self.data_entry_var.get() != '' and self.time_entry_var.get() != '':

            self.messages[mydate.strip()] = {
                'time':mytime.strip(),
                'message':mymessage.strip(),
            }

            # Create json file
            self.create_json()

            self.list_box.delete(0, END)
            self.read_reminders()
            self.update_listbox()
        else:
            messagebox.showerror(
                'Incorrect Input', 'Check if you inserted correct data format: "DD/MM/YYYY" or time format: "HH:MM"'
                )

    def read_reminders(self):
        """Read the data from messages.json file and assign it to self.messages dictionary.
        """

        # Check if messages.json exists, if not, create new empty file.
        if not JSON_FILE:
            with open('messages.json', 'w') as f:
                json.dump(self.messages, f)

        # load json file to self.messages dict.
        with open('messages.json', 'r') as f:
            self.messages = json.load(f)

    def update_fields(self, num):
        """Update fields when listbox is clicked
        """

        if self.messages.keys():
            data = self.messages.get(num)

            self.data_entry_var.set(num)
            self.time_entry_var.set(data['time'])
            self.message_box.delete('1.0', END)
            self.message_box.insert('1.0', data['message'])
        else:
            print('No reminders detected!')

    def update_listbox(self):
        """Create list of reminders inside listbox widget.
        List is taken from self.messages and is represented by the date of each reminder."""

        for i, key in enumerate(sorted(self.messages.keys())):
            self.list_box.insert(i, key)

    def delete_record(self, num):
        """Activate when 'Delete Record' button is clicked.
        Deletes key from self.messages dictionary and creates new json file with updated/deletes keys
        Clears and updates listbox
        """

        del self.messages[num]
        self.list_box.delete(0, END)
        self.time_entry_var.set('')
        self.data_entry_var.set('')
        self.message_box.delete('1.0', END)

        self.create_json()
        self.update_listbox()

    def window_top(self):
        """Displays the logo
        """
        window_top = Frame(self.container, bg='white', width=660, height=50)
        window_top.grid(row=0, column=0, sticky='nesw', columnspan=2)

        label_title = Label(window_top, text=APP_NAME, font=(('Helvetica', 'bold'), '25'), bg='white', bd=2, relief='groove', width=14)
        label_title.grid(row=0, padx=20, pady=20)

    def validate_data(self, data):
        """Validate if user entered correct DATE format:
        DD/MM/YYYY.
        """
        pattern = re.compile('^(\d{2}/\d{2}/\d{4})$')

        if pattern.match(data):
            self.data_entry_var.set(pattern.match(data).group(1))
        else:
            self.data_entry_var.set('DD/MM/YYYY')

    def validate_time(self, mytime):
        """Validate if user entered correct TIME format:
        HH:MM.
        """
        pattern = re.compile(r'^(([01]\d|2[0-3]):([0-5]\d)|24:00)$')

        if pattern.match(mytime):
            self.time_entry_var.set(pattern.match(mytime).group(1))
        else:
            self.time_entry_var.set('HH:MM')

    def window_left(self):
        """Displays date field, time field, message box field, clear button and Add Notification button.
        Each field is validated before action is applied.
        """
        window_left = Frame(self.container, bg='white', width=200, height=370)
        window_left.grid(row=1, column=0, sticky='nesw')

        # TIME & DATE
        time_date_window = Frame(window_left, bg='white', width=24)
        time_date_window.grid(row=0, column=0, sticky='we')

        time_date_window_title = Label(time_date_window, text='Date & Time:', font=WIDGET_FONT_TITLE, bg='white', bd=2, anchor='w')
        time_date_window_title.grid(row=0, column=0, padx=20, sticky='w')

        time_date_fields = Frame(time_date_window, bg='white')
        time_date_fields.grid(row=1, sticky='we', pady=10)

        date_field = Label(time_date_fields, text='Date:', font=APP_FONT, bg='white', bd=2, anchor='w')
        date_field.grid(row=0, column=0, padx=20, pady=5, sticky='w')
        self.data_entry_var = StringVar()
        date_entry = Entry(time_date_fields, textvariable=self.data_entry_var,width=14, font=APP_FONT)
        date_entry.grid(row=1, column=0, sticky='w', padx=20)
        date_entry.bind('<FocusOut>', lambda x: self.validate_data(self.data_entry_var.get()))

        time_field = Label(time_date_fields, text='Time:', font=APP_FONT, bg='white', bd=2, anchor='w')
        time_field.grid(row=0, column=1, padx=20, pady=5, sticky='w')
        self.time_entry_var = StringVar()
        time_entry = Entry(time_date_fields, textvariable=self.time_entry_var, width=15, font=APP_FONT)
        time_entry.grid(row=1, column=1, sticky='w', padx=20)
        time_entry.bind('<FocusOut>', lambda x: self.validate_time(self.time_entry_var.get()))

        # MESSAGE BOX
        message_box_title = Label(window_left, text='Message Box:', font=WIDGET_FONT_TITLE, bg='white', bd=2,anchor='w')
        message_box_title.grid(row=1, column=0, padx=20, sticky='w')

        self.message_box = Text(window_left, width=34, height=7, font=APP_FONT)
        self.message_box.grid(row=2, column=0, padx=(11,0))

        # BUTTONS FRAME
        button_frame = Frame(window_left, bg='white')
        button_frame.grid(row=3, sticky='we', pady=(5,0))

        # Submit button
        submit_button = Button(button_frame, text='Add Notification', command=lambda: self.write_reminders(self.data_entry_var.get(),self.time_entry_var.get(), self.message_box.get('1.0', END)), width=15)
        submit_button.pack(side=RIGHT, padx=20, pady=3)

        # Clear button
        clear_button = Button(button_frame, text='Clear', command=lambda: self.message_box.delete('1.0', END), width=10)
        clear_button.pack(side=RIGHT, pady=3)

    def window_right(self):
        """Displays reminder listbox widget where all valid reminders can be found.
        """
        window_right = Frame(self.container, bg='white', width=200, height=370)
        window_right.grid(row=1, column=1, sticky='nesw')

        reminder_list_title = Label(window_right, text='Reminders:', font=WIDGET_FONT_TITLE, bg='white', bd=2, anchor='w')
        reminder_list_title.grid(row=0, column=0, padx=(0,20), sticky='w')

        self.list_box = Listbox(window_right, width=25, height=12, font=APP_FONT)
        self.list_box.grid(row=2, column=0, sticky='n', padx=(5,0))
        self.list_box.bind('<<ListboxSelect>>', lambda x:self.update_fields(self.list_box.selection_get()))
        self.update_listbox()


        # Delete
        delete_record = Button(window_right, text='Delete Record', command=lambda: self.delete_record(self.list_box.selection_get()), width=10)
        delete_record.grid(row=3, column=0, padx=20, pady=(7,0), sticky='e')

    def window_bottom(self):
        window_bottom = Frame(self.container, bg='white', width=660, height=50)
        window_bottom.grid(row=2, column=0, sticky='nesw', columnspan=2)

    def run(self):
        """Starts main loop of the App.
        """
        self.mainloop()


class DateChecker:
    """Class for checking if any date from self.messages matches today's date.
    If match exists the message will be sent to the recipient.
    If no matches no email message will be sent.

    """

    def __init__(self, messages):
        self.messages = messages

    def run(self):
        """Loop over keys from self.messages dict and look for matches
        """
        for reminder in self.messages.keys():
            if str(reminder) == TODAY:
                # Start new thread to speed up Gui
                t = Thread(target=send_email, args=(username, password, recipient, self.messages[reminder]['message'], self.messages[reminder]['time']))
                t.start()

    def __str__(self):
        return str(self.messages)


root = Gui()
root.run()
