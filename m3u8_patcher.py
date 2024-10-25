import sys
import requests
import xml.etree.ElementTree as ET
import re

def normalize_channel_name(channel_name):
    return re.sub(r'\s*\(?4k\)?\s*|\s*\(?hd\)?\s*', '', channel_name.lower())

def update_url_tvg(playlist_lines, new_url):
    for i in range(len(playlist_lines)):
        if playlist_lines[i].startswith("#EXTM3U"):
            current_url_tvg_match = re.search(r'url-tvg="([^"]*)"', playlist_lines[i])
            if current_url_tvg_match:
                current_url_tvg = current_url_tvg_match.group(1)
                if new_url in current_url_tvg:
                    return
                if current_url_tvg:
                    new_url_tvg = f'{current_url_tvg}; {new_url}'
                else:
                    new_url_tvg = new_url
                playlist_lines[i] = re.sub(r'url-tvg="[^"]*"', f'url-tvg="{new_url_tvg}"', playlist_lines[i])
            break

def main(playlist_file, epg_url):
    try:
        with open(playlist_file, 'r') as file:
            playlist_lines = file.readlines()

        response = requests.get(epg_url)
        response.raise_for_status()
        epg_content = response.text
        epg_content = epg_content.replace('&', '&amp;')

        channels = []
        root = ET.fromstring(epg_content)
        for channel in root.findall('channel'):
            tvg_id = channel.get('id')
            display_name = channel.find('display-name').text if channel.find('display-name') is not None else None
            if tvg_id and display_name:
                channels.append({'channelName': display_name, 'tvgId': tvg_id})

        update_url_tvg(playlist_lines, epg_url)

        updated_playlist_lines = []
        
        for line in playlist_lines:
            if line.startswith("#EXTINF"):
                for channel in channels:
                    normalized_channel_name = normalize_channel_name(channel['channelName'])
                    normalized_line = normalize_channel_name(line)
                    if normalized_channel_name in normalized_line:
                        line = re.sub(r'tvg-id="[^"]*"', f'tvg-id="{channel["tvgId"]}"', line)
                        break
                    elif normalized_channel_name.replace('channel', 'ch') in normalized_line.replace('channel', 'ch'):
                        line = re.sub(r'tvg-id="[^"]*"', f'tvg-id="{channel["tvgId"]}"', line)
                        break
            updated_playlist_lines.append(line)

        with open(playlist_file, 'w') as file:
            file.writelines(updated_playlist_lines)

        print(f"Patched '{playlist_file}' with new tvg-id values and tvg-url.")

    except FileNotFoundError:
        print(f"Error: The file '{playlist_file}' does not exist.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching EPG URL: {e}")
    except ET.ParseError:
        print("Error: Failed to parse the EPG XML.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py playlist.m3u8 \"http://example.com/epg.xml\"")
        sys.exit(1)

    playlist_file = sys.argv[1]
    epg_url = sys.argv[2]
    main(playlist_file, epg_url)
