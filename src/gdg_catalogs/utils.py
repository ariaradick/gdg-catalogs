import validators
from pathlib import Path
from urlpath import URL

def _to_list(a):
    if type(a) == str:
        return [a]
    else:
        return list(a)

def _convert_time(gfdl_timestamp):
    t = gfdl_timestamp
    if len(t) == 4:
        time = t + '0101'
    elif len(t) == 6:
        time = t + '01'
    elif len(t) > 8:
        if 'T' in t:
            time = t
        else:
            time = t[:8] + 'T' + t[8:]
    else:
        time = t
    return datetime.fromisoformat(time).replace(tzinfo=timezone.utc)

def _convert_timerange(gfdl_timerange):
    return [_convert_time(t) for t in gfdl_timerange.split('-')]

def parse_path(path: str) -> URL | Path:
    if validators.url(path):
        return URL(path).resolve()
    else:
        return Path(path).resolve()
