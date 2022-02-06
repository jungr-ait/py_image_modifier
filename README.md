# py_image_modifier


Some tools to modify/convert images on your computer.

Run [setup-env.sh](./setup-env.sh) to create a local python environment. 


## HEIC2JPG converter:

My situation: Having an IPhone 12 with a ton of images and running Ubuntu to manage my images in Shotwell...
First, how to get the images copied on my computer? [Mount your IPhone](https://www.maketecheasier.com/easily-mount-your-iphone-as-an-external-drive-in-ubuntu/)

I wrote that script to have it available on my desktop:
```bash
#! /bin/bash
# author: Roland Jung
#
# https://www.maketecheasier.com/easily-mount-your-iphone-as-an-external-drive-in-ubuntu/
#
# prerequisites:
# sudo apt install libimobiledevice6 libimobiledevice-utils
# sudo apt install ifuse
# mkdir ~/iphone


read -p 'IPhone Unlocked? (y/N): ' everything_okay
if [ "$everything_okay" != "y"  ]; then
  echo "stopping..."
  exit 1
fi

idevicepair pair
usbmuxd -f -v
ifuse ~/iphone
```
Now you can copy the images from the `DCIM` folder onto your computer.

Second, the images are stored in the `HEIC` format which finds limited support. 
For a convinient handling of the pictures they need to be converted into `JPEG` format. 
According to this [article](https://ubuntuhandbook.org/index.php/2021/06/open-heic-convert-jpg-png-ubuntu-20-04/), `libheif` provides a converter called `heif-convert`.

This converter is used in the [convert_heic2jpg.py](./convert/convert_heic2jpg.py) script.

Run the tool in the activated python environment:
```bash
(env)$ python ./convert/convert_heic2jpg.py --input_dir ./convert/test/in --output_dir ../convert/test/out --ext HEIC --verbose --skip_duplicates --create_tree
```

## RENAME image name to timestamp:

You might know the issues traveling between timezones with multiple devices. If you have forgotten to adapt the time settings or, e.g., your camera, one ends up with a timestamp hell and images cannot be assoziated correctly in tools like `shotwell`. 
The timestamps per device need to be adapted manually and this is where the [rename_img_2_timestamp.py](./rename/rename_img_2_timestamp.py) come into the play. 
It reads the timestamps from the `JPEG` file header using the [Pillow](https://pillow.readthedocs.io/en/stable/reference/index.html) and allows to adjust the timestamp by adding an offset to it and copies the file given the new name into a desired  folder  

Run the tool in the activated python environment:
```bash
(env)$ python ./rename/rename_img_2_timestamp.py --input_dir ./rename/test/in --output_dir ./rename/test/out --ext jpg --prefix Whatever --verbose --no_recursive --add_hours -24 --add_minutes 23 --skip_duplicates  --create_tree
```

