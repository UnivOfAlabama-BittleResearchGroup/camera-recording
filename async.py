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
date = datetime.utcnow()
time_delta = date - timedelta(hours=1)
l = range(24)
times = [[date - timedelta(hours=_t) for _t in _l] for _l in zip(l[1:], l[:-1]) ]
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
    
    zero_time = "2023"
    for id in filtered_recording_id:
        export_request_url = (f"http://{ip}/axis-cgi/record/export/exportrecording.cgi?schemaversion=1"
        f"&recordingid={id}&diskid={disk_id}&exportformat=matroska&starttime=2023-02-04T17:45:09Z&stoptime=2023-02-04T18:45:15Z")

    return filtered_recording_id

async def fetch(session, url):
    async with session.get(url) as response:
        with open(f"export_{id}.mkv", "wb") as f:
            f.write(await response.content())


async def export_recordings(filtered_recording_id, ip):
    async with aiohttp.ClientSession() as session:
        for id in filtered_recording_id:
            for url in urls:
                tasks.append(fetch(session, url))
            htmls = await asyncio.gather(*tasks)
for ip in ip_list:
    get_recording_id(ip)
    export_recordings(ip)

print("Process finished --- %s seconds ---" % (time.time() - start_time))