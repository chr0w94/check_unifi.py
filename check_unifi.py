#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# check_unifi.py - A check plugin for Unifi devices via API.
# Copyright (C) 2018-2025  chr0w94
#
# Version: 1.0.0
#
# ------------------------------------------------------------------------------
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# ------------------------------------------------------------------------------

"""Unifi devices monitoring check command for various monitoring systems like Icinga and others."""

import sys, getopt
import requests
import json
import sys, getopt
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def main(argv):
    unifi_controller_addr = ''
    unifi_api_key = ''
    unifi_site_name = ''
    unifi_mode = ''
    unifi_device_mac = ''
    unifi_warn_level = ''
    unifi_crit_level = ''
    try:
        opts, args = getopt.getopt(argv,"hi:a:s:m:d:w:c:",["ifile=","ofile="])
    except getopt.GetoptError:
        print ('check_unifi.py -c <Unifi Controller IP-Addr> -a <Unifi API-Key> -s <Unifi Site-Name> -m <MODE> -d <Unifi Device MAC-Addr> -w <WARN Level> -c <CRIT LEVEL>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('check_unifi.py - Monitoring script via Unifi API')
            print('Options:')
            print('-h:   Help')
            print('-i:   Unifi Controller IP Address')
            print('-a:   Unifi API-Key')
            print("-s:   Unifi Site Name. Default is 'Default'")
            print("-m:   MODE; Available modes = cpu / memory")
            print('-d:   Unifi Device MAC Address. FORMAT:  00:11:22:33:44:55')
            print('-w:   WARN Level')
            print('-c:   CRIT Level')
            print('')
            print('Example:   check_unifi.py -i 192.168.2.1 -a Ua7t6TuB9p1q8UgVaatm4aiwobasfh12o9 -s MySite -m cpu -d 0c:ea:16:61:41:e9 -w 80 -c 90')
            sys.exit()
        elif opt in ("-i", "--controller"):
            unifi_controller_addr = arg
        elif opt in ("-a", "--api-key"):
            unifi_api_key = arg
        elif opt in ("-s", "--site"):
            unifi_site_name = arg
        elif opt in ("-m", "--mode"):
            unifi_mode = arg
        elif opt in ("-d", "--device"):
            unifi_device_mac = arg
        elif opt in ("-w", "--warn-level"):
            unifi_warn_level = arg
        elif opt in ("-c", "--crit-level"):
            unifi_crit_level = arg
    #START
    if unifi_site_name == '':
        unifi_site_name = "Default"
            
    # Header with API-Key
    headers = {
        'X-API-KEY': unifi_api_key
    }

    # Create session
    session = requests.Session()

    # Sites request
    unifi_api_url = f'https://{unifi_controller_addr}/proxy/network/integrations/v1/sites'
    response_sites = session.get(unifi_api_url, headers=headers, verify=False)

    if response_sites.status_code == 200:
        sites = response_sites.json()
        site = next((sit for sit in sites['data'] if sit['name'] == unifi_site_name), None)
        site_Id_raw = str({site['id']}).split("'")
        unifi_siteId = site_Id_raw[1]   
    else:
        print(f"Error for request sites: {response.status_code}")
        
    # Devices request
    dev_url = f'{unifi_api_url}/{unifi_siteId}/devices'
    response = session.get(dev_url, headers=headers, verify=False)

    if response.status_code == 200:
        devices = response.json()
        # Search for device with given mac-address
        device = next((dev for dev in devices['data'] if dev['macAddress'] == unifi_device_mac), None)

        if device:
            unifi_device_id_raw = {device['id']}
            unifi_device_id_raw = str(unifi_device_id_raw).split("'")
            unifi_device_id = unifi_device_id_raw[1]
            
            # Device statistics request
            stats_url = f'{unifi_api_url}/{unifi_siteId}/devices/{unifi_device_id}/statistics/latest'
            response_device = session.get(stats_url, headers=headers, verify=False)
            
            if response_device.status_code == 200:
                devices_stats = response_device.json()
                if unifi_mode == "cpu":
                    utilval = devices_stats['cpuUtilizationPct']
                elif unifi_mode == "memory":
                    utilval = devices_stats['memoryUtilizationPct']

                if int(utilval) >= int(unifi_warn_level) and int(utilval) < int(unifi_crit_level):
                    print(f"WARNING - {unifi_mode} utilization in %: {utilval}")
                    sys.exit(1)
                elif int(utilval) >= int(unifi_crit_level):
                    print(f"CRITICAL - {unifi_mode} utilization in %: {utilval}")
                    sys.exit(2)
                else:
                    print(f"OK - {unifi_mode} utilization in %: {utilval}")
                    sys.exit(0)
                    
            else:
                print(f"No statistics found.")
                
        else:
            print(f"No devices with mac-address {device_mac} found.")
    else:
        print(f"Error for request device statistics: {response.status_code}")

    # Closing session
    session.close()
        
if __name__ == "__main__":
    main(sys.argv[1:])
