import aiohttp
import asyncio
import time
import requests
import xmltodict
import yaml
import pprint
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

'''
get all camera ip_list
for ip in ip_list
    get recording id
        return filtered_recording_id
    for rec_id in filtered_recording_id
        get recording_times (start_time, end_time)
            delta time = end time - start_time
            run time url function
                one hour gaps from start time to end time
            for times in time function
                create URL with times
            for url in urls
                async write_export_recordings (url from time function)
'''
# functions
def get_recording_id(ip):
    try:
        recording_request = f"http://{ip}/axis-cgi/record/list.cgi?recordingid=all"
        recording_xml = requests.get(recording_request).content.decode()

        rec_dict = xmltodict.parse(recording_xml)
        recording_list = rec_dict['root']['recordings']['recording']
        filtered_recording_id = [recording['@recordingid'] for recording in recording_list]

        return filtered_recording_id
    except:
        print(f"{ip} has no recordings or HTTP request returned an error during get_recording_id")
        return []

def get_recording_times(ip, rec_id, disk_id):
    try:
        times_request = f"http://{ip}/axis-cgi/record/export/properties.cgi?schemaversion=1&recordingid={rec_id}&diskid={disk_id}"
        times_xml = requests.get(times_request).content.decode()

        times_dict = xmltodict.parse(times_xml)

        start_time = times_dict['ExportRecordingResponse']['PropertiesSuccess']['ExportProperties']['@Starttime']
        end_time = times_dict['ExportRecordingResponse']['PropertiesSuccess']['ExportProperties']['@Stoptime']

        times = list(start_time, end_time)

        return times
    except:
        print(f"{id} has no recordings or HTTP request returned an error during get_recording_times")
        return []

def times_url(ip, rec_id, disk_id, times):
    start_time = times[0]
    stop_time = times[1]
    format = "%Y-%m-%dT%H:%M:%S.%fZ"

    dt_start_time = datetime.strptime(start_time, format)
    dt_stop_time = datetime.strptime(stop_time, format)
    print(dt_start_time)
    print(dt_stop_time)

    delta = dt_stop_time - dt_start_time
    print(delta)

    '''
    note to self - continue working on the psuedocode, was extremely helpful. need to figure out
    how to best manage multiday recordings with time delta since it returns as a 5 day value
    options include just rounding up hours and losing some initial footage, and then doing it by the hour in the future
    
    '''


    # export_request_url = (f"http://{ip}/axis-cgi/record/export/exportrecording.cgi?schemaversion=1"
    # f"&recordingid={rec_id}&diskid={disk_id}&exportformat=matroska&starttime={start_time}&stoptime={end_time}")
    # print(export_request_url)

test = times_url("10.160.8.191","20230211_082645_365E_B8A44F292D8D", disk_id, ['2023-02-15T14:36:33.076983Z', '2023-02-20T18:03:40.656422Z'])
print(test)

# get all camera ip_list
with open("config.yaml", "r") as f:
    config_list = yaml.load(f, Loader=yaml.FullLoader)

ip_list = config_list["Config"]["ip"]

# for ip in ip list
# for ip in ip_list:
#     rec_ids = get_recording_id(ip)
#     for rec_id in rec_ids:
#         times_list = get_recording_times(ip, rec_id, disk_id)
#         for times in times_list:
#             urls = times_url(ip, rec_id, disk_id, times)



print("Process finished --- %s seconds ---" % (time.time() - start_time))