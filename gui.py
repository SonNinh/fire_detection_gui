
import numpy as np
import cv2
from tkinter import *
from PIL import Image, ImageTk
from datetime import datetime
from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep
from threading import Thread
import sys


image = np.zeros((320, 240, 3), np.uint8)
settingSpecs = {}
resolution = [320, 240]
end_thread = False

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


def closeButtonCllbck():
    global end_thread
    end_thread = True
    sleep(1)
    root.destroy()
    

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
gazInfo = Text(infoFrame1, height=5, width=25, font=20, yscrollcommand=True)
gazInfo.grid(row=0, column=0)

f = open('config/tempSensorText', 'r')
tempText = f.read()
f.close()
tempInfo = Text(infoFrame2, height=5, width=25, font=20, yscrollcommand=True)
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

resolutionButton = Button(buttonFrame, text='Close', command=closeButtonCllbck)
resolutionButton.grid(row=0, column=2)


def on_trackbar(val):
    pass


if len(sys.argv)>1 and sys.argv[1]== 'calib':
    title_window = 'Linear Blend'
    cv2.namedWindow(title_window)
    
    cv2.createTrackbar("Hmax", title_window, 0, 255, on_trackbar)
    cv2.createTrackbar("Hmin", title_window, 0, 255, on_trackbar)
    cv2.createTrackbar("Smax", title_window, 0, 255, on_trackbar)
    cv2.createTrackbar("Smin", title_window, 0, 255, on_trackbar)
    cv2.createTrackbar("Vmax", title_window, 0, 255, on_trackbar)
    cv2.createTrackbar("Vmin", title_window, 0, 255, on_trackbar)

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
    

def find_biggest_fire(src): # src la anh
    '''
    xac dinh mang mau co dien tich lon nhat trong anh trang den 'src'
    '''
    _, contours, _ = cv2.findContours(src, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE) ## contours la danh sach cac mang mau trang
    contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours] ## lay dien tich cac contour
    if len(contour_sizes) > 0:
        biggest_contour = max(contour_sizes, key=lambda x: x[0])[1] ## contour co dien toich lon nhat ## biggest_contour danh sach toa do cac pixel mau trang
        mask = np.zeros(src.shape, np.uint8)
        cv2.drawContours(mask, [biggest_contour], -1, 255, -1) ## chuyen tu biggest_contour qua anh mask
        rect = cv2.boundingRect(biggest_contour)
        return mask, rect
    else:
        return src, [0,0,0,0]
    
    
    
def thread_camera(threadname):
    global image
    cap = PiCamera()
    cap.resolution = (320, 240)
    cap.framerate = 15
    rawCapture = PiRGBArray(cap, size=(320, 240))
    sleep(0.1)
    
    last_white = 0
    sum_diff = 0
    loop = 0
    lower = [0, 0, 165]
    upper = [26, 37, 255]
    
    for frame in cap.capture_continuous(rawCapture, format='bgr', use_video_port=True):
        
        # lay gia tri tu trackbar
        if len(sys.argv)>1 and sys.argv[1]== 'calib':
            Hmax = cv2.getTrackbarPos('Hmax', title_window)
            Hmin = cv2.getTrackbarPos('Hmin', title_window)
            Smax = cv2.getTrackbarPos('Smax', title_window)
            Smin = cv2.getTrackbarPos('Smin', title_window)
            Vmax = cv2.getTrackbarPos('Vmax', title_window)
            Vmin = cv2.getTrackbarPos('Vmin', title_window)
            # gioi han tren duoi mau lua trong he mau HSV
            lower = [Hmin, Smin, Vmin]
            upper = [Hmax, Smax, Vmax]
        
        # chuyen doi khong gian mau
        hsv = cv2.cvtColor(frame.array, cv2.COLOR_BGR2HSV)
        
        
        # chuyen doi lower upper tu dang list sang mang numpy
        lower_np = np.array(lower, dtype="uint8")
        upper_np = np.array(upper, dtype="uint8")
        
        # lay nhung diem anh co gia tri mau nam trong khoang (lower, upper)
        mask = cv2.inRange(hsv, lower_np, upper_np)
        
        if len(sys.argv)>1 and sys.argv[1]== 'calib':
            cv2.imshow(title_window, mask)
            
        #cv2.imshow("resdfd", mask) ## mask la anh trang den cua cac vung co mau lua
        mask, rect = find_biggest_fire(mask)

        detected_edges = cv2.Canny(mask, 100, 200, 3) ## lay bien anh
        
        # tinh chu vi cua 'detected_edges'
        n_white = np.sum(detected_edges == 255)
        
        # tinh do thay doi chu vi cua 'detected_edges'
        diff_white = n_white - last_white
        last_white = n_white
        
        # tinh tong do thay doi chu vi qua 30 khung hinh
        if diff_white > 0 and diff_white < 100:
            sum_diff += diff_white
        loop += 1

        if loop > 30:
            loop = 0
            if sum_diff > 100:
                print("fire")
            else:
                print("clear")
            print("fluctuation:", sum_diff)
            sum_diff = 0
        # cv2.imshow("cen", detected_edges)
        # image display and key handling

#        output = cv2.bitwise_and(frame.array, frame.array, mask=mask)
        
        # ve khung bao quanh vung 'nghi ngo co lua' lon nhat
        x, y, w, h = rect
        cv2.rectangle(frame.array,(x,y),(x+w,y+h),(0,255,0),2)
        
        # cv2.imshow(title_window, output)
        
        image = frame.array
        rawCapture.truncate(0)
        
        # nhan 'q' de close camera
        key = cv2.waitKey(1) & 0xFF
        if end_thread == True:
            break


    
# function for video streaming
def video_stream():
    gazValue, tempVallue = readSensor()
    showInfo(gazValue, tempVallue)
    
    cv2image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
    newimage = cv2.resize(cv2image, (resolution[0], resolution[1]))
    img = Image.fromarray(newimage)
    imgtk = ImageTk.PhotoImage(image=img)
    labelVideo.imgtk = imgtk
    labelVideo.configure(image=imgtk)
    labelVideo.after(1, video_stream)
    

thread1 = Thread(target=thread_camera, args=('Thread-1', ))
thread1.start()

video_stream()
root.mainloop()

