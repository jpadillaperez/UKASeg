import os
import argparse
import subprocess
import torch
import nibabel as nib
import numpy as np

def main():
    parser = argparse.ArgumentParser(description='TotalSegmentator')
    parser.add_argument('-input', type=str, required=True, help='Path to the input folder')
    parser.add_argument('-output', type=str, required=True, help='Path to the output folder')
    args = parser.parse_args()

    input_folder = args.input
    output_folder = args.output

    #Get device
    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.startswith('.') or file.startswith('@'):
                continue
            if file.endswith(".nii.gz"):
                #Save voxel size
                input_img = nib.load(os.path.join(root, file))
                voxel_size = input_img.header.get_zooms()

                # Execute segmentation command
                command = ['TotalSegmentator', '-i', os.path.join(root, file), '-o', os.path.join(output_folder, file), '--task', 'hip_implant']
                subprocess.run(command, check=True)

if __name__ == "__main__":
    main()
