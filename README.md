# A simple proxy for OpenStack
This is an application of Django.

## Setup
1. Register this application in settings.py;
2. Correctly make configuration below;
```python
# Switch for this proxy
PROXY_ON = True
# URL for keystone
PROXY_360_AUTH_URL = "http://100.100.100.34"
# URL for this proxy server
PROXY_LOCATION = "localhost:9000"
```

## Test
```shell
python manager.py /path/to/proxy_360_view
```
Then you can check logs with 'DEBUG' level.
