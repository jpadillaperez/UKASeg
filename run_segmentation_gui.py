import os
import json
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def run_model(modality, organ, model, input_path, output_path):
    print(f"Running model {model} for {organ} on {modality} data from {input_path} to {output_path}")
    
    # Construct the command to run the model script with python
    model_script = os.path.join("./models", modality, organ, model.lower(), model.lower() + '.py')
    command = ['python', model_script, '-input', input_path, '-output', output_path]

    # Run the model script and wait for it to complete
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred while running the model: {e}")
    else:
        messagebox.showinfo("Success", "Model inference successfully")

def gui():
    window = tk.Tk()
    window.title("Organ Segmentation")

    #Read json file
    with open('default_models.json') as f:
        modalities_organs_models = json.load(f)

    # Define StringVars
    modality_var = tk.StringVar()
    organ_var = tk.StringVar()
    model_var = tk.StringVar()

    # Define the organ and model dropdowns ahead of their use
    organ_dropdown = ttk.Combobox(window, textvariable=organ_var)
    model_dropdown = ttk.Combobox(window, textvariable=model_var)

    def update_organ_options(*args):
        # This function now has access to organ_dropdown
        organs = list(modalities_organs_models[modality_var.get()].keys())
        organ_dropdown['values'] = organs
        organ_var.set('')  # Clear or set default value

    def update_model_options(*args):
        # This function now has access to model_dropdown
        models = modalities_organs_models[modality_var.get()].get(organ_var.get(), [])
        model_dropdown['values'] = models if models else ['No model available']
        model_var.set(models[0] if models else 'No model available')

    # Modality
    tk.Label(window, text="Modality:").grid(row=0, column=0, sticky="w")
    modality_dropdown = ttk.Combobox(window, textvariable=modality_var, values=list(modalities_organs_models.keys()))
    modality_dropdown.grid(row=0, column=1, sticky="ew")
    modality_dropdown.bind('<<ComboboxSelected>>', update_organ_options)

    # Organ
    tk.Label(window, text="Organ:").grid(row=1, column=0, sticky="w")
    organ_dropdown.grid(row=1, column=1, sticky="ew")
    organ_dropdown.bind('<<ComboboxSelected>>', update_model_options)

    # Model
    tk.Label(window, text="Model:").grid(row=2, column=0, sticky="w")
    model_dropdown.grid(row=2, column=1, sticky="ew")

    # Input Path
    tk.Label(window, text="Input Path:").grid(row=3, column=0, sticky="w")
    input_var = tk.StringVar()
    input_entry = ttk.Entry(window, textvariable=input_var)
    input_entry.grid(row=3, column=1, sticky="ew")
    ttk.Button(window, text="Browse...", command=lambda: input_var.set(filedialog.askdirectory())).grid(row=3, column=2)

    # Output Path
    tk.Label(window, text="Output Path:").grid(row=4, column=0, sticky="w")
    output_var = tk.StringVar()
    output_entry = ttk.Entry(window, textvariable=output_var)
    output_entry.grid(row=4, column=1, sticky="ew")
    ttk.Button(window, text="Browse...", command=lambda: output_var.set(filedialog.askdirectory())).grid(row=4, column=2)

    # Run Button
    ttk.Button(window, text="Run", command=lambda: run_model(
        modality_var.get(), organ_var.get(), model_var.get(), input_var.get(), output_var.get())
    ).grid(row=5, column=0, columnspan=3, sticky="ew")

    window.mainloop()

if __name__ == "__main__":
    gui()
