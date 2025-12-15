     
from skyfield.api import load
print("Starting download of DE441 (3.1 GB)... this may take a while.")
load('de441.bsp')
print("Download complete: de441.bsp")
