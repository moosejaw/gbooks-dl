"""
Many thanks to youtube-dl project for providing a solution to the 'CONSENT' problem.
"""
import re
import random
import http.client
from typing import Optional
from http.cookies import SimpleCookie, Morsel


class GoogleCookie(SimpleCookie):
    """
    Custom class for handling cookies when using the Google provider.

    We require some meaningful cookie data to be captured when we
    run the download process. We also need to set the 'CONSENT'.
    """
    def add_consent(self) -> None:
        consent_in_cookie = self.get('CONSENT') is not None
        if consent_in_cookie:
            if self._consent_is_pending():
                consent_id = self._get_consent_id()
                self._set_consent(consent_id)
        else:
            self._set_consent()

    def _consent_is_pending(self) -> bool:
        return 'PENDING' in self['CONSENT'].value

    def _get_consent_id(self) -> Optional[str]:
        match = re.match(r'PENDING\+(?P<num>\d+)', self['CONSENT'].value)
        if match is not None:
            return match.groupdict().get('num')
        return None

    def _set_consent(self, consent_id: Optional[str] = None) -> None:
        if consent_id is None:
            consent_id = random.randint(100, 999)
        consent_token = f'YES+cb.20210328-17-p0.en+FX+{consent_id}'
        self['CONSENT'] = Morsel()
        self['CONSENT'].set(
            'CONSENT',
            consent_token,
            consent_token
        )

    def output(self, **kw) -> str:
        return super().output(header='', sep=';').lstrip()

    @property
    def consent_id(self) -> str:
        return self._get_consent_id()


class GoogleCookieMixin:
    @staticmethod
    def extract_cookies_from_response(res: http.client.HTTPResponse) -> Optional[dict[str, str]]:
        # Set cookie
        morsels = [
            v.split(';')[0]
            for k, v in res.info().items()
            if k == 'Set-Cookie'
        ]
        if morsels:
            return {'cookie': GoogleCookie('; '.join(morsels)).output()}
        return None
