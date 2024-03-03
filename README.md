# UKASeg
## Usage
First of all, you need to install all the requirements:
```
pip install -r requirements.txt
```
Then you can run the script with the following command:
```
python run_segmentation.py -modality=ct -organ=bronchi -model=wingsnet -input=demo_dataset -output=output
```
Alternatively, you can run the interface version by running this command:
```
python run_segmentation_gui.py
```
## Info
To check available organs and models, check [default_models.json](./default_models.json)
