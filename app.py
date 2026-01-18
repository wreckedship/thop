from flask import Flask, request, jsonify, render_template
import os
import cv2
import pytesseract
# Initialize Flask app
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(image_path, lang="eng"):
    """ Extracts and cleans text from an image using Tesseract OCR """
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    raw_text = pytesseract.image_to_string(gray, lang=lang).strip()
    print(f"[DEBUG] Raw Extracted Text:\n{raw_text}")

    # Remove line breaks and multiple spaces
    clean_text = " ".join(raw_text.replace("\n", " ").split())
    print(f"[DEBUG] Cleaned Text:\n{clean_text}")

    return clean_text


def text_to_speech(text, lang="en"):
    """ Converts text to speech and plays as a WAV file """
    os.system(f'espeak-ng "{text}"')

def generate_no_text_audio():
    """ Generate an WAV file that says 'No new text detected' """
    audio_path = os.path.join(UPLOAD_FOLDER, "no_new_text.wav")
    if not os.path.exists(audio_path):
        os.system(f'espeak-ng "No new text detected. Please try again." -w {audio_path}')
    return "no_new_text.wav"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type or no file selected"}), 400

    #Added this file extension so other extensions are not saved as jpg's
    ext = file.filename.rsplit('.', 1)[1].lower()
    filepath = os.path.join(UPLOAD_FOLDER, f"latest.{ext}")
    file.save(filepath)


    text = extract_text(filepath)
    if not text:
        audio_file = generate_no_text_audio()
        audio_path = os.path.join(UPLOAD_FOLDER, audio_file)
        os.system(f"aplay {audio_path}")
        return jsonify({"status": "played"})
    else:
        text_to_speech(text)

    return jsonify({"status": "played"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
