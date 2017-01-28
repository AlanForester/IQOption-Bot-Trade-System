# -*- coding: utf-8 -*-
"""Module for IQ Option API."""

import time
import json
import logging
import threading
import requests

from src.api.iqoption.http.login import Login
from src.api.iqoption.http.loginv2 import Loginv2
from src.api.iqoption.http.getprofile import Getprofile
from src.api.iqoption.http.auth import Auth
from src.api.iqoption.http.token import Token
from src.api.iqoption.http.appinit import Appinit
# from src.api.iqoption.http.profile import Profile
from src.api.iqoption.http.billing import Billing
from src.api.iqoption.http.buyback import Buyback
from src.api.iqoption.http.changebalance import Changebalance
from src.api.iqoption.ws.client import WebsocketClient
from src.api.iqoption.ws.chanels.ssid import Ssid
from src.api.iqoption.ws.chanels.subscribe import Subscribe
from src.api.iqoption.ws.chanels.unsubscribe import Unsubscribe
from src.api.iqoption.ws.chanels.setactives import SetActives
from src.api.iqoption.ws.chanels.candles import GetCandles
from src.api.iqoption.ws.chanels.buyv2 import Buyv2

from src.api.iqoption.ws.objects.timesync import TimeSync
from src.api.iqoption.ws.objects.profile import Profile
from src.api.iqoption.ws.objects.candles import Candles
from src.api.iqoption.ws.objects.chartdata import ChartData

# InsecureRequestWarning: Unverified HTTPS request is being made.
# Adding certificate verification is strongly advised.
# See: https://urllib3.readthedocs.org/en/latest/security.html
requests.packages.urllib3.disable_warnings()


class IQOption(object):
    """Class for communication with IQ Option API."""
    # pylint: disable=too-many-public-methods

    timesync = TimeSync()
    profile = Profile()
    candles = Candles()
    chartData = ChartData()

    def __init__(self, host, username, password, proxies=None):
        """
        :param str host: The hostname or ip address of a IQ Option server.
        :param str username: The username of a IQ Option server.
        :param str password: The password of a IQ Option server.
        :param dict proxies: (optional) The http request proxies.
        """
        self.https_url = "https://{host}/api".format(host=host)
        self.wss_url = "wss://{host}/echo/websocket".format(host=host)
        self.websocket_client = None
        self.session = requests.Session()
        self.session.verify = False
        self.session.trust_env = False
        self.username = username
        self.password = password
        self.proxies = proxies

    def prepare_http_url(self, resource):
        """Construct http url from resource url.

        :param resource: The instance of
            :class:`Resource <src.api.iqoption.http.resource.Resource>`.

        :returns: The full url to IQ Option http resource.
        """
        return "/".join((self.https_url, resource.url))

    def send_http_request(self, resource, method, data=None, params=None, headers=None):
        """Send http request to IQ Option server.

        :param resource: The instance of
            :class:`Resource <src.api.iqoption.http.resource.Resource>`.
        :param str method: The http request method.
        :param dict data: (optional) The http request data.
        :param dict params: (optional) The http request params.
        :param dict headers: (optional) The http request headers.

        :returns: The instance of :class:`Response <requests.Response>`.
        """
        # pylint: disable=too-many-arguments
        logger = logging.getLogger(__name__)
        url = self.prepare_http_url(resource)

        logger.debug(url)

        response = self.session.request(method=method,
                                        url=url,
                                        data=data,
                                        params=params,
                                        headers=headers,
                                        proxies=self.proxies)
        logger.debug(response)
        logger.debug(response.text)
        logger.debug(response.headers)
        logger.debug(response.cookies)

        response.raise_for_status()
        return response

    @property
    def websocket(self):
        """Property to get websocket.

        :returns: The instance of :class:`WebSocket <websocket.WebSocket>`.
        """
        return self.websocket_client.wss

    def send_websocket_request(self, name, msg):
        """Send websocket request to IQ Option server.

        :param str name: The websocket request name.
        :param dict msg: The websocket request msg.
        """
        logger = logging.getLogger("api")

        data = json.dumps(dict(name=name,
                               msg=msg))
        logger.debug(data)
        self.websocket.send(data)

    @property
    def login(self):
        """Property for get IQ Option http login resource.

        :returns: The instance of
            :class:`Login <src.api.iqoption.http.login.Login>`.
        """
        return Login(self)

    @property
    def loginv2(self):
        """Property for get IQ Option http loginv2 resource.

        :returns: The instance of
            :class:`Loginv2 <src.api.iqoption.http.loginv2.Loginv2>`.
        """
        return Loginv2(self)

    @property
    def auth(self):
        """Property for get IQ Option http auth resource.

        :returns: The instance of
            :class:`Auth <src.api.iqoption.http.auth.Auth>`.
        """
        return Auth(self)

    @property
    def appinit(self):
        """Property for get IQ Option http appinit resource.

        :returns: The instance of
            :class:`Appinit <src.api.iqoption.http.appinit.Appinit>`.
        """
        return Appinit(self)

    @property
    def token(self):
        """Property for get IQ Option http token resource.

        :returns: The instance of
            :class:`Token <src.api.iqoption.http.auth.Token>`.
        """
        return Token(self)

    # @property
    # def profile(self):
    #     """Property for get IQ Option http profile resource.

    #     :returns: The instance of
    #         :class:`Profile <src.api.iqoption.http.profile.Profile>`.
    #     """
    #     return Profile(self)

    @property
    def changebalance(self):
        """Property for get IQ Option http changebalance resource.

        :returns: The instance of
            :class:`Changebalance <src.api.iqoption.http.changebalance.Changebalance>`.
        """
        return Changebalance(self)

    @property
    def billing(self):
        """Property for get IQ Option http billing resource.

        :returns: The instance of
            :class:`Billing <src.api.iqoption.http.billing.Billing>`.
        """
        return Billing(self)

    @property
    def buyback(self):
        """Property for get IQ Option http buyback resource.

        :returns: The instance of
            :class:`Buyback <src.api.iqoption.http.buyback.Buyback>`.
        """
        return Buyback(self)

    @property
    def getprofile(self):
        """Property for get IQ Option http getprofile resource.

        :returns: The instance of
            :class:`Login <src.api.iqoption.http.getprofile.Getprofile>`.
        """
        return Getprofile(self)

    @property
    def ssid(self):
        """Property for get IQ Option websocket ssid chanel.

        :returns: The instance of :class:`Ssid <src.api.iqoption.ws.chanels.ssid.Ssid>`.
        """
        return Ssid(self)

    @property
    def subscribe(self):
        """Property for get IQ Option websocket subscribe chanel.

        :returns: The instance of
            :class:`Subscribe <src.api.iqoption.ws.chanels.subscribe.Subscribe>`.
        """
        return Subscribe(self)

    @property
    def unsubscribe(self):
        """Property for get IQ Option websocket unsubscribe chanel.

        :returns: The instance of
            :class:`Unsubscribe <src.api.iqoption.ws.chanels.unsubscribe.Unsubscribe>`.
        """
        return Unsubscribe(self)

    @property
    def setactives(self):
        """Property for get IQ Option websocket setactives chanel.

        :returns: The instance of
            :class:`SetActives <src.api.iqoption.ws.chanels.setactives.SetActives>`.
        """
        return SetActives(self)

    @property
    def getcandles(self):
        """Property for get IQ Option websocket candles chanel.

        :returns: The instance of
            :class:`GetCandles <src.api.iqoption.ws.chanels.candles.GetCandles>`.
        """
        return GetCandles(self)

    @property
    def buy(self):
        """Property for get IQ Option websocket buyv2 request.

        :returns: The instance of :class:`Buyv2 <src.api.iqoption.ws.chanels.buyv2.Buyv2>`.
        """
        return Buyv2(self)

    def set_session_cookies(self):
        """Method to set session cookies."""
        cookies = dict(platform="9")
        requests.utils.add_dict_to_cookiejar(self.session.cookies, cookies)
        self.getprofile() # pylint: disable=not-callable

    def connect(self):
        """Method for connection to IQ Option API."""
        response = self.login(self.username, self.password) # pylint: disable=not-callable
        self.set_session_cookies()
        self.websocket_client = WebsocketClient(self)

        websocket_thread = threading.Thread(target=self.websocket.run_forever)
        websocket_thread.daemon = True
        websocket_thread.start()

        time.sleep(3)
        self.ssid(response.cookies["ssid"]) # pylint: disable=not-callable



