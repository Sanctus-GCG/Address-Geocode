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

from temboo.Library.Google.Geocoding import GeocodeByAddress
from temboo.core.session import TembooSession
import os
import codecs

class GeocodeAddress:
   def __init__(self):
      ### Instantiate the choreography, using a previously instantiated TembooSession object, eg:
      ### replace the Account_Name, App_Key_Name, AppKey_Value
	  ## with your actual keys from Temboo
	  session = TembooSession('ACCOUNT_NAME', 'APP_KEY_NAME', 'APP_KEY_VALUE')      
      
      self.geocodeByAddressChoreo = GeocodeByAddress(self.session)
      # Set inputs and get an InputSet object for the choreo
      self.geocodeByAddressInputs = self.geocodeByAddressChoreo.new_input_set()       

   ''' BEGIN: Geocode - get formatted address'''
   def api_connect(self, db_conn, stage_file):  
      '''
         creates a connection to the Google Geocode API
         appends each of the geocoded address(es) to one big XML file
      
         PARAMETERS: 
            db_conn:    cursor; a result set with records from a sql query
            stage_file:    the file to append all the XML to
      '''    
      for record_id, record in db_conn:      
         ###remove the closing/opening braces and special characters, eg "u'"
         record = str(record).replace("u'", "").replace("'", "").replace("[", "").replace("]", "") 
      
         # Execute choreo
         self.geocodeByAddressInputs.set_Address(record)       
         geocode_result = self.geocodeByAddressChoreo.execute_with_results(self.geocodeByAddressInputs)
         geocodeByLat = self.geocodeByAddressChoreo._make_result_set(geocode_result, None)   
         xml_result = geocodeByLat.get_Response() #returns an xml value for the address
      
         try:                    
            ## append the <Record> </Record> tags to top and bottom of each record, 
            ## and database record ID to top of each XML node
            with codecs.open(stage_file, 'ab', 'utf-8') as f:                  
               f.write('<Record>\n <VisitorDataID>{}</VisitorDataID>\n {} </Record>\n'.format(str(record_id), str(xml_result)))
               print("Calling Google Map API / Writing to file: {}\n").format(record_id)            
         except Exception as err:
            print("Ooooooooooops! Could not write to file. Record ID: {}\nError:  {}".format(record_id, err))           
         finally:
            f.close()    
      ### end for   
   
      print('Address geocoding completed.\n')
      print('Parsing XML...')
   
      return stage_file  
      ''' END: Geocode - formatted address'''