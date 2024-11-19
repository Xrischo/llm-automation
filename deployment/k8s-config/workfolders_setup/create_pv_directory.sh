#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <target-directory>"
    exit 1
fi

# Get the target directory from the first argument
TARGET_DIR=$1

# Check if the target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "The specified directory does not exist: $TARGET_DIR"
    exit 1
fi

FOLDERS=(
    "$TARGET_DIR/base_videos"
    "$TARGET_DIR/llm"
    "$TARGET_DIR/llm/gen1"
    "$TARGET_DIR/llm/gen1/done"
    "$TARGET_DIR/llm/gen1/err"
    "$TARGET_DIR/llm/gen2"
    "$TARGET_DIR/llm/gen2/done"
    "$TARGET_DIR/llm/gen2/err"
    "$TARGET_DIR/llm/gen3"
    "$TARGET_DIR/llm/gen3/done"
    "$TARGET_DIR/llm/gen3/err"
    "$TARGET_DIR/llm/gen4"
    "$TARGET_DIR/llm/gen4/done"
    "$TARGET_DIR/llm/gen4/err"
    "$TARGET_DIR/llm/gen5"
    "$TARGET_DIR/llm/gen5/done"
    "$TARGET_DIR/llm/gen5/err"
    "$TARGET_DIR/editor"
    "$TARGET_DIR/editor/new_text"
    "$TARGET_DIR/editor/done"
    "$TARGET_DIR/editor/err"
    "$TARGET_DIR/editor/audio"
    "$TARGET_DIR/editor/audio/done"
    "$TARGET_DIR/editor/audio/err"
    "$TARGET_DIR/editor/subs_audio"
    "$TARGET_DIR/editor/subs_audio/done"
    "$TARGET_DIR/editor/subs_audio/err"
    "$TARGET_DIR/final_videos"
)

# Loop through the array to create the folders
for FOLDER in "${FOLDERS[@]}"; do
    mkdir -p "$FOLDER"

    if [ $? -eq 0 ]; then
        echo "Created: $FOLDER"
    else
        echo "Failed to create: $FOLDER"
        exit 1
    fi
done

INITIAL_PROMPT="/home/k8s-config/workfolders_setup/initial_prompt/prompt.txt"
GENDER_PROMPT="/home/k8s-config/workfolders_setup/initial_prompt/gender_prompt.txt"

if [ -f $INITIAL_PROMPT ]; then
	cp $INITIAL_PROMPT /home/cluster/llm
else
	echo "FATAL: Initial Prompt does not exist!"
	exit 1
fi

if [ -f $GENDER_PROMPT ]; then
	cp $GENDER_PROMPT /home/cluster/llm
else
	echo "WARNING: Gender Prompt does not exist! Creating a dummy one..."
	echo "You are an expert in categorisation. You need to decide whether the following piece of text is written from the perspective of a man, or from the perspective of a woman: '$!$!$'   .This was the end of the story. Please respond with 1 word only - 'male' if it is from the perspective of a man, or 'female' if it is from the perspective of a woman." > "/home/cluster/llm/gender_prompt.txt" 
fi

# Define source directories and their corresponding target directories
declare -A PROMPT_DIRS=(
    ["./gen1_prompt/prompt.txt"]="/home/cluster/llm/gen1"
    ["./gen2_prompt/prompt.txt"]="/home/cluster/llm/gen2"
    ["./gen3_prompt/prompt.txt"]="/home/cluster/llm/gen3"
    ["./gen4_prompt/prompt.txt"]="/home/cluster/llm/gen4"
    ["./gen5_prompt/prompt.txt"]="/home/cluster/llm/gen5"
)

# Iterate over the associative array
for SRC in "${!PROMPT_DIRS[@]}"; do
    TARGET_DIR="${PROMPT_DIRS[$SRC]}"
    
    # Check if the target directory exists, if not create it
    if [ ! -d $TARGET_DIR ]; then
        mkdir -p $TARGET_DIR
    fi
    
    # Check if the source file exists and copy it to the target directory
    if [ -f $SRC ]; then
        cp $SRC $TARGET_DIR
        echo "Copied $SRC to $TARGET_DIR"
    else
        echo "WARNING: $SRC does not exist! Creating a dummy one..."
	echo "You are an expert at evaluating stories and recreating them in a more entertaining manner. You know how to make them interesting and how to capture the audience's attention from the beginning. You have been tasked to re-tell the following story to be more shocking and unpredictable: '$!$!$'   - Please only have your improved story as your response." > "$TARGET_DIR/prompt.txt"
    fi
done

echo "All folders created successfully."
