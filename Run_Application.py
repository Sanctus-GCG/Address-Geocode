#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2013 Godwin Effiong

'''
    DAM-Geocoder: geocodes lists of addresses stored in SQL Server database or csv file
    Copyright (C) 2013 Godwin Effiong

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import datetime
import xml.dom.minidom

#import DatabaseConnection as dbConnection
import GeocodeAddress as ga
import ExtractAddressesFromXML as exml
import DatabaseConnection as dbConn

now = datetime.datetime.now()
file_name = now.strftime("%Y%m%d_%H%M%S")

XML_STAGING = 'XML_Files\{}.xml'.format(file_name)
XML_FINAL = 'XML_Files\{}_FINAL.xml'.format(file_name)
GEOCODE_RESULTS_CSV = 'CSV_Files\{}_GeocodeResult.csv'.format(file_name)

def main():   
   db = dbConn.DatabaseConnection()
   ext = exml.ExtractAddressesFromXML()
   geo = ga.GeocodeAddress()
      
   dbSelect = db.sql_select()         
   if dbSelect:
      # redirect to Google API and perform geocoding
      geo.api_connect(dbSelect, XML_STAGING)            
   
      ## grab the google XML files for each address   
      ext.transform_resultset(XML_STAGING, XML_FINAL)   
      ext.add_xml_header(XML_FINAL)   
      ## strip out the XML #create the address list from the XML
      xml_file = xml.dom.minidom.parse(XML_FINAL)   
      address_list = ext.get_xml_nodes(xml_file) 
   
      ## insert the result to the sql database
      db.sql_insert(address_list)   
      ## update the database fields
      db.sql_update()   
      # get data for eMerge   
      db.get_eMerge()
      #close the connection
      db.close_connection()
   else:
       #is None:
      db.close_connection()
      print('Empty address list...geocode process terminated\nPress "Enter" to Continue')
      raw_input()
      return None

   raw_input()
   
if __name__ == '__main__':
   main() 