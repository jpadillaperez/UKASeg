import subprocess
import os
import sys
from glob import glob
import matplotlib
matplotlib.use('Agg')

def main():
    parser = argparse.ArgumentParser(description='Payer Inference')
    parser.add_argument('-input', type=str, required=True, help='Path to the input folder')
    parser.add_argument('-output', type=str, required=True, help='Path to the output folder')
    args = parser.parse_args()

    base_image_folder = args.input
    base_output_folder = args.output
    base_intermediate_folder = os.path.join(base_image_folder, 'tmp')
    models_folder = 'ckpts'
        
    preprocessed_image_folder = os.path.join(base_intermediate_folder, 'data_preprocessed')
    spine_localization_folder = os.path.join(base_intermediate_folder, 'spine_localization')
    spine_localization_model = os.path.join(models_folder, 'spine_localization')
    vertebrae_localization_folder = os.path.join(base_intermediate_folder, 'vertebrae_localization')
    vertebrae_localization_model = os.path.join(models_folder, 'vertebrae_localization')
    vertebrae_segmentation_folder = os.path.join(base_intermediate_folder, 'vertebrae_segmentation')
    vertebrae_segmentation_model = os.path.join(models_folder, 'vertebrae_segmentation')

    subprocess.run(['python', 'preprocess.py',
                    '--image_folder', base_image_folder,
                    '--output_folder', preprocessed_image_folder,
                    '--sigma', '0.75'])

    subprocess.run(['python', 'main_spine_localization.py',
                    '--image_folder', preprocessed_image_folder,
                    '--setup_folder', base_intermediate_folder,
                    '--model_files', spine_localization_model,
                    '--output_folder', spine_localization_folder])

    subprocess.run(['python', 'main_vertebrae_localization.py',
                    '--image_folder', preprocessed_image_folder,
                    '--setup_folder', base_intermediate_folder,
                    '--model_files', vertebrae_localization_model,
                    '--output_folder', vertebrae_localization_folder])

    subprocess.run(['python', 'main_vertebrae_segmentation.py',
                    '--image_folder', preprocessed_image_folder,
                    '--setup_folder', base_intermediate_folder,
                    '--model_files', vertebrae_segmentation_model,
                    '--output_folder', vertebrae_segmentation_folder])

    subprocess.run(['python', 'cp_landmark_files.py',
                    '--landmark_folder', vertebrae_localization_folder,
                    '--output_folder', base_output_folder])

    subprocess.run(['python', 'reorient_prediction_to_reference.py',
                    '--image_folder', vertebrae_segmentation_folder,
                    '--reference_folder', base_image_folder,
                        '--output_folder', base_output_folder])


if __name__ == '__main__':
    os.system(f"conda activate {payer}")
    main()
    os.system("conda deactivate")
