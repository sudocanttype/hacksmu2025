import cv2
import os
from dotenv import load_dotenv

from propelauth_flask import init_auth, current_user
from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit

from flask_cors import CORS

import C1
#
#
load_dotenv(".env")
app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": ["http://localhost:5000", "http://your-other-domain.com"]}})
CORS(app)
socketio = SocketIO(app)

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
def index():
    return render_template('dashindex.html')
#
@app.route('/parking')
def parking():
    return render_template('parking.html')

@app.route('/dash')
def handicap():
    return render_template('handicap.html')

@app.route('/comprehensiveindex')
def comprehensiveindex():
    return render_template('comprehensiveindex.html')

@app.route('/toggleindex')
def togglestyles():
    return render_template('toggleindex.html')


@socketio.on('offer')
def handle_offer(offer):
    # Broadcast the received offer to all clients except the sender
    emit('offer', offer, broadcast=True, include_self=False)

@socketio.on('answer')
def handle_answer(answer):
    emit('answer', answer, broadcast=True, include_self=False)

@socketio.on('candidate')
def handle_candidate(candidate):
    emit('candidate', candidate, broadcast=True, include_self=False)


@app.route("/api/whoami")
@auth.require_user
def who_am_i():
    return {"user_id": current_user.user_id}

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
