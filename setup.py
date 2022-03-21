#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='Mefamo - MediapipeFaceMocap',
    version='0.1',
    description='Python Library for generating blendshapes with MediaPipe FaceMesh and sending it to the Unreal Engine for live face tracking',
    author='Marco Pattke',
    author_email='j1m_w3st@web.de',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'cv2',
        'pylivelinkface',
        'mediapipe',
        'transforms3d',
        'open3d'
    ]
)

