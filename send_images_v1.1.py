import cv2
import requests
import time

# Server URL where the image will be sent
SERVER_URL = "http://192.168.217.197:5000/upload"

# Your phone's IP Camera URL (change this!)
PHONE_CAMERA_URL = "http://192.168.217.40:8080/video"  # Replace with actual IP from your phone app

# Open the phone camera stream
cap = cv2.VideoCapture(PHONE_CAMERA_URL)

if not cap.isOpened():
    print("Failed to open phone camera stream")
    exit()

# Set the interval time (in seconds)
INTERVAL = 10  # Change this to your preferred time limit

try:
    while True:
        # Capture a frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break

        # Generate a timestamped filename
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        image_filename = f"captured_image_{timestamp}.jpg"

        # Save the image locally
        cv2.imwrite(image_filename, frame)
        print(f"Image saved as '{image_filename}'")

        # Convert image to bytes and send to the server
        _, img_encoded = cv2.imencode('.jpg', frame)
        files = {'file': (image_filename, img_encoded.tobytes(), 'image/jpeg')}

        try:
            response = requests.post(SERVER_URL, files=files)
            print("Server Response:", response.text)
        except Exception as e:
            print("Error sending image:", e)

        # Wait for the specified interval before capturing again
        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("\nProcess interrupted by user")

finally:
    # Release the camera when done
    cap.release()
    print("Camera released")

