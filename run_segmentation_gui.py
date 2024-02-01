import os
import sys
import json
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Assuming your existing functions like get_default_model() remain unchanged

def run_model(modality, organ, model, input_path, output_path):
    # This function will contain the core logic that was previously in the main function
    # Simplified for brevity; you'll need to integrate your existing script logic here

    # Example: Run a simple check and print something
    print(f"Running model with {modality}, {organ}, {model}, {input_path}, {output_path}")
    # You might want to integrate subprocess calls or other logic here

def gui():
    window = tk.Tk()
    window.title("Organ Segmentation")

    # Modality
    tk.Label(window, text="Modality:").grid(row=0, column=0, sticky="w")
    modality_var = tk.StringVar()
    modality_dropdown = ttk.Combobox(window, textvariable=modality_var, values=['ct', 'mri', 'pet'])
    modality_dropdown.grid(row=0, column=1, sticky="ew")

    # Organ
    tk.Label(window, text="Organ:").grid(row=1, column=0, sticky="w")
    organ_var = tk.StringVar()
    organ_entry = ttk.Entry(window, textvariable=organ_var)
    organ_entry.grid(row=1, column=1, sticky="ew")

    # Model
    tk.Label(window, text="Model:").grid(row=2, column=0, sticky="w")
    model_var = tk.StringVar()
    model_entry = ttk.Entry(window, textvariable=model_var)
    model_entry.grid(row=2, column=1, sticky="ew")

    # Input
    tk.Label(window, text="Input Path:").grid(row=3, column=0, sticky="w")
    input_var = tk.StringVar()
    input_entry = ttk.Entry(window, textvariable=input_var)
    input_entry.grid(row=3, column=1, sticky="ew")
    ttk.Button(window, text="Browse...", command=lambda: input_var.set(filedialog.askdirectory())).grid(row=3, column=2)

    # Output
    tk.Label(window, text="Output Path:").grid(row=4, column=0, sticky="w")
    output_var = tk.StringVar()
    output_entry = ttk.Entry(window, textvariable=output_var)
    output_entry.grid(row=4, column=1, sticky="ew")
    ttk.Button(window, text="Browse...", command=lambda: output_var.set(filedialog.askdirectory())).grid(row=4, column=2)

    # Run Button
    run_button = ttk.Button(window, text="Run", command=lambda: run_model(
        modality_var.get(), organ_var.get(), model_var.get(), input_var.get(), output_var.get()))
    run_button.grid(row=5, column=0, columnspan=3)

    window.mainloop()

if __name__ == "__main__":
    gui()
