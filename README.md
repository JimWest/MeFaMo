# MeFaMo - MediapipeFaceMocap

If you find this project useful and want to support me, feel free to buy me a coffee:

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/jimwest)


MeFaMo calculates the facial keypoints and blend shapes of a user. Instead of using the built in IPhone blend shape calculation (like [LiveLinkFace App](https://apps.apple.com/us/app/live-link-face/id1495370836) does), this uses the Googles [Mediapipe](https://github.com/google/mediapipe) to calculate the facial key points of a face. Those key points will then be used to calculate several facial blend shapes (like eyebrows, blinking, smiling etc.). You only need a PC with a webcam and no external device to use it. 
It uses my [PyLiveLinkFace](https://github.com/JimWest/PyLiveLinkFace) library to send the blend shapes directly into the currently opened Unreal LiveLink Project (the Unreal Engine can also run on a separate PC).

![alt text](https://github.com/JimWest/MeFaMo/blob/main/images/showoff_2.gif?raw=true)

It's not fully finished yet and missing a calibration feature to recalibrate all the values to several other faces, but it's a good start on how to calculate the blend shapes and create your own facial motion capture with Unreal. 

## Prerequisites
To setup the LiveLink plugin and system in Unreal, see the following tutorial:
https://docs.unrealengine.com/4.27/en-US/AnimatingObjects/SkeletalMeshAnimation/FacialRecordingiPhone/

## Requirements
MeFaMo needs the following python libraries:
<ul>
  <li>numpy</li>
  <li>cv2</li>
  <li>pylivelinkface</li>
  <li>mediapipe</li>
  <li>transforms3d</li>
  <li>open3d</li>
</ul>

## Install

To install it, clone the git repo and install it with the setup.py file:
```
python setup.py install
```
 
## Usage

If you just want to use it and don't have an active python environment or want to install other python packages, you can just the the .exe file of the [release](https://github.com/JimWest/MeFaMo/releases) (unzip the mefamo_win64.zip zip file).

To use MeFaMo in python, just execute the mefamo_cli.py file in the examples folder:
```
python mefamo_cli.py
```

mefamo_cli gives you several options for image input, the default behavior is to open the Webcam (camera 0). But you can also
specfiy the webcam you want to use (if you have more with one) with the number of the webcam (0, 1, 2 etc.). You can also specfiy a video or still image which will then be used by mefamo. To use this feauture, you need to pass the `--input` paramter (like `--input D:\\Videos\\test.mp4` or `--input 1).

If you use the MeFaMo tool on another PC than your Unreal Engine, you can specify the ip of that machine (and also the port if you changed that in the LiveLink settings in unreal) with `--ip 192.168.0.1`  and `--input 12345` for running the Unreal Engine on a machine with the IP 192.168.0.1 and the port 12345.

If you want to see the normalized 3d points of the detected face (projected on a 2d image), you can use the `--show_3d` parameter, which will open a new window.

The parameter'--hide_image` will hide the 2d webcam image with keypoint overlay.

There's also an experemental GUI (which doesn't look different to the default executable, but uses kivy for future work).


## Build the exe yourself

In order to build an exe from all needed python libs and files, pyinstaller was used.
It can be installed via pip:
```
pip install pyinstaller
```

After that, you can use pyinstaller and the included mefamo.spec file under examples to build the exe:
```
pyinstaller --onefile .\examples\mefamo.spec
```
This will take a bit time, you'll find the exe then in the `mefamo\dist\` folder.