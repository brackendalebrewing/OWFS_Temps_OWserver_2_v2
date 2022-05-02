
# -*- coding: utf-8 -*-
import asyncio
import os
import sys
import random
import re
import random
from aiohttp import web
from cbpi.api import *
import os, re, threading, time
from subprocess import call
import random
import logging

from pyownet import protocol

logger = logging.getLogger(__name__)



def getSensors(type):

    logger.info('***************************************get sensors **********************************************')	

    sensorList = []
    try:
            proxy = protocol.proxy()
    except (protocol.ConnError, protocol.ProtocolError) as err:
            print(err)

    for sensor in proxy.dir(slash=False, bus=False):
        
        stype = proxy.read(sensor + '/type').decode()
        logger.info('Sensor name and type--------------------------------------->%s  %s', sensor,stype)
        if (stype == type):
            sensorList.append(sensor)
            #logger.info('Sensor name and type--------------------------------------->%s  %s', sensor,stype)


    logger.info('***************************************Sensor List--------> %s ',sensorList)
    return(sensorList)



class ReadThread (threading.Thread):
    
    value = [0]
    def __init__(self, sensor_name ,dataName):
        threading.Thread.__init__(self)
        self.value = [0]
        self.sensor_name = sensor_name
        self.dataName = dataName
        self.runnig = True
        logger.info('***************************************Init Thread**********************************************')
        logger.warning('--------------------------dataName -------------------->%s',dataName)
    try:
            proxy = protocol.proxy()
    except (protocol.ConnError, protocol.ProtocolError) as err:
            logger.info('************************owfs server fail--------')
            print(err)        

        

    def shutdown(self):
        pass

    def stop(self):
        self.runnig = False

    def run(self):
        
        #cache = '/uncached'
        cache = ''
        while self.runnig:
            #logger.warning('***************************************RUN Thread**********************************************')
            try:                
                if self.sensor_name is None:
                    return

                #logger.warning('--------------------------sensor name -------------------->%s',(  cache + self.sensor_name + self.dataName) )
                proxy = protocol.proxy()
                 
                temp  = float( proxy.read(  cache + self.sensor_name + self.dataName) )
                self.value[0] = float(temp)
                #logger.warning('--------------------------temp -------------------->%s',self.value[0] )
            except:
                logger.warning('--------------------------Temp Disconected -------------------->%s',self.sensor_name )
                
                pass
            
            time.sleep(1)






@parameters( [Property.Select(label="Sensor", options= getSensors("DS18B20") ), 
             Property.Number(label="offset",configurable = True, default_value = 0, description="Sensor Offset (Default is 0)"),
             Property.Select(label="Interval", options=[1,5,10,30,60], description="Interval in Seconds")])
class OWFS_Temp(CBPiSensor):
    
    def __init__(self, cbpi, id, props):
        super(OWFS_Temp, self).__init__(cbpi, id, props)
        self.value = 200

    async def start(self):
        
        await super().start()
        self.name = self.props.get("Sensor")
        self.interval = self.props.get("Interval", 60)
        self.offset = float(self.props.get("offset",0))
        self.dataName = '/temperature'

        dataName = '/temperature'
        self.t = ReadThread(self.name , self.dataName )
        self.t.daemon = True
        
        def shudown():
            shudown.cb.shutdown()
        shudown.cb = self.t
        self.t.start()
        #logger.info('**************************************start owfs**********************************************')
    
    async def stop(self):
        try:
            self.t.stop()
            self.running = False
        except:
            pass

    async def run(self):
        while self.running == True:
            
            self.TEMP_UNIT=self.get_config_value("TEMP_UNIT", "C")
            #logger.info('self.get_config_value--------------------------------------->%s', (self.TEMP_UNIT) )
            if self.TEMP_UNIT == "C": # Report temp in C if nothing else is selected in settings
                 #logger.info('self.value --------------------------------------->%s', (self.t.value) )
                 self.value = round((self.t.value[0] + self.offset),2)
                 
            else: # Report temp in F if unit selected in settings
                 self.value = round((9.0 / 5.0 * self.t.value[0] + 32 + self.offset), 2)
            #self.value = 
            #logger.info('self.value --------------------------------------->%s', self.t.value )
            self.log_data(self.value)
            self.push_update(self.value)
            await asyncio.sleep(self.interval)
    
    def get_state(self):
        return dict(value=self.value)


def setup(cbpi):
    cbpi.plugin.register("OWFS_Temp", OWFS_Temp)
    