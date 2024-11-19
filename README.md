# Streamlined LLM-Powered Video Content Automation

This project orchestrates an advanced, fully automated video content generation pipeline using a Kubernetes deployment on a Linux machine. Once deployed, the system leverages Large Language Models to autonomously produce compelling story-driven video content at scale:



# How it works

1. **Content Generation**: The application generates original stories using a Large Language Model or curates content by searching Reddit based on popularity.
2. **Contextual Voice Analysis**: It determines the gender of the storyteller to match an appropriate voice profile.
3. **Text-to-Speech**: Using a local neural text to speech system it converts the text into lifelike voiceovers.
4. **Transcription**: The generated speech is transcribed with timestamps.
5. **Video Overlay**: Subtitles and voiceovers are overlaid onto videos provided by the user (from a folder).
6. **Thumbnail**: A reddit post thumbnail is created with different names, avatars and the story title.
7. **Scalability**: The system can autonomously produce an unlimited amount of content, and since deployed as microservices it is scalable horizontally.

# Setting up the K8s Cluster (with K3s)

Place the k8s configuration directory in /home.

Run `setup_cluster.sh` file. 

Go to `workfolders_setup` and create the folders `gen1_prompt`, `gen2_prompt` ... `gen5_prompt`, and inside them, `prompt.txt` files, with the prompt for the LLM for each layer. Otherwise, these will be automatically generated with a generic re-evaluation prompt.

To replace the output from the previous layer inside the text document, substitute with `$!$!$` . Within `initial_prompt`, include `prompt.txt` and `gender_prompt.txt`, where `gender_prompt.txt` requires `$!$!$` substitution as it gets the output from the initial prompt. The initial `prompt.txt` doesn't have a substitution, because this is the entrypoint for the LLM.

Run the shell file: `sh /home/k8s-config/workfolders_setup/create_pv_directory.sh /home/cluster`. This command will create the folders and copy the prompts over, to the Persistent Volume mounted for both applications to work on, in the necessary folders. (TODO: Add to setup_cluster.sh)

Create the PVs and PVCs: in /global-config/, run `kubectl apply -f` for each file in the directory. (TODO: Add to setup_cluster.sh)

Add the /models folder inside /llm/build/, and the /voices and the piper_x86 tar inside the /editor/build/ folder.

`sh /home/k8s-cluster/llm/build/build.sh`

Then inside the LLM/k8s-configuration folder, run `kubectl apply -f deployment-llm.yaml`.

# Pre-Requisites

1. Videos for the application to use
2. Piper (TTS)
3. Voice models

A script which automates the download and extraction process would be nice, but since this is more of a showcase project I haven't created one.

# Running the application

Run the python file: `py main.py` inside the `app` folder. This will start the content creation process.

What it then does is it traverses the folders from last to first - thumbnail, subtitling, transcription, tts, content evaluation, content creation/gathering - in an infinite loop. It moves any files that it deems unfit in `err` folders for each step. It logs each step so you can keep track of the process.

