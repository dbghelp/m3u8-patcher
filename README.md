# m3u8 patcher

Scans for `tvg-id` values of channels from a provided EPG XML and patches the `tvg-id` of channels and `url-tvg`in an M3U8 playlist to use the specified EPG XML.

## Usage

```
python m3u8_patcher.py playlist.m3u8 "http://example.com/epg.xml"
```
