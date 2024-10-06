import cv2
from dotenv import load_dotenv

from propelauth_flask import init_auth, current_user
from flask import Flask, render_template, Response
#
#
app = Flask(__name__)
auth = init_auth("https://53997336.propelauthtest.com", os.environ.get("PROPEL_KEY"))
GPT_KEY = os.environ.get("GPT_KEY")

#
#
def generate_frames():
    camera = cv2.VideoCapture(0)

    while True:
        success, frame = camera.read()  # Read a frame from the webcam

        if not success:
            print("failed to get webcam")

            break
        else:
            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield the frame in the proper format for streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/fetch_c2_data')
def fetch_c2_data():
    return {
        'is_occupied': True,
        'car_license_plate': "PINK CAR",
        'is_spot_handicapped' : True,
        'has_handicapped_car': True,
        'objects_detected_in_spot': False,
        'objects_in_spot': []

    }


@app.route('/')
def welcome():
    return render_template('index.html')
#
@app.route("/api/whoami")
@auth.require_user
def who_am_i():
    return {"user_id": current_user.user_id}


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
