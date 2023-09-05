import json
import requests


def fetch_m3u_lines(iptv_server, iptv_username, iptv_password, keywords):
    data = fetch_data(iptv_server, iptv_username, iptv_password)
    channels = parse_data(json.loads(data), keywords)
    return to_m3u_file(channels, f'{iptv_server}/{iptv_username}/{iptv_password}')


def fetch_data(iptv_server, iptv_username, iptv_password):
    url = f'{iptv_server}/panel_api.php?username={iptv_username}&password={iptv_password}'
    print(f'=== {url}')
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        print(f"Successfully retrieved data from the IPTV server")
        chunk_size = 1024
        return b''.join(response.iter_content(chunk_size)).decode('utf-8')
    else:
        print(f"Failed to retrieve data from the IPTV server. Status code: {response.status_code}")


def parse_data(data, keywords):
    available_channels = data['available_channels'].values()
    return list(map(lambda c: map_channel(c), filter(lambda chan: is_good_channel(chan, keywords), available_channels)))


def to_m3u_file(channels, link_prefix):
    sorted_channels = sorted(channels, key=lambda x: x["name"].lower())
    lines = ['#EXTM3U', '#EXT-X-SESSION-DATA:DATA-ID="com.xui.1_5_5r2"']
    for c in sorted_channels:
        name = c['name']
        icon = c['icon']
        cat_name = c['category_name']
        lines.append(f'#EXTINF:-1 tvg-id="" tvg-name="{name}" tvg-logo="{icon}" group-title="{cat_name}",{name}')
        lines.append(f'{link_prefix}/{c["id"]}.ts')
    return lines


def map_channel(obj):
    return {
        "id": obj['stream_id'],
        "name": obj['name'],
        "category_id": obj['category_id'],
        "category_name": obj['category_name'],
        "icon": obj['stream_icon']
    }


def is_good_channel(channel, keywords):
    return any(keyword.lower() in channel['name'].lower() for keyword in keywords)
