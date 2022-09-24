import re
import locale
from enum import Enum, auto
from typing import Optional

from gbooks_dl.types import Headers, HeadersKind, RequestHeadersFactory
from gbooks_dl.utils import random_user_agent


class GoogleHeaderKinds(Enum):
    LOOKUP = auto
    PAGE_IMAGE = auto


class GoogleRequestHeadersFactory(RequestHeadersFactory):
    @staticmethod
    def get_headers(*, kind: Optional[HeadersKind] = None) -> Headers:
        if kind == GoogleHeaderKinds.LOOKUP:
            accept = 'application/json'
            sec_fetch_dest = 'empty'
        elif kind == GoogleHeaderKinds.PAGE_IMAGE:
            accept = 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
            sec_fetch_dest = 'image'
        else:
            accept = '*/*'
            sec_fetch_dest = 'empty'
        loc = locale.getlocale()[0]
        loc_pat = re.compile(r"(\w{2})(_)(\w{2})")
        return {
            'accept': accept,
            'accept-encoding': 'gzip',
            'accept-language': '%s,%s;q=0.6'.format(
                re.sub(
                    loc_pat,
                    lambda m: f"{m.group(1)}-{m.group(3)}",
                    loc
                ),
                re.match(
                    loc_pat,
                    loc
                ).group(1).lower()
            ),
            'sec-fetch-dest': sec_fetch_dest,
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': 1,
            'user-agent': random_user_agent()
        }
