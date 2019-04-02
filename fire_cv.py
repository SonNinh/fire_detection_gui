import cv2
import numpy as np
import sys
import math



title_window = 'Linear Blend'
cv2.namedWindow(title_window)

def on_trackbar(val):
    pass

cv2.createTrackbar("Hmax", title_window , 0, 255, on_trackbar)
cv2.createTrackbar("Hmin", title_window , 0, 255, on_trackbar)
cv2.createTrackbar("Smax", title_window , 0, 255, on_trackbar)
cv2.createTrackbar("Smin", title_window , 0, 255, on_trackbar)
cv2.createTrackbar("Vmax", title_window , 0, 255, on_trackbar)
cv2.createTrackbar("Vmin", title_window , 0, 255, on_trackbar)

def detectFire(src): # src la anh
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

if len(sys.argv) == 2:

    # load video file from first command line argument

    video = cv2.VideoCapture(sys.argv[1]) # doc video tu duong dan

    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH)); # lay gia tri do rong video
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)) # do cao
    fps = video.get(cv2.CAP_PROP_FPS) # lay gia tri fps, frame per secoond, so khung tren 1 giay
    frame_time = round(1000/fps);
    last_white = 0
    ret, frame = video.read()
    pause = False
    sum_diff = 0
    loop = 0
    while True:
        if pause is False:
            ret, frame = video.read()
            if not ret:
                print("... end of video file reached");
                break

        cv2.imshow("origin", frame)

        Hmax = cv2.getTrackbarPos('Hmax',title_window)
        Hmin = cv2.getTrackbarPos('Hmin',title_window)
        Smax = cv2.getTrackbarPos('Smax',title_window)
        Smin = cv2.getTrackbarPos('Smin',title_window)
        Vmax = cv2.getTrackbarPos('Vmax',title_window)
        Vmin = cv2.getTrackbarPos('Vmin',title_window)

        # lower = [Hmin, Smin, Vmin]
        # upper = [Hmax, Smax, Vmax]
        lower = [6, 152, 138] # gioi han duoi mau lua trong he mau HSV
        upper = [48, 248, 255]


        blur = cv2.GaussianBlur(frame, (21, 21), 0) # loc nhieu
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV) # chuyen doi khong gian mau

        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")

        mask = cv2.inRange(hsv, lower, upper) #

        cv2.imshow("resdfd", mask) ## mask la anh trang den cua cac vung co mau lua
        mask, rect = detectFire(mask)

        detected_edges = cv2.Canny(mask, 100, 200, 3) ## lay bien anh

        n_white = np.sum(detected_edges == 255)
        diff_white = n_white - last_white
        last_white = n_white
        if diff_white > 0 and diff_white < 100:
            sum_diff += diff_white
        loop += 1

        if loop > 50:
            loop = 0
            if sum_diff > 150:
                print("fire")
            else:
                print("clear")
            print("fluctuation:", sum_diff)
            sum_diff = 0
        cv2.imshow("cen", detected_edges)
        # image display and key handling




        output = cv2.bitwise_and(frame, frame, mask=mask)
        x, y, w, h = rect
        cv2.rectangle(output,(x,y),(x+w,y+h),(0,255,0),2)
        cv2.line(output, (width-10, height-10), (width-10, height-10-int(n_white*height/5000)), (0,0,255), 5)
        cv2.imshow(title_window, output)


        if cv2.waitKey(10) == ord('x'):
            break
        elif cv2.waitKey(10) == ord('p'):
            pause = True
        elif cv2.waitKey(10) == ord('r'):
            pause = False



cv2.destroyAllWindows()
video.release()
