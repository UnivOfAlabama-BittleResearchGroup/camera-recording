import cv2
from pathlib import Path
from datetime import datetime, timedelta
import click
import pendulum
import yaml
import tempfile
import os
import shutil
import time

'''
enter a timestamp
a: returns the frame
b: returns video
if b:
    option on minute, 2 min, etc
'''

class temporary_copy(object):

    def __init__(self,original_path):
        self.original_path = original_path

    def __enter__(self):
        temp_dir = tempfile.gettempdir()
        base_path = os.path.basename(self.original_path)
        self.path = os.path.join(temp_dir,base_path)
        shutil.copy2(self.original_path, self.path)
        return self.path

    def __exit__(self,exc_type, exc_val, exc_tb):
        os.remove(self.path)

@click.argument("search_time")
@click.argument("ip_address")
@click.argument("save_path")
@click.option("--resolution", default='1080')
def _main(search_time, ip_address, save_path, resolution):
    # get all camera ip_list
    with open("config.yaml", "r") as f:
        config_list = yaml.load(f, Loader=yaml.FullLoader)

    ip_list = config_list["Config"]["ip"]
    output_path = Path(config_list["Config"]["output_path"])

    input_time = pendulum.parse(search_time, strict=False, tz="local")
    utc_time = input_time.in_tz("UTC")

    date = utc_time.to_date_string()
    hour = utc_time.hour

    if ip_address not in ip_list:
        raise Exception
    
    search_path = output_path / ip_address / date / (f"{hour}_{resolution}.mkv")
    video_parse(search_path, utc_time, save_path)
    


def video_parse(video_path, time: datetime, save_path):
    with temporary_copy(str(video_path)) as temp_path:
        cap = cv2.VideoCapture(str(temp_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(4))
        height = int(cap.get(3))
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        output_time = time.in_tz("America/Chicago")
        time_string = output_time.to_datetime_string().replace(":", "_").replace(" ", "_")
        out = cv2.VideoWriter(f'{save_path}/{time_string}_frames.avi', fourcc, fps, (height, width))

        target_time = time.minute * 60 + time.second + time.microsecond / 1e6
        seconds = 0
        while(cap.isOpened() and seconds <= (target_time + 10)):
            ret, frame = cap.read()

            if seconds >= (target_time - 10):
                out.write(
                    frame
                )

            seconds += (1 / fps)
            
        cap.release()



main = click.command(_main)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("Process finished --- %s seconds ---" % (time.time() - start_time))