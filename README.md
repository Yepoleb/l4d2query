# L4D2query

Library to query additional server data from L4D2 servers.

## Requirements

Python >=3.7, no external dependencies

## Install

`python3 setup.py install`

## API

### Functions

* `l4d2query.query_serverdetails(address, timeout=DEFAULT_TIMEOUT, encoding=DEFAULT_ENCODING)`

### Parameters

* address: `Tuple[str, int]` - Address of the server.
* timeout: `float` - Timeout in seconds. Default: 3.0
* encoding: `str` or `None` - String encoding, None disables string decoding. Default: utf-8

### Return Values

* info: TokenPacket

### Exceptions

* `l4d2query.BufferExhaustedError` - Response too short
* `socket.timeout` - No response
* `socket.gaierror` - Address resolution error

## Examples

```py
>>> import l4d2query
>>> address = ("127.0.1.1", 27015)
>>> l4d2query.query_serverdetails(address)
TokenPacket(header=b'\xff\xff\xff\xff\x00\x00\x00\x00', type=41736, unknown_1=0, payload_size=154,
unknown_2=2, data={'GameDetailsServer': {'System': {'network': 'LIVE', 'access': 'friends'},
'Server': {'name': 'Yepoleb', 'Server': 'listen', 'adrlocal': '127.0.1.1:27015',
'adronline':'127.0.1.1:27015'}, 'Members': {'numPlayers': 1, 'numSlots': 4}, 'game':
{'state': 'game', 'Mode': 'coop', 'vanilla': 0, 'campaign': 'L4D2C1', 'chapter': 1,
'MissionInfo': {'Version': '1', 'builtin': '1', 'addon': 0,
'DisplayTitle': '#L4D360UI_CampaignName_C1', 'Author': 'Valve',
'Website': 'http://store.steampowered.com', 'MissionFile': 'missions/campaign1.txt',
'workshopid': 0, 'InfectedOnly': 0, 'SurvivorSet': 2}, 'ModeInfo': {'DisplayTitle': '',
'workshopid': 0, 'addon': 0}, 'difficulty': 'normal', 'maxrounds': 3, 'dlcrequired': 0},
'InetSearchServerDetails': {'timestamp': 0, 'pingxuid': 0}}})
```

## License

MIT
