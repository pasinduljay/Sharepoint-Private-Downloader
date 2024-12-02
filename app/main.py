from flask import Flask, render_template, request, Response
import subprocess
import os
import threading
import time

app = Flask(__name__)

# Directory paths
download_path = "/downloads"
incompleted_path = f"{download_path}/incompleted"
completed_path = f"{download_path}/completed"

# Ensure directories exist
os.makedirs(incompleted_path, exist_ok=True)
os.makedirs(completed_path, exist_ok=True)

# Dictionary to store incompleted downloads
downloads = {}

# Background download process
def download_file(url, filename):
    cmd = ["yt-dlp", url, "-o", f"{incompleted_path}/{filename}.%(ext)s", "--progress"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    for line in process.stdout:
        if 'ETA' in line or 'percent' in line:
            # Capture the progress percentage
            progress = line.strip().split(" ")[-1]
            downloads[filename]["progress"] = progress
        
        # Detect completion
        if "has already been downloaded" in line or "100%" in line:
            process.wait()
            downloads[filename]["status"] = "completed"
            os.rename(f"{incompleted_path}/{filename}.mp4", f"{completed_path}/{filename}.mp4")
            break

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        filename = request.form["filename"]
        downloads[filename] = {"status": "incompleted", "progress": "0%"}
        
        # Start a new thread to handle the download process in the background
        threading.Thread(target=download_file, args=(url, filename), daemon=True).start()
        return render_template("index.html", downloads=downloads, message="Download started!")
    
    return render_template("index.html", downloads=downloads)

@app.route("/progress/<filename>")
def progress(filename):
    # Return the current progress of the download as JSON
    return {"progress": downloads.get(filename, {}).get("progress", "0%")}

@app.route('/events')
def sse():
    def generate():
        while True:
            for filename, data in downloads.items():
                yield f"data: {filename} - {data['progress']}\n\n"
            time.sleep(1)
    return Response(generate(), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
