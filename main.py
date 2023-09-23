import tkinter as tk
from tkinter import ttk
from tkinter import font
import cv2 as cv
from PIL import Image, ImageTk
import time
import datetime
from threading import Thread
from file_manager import FileManager, Session, Sessions
from camera_feed import CameraFeed
from typing import List


class App(tk.Tk):
    name: ttk.Label
    sessions: Sessions
    auto_session_selection: bool
    switch_state: bool = False

    def __init__(self):
        super().__init__()

        self.input_file_path = "Sessions.xlsx"
        self.output_file_path = "Main file.xlsx"
        self.fileManager = FileManager(self.input_file_path, self.output_file_path)
        self.sessions = Sessions
        self.auto_session_selection = True

        self.title("QR-Code Scanner")
        # self.attributes('-topmost', 1)         # optionally keep window always in foreground
        self.attributes("-fullscreen", True)  # optionally set window to fullscreen

        # self.iconbitmap("icon.ico")

        self.screen_width = self.winfo_screenwidth()  # determine screen size
        self.screen_height = self.winfo_screenheight()

        center_x = int(
            self.screen_width / 2 - self.screen_width / 2
        )  # determine the center of the screen
        center_y = int(self.screen_height / 2 - self.screen_height / 2)

        # self.geometry(
        #    f"{self.screen_width }x{self.screen_height }+{center_x}+{center_y}"
        # )  # center the window on the screen

        self.columnconfigure(0, weight=5)  # set the size ratio of the different columns
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=5)
        self.bind("<Configure>", self.resize_elements)
        self.fileManager.downloadRemoteFile(self.input_file_path)
        # self.create_window()        # create the GUI window
        # self.guiThread = Thread(target=self.create_window)
        self.create_window()
        # self.guiThread.daemon = (
        #     True  # necessary to stop the thread when exiting the program
        # )
        # self.guiThread.start()
        self.cameraFeed = CameraFeed()
        self.cameraThread = Thread(target=self.main)
        self.cameraThread.daemon = (
            True  # necessary to stop the thread when exiting the program
        )
        self.cameraThread.start()

    def main(self):
        lastRegisteredPerson = ""
        while True:
            (
                camera_is_found,
                image,
            ) = self.cameraFeed.get_image()  # start the camera thread
            currentTime = datetime.datetime.now()
            if camera_is_found:
                try:
                    value, points = self.QR_read(image)
                except Exception as ex:
                    print(ex)

                img = cv.cvtColor(image, cv.COLOR_BGR2RGB)
                img = Image.fromarray(img)

                # Calculate the aspect ratio of the image
                aspect_ratio = img.height / img.width
                new_width = int(self.screen_width / 2)

                # Calculate the new dimensions
                finalHeight = int(new_width * aspect_ratio)

                img = img.resize((new_width, finalHeight), Image.LANCZOS)
                img = ImageTk.PhotoImage(img)
                self.imageLabel.config(image=img)
                self.imageLabel.image = img

                self.time.config(text=currentTime.strftime("%d.%m.%Y, %H:%M:%S"))

                if points is None or value == "":  # no QR code detected
                    self.tellNoQRC()
                elif value == lastRegisteredPerson:
                    pass
                else:  # QR code detected
                    self.OnQRCodeDetected(value)
                    lastRegisteredPerson = value
                    self.lastRegisteredPerson.config(
                        text="Last registered participant:\n" + lastRegisteredPerson,
                        foreground="green",
                        justify="center",
                    )

            else:
                self.tellNoCameraFound()

    def create_window(self):
        standardFont = font.nametofont("TkDefaultFont")
        self.titleFont = (standardFont, self.screen_width // 40)
        self.regularFont = (standardFont, self.screen_width // 55)

        self.programName = ttk.Label(
            self,
            text="MST - Attendees Tracker",
            foreground=("black"),
            font=self.titleFont,
            justify=("center"),
        )  # program name
        self.name = ttk.Label(self, font=self.regularFont)  # display the scanned name
        self.indicator = ttk.Label(self)  # image if enrolment was successful or not
        self.info = ttk.Label(
            self, text="", font=self.regularFont
        )  # text if enrolment was successful or not
        self.cloudInfo = ttk.Label(
            self, text="", font=self.regularFont
        )  # text for upload status
        self.imageLabel = tk.Label(self)  # place for the camera image
        self.imageLabel.config(
            width=self.screen_width // 2, height=self.screen_height // 2
        )
        self.time = ttk.Label(self, text="", font=self.regularFont)  # current time
        self.lastRegisteredPerson = ttk.Label(
            self, text="", font=self.regularFont, justify="center"
        )
        self.selected_day = tk.StringVar()
        self.day_selector = ttk.Combobox(
            self,
            textvariable=self.selected_day,
            state="readonly",
            font=self.regularFont,
        )  # session selector
        self.day_selector[
            "values"
        ] = self.fileManager.get_sheet_names()  # custom sessions can be entered here
        print(self.day_selector["values"])
        self.day_selector.current(0)  # make the first entry the default one
        self.day_selector.bind("<<ComboboxSelected>>", self.on_day_selector_select)
        self.day_selector.config(width=self.screen_width // 70)
        self.selected_session = tk.StringVar()
        self.session_selector = ttk.Combobox(
            self,
            textvariable=self.selected_session,
            state="readonly",
            font=self.regularFont,
        )
        self.sessions = self.fileManager.get_Sessions(self.day_selector.get())
        session_names: List[str] = self.sessions.get_session_names()
        self.session_selector["values"] = session_names
        self.session_selector.current(0)  # Make the first entry the default one
        self.session_selector.config(width=self.screen_width // 70)
        self.session_selector.bind(
            "<<ComboboxSelected>>", self.on_session_selector_select
        )

        padx = self.screen_width // 60
        pady = self.screen_height // 50

        # place all GUI elements on the grid layout
        self.programName.grid(column=0, row=0, columnspan=3, padx=padx, pady=pady)
        self.name.grid(column=2, row=2)
        self.indicator.grid(column=1, row=3, padx=padx, pady=pady)
        self.info.grid(column=2, row=3)
        self.cloudInfo.grid(column=2, row=4)
        self.imageLabel.grid(column=0, row=1, rowspan=4, padx=padx, pady=pady)
        self.time.grid(column=0, row=5, padx=padx, pady=pady)
        self.lastRegisteredPerson.grid(column=0, row=6, padx=padx, pady=pady)
        self.day_selector.grid(column=2, row=5, padx=30, pady=pady)
        self.session_selector.grid(column=2, row=6, padx=30, pady=pady)

        self.close_button = tk.Button(
            self, text="Close", command=self.close_window, fg="red"
        )
        self.close_button.grid(row=0, column=3, padx=padx, pady=pady)

        self.auto_session_var = False
        self.auto_session_selection_button = tk.Button(
            self, text="OFF", width=self.screen_width//200, height=self.screen_height//200, command=self.toggle_switch
        )
        self.auto_session_selection_button.grid(row=7, column=3, padx=padx, pady=pady)

        self.auto_session_label = ttk.Label(
            self, text="Autotmatically select session -->", font=self.regularFont
        )  # current time
        self.auto_session_label.grid(row=7, column=2, padx=padx, pady=pady)

    def toggle_switch(self):
        self.auto_session_var = not self.auto_session_var
        self.update_auto_session_selection_button()

    def update_auto_session_selection_button(self):
        if self.auto_session_var:
            self.auto_session_selection_button.config(text="ON", bg="green")
        else:
            self.auto_session_selection_button.config(text="OFF", bg="red")

    def close_window(self):
        self.destroy()

    def on_session_selector_select(self, event):
        # Get the selected option
        selected_session = self.session_selector.get()
        print("Selected Option:", selected_session)

    def on_day_selector_select(self, event):
        # Get the selected option
        selected_day = self.day_selector.get()
        print("Selected Option:", selected_day)

        self.sessions = self.fileManager.get_Sessions(selected_day)
        session_names: List[str] = self.sessions.get_session_names()
        session, current_session_index = self.sessions.get_current_session()

        self.session_selector["values"] = session_names
        if session_names:
            self.session_selector.current(current_session_index)
        else:
            self.session_selector.set("")  # Clear the selection if there are no values

    def statusMessage(self, status):  # display status message + image
        if status == "file":
            message = "can't write file"
            statusImage = "enrolment_failed.png"
        if status == "success":
            message = "Enrolment was successful"
            statusImage = "enrolment_successful.png"
        self.info.config(text=message)
        newImg = ImageTk.PhotoImage(
            (Image.open(statusImage)).resize(
                (self.screen_height // 10, self.screen_height // 10),
                Image.Resampling.LANCZOS,
            )
        )
        self.indicator.config(image=newImg)
        self.indicator.image = newImg

    def tellNoCameraFound(self):
        self.name.config(
            text="No Camera Found"
        )  # display message and image if no camera found
        img = Image.open("no-video.png")
        img = img.resize((300, 300), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        self.imageLabel.config(image=img)
        self.imageLabel.image = img

    def OnQRCodeDetected(self, value):
        self.name.config(text="QR Code Found")
        if (self.auto_session_var):
            self.fileManager.downloadRemoteFile(self.input_file_path)
            self.sessions = self.fileManager.get_Sessions(self.selected_day.get())
            session, current_session_index = self.sessions.get_current_session()
            self.session_selector.current(current_session_index)
        result = self.fileManager.appendQRData(
            value, str(self.selected_day.get()), str(self.selected_session.get())
        )
        self.cloudInfo.config(text=result)
        self.statusMessage("success")
        time.sleep(1)

    def tellNoQRC(self):
        self.name.config(text="No QR Code Found")
        self.info.config(text="")
        self.cloudInfo.config(text="")
        self.indicator.config(image="")
        self.indicator.image = ""

    def QR_read(self, image):
        try:
            detect = cv.QRCodeDetector()
            value, points, straight_qrcode = detect.detectAndDecode(image)
            return value, points
        except:
            return None

    def resize_elements(self, event):
        new_width = event.width
        new_height = event.height

        # Calculate the new size for elements based on the window size
        # self.selector.config(width=new_width // 20, height=new_height // 20)
        # self.sub_selector.config(width=new_width // 10)


if __name__ == "__main__":  # lauch the main GUI loop
    app = App()

    app.mainloop()
