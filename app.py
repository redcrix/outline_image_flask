import cv2
from flask import Flask, json, request
import time
cropping = False
x_start, y_start, x_end, y_end = 0, 0, 0, 0
app = Flask(__name__)


@app.route("/outline", methods=['POST', 'GET'])
def outline():
    time_str = time.strftime("%Y%m%d-%H%M%S")
    if 'image1' not in request.files:
        return json.dumps({"message": 'No Picture found! ', "success": False})
    image1 = request.files['image1']
    image1.save('./images/' + time_str + 'original.jpg')

    image = cv2.imread("./images/" + time_str + "original.jpg")
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
                cv2.imshow("Cropped", roi)
                zap = cv2.imwrite("./images/" + time_str + "crop.jpg", roi)

                # convert to grayscale and apply median blur
                img = cv2.imread("./images/" + time_str + "crop.jpg")
                img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                img_blur = cv2.medianBlur(img_gray, 7)
                img_edge = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 7, 3.5)
                cv2.imshow('pencil sketch2', img_edge)
                cv2.imwrite('./images/' + time_str + 'outlined.jpg', img_edge)

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
        if k == 27:                          # Esc key to stop
            break

        # close all open windows

    cv2.destroyAllWindows()
    return json.dumps({"crop_pic": time_str + 'outlined.jpg'})


if __name__ == "__main__":
    app.run(debug=True)
