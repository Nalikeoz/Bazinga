import cv2
import numpy
import StringIO
from PIL import Image
import datetime
import os


def generate_video_name():
    """
    return: currend date and time as the name of the video.
    """
    time = datetime.datetime.now()
    video_name = str(time.day) + '.' + str(time.month) + '.' + str(time.year) + ' ' + str(time.hour) + '.' + str(
        time.minute) + '.' + str(time.second)
    return video_name


FPS = 15.0
VIDEO_RESOLUTION = (800, 600)
VIDEOS_FOLDER = 'Records\\'


class VideoWriter(object):
    def __init__(self, video_resolution=VIDEO_RESOLUTION):
        self._create_folder()
        video_name = VIDEOS_FOLDER + generate_video_name() + '.avi'
        self.video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'DIVX'),
                                     FPS, video_resolution)
    @staticmethod
    def _create_folder():
        try:
            os.mkdir('Records')
        except WindowsError:
            pass

    def write(self, image_data):
        """
        :param image_data: raw data of a PIL image.
        the function writes the image data to the full video.
        """
        data = StringIO.StringIO(image_data)
        image = Image.open(data).resize(VIDEO_RESOLUTION, Image.ANTIALIAS)
        self.video.write(cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR))

    def close(self):
        """
        the function stops the video writing and closes the opencv windows.
        """
        cv2.destroyAllWindows()
        self.video.release()
        print 'closed video writer'
