# L4D2query

Library to query additional server data from L4D2 servers. Hacked together in 4 hours because
someone messaged me on Steam to ask how to query campaign difficulty and I didn't know at the time.

## Requirements

Python >=3.7, no external dependencies

## Install

`python3 setup.py install`

## API

### Functions

* `l4d2query.query_serverdetails(address, engine_build, timeout=DEFAULT_TIMEOUT, encoding=DEFAULT_ENCODING)`

### Parameters

* address: `Tuple[str, int]` - Address of the server.
* engine_build: `int` - Engine build number, see next section for more details.
* timeout: `float` - Timeout in seconds. Default: 3.0
* encoding: `str` or `None` - String encoding, None disables string decoding. Default: utf-8

### Return Values

* query_serverdetails: TokenPacket

### Exceptions

* `l4d2query.BufferExhaustedError` - Response too short
* `socket.timeout` - No response
* `socket.gaierror` - Address resolution error

## Engine build number

The engine build number parameter was added in version 2.0.0. It has to match the value of the
server software or the request will not be answered and a `socket.timeout` exception will be
raised. At the time of writing the correct value has just changed from 2211 to 2212 and this
might continue in the future. There is no reliable automated way to find out this number
because it's hardcoded in the game binary. A possible workaround would be to query the server
with python-a2s and use the returned version string (for example "2.2.1.2") and parse it into
an integer representation. This method has not been tested across version changes though and
might not actually be suitable to make the library future-proof.

## Examples

```py
>>> import l4d2query
>>> address = ("127.0.1.1", 27015)
>>> l4d2query.query_serverdetails(address, 2212)
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
