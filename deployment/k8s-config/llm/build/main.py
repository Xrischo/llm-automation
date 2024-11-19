import os
import time
import subprocess
import shutil
import glob
import ollama
from datetime import datetime

directories_filepath="/data/application/gen-directories.txt"

def increment_last_digit(filepath):
    base, ext = os.path.splitext(filepath)
    if base[-1].isdigit():
        base = base[:-1] + str(int(base[-1]) + 1)
    else:
        base += "1"
    return base + ext

def process_file(generated_text_filepath, prompt_filepath, directory, folder_name, model_name):
    print(f"Processing file: {generated_text_filepath} WITH {prompt_filepath} INSIDE {folder_name}")
    try:
        # Read the contents of the prompt file
        with open(prompt_filepath, 'r') as prompt_file:
            prompt_contents = prompt_file.read()

        # Read the contents of the text file to replace the placeholder in the prompt
        with open(generated_text_filepath, 'r') as generated_text_file:
            generated_text_contents = generated_text_file.read()

        # Replace the prompt placeholder with the content
        new_prompt_contents = prompt_contents.replace('$!$!$', generated_text_contents)

        print(f"Combined prompt: {new_prompt_contents}")
        # Run the CLI command and capture the output
        response = ollama.chat(model=model_name, messages=[
            {
                'role': 'user',
                'content': generated_text_contents,
            },
        ])

        output = response['message']['content']

        print(f"New output: {output}")

        # Define the output file path based on folder_name
        if folder_name == "gen5":
            output_filepath = "/data/application/editor/new_text"
        else:
            new_folder_name = increment_last_digit_in_folder_name(folder_name)
            output_filepath = os.path.join(os.path.dirname(directory), f"{new_folder_name}/output.txt")


        # Write the output to the file
        with open(output_filepath, 'w') as f:
            f.write(output)

        shutil.move(os.path.join(os.path.dirname(prompt_filepath), "/done/"))

        print(f"Processed {generated_text_filepath}, output saved to {output_filepath}")

    except Exception as e:
        print(f"Error processing {generated_text_filepath}: {e}")

def generate_new_text(model_name):
    print(f"Generating new text with model: {model_name}")
    prompt_filepath = "/data/application/llm/prompt.txt"
    gender_prompt_filepath = "/data/application/llm/gender_prompt.txt"

    try:
        with open(prompt_filepath, 'r') as prompt_file:
            prompt_contents = prompt_file.read()


        print(f"Prompt: {prompt_contents}")
        text_response = ollama.chat(model="phi3", messages=[
            {
                'role': 'user',
                'content': prompt_contents,
            },
        ])

        # Get the output string
        new_text_output = text_response['message']['content']

        print(f"Output: {new_text_output}")

        response = ollama.chat(model=model_name, messages=[
            {
                'role': 'user',
                'content': new_text_output,
            },
        ])

        gender = response['message']['content']

        print(f"Gender output: {gender}")
        if gender != "male" and gender != "female":
            gender = "male"

        today_date = datetime.now().strftime('%Y-%m-%d')

        # Define the output file path based on folder_name
        output_filepath = f"/data/application/llm/gen1/{gender}_{today_date}.txt"

        # Write the output to the file
        with open(output_filepath, 'w') as f:
            f.write(new_text_output)

        print(f"Generated a new text file, output saved to {output_filepath}")

    except Exception as e:
        print(f"Error generating a new text file: {e}")

def check_directories():
    try:
        with open(directories_filepath, 'r') as file:
            # Read all lines and strip any trailing newline or spaces
            directories = [line.strip() for line in file.readlines()]
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    for directory in directories:
        print(f"Checking directory: {directory}")
        if not os.path.isdir(directory):
            print(f"Directory {directory} does not exist")
            break

        folder_name = os.path.basename(directory)
        contents = glob.glob(directory + '/*.txt')

        if folder_name == "gen1" and len(contents) == 1:
            generate_new_text("phi3")
        else:
            for filename in os.listdir(directory):
                if filename.endswith(".txt"):
                    generated_text_filepath = os.path.join(directory, filename)
                    prompt_text_filepath = os.path.join(directory, "prompt.txt")
                    print(f"Generated text filepath: {generated_text_filepath}")
                    print(f"Prompt text filepath: {prompt_text_filepath}")
                    process_file(generated_text_filepath, prompt_text_filepath, directory, folder_name, "phi3")
                    print("Moving to done: " + os.path.join(directory, "/done/"))
                    shutil.move(generated_text_filepath, os.path.join(directory, "/done/"))
                break

def run_ollama_serve():
    # Start the ollama serve command
    print("Starting 'ollama serve'...")
    process = subprocess.Popen(['ollama', 'serve'])

    # Wait for 5 seconds
    print("Waiting for 5 seconds...")
    time.sleep(5)

if __name__ == "__main__":

    run_ollama_serve()

    while True:
        check_directories()
        time.sleep(10)  # Pause for 10 seconds before checking again
