import tkinter as tk
from tkinter import ttk
from tkinter import font
import cv2 as cv
from PIL import Image, ImageTk
import time
import datetime
from threading import Thread
from file_manager import FileManager
from camera_feed import CameraFeed


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.input_file_path = "Sessions.xlsx"
        self.output_file_path = "Main file.xlsx"
        self.fileManager = FileManager(self.input_file_path, self.output_file_path)

        self.title("QR-Code Scanner")
        # self.attributes('-topmost', 1)         # optionally keep window always in foreground
        # self.attributes('-fullscreen', True)   # optionally set window to fullscreen

        self.iconbitmap("icon.ico")

        self.window_width = 1280  # define window size
        self.window_height = 800

        screen_width = self.winfo_screenwidth()  # determine screen size
        screen_height = self.winfo_screenheight()

        center_x = int(
            screen_width / 2 - self.window_width / 2
        )  # determine the center of the screen
        center_y = int(screen_height / 2 - self.window_height / 2)

        self.geometry(
            f"{self.window_width}x{self.window_height}+{center_x}+{center_y}"
        )  # center the window on the screen

        self.columnconfigure(0, weight=5)  # set the size ratio of the different columns
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=5)
        self.bind("<Configure>", self.resize_elements)

        self.cameraFeed = CameraFeed()
        self.fileManager.downloadRemoteFile(self.input_file_path)
        # self.create_window()        # create the GUI window
        self.guiThread = Thread(target=self.create_window)
        self.guiThread.daemon = (
            True  # necessary to stop the thread when exiting the program
        )
        self.guiThread.start()
        self.cameraThread = Thread(target=self.main)
        self.cameraThread.daemon = (
            True  # necessary to stop the thread when exiting the program
        )
        self.cameraThread.start()

    def main(self):
        lastRegisteredPerson: str = ""
        while True:
            (
                camera_is_found,
                image,
            ) = self.cameraFeed.get_image()  # start the camera thread
            currentTime = datetime.datetime.now()
            if camera_is_found:
                value, points = self.QR_read(image)

                img = cv.cvtColor(image, cv.COLOR_BGR2RGB)
                img = Image.fromarray(img)

                # Calculate the aspect ratio of the image
                aspect_ratio = img.height / img.width
                new_width = self.window_width // 4

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
                        text="Last registered participant:\n" + lastRegisteredPerson
                    )

            else:
                self.tellNoCameraFound()

    def create_window(self):
        standardFont = font.nametofont("TkDefaultFont")
        self.titleFont = (standardFont, self.window_width // 30)
        self.regularFont = (standardFont, self.window_width // 40)

        self.programName = ttk.Label(
            self,
            text="Conference Enrollment",
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
            width=self.window_width // 2, height=self.window_height // 2
        )
        self.time = ttk.Label(self, text="", font=self.regularFont)  # current time
        self.lastRegisteredPerson = ttk.Label(self, text="", font=self.regularFont)
        self.selected_entry = tk.StringVar()
        self.selector = ttk.Combobox(
            self,
            textvariable=self.selected_entry,
            state="readonly",
            font=self.regularFont,
        )  # session selector
        self.selector[
            "values"
        ] = self.fileManager.get_sheet_names()  # custom sessions can be entered here
        print(self.selector["values"])
        self.selector.current(0)  # make the first entry the default one
        self.selector.bind("<<ComboboxSelected>>", self.on_combobox_select)
        self.selector.config(width=self.window_width // 40)
        self.sub_session_var = tk.StringVar()
        self.sub_selector = ttk.Combobox(
            self,
            textvariable=self.sub_session_var,
            state="readonly",
            font=self.regularFont,
        )
        self.sub_selector["values"] = self.fileManager.get_sessions(self.selector.get())
        self.sub_selector.current(0)  # Make the first entry the default one
        self.sub_selector.config(width=self.window_width // 40)

        # place all GUI elements on the grid layout
        self.programName.grid(column=0, row=0, columnspan=3, padx=15, pady=15)
        self.name.grid(column=2, row=2)
        self.indicator.grid(column=1, row=3, padx=15, pady=15)
        self.info.grid(column=2, row=3)
        self.cloudInfo.grid(column=2, row=4)
        self.imageLabel.grid(column=0, row=1, rowspan=4, padx=15, pady=15)
        self.time.grid(column=0, row=5, padx=15, pady=15)
        self.lastRegisteredPerson.grid(column=0, row=6, padx=15, pady=15)
        self.selector.grid(column=2, row=5, padx=30, pady=15)
        self.sub_selector.grid(column=2, row=6, padx=30, pady=15)

    def on_combobox_select(self, event):
        # Get the selected option
        selected_day = self.selector.get()
        print("Selected Option:", selected_day)

        new_options = self.fileManager.get_sessions(selected_day)

        self.sub_selector["values"] = new_options
        if new_options:
            self.sub_selector.current(0)
        else:
            self.sub_selector.set("")  # Clear the selection if there are no values

    def statusMessage(self, status):  # display status message + image
        if status == "file":
            message = "can't write file"
            statusImage = "enrolment_failed.png"
        if status == "success":
            message = "Enrolment was successful"
            statusImage = "enrolment_successful.png"
        self.info.config(text=message)
        newImg = ImageTk.PhotoImage(
            (Image.open(statusImage)).resize((32, 32), Image.Resampling.LANCZOS)
        )
        self.indicator.config(image=newImg)
        self.indicator.image = newImg

    def tellNoCameraFound(self):
        self.name.config(
            text="No Camera Found"
        )  # display message and image if no camera found
        img = Image.open("no-video.png")
        # img = img.resize((300,300), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        self.imageLabel.config(image=img)
        self.imageLabel.image = img

    def OnQRCodeDetected(self, value):
        self.name.config(text="QR Code Found")
        result = self.fileManager.appendQRData(value, str(self.selected_entry.get()))
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
