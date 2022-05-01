
 # -*- coding: utf-8 -*-
import asyncio
import random
import re
import random
from aiohttp import web
from cbpi.api import *
import os, re, threading, time
from subprocess import call
import random

import logging
import sys

from pyownet import protocol


logger = logging.getLogger(__name__)


"""
async def getSensors():
    device = None
    debug = False
    host = "localhost"
    port = 4304
    sensorList = []

    async with OWFS() as ow:
        if debug:
            await ow.add_task(mon, ow)
        s = await ow.add_server(host, port)
        if device:
            device = device.rsplit("/", 1)[-1]
            sensorList.append(device)
            d = await ow.get_device(device)
            for f in d.fields:
                print(f)
        else:
            for b in s.all_buses:
                for d in b.devices:
                    p = "/" + "/".join(d.bus.path) + "/" + d.id
                    print(p)

    
    return(sensorList)
        
"""
async def getSensors():

    sensorList = []

    if len(sys.argv) >= 2:
        args = sys.argv[1:]
    else:
        args = ['localhost']
    for netloc in args:
        print('{0:=^33}'.format(netloc))
        try:
            host, port = netloc.split(':', 1)
        except ValueError:
            host, port = netloc, 4304
        try:
            proxy = protocol.proxy(host, port)
        except (protocol.ConnError, protocol.ProtocolError) as err:
            print(err)
            continue
        pid = None
        ver = None
        try:
            pid = int(proxy.read('/system/process/pid'))
            ver = proxy.read('/system/configuration/version').decode()
        except protocol.OwnetError:
            pass
        print('{0}, pid = {1:d}, ver = {2}'.format(proxy, pid, ver))
        print('{0:^17} {1:^7} {2:>7}'.format('id', 'type', 'temp.'))
        for sensor in proxy.dir(slash=False, bus=False):
            sensorList.apend(sensor)
            stype = proxy.read(sensor + '/type').decode()
            try:
                temp = float(proxy.read(sensor + '/temperature'))
                temp = "{0:.2f}".format(temp)
            except protocol.OwnetError:
                temp = ''
            print('{0:<17} {1:<7} {2:>7}'.format(sensor, stype, temp))




        return(sensorList)

class ReadThread (threading.Thread):

    value = 0
    def __init__(self, sensor_name):
        threading.Thread.__init__(self)
        self.value = 0
        self.sensor_name = sensor_name
        self.runnig = True
        logger.info('***************************************Init Thread**********************************************')

    def shutdown(self):
        pass

    def stop(self):
        self.runnig = False

    def run(self):
        logger.info('***************************************RUN Thread**********************************************')

        while self.runnig:
            try:                
                if self.sensor_name is None:
                    return
                #with open('/sys/bus/w1/devices/w1_bus_master1/%s/w1_slave' % self.sensor_name, 'r') as content_file:
                with open("/mnt/1wire/" + self.sensor_name + "/temperature", "r") as content_file:    
                    temp = content_file.read()
                    
                    self.value = float(temp)
                    #logger.info('Temp in thread--------------------------------------->%s', temp)
                    #logger.info('Name in thread--------------------------------------->%s', self.sensor_name)
                    #self.value = 99
            except:
                pass
            
            time.sleep(1)





@parameters([Property.Select(label="Sensor", options= list), 
             Property.Number(label="offset",configurable = True, default_value = 0, description="Sensor Offset (Default is 0)"),
             Property.Select(label="Interval", options=[1,5,10,30,60], description="Interval in Seconds")])
class OWFS_Temp(CBPiSensor):
    
    def __init__(self, cbpi, id, props):
        super(OWFS_Temp, self).__init__(cbpi, id, props)
        self.value = 200

    async def start(self):
        await super().start()
        list = await getSensors()
        self.name = self.props.get("Sensor")
        self.interval = self.props.get("Interval", 60)
        self.offset = float(self.props.get("offset",0))

        #self.t = ReadThread(self.name)
        #self.t.daemon = True
        def shudown():
            shudown.cb.shutdown()
        shudown.cb = self.t
        self.t.start()
    
    async def stop(self):
        try:
            self.t.stop()
            self.running = False
        except:
            pass

    async def run(self):
        while self.running == True:
            self.TEMP_UNIT=self.get_config_value("TEMP_UNIT", "C")
            #if self.TEMP_UNIT == "C": # Report temp in C if nothing else is selected in settings
                #self.value = round((self.t.value + self.offset),2)
            #else: # Report temp in F if unit selected in settings
                #self.value = round((9.0 / 5.0 * self.t.value + 32 + self.offset), 2)
            self.value = 999
            self.log_data(self.value)
            self.push_update(self.value)
            await asyncio.sleep(self.interval)
    
    def get_state(self):
        return dict(value=self.value)


def setup(cbpi):
    cbpi.plugin.register("OWFS_Temp", OWFS_Temp)
    