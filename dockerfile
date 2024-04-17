# Base image
FROM continuumio/miniconda3:latest

# Set the working directory
WORKDIR /app

# Create the folder models
RUN mkdir models
RUN mkdir environments

# Copy all the necessary files
COPY models /app/models
COPY environments /app/environments
COPY default_models.json .
COPY run_segmentation.py .
COPY run_segmentation_gui.py .
COPY run_segmentation.slurm .

# Create the first environment
RUN conda env create -f environments/environment_payer.yaml
RUN conda run -n payer pip install -r requirements_payer.txt

# Create the second environment
RUN conda env create -f environments/environment_general.yaml
RUN conda run -n general pip install -r requirements_general.txt

# Set the default shell
SHELL ["/bin/sh", "-c"]