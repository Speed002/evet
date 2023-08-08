import os
from tkinter import *
import customtkinter
import cv2
from PIL import ImageTk, Image
import face_recognition
import sys

customtkinter.set_default_color_theme("blue")
folderModePath = 'images'
faces_dir = 'picked_faces'
faces_list = os.listdir(faces_dir) # Lists all the faces picked from the live feed
imageList = os.listdir(folderModePath) # lists everything within that directory


class App(customtkinter.CTk):
    APP_NAME = "cv2"
    WIDTH = 800
    HEIGHT = 500

    def __init__(self, video_source=0, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Accessing the facades
        self.faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        # capturing the video source
        self.video_source = video_source
        self.vid = MyVideoCapture(self.video_source)

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.marker_list = []

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=2, border_width=0)
        self.frame_right.grid(row=0, column=0, rowspan=1, pady=0, padx=10, sticky="nsew")

        # # create canvas to hold the camera feed
        self.canvas = customtkinter.CTkCanvas(self.frame_right, width=1080, height=1000, bg="black", highlightthickness=0)
        self.canvas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # ============ frame_left ============
        self.frame_left.grid_rowconfigure(2, weight=1)

        # create scrollable frame
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self.frame_left, label_text="")
        self.scrollable_frame.grid(row=0, column=0, rowspan=3, padx=(10, 10), pady=(10, 0), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        # self.scrollable_frame_switches = []

        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")

        # ============ frame_right ============
        self.frame_right.grid_rowconfigure(1, weight=0)
        self.frame_right.grid_rowconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=1)

        # create scrollable frame below for unknown faces
        self.scrollable_frame2 = customtkinter.CTkScrollableFrame(master=self.frame_right, height=130, orientation="horizontal", corner_radius=2, label_text="")
        self.scrollable_frame2.grid(row=1, column=0, columnspan=3, sticky="news", padx=10, pady=(0, 10))
        self.scrollable_frame2.grid_rowconfigure(0, weight=0)
        # self.scrollable_frame_switches2 = []

        # Set default values
        self.load_image_side_frame()
        self.load_image_lower_frame()
        self.appearance_mode_optionemenu.set("Dark")
        self.update()
        self.detect_faces()

    def load_image_side_frame(self):
        # for image in imageList:
        for index in range(len(imageList)):
            img = Image.open(os.path.join(folderModePath, imageList[index]))
            photo = customtkinter.CTkImage(img, size=(162, 162))
            self.image_label = customtkinter.CTkLabel(self.scrollable_frame, image=photo, text="", width=12, height=45)
            self.image_label.grid(row=index, padx=0, pady=10, column=0)
            # Custom Label
            self.image_name = customtkinter.CTkLabel(self.scrollable_frame, text="Persons Name", width=162, bg_color="#1071b2")
            self.image_name.grid(row=index, padx=0, pady=(150, 0), column=0)

    # for image in imageList:
    def load_image_lower_frame(self):
        for index in range(len(faces_list)):
            img = Image.open(os.path.join(faces_dir, faces_list[index]))
            self.photo = customtkinter.CTkImage(img, size=(109, 109))
            self.image_label = customtkinter.CTkLabel(self.scrollable_frame2, image=self.photo, text="")
            self.image_label.grid(row=0, padx=10, pady=10, column=index)
        # self.after(1, self.load_image_lower_frame)

    def update(self):
        # width = 1280
        # height = 960
        width = 640
        height = 480
        dim = (width, height)
        # Get a frame from the video feed
        isTrue, frame = self.vid.getFrame()
        # Resize the camera window
        frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

        if isTrue:
            self.video = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.video, anchor=NW)
        self.detect_faces()
        # self.load_image_lower_frame()
        self.after(1, self.update)

    def detect_faces(self):
        counter = 0
        # while True:
        is_true, frame = self.vid.getFrame()
        grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # detection with face_recognition
        if is_true:
            if counter % 30 == 0:
                face_locations = face_recognition.face_locations(frame)
            counter +=1
        # detection with opencv
        # faces = self.faceCascade.detectMultiScale(
        #     frame,
        #     scaleFactor=1.2,
        #     minNeighbors=5,
        #     minSize=(20, 20)
        # )
        # Looping through the faces detected

        for face_location in face_locations:
            top, right, bottom, left = face_location
            face_image = frame[top:bottom, left:right]
            pil_image = Image.fromarray(face_image)
            # if face location already exists, then do not print it again

            pil_image.save(f'{faces_dir}/{top}.jpg')


    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()


class MyVideoCapture:
    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open This camera \n select another video source", video_source)
        # Get video source width and height
        # self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        # self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def getFrame(self):
        if self.vid.isOpened():
            is_true, frame = self.vid.read()
            if is_true:
                # if the current frame indeed exists, then convert it to RGB
                return is_true, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                return is_true, None
        else:
            return None

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


if __name__ == "__main__":
    app = App()
    app.start()

