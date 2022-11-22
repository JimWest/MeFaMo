from __future__ import annotations
from collections import deque
from statistics import mean
from enum import Enum
import struct
from typing import Tuple
import datetime
import uuid
import numpy as np
from timecode import Timecode

class FaceBlendShape(Enum):
    EyeBlinkLeft = 0
    EyeLookDownLeft = 1
    EyeLookInLeft = 2
    EyeLookOutLeft = 3
    EyeLookUpLeft = 4
    EyeSquintLeft = 5
    EyeWideLeft = 6
    EyeBlinkRight = 7
    EyeLookDownRight = 8
    EyeLookInRight = 9
    EyeLookOutRight = 10
    EyeLookUpRight = 11
    EyeSquintRight = 12
    EyeWideRight = 13
    JawForward = 14
    JawLeft = 15
    JawRight = 16
    JawOpen = 17
    MouthClose = 18
    MouthFunnel = 19
    MouthPucker = 20
    MouthLeft = 21
    MouthRight = 22
    MouthSmileLeft = 23
    MouthSmileRight = 24
    MouthFrownLeft = 25
    MouthFrownRight = 26
    MouthDimpleLeft = 27
    MouthDimpleRight = 28
    MouthStretchLeft = 29
    MouthStretchRight = 30
    MouthRollLower = 31
    MouthRollUpper = 32
    MouthShrugLower = 33
    MouthShrugUpper = 34
    MouthPressLeft = 35
    MouthPressRight = 36
    MouthLowerDownLeft = 37
    MouthLowerDownRight = 38
    MouthUpperUpLeft = 39
    MouthUpperUpRight = 40
    BrowDownLeft = 41
    BrowDownRight = 42
    BrowInnerUp = 43
    BrowOuterUpLeft = 44
    BrowOuterUpRight = 45
    CheekPuff = 46
    CheekSquintLeft = 47
    CheekSquintRight = 48
    NoseSneerLeft = 49
    NoseSneerRight = 50
    TongueOut = 51
    HeadYaw = 52
    HeadPitch = 53
    HeadRoll = 54
    LeftEyeYaw = 55
    LeftEyePitch = 56
    LeftEyeRoll = 57
    RightEyeYaw = 58
    RightEyePitch = 59
    RightEyeRoll = 60


class PyLiveLinkFace:
    """PyLiveLinkFace class

    Can be used to receive PyLiveLinkFace from the PyLiveLinkFace IPhone app or
    other PyLiveLinkFace compatible programs like this library.
    """

    def __init__(self, name: str = "Python_LiveLinkFace", 
                        uuid: str = str(uuid.uuid1()), fps=60, 
                        filter_size: int = 5) -> None:

        # properties
        self.uuid = uuid
        self.name = name
        self.fps = fps
        self._filter_size = filter_size

        self._version = 6
        now = datetime.datetime.now()
        timcode = Timecode(
            self._fps, f'{now.hour}:{now.minute}:{now.second}:{now.microsecond * 0.001}')
        self._frames = timcode.frames
        self._sub_frame = 1056060032                # I don't know how to calculate this
        self._denominator = int(self._fps / 60)     # 1 most of the time
        self._blend_shapes = [0.000] * 61
        self._old_blend_shapes = []                 # used for filtering
        for i in range(61):
            self._old_blend_shapes.append(deque([0.0], maxlen = self._filter_size))

    @property
    def uuid(self) -> str:
        return self._uuid

    @uuid.setter
    def uuid(self, value: str) -> None:
        # uuid needs to start with a $, if it doesn't add it
        if not value.startswith("$"):
            self._uuid = '$' + value
        else:
            self._uuid = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def fps(self) -> int:
        return self._fps

    @fps.setter
    def fps(self, value: int) -> None:
        if value < 1:
            raise ValueError("Only fps values greater than 1 are allowed.")
        self._fps = value

    def encode(self) -> bytes:
        """ Encodes the PyLiveLinkFace object into a bytes object so it can be 
        send over a network. """              
        
        version_packed = struct.pack('<I', self._version)
        uuiid_packed = bytes(self._uuid, 'utf-8')
        name_lenght_packed = struct.pack('!i', len(self._name))
        name_packed = bytes(self._name, 'utf-8')

        now = datetime.datetime.now()
        timcode = Timecode(
            self._fps, f'{now.hour}:{now.minute}:{now.second}:{now.microsecond * 0.001}')
        frames_packed = struct.pack("!II", timcode.frames, self._sub_frame)  
        frame_rate_packed = struct.pack("!II", self._fps, self._denominator)
        data_packed = struct.pack('!B61f', 61, *self._blend_shapes)
        
        return version_packed + uuiid_packed + name_lenght_packed + name_packed + \
            frames_packed + frame_rate_packed + data_packed

    def get_blendshape(self, index: FaceBlendShape) -> float:
        """ Get the current value of the blend shape. 

        Parameters
        ----------
        index : FaceBlendShape
            Index of the BlendShape to get the value from.

        Returns
        -------
        float
            The value of the BlendShape.
        """        
        return self._blend_shapes[index.value]

    def set_blendshape(self, index: FaceBlendShape, value: float, 
                        no_filter: bool = False) -> None:
        """ Sets the value of the blendshape. 
        
        The function will use mean to filter between the old and the new 
        values, unless `no_filter` is set to True.

        Parameters
        ----------
        index : FaceBlendShape
            Index of the BlendShape to get the value from.
        value: float
            Value to set the BlendShape to, should be in the range of 0 - 1 for 
            the blendshapes and between -1 and 1 for the head rotation 
            (yaw, pitch, roll).
        no_filter: bool
            If set to True, the blendshape will be set to the value without 
            filtering.
        
        Returns
        ----------
        None
        """

        if no_filter:
            self._blend_shapes[index.value] = value
        else:
            self._old_blend_shapes[index.value].append(value)
            filterd_value = mean(self._old_blend_shapes[index.value])
            self._blend_shapes[index.value] = filterd_value

    @staticmethod
    def decode(bytes_data: bytes) -> Tuple[bool, PyLiveLinkFace]:
        """ Decodes the given bytes (send from an PyLiveLinkFace App or from 
        this library) and creates a new PyLiveLinkFace object.
        Returns True and the generated object if a face was found in the data, 
        False an a new empty PyLiveLinkFace otherwise. 

        Parameters
        ----------
        bytes_data : bytes
            Bytes input to create the PyLiveLinkFace object from.

        Returns
        -------
        bool
            True if the bytes data contained a face, False if not.        
        PyLiveLinkFace
            The PyLiveLinkFace object.

        """
        version = struct.unpack('<i', bytes_data[0:4])[0]
        uuid = bytes_data[4:41].decode("utf-8")
        name_length = struct.unpack('!i', bytes_data[41:45])[0]
        name_end_pos = 45 + name_length
        name = bytes_data[45:name_end_pos].decode("utf-8")
        if len(bytes_data) > name_end_pos + 16:

            #FFrameTime, FFrameRate and data length
            frame_number, sub_frame, fps, denominator, data_length = struct.unpack(
                "!if2ib", bytes_data[name_end_pos:name_end_pos + 17])

            if data_length != 61:
                raise ValueError(
                    f'Blend shape length is {data_length} but should be 61, something is wrong with the data.')

            data = struct.unpack(
                "!61f", bytes_data[name_end_pos + 17:])

            live_link_face = PyLiveLinkFace(name, uuid, fps)
            live_link_face._version = version
            live_link_face._frames = frame_number
            live_link_face._sub_frame = sub_frame
            live_link_face._denominator = denominator
            live_link_face._blend_shapes = data

            return True, live_link_face
        else:
            #print("Data does not contain a face, returning default empty face.")
            return False, PyLiveLinkFace()
