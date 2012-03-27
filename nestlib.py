#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 06:51:14 2012

@author: JF Casley
"""

import httplib
import urllib
import simplejson

class Nest():

    def __init__(self):
        self.connection = None
        self.auth = {}
        self.access_token = None
        self.transport_host = None
        self.transport_port = None
        self.user = None
        self.userid = None
        self.status = {}
        
    def login(self, username, password):
        params = urllib.urlencode({'username': username, 'password': password})
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/plain',
                   'User-Agent': 'Nest/1.1.0.10 CFNetwork/548.0.4'}
        self.connection = httplib.HTTPSConnection('home.nest.com')
        
        self.connection.request('POST', '/user/login', params, headers)
        response = self.connection.getresponse()
        if response.status == 200:
            auth = response.read()
            decoder = simplejson.JSONDecoder()
            self.auth = decoder.decode(auth)
            self.access_token = self.auth['access_token']
            # at this time (2012/03/26) there are three urls in the auth packet
            # the one I am interested in at this time is the transport url
            # i.e. https://xxxxxx.transport.nest.com:9443
            urls = self.auth['urls']
            transport_url = urls['transport_url']
            (junk, self.transport_host) = transport_url.split('//')
            self.user = self.auth['user']
            self.userid = self.auth['userid']
            return True
        else:
            return False
    
    def get_status(self):
        if self.access_token:
            authorization = "Basic %s" % self.access_token
            headers = {'Host': self.transport_host,
                       'User-Agent': 'Nest/1.1.0.10 CFNetwork/548.0.4',
                       'Authorization': authorization,
                       'X-nl-user-id': self.userid,
                       'X-nl-protocol-version': '1',
                       'Accept-Language': 'en-us',
                       'Connection': 'keep-alive',
                       'Accept': '*/*'}
            url = "/v2/mobile/%s" % self.user

            self.connection = httplib.HTTPSConnection(self.transport_host)
            self.connection.request('GET', url, None, headers)
            response = self.connection.getresponse()
            if response.status == 200:
                status = response.read()                
                decoder = simplejson.JSONDecoder()
                self.status = decoder.decode(status)
                self.structure_id = self.status['user'][self.userid]["structures"][0].split('.')[1]
                # TODO add support for multiple devices
                self.device_id = self.status['structure'][self.structure_id]['devices'][0].split('.')[1]
                self.current_temp = round(self.status['shared'][self.device_id]['current_temperature'] * 1.8 + 32)
                self.target_temp = round(self.status['shared'][self.device_id]['target_temperature'] * 1.8 + 32)
                
        
    def close(self):
        if self.connection:
            self.connection.close()
            return True

