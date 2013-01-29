import os
import time

st = time.strftime("%y%m%d_%H%M%S")
os.system("ffmpeg -f oss -f video4linux2 -s 320x240 -i /dev/video0 %s_video.mpg " % (st))
