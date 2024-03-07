import os
import json
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description='Organ Segmentation CLI')
    parser.add_argument('-modality', choices=['ct', 'mri', 'pet'], required=True)
    parser.add_argument('-organ', required=True)  # Extend choices as per available models
    parser.add_argument('-model', default=None)  # Default model selection logic will be implemented later
    parser.add_argument('-input', type=str, required=True)
    parser.add_argument('-output', type=str, required=True)
    # Add any other arguments here

    args = parser.parse_args()

    # Check modality
    modality_path = os.path.join('./models', args.modality)
    if not os.path.exists(modality_path):
        raise ValueError(f"Invalid modality '{args.modality}'. Please choose from 'ct', 'mri', or 'pet'.")

    # Check organ
    organ_path = os.path.join(modality_path, args.organ)
    if not os.path.exists(organ_path):
        raise NotImplementedError(f"The organ '{args.organ}' is not implemented.")

    # Check model
    if not args.model:
        print(f"No model specified. Using default model for '{args.organ}'.")
        args.model = get_default_model(args.modality, args.organ)
    elif args.model and not os.path.exists(os.path.join(organ_path, args.model)):
        print(f"Specified model '{args.model}' does not exist. Using default model for '{args.organ}'.")
        args.model = get_default_model(args.modality, args.organ)
    model_script = os.path.join(organ_path, args.model.lower(), args.model.lower() + '.py')

    # Ensure the model script exists
    if not os.path.isfile(model_script):
        raise FileNotFoundError(f"Model script '{model_script}' not found.")

    # Check input
    if not os.path.exists(args.input):
        raise ValueError(f"Input folder '{args.input}' does not exist.")
    
    # Check output
    if not os.path.exists(args.output):
        os.makedirs(args.output, exist_ok=True)
        print(f"Saving output to '{args.output}'.")

    # Construct the command to run the model script with python
    command = ['python', model_script, '-input', args.input, '-output', args.output]

    print(f"Running command: {' '.join(command)}")

    # Run the model script
    subprocess.run(command, check=True)



def get_default_model(modality, organ):
    try:
        with open('default_models.json', 'r') as file:
            models = json.load(file)
            return models.get(modality, {}).get(organ)
    except FileNotFoundError:
        print("Default models JSON file not found.")
        return None
    except json.JSONDecodeError:
        print("Error decoding default_models JSON file.")
        return None


if __name__ == "__main__":
    main()
