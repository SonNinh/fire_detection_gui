#!/usr/bin/python3


import cv2
from tkinter import *
from PIL import Image, ImageTk
from datetime import datetime


settingSpecs = {}
resolution = [320, 240]
def configButtonCllbck():
    global settingSpecs

    f = open('config/settings', 'r')
    content = f.readlines()
    f.close()
    for line in content:
        splitline = line.split('=')
        settingSpecs[splitline[0]] = int(splitline[1][:-1])


def resButtonCllbck():
    global resolution
    if resolution == [320, 240]:
        resolution = [640, 480]
    else:
        resolution = [320, 240]


configButtonCllbck()

root = Tk()
'''
Create a frame contaning video streaming
'''
videoFrame = Frame(root, bg="white")
videoFrame.pack()

labelVideo = Label(videoFrame)
labelVideo.pack()

'''
Create a frame contaning infomation
'''
infoFrame = Frame(root, relief=RAISED, borderwidth=2)
infoFrame.pack(fill=BOTH, expand=True)

infoFrame1 = Frame(infoFrame, relief=RAISED, borderwidth=2)
infoFrame1.pack(fill=BOTH, expand=True, side=LEFT)

infoFrame2 = Frame(infoFrame, relief=RAISED, borderwidth=2)
infoFrame2.pack(fill=BOTH, expand=True, side=RIGHT)

f = open('config/gazSensorText', 'r')
gazText = f.read()
f.close()
gazInfo = Text(infoFrame1, height=10, width=25, font=20, yscrollcommand=True)
gazInfo.grid(row=0, column=0)

f = open('config/tempSensorText', 'r')
tempText = f.read()
f.close()
tempInfo = Text(infoFrame2, height=10, width=25, font=20, yscrollcommand=True)
tempInfo.grid(row=0, column=0)

'''
Create a frame contaning button
'''
buttonFrame = Frame(root, relief=RAISED, borderwidth=2)
buttonFrame.pack(fill=BOTH, expand=True)

configButton = Button(buttonFrame, text='Update', command=configButtonCllbck)
configButton.grid(row=0, column=0)

resolutionButton = Button(buttonFrame, text='Resolution', command=resButtonCllbck)
resolutionButton.grid(row=0, column=1)

# Capture from camera
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

def showInfo(gazValue, tempVallue):
    try:
        # default ref temperature vallue
        temp = tempText.format(settingSpecs['tempRef'], tempVallue)
        tempInfo.delete(1.0, END)
        tempInfo.insert(1.0, temp)
        tempInfo.grid(row=0, column=0)
        tempInfo.tag_add("temptag", "1.0", END)
        if tempVallue >= settingSpecs['tempRef']:
            tempInfo.tag_config("temptag", background="red", foreground="blue")
        else:
            tempInfo.tag_config("temptag", background="white", foreground="black")
    except Exception as e:
        print(e)

    try:
        # default ref gaz vallue
        gaz = gazText.format(settingSpecs['gazRef'], gazValue)
        gazInfo.delete(1.0, END)
        gazInfo.insert(1.0, gaz)
        gazInfo.grid(row=0, column=0)
        gazInfo.tag_add("temptag", "1.0", END)
        if gazValue >= settingSpecs['gazRef']:
            gazInfo.tag_config("temptag", background="red", foreground="blue")
        else:
            gazInfo.tag_config("temptag", background="white", foreground="black")
    except Exception as e:
        print(e)


def readSensor():
    return datetime.now().second, datetime.now().second


# function for video streaming
def video_stream():
    gazValue, tempVallue = readSensor()
    showInfo(gazValue, tempVallue)
    _, frame = cap.read()
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    newimage = cv2.resize(cv2image, (resolution[0], resolution[1]))
    img = Image.fromarray(newimage)
    imgtk = ImageTk.PhotoImage(image=img)
    labelVideo.imgtk = imgtk
    labelVideo.configure(image=imgtk)
    labelVideo.after(1, video_stream)


video_stream()
root.mainloop()
