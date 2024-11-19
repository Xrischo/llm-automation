import os
import random
import time
import subprocess
import shutil
import stable_whisper
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from pydub import AudioSegment


# Define the directories to loop through
MAIN_DIRECTORY = "/home/editor/applications/"

APPLICATIONS = [
    "aita"
    # all other applications
]

STEPS = [
    "new_text",
    "audio",
    "subs_audio"
]

CURRENT_APPLICATION_DIRECTORY = os.path.join(MAIN_DIRECTORY, APPLICATIONS[0])

PIPER_DIRECTORY = "/home/editor/control_plane/piper/piper"
VOICES_DIRECTORY = "/home/editor/control_plane/voices"

ITERATIONS_PER_APPLICATION = 33

def create_folder(dst_folder):
    # If the folder does not exist, create it
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)
        return dst_folder
    
    # If the folder exists, find a unique name
    counter = 1
    base_folder = dst_folder
    while os.path.exists(dst_folder):
        dst_folder = f"{base_folder}_{counter}"
        counter += 1
    
    # Create the unique folder
    os.makedirs(dst_folder)
    return dst_folder

def move_file(source, destination):
    try:
        if os.path.isfile(source):
            # Move a single file
            dest_file = os.path.join(destination, os.path.basename(source))
            if os.path.exists(dest_file):
                os.remove(dest_file)
            shutil.move(source, dest_file)
            print(f"File '{source}' moved to '{destination}'")
        elif os.path.isdir(source):
            # Move an entire directory
            dest_folder = os.path.join(destination, os.path.basename(source))
            if os.path.exists(dest_folder):
                shutil.rmtree(dest_folder)
            shutil.move(source, dest_folder)
            print(f"Folder '{source}' moved to '{destination}'")
        else:
            print(f"'{source}' is not a valid file or folder.")
    except Exception as e:
        print(f"Error moving '{source}' to '{destination}': {e}")

def get_audio_length(audio_file):
    audio = AudioSegment.from_file(audio_file)
    return len(audio) / 1000  # Length in seconds

def get_video_length(video_file):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
         "-of", "default=noprint_wrappers=1:nokey=1", video_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return float(result.stdout)

def process_audio_subtitles(subtitles_path, audio_path, audio_title_path, thumbnail_path):
    # Paths
    base_videos_path = os.path.join(CURRENT_APPLICATION_DIRECTORY, "base_videos")
    final_videos_path = os.path.join(CURRENT_APPLICATION_DIRECTORY, "final_videos")

    audio_length = get_audio_length(audio_path)
    audio_title_duration = get_audio_length(audio_title_path)
    print(f"Audio length: {audio_length} seconds")

    video_files = [f for f in os.listdir(base_videos_path) if f.endswith(('.mp4', '.mkv', '.avi'))]
    eligible_videos = []
    
    for video in video_files:
        video_path = os.path.join(base_videos_path, video)
        video_length = get_video_length(video_path)
        if video_length > audio_length:
            eligible_videos.append((video, video_length))
    
    if not eligible_videos:
        print("No eligible videos found.")
        return
    
    # Randomly select one eligible video
    selected_video, selected_video_length = random.choice(eligible_videos)
    print(f"Selected video: {selected_video} with length {selected_video_length} seconds")
    
    # Calculate random start and end points
    max_start_time = selected_video_length - audio_length
    start_time = random.uniform(0, max_start_time)
    end_time = start_time + audio_length
    
    base_video = os.path.join(base_videos_path, selected_video)

    # Create the final output file path with today's date
    today_date = datetime.now().strftime('%Y-%m-%d-%m-%h-%s')
    output_video = os.path.join(final_videos_path, f'{today_date}.mp4')
	
    # Run the ffmpeg command
    ffmpeg_command = [
        'ffmpeg',
        '-ss', str(start_time), # Start time
        '-to', str(end_time),   # End time
        '-i', base_video,       # Base video input
        '-i', audio_path,       # Main audio input
        '-i', audio_title_path, # Title audio input (for duration reference)
        '-i', thumbnail_path,   # Thumbnail image input
        '-filter_complex', (
            '[0:v] subtitles=' + subtitles_path + ':force_style=' + "'FontName=Outfit,FontFile=/usr/share/fonts/Outfit-VariableFont_wght.ttf,FontSize=18,Bold=1,Outline=1,OutlineColour=&H80000000,Shadow=1,ShadowColour=&H80000000,Alignment=10' [subbed];"  # Add subtitles to the overlayed video
            f'[subbed][3:v] overlay=x=(W-w)/2:y=(H-h)/2:enable=\'between(t,0,{audio_title_duration})\''  # Center the thumbnail and limit its duration
        ),
        '-c:a', 'aac',          # Audio codec
        '-map', '0:v:0',        # Map the base video
        '-map', '1:a:0',        # Map the main audio
        '-b:v', '5M',           # Set video bitrate to 5 Mbps for high quality
        output_video
    ]


    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing merge or ffmpeg: {e}")
        return
	
    # Rename the base video to today's date
    new_base_video_path = os.path.join(base_videos_path, f'{today_date}.mp4')
    os.rename(base_video, new_base_video_path)

def process_audio(audio_path, workfolder_name):
    subtitles_save_to = os.path.join(CURRENT_APPLICATION_DIRECTORY, "subs_audio", workfolder_name, "subtitles.ass")

    model = stable_whisper.load_model('base')
    result = model.transcribe(audio_path, suppress_silence=False)
    result.to_ass(subtitles_save_to, segment_level=False, highlight_color='ffffff', font='Outfit', font_size=16, Name='Default', Alignment=10, Outline=1, OutlineColour='000000')

    shutil.copy2(audio_path, os.path.join(CURRENT_APPLICATION_DIRECTORY, "subs_audio", workfolder_name, 'body.wav'))
	
def process_new_text(body_text_path, title_text_path, workfolder_name):
    speaker_number = 0
    if workfolder_name.startswith('female_'):
        speaker_number = 141
    else:
        speaker_number = 613
		
    audio_folder = create_folder(os.path.join(CURRENT_APPLICATION_DIRECTORY, 'audio', workfolder_name))
    subs_audio_folder = create_folder(os.path.join(CURRENT_APPLICATION_DIRECTORY, 'subs_audio', workfolder_name))

    command1 = f"cat {title_text_path} <(printf '\n\n') {body_text_path} | {PIPER_DIRECTORY} --model {os.path.join(VOICES_DIRECTORY, 'en_US-libritts_r-medium.onnx')} --speaker {speaker_number} --length_scale 1.2 --sentence_silence 0.4 --output_file {os.path.join(audio_folder, 'body.wav')}"
    command2 = f"cat {title_text_path} | {PIPER_DIRECTORY} --model {os.path.join(VOICES_DIRECTORY, 'en_US-libritts_r-medium.onnx')} --speaker {speaker_number} --length_scale 1.2 --sentence_silence 0.4 --output_file {os.path.join(subs_audio_folder, 'title.wav')}"

    subprocess.run(command1, shell=True, check=True)
    print(f"Piper executed successfully for TITLE + BODY")

    subprocess.run(command2, shell=True, check=True)
    print(f"Piper executed successfully for TITLE only")

    # Read the title to create thumbnail
    title_content = ''
    with open(title_text_path, 'r') as f:
        title_content = f.read()

    thumbnail_save_to = os.path.join(subs_audio_folder, 'thumbnail.png')

    # Create the thumbnail
    create_thumbnail(title_content, thumbnail_save_to)
    print(f"LOG: Thumbnail created and saved to: {thumbnail_save_to}")

def check_work_folders():
    print(f"Checking work folders in current application directory: {CURRENT_APPLICATION_DIRECTORY}")
    work_folders = list(map(lambda x: os.path.join(CURRENT_APPLICATION_DIRECTORY, x), STEPS))
    print(f"Work folders: {work_folders}")
    for work_folder in work_folders:
        if not os.path.isdir(work_folder):
            print(f"Directory {work_folder} does not exist")
            continue

        folder_name = os.path.basename(work_folder)
        subs_audio_path = os.path.join(CURRENT_APPLICATION_DIRECTORY, "subs_audio")
        audio_path = os.path.join(CURRENT_APPLICATION_DIRECTORY, "audio")
        new_text_path = os.path.join(CURRENT_APPLICATION_DIRECTORY, "new_text")

        done_folder_path = os.path.join(CURRENT_APPLICATION_DIRECTORY, folder_name, 'done')
        err_folder_path = os.path.join(CURRENT_APPLICATION_DIRECTORY, folder_name, 'err')

		# Check the folder_name and process files accordingly
        if folder_name == "subs_audio":
            for folder in os.listdir(subs_audio_path):

                folder_path = os.path.join(subs_audio_path, folder)
                if os.path.isdir(folder_path) and folder not in ['done', 'err']:
                    print(f"LOG: Found work folder in /subs_audio: {folder}")
                    subtitles_path = os.path.join(folder_path, 'subtitles.ass')
                    audio_body_path = os.path.join(folder_path, 'body.wav')
                    audio_title_path = os.path.join(folder_path, 'title.wav')
                    thumbnail_path = os.path.join(folder_path, 'thumbnail.png')

                    if not os.path.exists(subtitles_path) or not os.path.exists(audio_body_path) or not os.path.exists(audio_title_path) or not os.path.exists(thumbnail_path):
                        print(f"ERROR: Not all necessary files found in {folder_path}. Moving to: {err_folder_path}")
                        move_file(folder_path, err_folder_path)
                        continue
                    
                    try:
                        process_audio_subtitles(subtitles_path, audio_body_path, audio_title_path, thumbnail_path)
                        move_file(folder_path, done_folder_path)
                        print('------------------------------------------------------ VIDEO CREATED ------------------------------------------------------')
                    except Exception as e:
                        print(f"ERROR: Error processing audio and subtitles in {folder_path}: {e}")
                        move_file(folder_path, err_folder_path)

        elif folder_name == "audio":
            for folder in os.listdir(audio_path):

                folder_path = os.path.join(audio_path, folder)
                if os.path.isdir(folder_path) and folder not in ['done', 'err']:
                    print(f"LOG: Found new work folder in /audio: {folder}")
                    audio_body_path = os.path.join(audio_path, folder, 'body.wav')

                    if not os.path.exists(audio_body_path):
                        print(f"ERROR: Body .WAV file not found in: {folder}. Moving to: {err_folder_path}")
                        move_file(folder_path, err_folder_path)

                    try:
                        process_audio(audio_body_path, folder)
                        move_file(folder_path, done_folder_path)
                    except Exception as e:
                        print(f"ERROR: Error processing audio in {folder_path}: {e}. Moving to: {err_folder_path}")
                        move_file(folder_path, err_folder_path)

        elif folder_name == "new_text":
            for folder in os.listdir(new_text_path):

                folder_path = os.path.join(new_text_path, folder)
                if os.path.isdir(folder_path) and folder not in ['done', 'err']:
                    print(f"LOG: Found new work folder in /new_text: {folder}")

                    body_path_txt = os.path.join(folder_path, 'body.txt')
                    title_path_txt = os.path.join(folder_path, 'title.txt')

                    if not os.path.exists(title_path_txt) or not os.path.exists(body_path_txt):
                        print(f"ERROR: Not all necessary files found in {folder_path}. Moving to: {err_folder_path}")
                        move_file(folder_path, err_folder_path)
                        continue

                    # TTS the body and the title
                    try:
                        process_new_text(body_path_txt, title_path_txt, folder)
                        move_file(folder_path, done_folder_path)
                    except Exception as e:
                        print(f"ERROR: Error processing new text in {folder_path}: {e}")
                        move_file(folder_path, err_folder_path)


def create_thumbnail(title, save_to):
    template_path = '/home/editor/control_plane/templates/template.png'

    listOfRandomUsernames = [
        "PixelPioneer89",
        "QuantumQuokka",
        "NimbusNerd",
        "SynthwaveSamurai",
        "GalacticGopher",
        "CryptoCactus",
        "LunarLynx",
        "VelvetVoyager",
        "StardustSpectre",
        "EchoEnigma",
        "NebulaNomad",
        "CosmicCorsair",
        "AstralArtisan",
        "PhotonPhoenix",
        "QuantumQuokka",
        "StellarScribe",
        "PlasmaPenguin",
        "ZephyrZebra",
        "TurboTamarin",
        "SpectralShark",
        "MysticMarauder",
        "PixelPaladin",
        "TurboToad",
        "PhotonPanda",
        "SolarSailor",
        "FrostyFalcon",
        "NebulaNinja",
        "GalacticGazelle",
        "CosmicCrusader",
        "QuantumQuestor",
    ]

    randomUsername = random.choice(listOfRandomUsernames)

    avatars_file_path = "/home/editor/control_plane/templates/avatars"
    avatars = os.listdir(avatars_file_path)

    randomAvatar = os.path.join(avatars_file_path, random.choice(avatars))

    font_file_path = "/home/editor/control_plane/templates/Outfit-Bold.ttf"

    def draw_text(draw, text, position, font, max_width):
        # Initialize variables
        lines = []
        words = text.split()
        current_line = []
        current_line_width = 0

        # Iterate over words to split text into lines
        for word in words:
            # Calculate the width of the current line with the new word
            word_size = draw.textbbox((0, 0), word, font=font)
            word_width = word_size[2] - word_size[0]
            word_height = word_size[3] - word_size[1]
            space_size = draw.textbbox((0, 0), ' ', font=font)
            space_width = space_size[2] - space_size[0]

            new_line_width = current_line_width + word_width + (space_width if current_line else 0)

            # If the current line + word is within the max width, add the word to the line
            if new_line_width <= max_width:
                current_line.append(word)
                current_line_width = new_line_width
            else:
                # Otherwise, finalize the current line and start a new one
                lines.append(' '.join(current_line))
                current_line = [word]
                current_line_width = word_width

        # Append the last line
        if current_line:
            lines.append(' '.join(current_line))

        # Draw the lines on the image
        y = position[1]
        for line in lines:
            draw.text((position[0], y), line, font=font, fill=(0, 0, 0))
            y += word_height + 10

    # Load the original image
    base_image = Image.open(template_path)

    # Load the overlay image
    overlay_image = Image.open(randomAvatar).convert('RGBA')

    # Resize the overlay image if necessary
    overlay_size = (80, 80)  # Resize to 100x100 pixels
    overlay_image = overlay_image.resize(overlay_size)

    # Create a circular mask
    mask = Image.new('L', overlay_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, overlay_size[0], overlay_size[1]), fill=255)

    # Apply the circular mask to the overlay image
    overlay_image.putalpha(mask)

    # Initialize the drawing context for the base image
    draw = ImageDraw.Draw(base_image)

    # Define the font and size
    font = ImageFont.truetype(font_file_path, 36)
    font_body = ImageFont.truetype(font_file_path, 44)

    # Define text and positions
    position_username = (120, 20)
    position_title = (30, base_image.height - 180)

    # Add text to the image with black color
    draw.text(position_username, randomUsername, (0, 0, 0), font=font)
    draw_text(draw, title, position_title, font_body, base_image.width - 20)

    # Define the position for the overlay image
    overlay_position = (30, 20)  # You can change this to the desired position

    # Paste the circular overlay image on top of the base image
    base_image.paste(overlay_image, overlay_position, overlay_image)

    # Save the modified image
    base_image.save(save_to)

					
if __name__ == "__main__":
    application_index = 0
    counter = 0
    CURRENT_APPLICATION_DIRECTORY = os.path.join(MAIN_DIRECTORY, APPLICATIONS[application_index])
    while True:
        print(f"Running loop, counter: {counter}")
        check_work_folders()
        counter += 1
        if (counter == ITERATIONS_PER_APPLICATION):
            counter = 0
            application_index += 1
            if (application_index == len(APPLICATIONS)):
                application_index = 0
            CURRENT_APPLICATION_DIRECTORY = os.path.join(MAIN_DIRECTORY, APPLICATIONS[application_index])

        time.sleep(10)  # Pause for 10 seconds before checking again
