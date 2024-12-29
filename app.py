from venv import logger
from flask import Flask, render_template, Response, request, jsonify
import cv2
from ultralytics import YOLO
import json
from datetime import datetime
import logging
import os
from contextlib import redirect_stdout

app = Flask(__name__)

# Initialize logging for system activities and errors
logging.basicConfig(
    filename="Output/system_log.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize dictionary to store events
events = []

# Initialize JSON file to store events
event_log_file = "Output/events_log.json"

# Check if event log file exists; if not, create an empty JSON list
if not os.path.exists(event_log_file):
    with open(event_log_file, 'w') as file:
        json.dump([], file)

# Ensure images folder exists
images_folder = "Output/captured_images"
os.makedirs(images_folder, exist_ok=True)


# Function to log an event
def log_event(event_type, image_filename):
    try:
        event = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event_type": event_type,
            "image_filename": image_filename
        }
        events.append(event)
        logging.info(f"Event logged: {event_type} with file {image_filename}")
    except Exception as e:
        logging.error(f"Error: Logging event: {e}")


# Save all events to JSON file
def save_events_to_file():
    try:
        with open(event_log_file, 'w') as file:
            json.dump(events, file, indent=4)
        logging.info(f"Events saved to {event_log_file}.")
    except Exception as e:
        logging.error(f"Error: Saving events to file: {e}")


# Global variables for camera URL and video capture
camera_url = None
cap = None

# Load YOLOv5 model
try:
    # Prevent libraries or code blocks that produce unnecessary console output from cluttering the terminal.
    with open(os.devnull, 'w') as fnull:
        with redirect_stdout(fnull):
            pass

    model = YOLO('sources/yolov5-7.0/models/yolov5su.pt')
    logging.info("YOLOv5 model loaded successfully.")
except Exception as e:
    logging.error(f"Error: Loading YOLOv5 model: {e}")
    raise


# Route for the main page
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template('index.html')


# Route to provide the camera setup and start security system
@app.route("/start", methods=['POST', 'GET'])
def start_security_system():
    if request.method == 'POST' or request.method == 'GET':
        global camera_url
        try:
            camera_type = request.form.get("value-radio")  # Get the selected camera type

            if camera_type == "local":
                camera_url = 0  # Use the local webcam
            elif camera_type == "http":
                camera_url = request.form.get("camera_url")  # Use the HTTP camera URL
                if not camera_url:
                    return jsonify({"video_started": False, "error": "Camera URL is required for HTTP camera"}), 400

            # Successful camera setup
            return jsonify({"video_started": True})
        except Exception as e:
            logging.error(f"Error in index route: {e}")
            return jsonify({"video_started": False, "error": str(e)}), 500


# Route to provide the video feed with YOLO integration
@app.route("/video_feed")
def video_feed():
    global camera_url, cap
    if camera_url is None:
        logging.error(f"Error Camera URL is required")

    # Open the camera feed
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        logging.error(f"Error Unable to access the camera feed.")

    def generate():
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            try:
                # Perform object detection
                results = model(frame)

                for result in results:
                    annotated_frame = result.plot()

                    # Access bounding box data
                    for box in result.boxes:
                        xyxy = box.xyxy.cpu().numpy()
                        cls = int(box.cls.cpu().numpy())
                        confidence = float(box.conf.cpu().numpy())

                        object_detected = result.names[cls]
                        image_filename = f"detected_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                        image_filepath = os.path.join(images_folder, image_filename)

                        # Save image and log event
                        try:
                            cv2.imwrite(image_filepath, frame)
                            log_event(event_type=f"Detected {object_detected}", image_filename=image_filepath)
                        except Exception as e:
                            logging.error(f"Error saving image or logging event: {e}")

                # Encode frame for streaming
                _, buffer = cv2.imencode(".jpg", annotated_frame)
                frame = buffer.tobytes()
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

            except Exception as e:
                logging.error(f"Error during object detection: {e}")
                break

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


# Route to stop the camera feed
@app.route("/stop", methods=["POST"])
def stop():
    global cap
    if cap and cap.isOpened():
        cap.release()
    save_events_to_file()
    return render_template("index.html", camera_url=None, video_started=False)


if __name__ == "__main__":
    print("\n========================================", flush=True)
    print("The app is running!", flush=True)
    logger.info("The app is running")
    print("Access it at: http://127.0.0.1:5000", flush=True)
    print("========================================\n", flush=True)
    app.run(host="127.0.0.1", port=5000, debug=True)
