from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import requests
import uuid
import os
import subprocess

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Merger Service is running!"}

@app.post("/merge")
def merge_media(data: dict):
    video_url = data.get("video_url")
    audio_url = data.get("audio_url")
    
    if not video_url or not audio_url:
        raise HTTPException(status_code=400, detail="Missing video_url or audio_url")
    
    unique_id = str(uuid.uuid4())[:8]
    video_path = f"/tmp/input_vid_{unique_id}.mp4"
    audio_path = f"/tmp/input_aud_{unique_id}.mp3"
    output_path = f"/tmp/output_{unique_id}.mp4"
    
    # تنزيل الفيديو والصوت
    with open(video_path, "wb") as f:
        f.write(requests.get(video_url).content)
    with open(audio_path, "wb") as f:
        f.write(requests.get(audio_url).content)
        
    # دمج باستخدام FFmpeg
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest", output_path
    ]
    subprocess.run(cmd, check=True)
    
    # تنظيف الملفات المؤقتة
    if os.path.exists(video_path): os.remove(video_path)
    if os.path.exists(audio_path): os.remove(audio_path)
    
    return FileResponse(output_path, media_type="video/mp4", filename="merged_video.mp4")
