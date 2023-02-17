import aiohttp
import asyncio
import time
import requests
import xmltodict
import yaml
from datetime import datetime, timedelta

# create timestamp variable
timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
# get start time
start_time = time.time()

# constants
disk_id = "SD_DISK"
year = datetime.utcnow().year
month = str(datetime.utcnow().month).zfill(2)
day = str(datetime.utcnow().day).zfill(2)
date = datetime.utcnow()
time_delta = date - timedelta(hours=1)
l = range(24)
times = [[date - timedelta(hours=_t) for _t in _l] for _l in zip(l[1:], l[:-1]) ] # this might need to change
#print(times)
time_format = f"{year}-{month}-{day}Thh:mm:ssZ" # YYYY-MM-DDThh:mm:ssZ

print(time_format)

# ip list
with open("config.yaml", "r") as f:
    config_list = yaml.load(f, Loader=yaml.FullLoader)

ip_list = config_list["Config"]["ip"]


def get_recording_id(ip):
    recording_request = f"http://{ip}/axis-cgi/record/list.cgi?recordingid=all"
    recording_xml = requests.get(recording_request).content.decode()

    rec_dict = xmltodict.parse(recording_xml)
    recording_list = rec_dict['root']['recordings']['recording']
    filtered_recording_id = [recording['@recordingid'] for recording in recording_list]

    return filtered_recording_id

def get_recording_times(ip, id, disk_id):
    times_request = f"http://{ip}/axis-cgi/record/export/properties.cgi?schemaversion=1&recordingid={id}&diskid={disk_id}"
    times_xml = requests.get(times_request).content.decode()

    times_dict = xmltodict.parse(times_xml)
    start_time = 0 # pulls out start time from dict
    end_time = 1 # pulls out end time from dict

    return start_time, end_time

#def time

def write_export_recordings(ip, id, disk_id, start_time, end_time):
    export_request_url = (f"http://{ip}/axis-cgi/record/export/exportrecording.cgi?schemaversion=1"
    f"&recordingid={id}&diskid={disk_id}&exportformat=matroska&starttime={start_time}&stoptime={end_time}")

async def fetch(session, url, rec_id):
    async with session.get(url) as response:
        with open(f"export_{rec_id}.mkv", "wb") as f:
            f.write(await response.content())

async def export_recordings(filtered_recording_id, ip):
    async with aiohttp.ClientSession() as session:
        for ip in ip_list:
            rec_id = get_recording_id(ip)
            get_recording_times(ip, rec_id, disk_id)
            export_request_url = (f"http://{ip}/axis-cgi/record/export/exportrecording.cgi?schemaversion=1"
            f"&recordingid={rec_id}&diskid={disk_id}&exportformat=matroska&starttime=2023-02-04T17:45:09Z&stoptime=2023-02-04T18:45:15Z")
            urls = []
            urls.append(export_request_url)
            tasks = []
            for url in urls:
                tasks.append(fetch(session, url))
            htmls = await asyncio.gather(*tasks)
            for html in htmls:
                print(html)

for ip in ip_list:
    get_recording_id(ip)
    #export_recordings(ip)

print("Process finished --- %s seconds ---" % (time.time() - start_time))