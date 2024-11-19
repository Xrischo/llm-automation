#!/bin/bash

# Directory containing the files
dir="/home/editor/applications/aita/raw_text"

# Navigate to the directory
cd "$dir" || exit

# Loop through all *_title.txt files
for title_file in *_title.txt; do
    # Get the base ID by removing the _title.txt part
    base_id="${title_file%_title.txt}"
    
    # Construct the corresponding body file name
    body_file="${base_id}_body.txt"
    
    # Check if both title and body files exist
    if [[ -f "$title_file" && -f "$body_file" ]]; then
        # Get the current time with milliseconds
        timestamp=$(date +%Y%m%d%H%M%S%3N)
        
        # Construct new file names
        new_title_file="male_${timestamp}_title.txt"
        new_body_file="male_${timestamp}_body.txt"
        
        # Rename the files
        mv "$title_file" "../new_text/$new_title_file"
        mv "$body_file" "../new_text/$new_body_file"
        
        echo "Renamed $title_file and $body_file to $new_title_file and $new_body_file"
        
        # Wait for half a second
        sleep 0.5
    else
        echo "Skipping $title_file and $body_file as one of them does not exist"
    fi
done
