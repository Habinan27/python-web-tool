from flask import Flask, render_template, request, send_file
from PIL import Image
from PyPDF2 import PdfMerger

from moviepy import VideoFileClip
from moviepy import concatenate_videoclips

import qrcode
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# HOME
@app.route("/")
def home():
    return render_template("index.html")


# IMAGE PAGE
@app.route("/image")
def image_page():
    return render_template("image.html")


# PDF PAGE
@app.route("/pdf")
def pdf_page():
    return render_template("pdf.html")


# QR PAGE
@app.route("/qr")
def qr_page():
    return render_template("qr.html")


# VIDEO PAGE
@app.route("/video")
def video_page():
    return render_template("video.html")


# IMAGE CONVERTER
@app.route("/convert-image", methods=["POST"])
def convert_image():

    file = request.files["image"]
    format_type = request.form["format"]

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    img = Image.open(input_path)

    output_filename = f"converted.{format_type}"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    img.save(output_path)

    return send_file(output_path, as_attachment=True)


# PDF MERGE
@app.route("/merge-pdf", methods=["POST"])
def merge_pdf():

    files = request.files.getlist("pdfs")

    merger = PdfMerger()

    for file in files:

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        merger.append(path)

    output_path = os.path.join(OUTPUT_FOLDER, "merged.pdf")

    merger.write(output_path)
    merger.close()

    return send_file(output_path, as_attachment=True)


# QR GENERATOR
@app.route("/generate-qr", methods=["POST"])
def generate_qr():

    text = request.form["text"]

    qr = qrcode.make(text)

    output_path = os.path.join(OUTPUT_FOLDER, "qr.png")

    qr.save(output_path)

    return send_file(output_path, as_attachment=True)


# VIDEO MERGE
@app.route("/merge-video", methods=["POST"])
def merge_video():

    files = request.files.getlist("videos")

    clips = []

    for file in files:

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        clip = VideoFileClip(path)

        clips.append(clip)

    final = concatenate_videoclips(clips)

    output_path = os.path.join(OUTPUT_FOLDER, "final_video.mp4")

    final.write_videofile(output_path)

    return send_file(output_path, as_attachment=True)

@app.route("/audio")
def audio_page():
    return render_template("audio.html")

@app.route("/convert-audio", methods=["POST"])
def convert_audio():

    file = request.files["video"]

    unique_id = str(uuid.uuid4())

    video_path = os.path.join(
        UPLOAD_FOLDER,
        unique_id + "_" + file.filename
    )

    file.save(video_path)

    output_path = os.path.join(
        OUTPUT_FOLDER,
        unique_id + ".mp3"
    )

    video = VideoFileClip(video_path)

    audio = video.audio

    audio.write_audiofile(output_path)

    audio.close()
    video.close()

    return send_file(
        output_path,
        as_attachment=True,
        download_name="converted.mp3"
    )

if __name__ == "__main__":
    app.run(debug=True)