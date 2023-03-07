import os
from typing import List
import aiohttp
import asyncio
import time
import requests
import xmltodict
import yaml
import pprint
from datetime import datetime, timedelta
from pathlib import Path
import logging

# create timestamp variable
timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

# get start time
start_time = time.time()

# constants
disk_id = "SD_DISK"
#year = datetime.utcnow().year
#month = str(datetime.utcnow().month).zfill(2)
#day = str(datetime.utcnow().day).zfill(2)
#date = datetime.utcnow()
#time_delta = date - timedelta(hours=1)
#l = range(24)
#times = [[date - timedelta(hours=_t) for _t in _l]
         #for _l in zip(l[1:], l[:-1])]  # this might need to change
# print(times)
#time_format = f"{year}-{month}-{day}Thh:mm:ssZ"  # YYYY-MM-DDThh:mm:ssZ

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

        filtered_recording_id = [[recording['@recordingid'], recording['video']['@height']]
                                 for recording in recording_list]

        return filtered_recording_id
    except:
        print(
            f"{ip} has no recordings or HTTP request returned an error during get_recording_id")
        return []


def get_recording_times(ip, rec_id, disk_id):
    try:
        times_request = f"http://{ip}/axis-cgi/record/export/properties.cgi?schemaversion=1&recordingid={rec_id}&diskid={disk_id}"
        times_xml = requests.get(times_request).content.decode()

        times_dict = xmltodict.parse(times_xml)

        start_time = times_dict['ExportRecordingResponse']['PropertiesSuccess']['ExportProperties']['@Starttime']
        end_time = times_dict['ExportRecordingResponse']['PropertiesSuccess']['ExportProperties']['@Stoptime']

        return start_time, end_time
    except Exception as e:
        raise FileNotFoundError(f"{rec_id} has no recordings or HTTP request returned an error during get_recording_times")


def times_url(ip, rec_id, disk_id, times, output_path: Path, height):
    try:
        start_time = times[0]
        stop_time = times[1]

        dt_start_time = datetime.strptime(start_time, FORMAT)
        dt_stop_time = datetime.strptime(stop_time, FORMAT)
        # print(dt_start_time)
        # print(dt_stop_time)

        hour_delta = timedelta(hours=1)
        #new_time = dt_start_time + hour_delta

        delta = dt_stop_time - dt_start_time
        # print(new_time)
        # print(delta)

        
        times = []

        while (dt_start_time <= dt_stop_time):
            #print(dt_start_time, end="\n")
            hour = dt_start_time.strftime("%H")
            hour_output_path = output_path / f"{hour}_{height}.mkv"
            #stop_time = ???
            #export_request_url = (f"http://{ip}/axis-cgi/record/export/exportrecording.cgi?schemaversion=1"
        #f"&recordingid={rec_id}&diskid={disk_id}&exportformat=matroska&starttime={start_time}&stoptime={end_time}")
            #urls.append([export_request_url, hour_output_path])
            dt_end_time = dt_start_time + hour_delta
            if dt_end_time > dt_stop_time:
                dt_end_time = dt_stop_time
            times.append([dt_start_time, dt_end_time, hour_output_path])
            dt_start_time += hour_delta
        
        urls = []
        for time in times:
            str_start_time = time[0].strftime(FORMAT)
            str_end_time = time[1].strftime(FORMAT)
            hour_output_path = time[2]
            urls.append([f"http://{ip}/axis-cgi/record/export/exportrecording.cgi?schemaversion=1&recordingid={rec_id}&diskid={disk_id}&exportformat=matroska&starttime={str_start_time}&stoptime={str_end_time}", hour_output_path, ip])

        #print.pprint(urls)

        return urls
    except Exception as e:
        print(start_time)
        print(stop_time)
        print(times)
        print(
            f"{ip} {rec_id} ValueError during times_url" + str(e))
        return []


#test = times_url("10.160.8.191", "20230211_082645_365E_B8A44F292D8D", disk_id, ['2023-02-15T14:36:33.076983Z', '2023-02-20T18:03:40.656422Z'], 'C:/Users/abkarnik/Desktop/test')

# for ip in ip list
#urls = []


async def fetch(session, url, output_path, ip, locks):
    # if os.path.getsize(output_path) > 0:
    #     return
    async with locks[ip]:
        print(f"Pulling data for {ip}")
        async with session.get(url) as response:
            with open(output_path, "wb") as f:
                async for chunk, _ in response.content.iter_chunks():
                # data = await response.content.read()
                # if data:
                    f.write(chunk)
        print(f"{output_path} is done")


def get_export_urls(ip_list: List[str], output_path: Path)->List[str]:
    urls = []
    for ip in ip_list:
        ip_output_path = output_path / ip
        ip_output_path.mkdir(exist_ok = True, parents = True)
        rec_ids = get_recording_id(ip)
        for rec_id, height in rec_ids:
            try:
                st, et = get_recording_times(ip, rec_id, disk_id)
            except FileNotFoundError as e:
                print(e)
                continue
            #print(times_list)
            # for times in times_list:
            dt_start_time = datetime.strptime(st, FORMAT)
            dt_end_time = datetime.strptime(et, FORMAT)
            
            dt_start_time = dt_end_time - timedelta(hours=24)
            # dt_start_time = dt_start_time + timedelta(hours=1)
            dt_start_time = dt_start_time.replace(minute=0, second=0, microsecond=0)
            for day_delta in range((dt_end_time - dt_start_time).days):
                target_day =  dt_start_time + timedelta(days=day_delta)
        
                time_output_path = ip_output_path / (f"{target_day.date()}") # replace with times

                min_time = max(dt_start_time, target_day.replace(hour=0, second=0, minute=0))
                end_time = min(dt_end_time, target_day.replace(hour=23, minute=59, second=59))
                times = [min_time.strftime(FORMAT), end_time.strftime(FORMAT)]

                time_output_path.mkdir(exist_ok = True, parents = True)
                urls.extend(times_url(ip, rec_id, disk_id, times, time_output_path, height))

    return urls


async def export_recordings(urls, locks):
    timeout = aiohttp.ClientTimeout(10000)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = []
        for url, output_path, ip in urls:
            tasks.append(fetch(session, url, output_path, ip, locks))
        htmls = await asyncio.gather(*tasks)
        for html in htmls:
            print(html)


def run():
    # get all camera ip_list
    with open("config.yaml", "r") as f:
        config_list = yaml.load(f, Loader=yaml.FullLoader)

    ip_list = config_list["Config"]["ip"]
    output_path = Path(config_list["Config"]["output_path"])

    locks = {}
    for ip in ip_list:
        locks[ip] = asyncio.Lock()

    #pprint.pprint(get_export_urls(ip_list, output_path))
    asyncio.run(export_recordings(get_export_urls(ip_list, output_path), locks))


if __name__ == '__main__':
    run()


print("Process finished --- %s seconds ---" % (time.time() - start_time))
