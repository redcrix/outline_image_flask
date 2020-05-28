
from flask import Flask, render_template, request, send_file,redirect,send_from_directory
import cv2
import time

time_str = time.strftime("%Y%m%d-%H%M%S")
cropping = False
x_start, y_start, x_end, y_end = 0, 0, 0, 0
app = Flask(__name__, template_folder='templates')


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():

    if request.method == 'POST':
        file1 = request.files['file1']
        file1.save('./images/' + time_str + '_flask.jpg')
        image = cv2.imread('./images/' + time_str + '_flask.jpg')
        oriImage = image.copy()

        resized = cv2.resize(image, (700, 529))

        def mouse_crop(event, x, y, flags, param):
            # grab references to the global variables
            global x_start, y_start, x_end, y_end, cropping

            # if the left mouse button was DOWN, start RECORDING
            # (x, y) coordinates and indicate that cropping is being
            if event == cv2.EVENT_LBUTTONDOWN:
                x_start, y_start, x_end, y_end = x, y, x, y
                cropping = True

            # Mouse is Moving
            elif event == cv2.EVENT_MOUSEMOVE:
                if cropping == True:
                    x_end, y_end = x, y

            # if the left mouse button was released
            elif event == cv2.EVENT_LBUTTONUP:
                # record the ending (x, y) coordinates
                x_end, y_end = x, y
                cropping = False  # cropping is finished

                refPoint = [(x_start, y_start), (x_end, y_end)]

                if len(refPoint) == 2:  # when two points were found
                    roi = resized[refPoint[0][1]:refPoint[1][1], refPoint[0][0]:refPoint[1][0]]
                    #cv2.imshow("Cropped", roi)
                    zap = cv2.imwrite("./images/" +time_str + "_crop.jpg", roi)

                    # convert to grayscale and apply median blur
                    img = cv2.imread("./images/" + time_str+ "_crop.jpg")
                    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                    img_blur = cv2.medianBlur(img_gray, 5)
                    img_edge = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 3.9)
                    cv2.imshow('outline image', img_edge)
                    cv2.imwrite('./images/' + time_str + '_outlined10.png', img_edge)

        cv2.namedWindow("image")
        cv2.setMouseCallback("image", mouse_crop)
        while True:

            i = resized.copy()

            if not cropping:
                cv2.imshow("image", resized)

            elif cropping:
                cv2.rectangle(i, (x_start, y_start), (x_end, y_end), (0, 0, 255), 2)
                cv2.imshow("image", i)

            k = cv2.waitKey(1)
            if k == 27:  # Esc key to stop
                break

            # close all open windows

        cv2.destroyAllWindows()
        return redirect('/download')

@app.route('/download_file')
def download_file():

    filename = './images/'
    p = time_str + '_outlined10.png'
    return send_from_directory(filename,p)

@app.route('/download')
def file_download():
    return render_template('download.html')

if __name__ == '__main__':
    app.run(debug = True)