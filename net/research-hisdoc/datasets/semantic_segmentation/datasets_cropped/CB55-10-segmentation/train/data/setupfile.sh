#!/bin/bash

# Loop through each file in the directory
for file in *.jpg; do
    # Extract filename without extension
    filename=$(basename -- "$file")
    filename_no_ext="${filename%.*}"
    
    # Create directory if it doesn't exist
    mkdir -p "$filename_no_ext"
    
    # Move file into directory
    mv "$file" "$filename_no_ext/"
done
