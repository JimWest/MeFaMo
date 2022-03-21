# MeFaMo - MediapipeFaceMocap

MeFaMo calculates the facial keypoints and blend shapes of a user. Instead of using the built in IPhone blend shape calculation (like [LiveLinkFace App](https://apps.apple.com/us/app/live-link-face/id1495370836) does), this uses the Googles [Mediapipe](https://github.com/google/mediapipe) to calculate the facial key points of a face. Those key points will then be used to calculate several facial blend shapes (like eyebrows, blinking, smiling etc.). You only need a PC with a webcam and no external device to use it. 
It uses my [PyLiveLinkFace](https://github.com/JimWest/PyLiveLinkFace) library to send the blend shapes directly into the currently opened Unreal LiveLink Project (the Unreal Engine can also run on a separate PC).

![alt text](https://github.com/JimWest/MeFaMo/blob/main/images/showoff_2.gif?raw=true)

It's not fully finished yet and missing a calibration feature to recalibrate all the values to several other faces, but it's a good start on how to calculate the blend shapes and create your own facial motion capture with Unreal. 

If you find this project useful and want to support me, feel free to buy me a coffee:

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/jimwest)

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

To use MeFaMo, just execute the mefamo.py file:
```
python mefamo.py
```

There's also an experemental GUI (which doesn't look different to the default executable, but uses kivy for future work).
