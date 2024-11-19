import os
import time
import subprocess
import shutil
import stable_whisper
from datetime import datetime

# Define the directories to loop through
directories = [
    "/data/application/editor/subs_audio",
    "/data/application/editor/audio",
    "/data/application/editor/new_text"
]

def process_audio_subtitles(subtitles_path, audio_path):
    # Paths
    base_videos_path = '/data/application/base_videos'
    final_videos_path = '/data/application/final_videos'

    # Get the first video from the base_videos directory
    base_videos = sorted(os.listdir(base_videos_path))
    if not base_videos:
        raise FileNotFoundError("No videos found in the base_videos directory")

    base_video = os.path.join(base_videos_path, base_videos[0])

    # Create the final output file path with today's date
    today_date = datetime.now().strftime('%Y-%m-%d')
    output_video = os.path.join(final_videos_path, f'{today_date}.mp4')
	
    # Run the ffmpeg command
    ffmpeg_command = [
        'ffmpeg',
        '-i', base_video,
        '-i', audio_path,
        '-i', subtitles_path,
        '-c:a', 'aac',
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-vf', f"subtitles={subtitles_path}:force_style='FontSize=24,Alignment=10'",
        output_video
    ]

    subprocess.run(ffmpeg_command, check=True)

    shutil.move(subtitles_path, "/data/application/editor/subs_audio/done")
    shutil.move(audio_path, "/data/application/editor/subs_audio/done")
	
    # Rename the base video to today's date
    new_base_video_path = os.path.join(base_videos_path, f'{today_date}.mp4')
    os.rename(base_video, new_base_video_path)

def process_audio(audio_path, audio_file_name):
    srt_file_name = audio_file_name.replace(".wav", ".srt")
	
    model = stable_whisper.load_model('base')
    result = model.transcribe(audio_path)
    result.to_srt_vtt(f"/data/application/subs_audio/{srt_file_name}", segment_level=False)
    shutil.copy2(audio_path, "data/application/editor/audio/done")
    shutil.move(audio_path, "/data/application/editor/subs_audio/")
	
def process_new_text(text_path, text_file_name):
    if text_file_name.startsWith('female_'):
        gender = "female"
    else:
        gender = "male"
		
    command = f"cat {filepath} | /app/tts/piper/piper --model /app/tts/voices/en_US-hfc_{gender}-medium.onnx --output_file /data/application/editor/audio/{filename}.wav"
	
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Piper executed successfully for file: {text_path}")
        shutil.move(text_path, "/data/application/editor/new_text/done")
    except subprocess.CalledProcessError as e:
        print(f"Error executing piper for file {text_path}: {e}")
        shutil.move(text_path, "/data/application/editor/new_text/err")
	
def check_directories():
    for directory in directories:
        if not os.path.isdir(directory):
            print(f"Directory {directory} does not exist")
            continue

        folder_name = os.path.basename(directory)
        subs_audio_path = "/data/application/editor/subs_audio"
        audio_path = "/data/application/editor/audio"
        new_text_path = "/data/application/editor/new_text"
        err_path = "/data/application/editor/subs_audio/err"

		# Check the folder_name and process files accordingly
        if folder_name == "subs_audio":
            for file in os.listdir(subs_audio_path):
                if file.endswith(".srt"):
                    srt_file = file
                    wav_file = srt_file.replace(".srt", ".wav")
                    srt_file_path = os.path.join(subs_audio_path, srt_file)
                    wav_file_path = os.path.join(subs_audio_path, wav_file)

                if os.path.exists(wav_file_path):
                    process_audio_subtitles(srt_file_path, wav_file_path)
                else:
                    shutil.move(srt_file_path, os.path.join(err_path, srt_file))
                break

        elif folder_name == "audio":
            for file in os.listdir(audio_path):
                if file.endswith(".wav"):
                    wav_file_path = os.path.join(audio_path, file)
                    process_audio(wav_file_path, file)
                break

        elif folder_name == "new_text":
            for file in os.listdir(new_text_path):
                if file.endswith(".txt"):
                    txt_file_path = os.path.join(new_text_path, file)
                    process_new_text(txt_file_path, file)
                break
					
if __name__ == "__main__":
    while True:
        check_directories()
        time.sleep(10)  # Pause for 10 seconds before checking again
