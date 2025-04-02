#!/bin/bash

# define the target directry
LAYER_DIR="../modules/terraform-aws-automate-ec2-start-stop/layer"
ZIP_FILE="$LAYER_DIR/requests.zip"

# create the layer directory if it doesnt exist
echo "[INFO]: creating layer directory: $LAYER_DIR"
mkdir -p "$LAYER_DIR"

# navigate to the layer directory
cd "$LAYER_DIR" || { echo "[ERROR]: failed to enter directory: $LAYER_DIR"; exit 1; }

# install the 'requests' package into the directory
echo "[INFO]: installing requests package..."
pip install requests -t .

# create a ZIP archive of the installed packages
echo "[INFO]: creating ZIP file: $ZIP_FILE"
zip -r requests.zip .

echo "[INFO]: lambda layer ZIP created successfully: $ZIP_FILE"
