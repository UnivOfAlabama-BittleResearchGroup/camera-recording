import requests
import dotenv
import os
import xmltodict
import pprint
import json

dotenv.load_dotenv()

ip = os.environ.get("IP")
ex_password = os.environ.get("EXPORT_PASS") # password for encrypted zip files
disk_id = "SD_DISK"

recording_request = f"http://{ip}/axis-cgi/record/list.cgi?recordingid=all"
recording_xml = requests.get(recording_request).content.decode()

rec_dict = xmltodict.parse(recording_xml)
recording_list = rec_dict['root']['recordings']['recording']
filtered_recording_id = [recording['@recordingid'] for recording in recording_list]
# print(filtered_recording_id)
# pprint.pprint(rec_dict)
for id in filtered_recording_id:
    # export_format = (f"http://{ip}/axis-cgi/record/list.cgi?recordingid=all")
    # format_xml = requests.get(export_format).content.decode()
    # pprint.pprint(format_xml)
    # print(id)
    # export_capabilities = f"http://{ip}/axis-cgi/record/export/properties.cgi?schemaversion=1&recordingid={id}&diskid={disk_id}"
    # capabilities_list = requests.get(export_capabilities).content.decode()
    # pprint.pprint(capabilities_list)

    export_request_mkv = (f"http://{ip}/axis-cgi/record/export/exportrecording.cgi?schemaversion=1&recordingid={id}&diskid={disk_id}&exportformat=matroska")
    request_xml = requests.get(export_request_mkv).content.decode()
    pprint.pprint(request_xml)

    # export_request_zip = (f"http://{ip}/axis-cgi/record/export/exportrecording.cgi?schemaversion=1"
    # f"&recordingid={id}&diskid={disk_id}&exportformat=matroska&starttime=2023-02-03T17:45:09Z&stoptime=2023-02-03T17:45:15")
    # request_xml = requests.get(export_request_zip).content.decode()
    # print(export_request_zip)
    # pprint.pprint(request_xml)

    

#delete_request = f"//{ip}/axis-cgi/record/remove.cgi?recordingid={recording_list}"


# for camera in cameras:
#     stop recording at (declared length)
#     extract videos from SD card on camera
#     save videos to local server (renamed to date_cameraloc_video#.mp4) or something along those lines
#     delete videos from SD card on camera
#     start recording again until (declared length)