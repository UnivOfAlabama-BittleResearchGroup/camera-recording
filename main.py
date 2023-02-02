import requests
import dotenv
import os
import xmltodict, json

dotenv.load_dotenv()

ip = os.environ.get("IP")
disk_id = "SD_DISK"

recording_request = f"http://{ip}/axis-cgi/record/list.cgi?recordingid=all"
recording_list = requests.get(recording_request).content.decode()
print(recording_list)
rec_dict = xmltodict.parse(recording_list)


#export_request = f"//{ip}/axis-cgi/record/export/exportrecording.cgi?schemaversion=1&recordingid={recording_list}&diskid={disk_id}&exportformat=matroska"
#export_list = requests.get(export_request)
#print(export_list)

#delete_request = f"//{ip}/axis-cgi/record/remove.cgi?recordingid={recording_list}"


# for camera in cameras:
#     stop recording at (declared length)
#     extract videos from SD card on camera
#     save videos to local server (renamed to date_cameraloc_video#.mp4) or something along those lines
#     delete videos from SD card on camera
#     start recording again until (declared length)