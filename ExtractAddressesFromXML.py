#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2013 Godwin Effiong

'''
    AddressGeocoder: geocodes lists of addresses stored in SQL Server database or csv file
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

import io
import os
import codecs
import fileinput
from xml.dom.minidom import Node

class ExtractAddressesFromXML:
   def __init__(self):
      #list to hold the final results - geocded addresses and the sql record ID
      ## example list is [ ('1049', '450 S Lincoln St, Denver, CO 80105 '), ('1045', '110 Broadway St, Denver, CO 80204') ]
      self.mapping = []

   ''' BEGIN: XML parsing - get formatted addresses'''
   ####--- Step 1: Strip the XML from the Geocode results
   def find_replace(self, line_item):
        ''' Remove the TagElements below:
		         a.	<?xml version="1.0" encoding="UTF-8"?>
		         b.	<GeocodeResponse>
		         c.	<status>OK</status>
		         d.	<result>
		         e.	</result>
		         f.	</GeocodeResponse>
        ''' 
        repl = {            
               '<?xml version="1.0" encoding="UTF-8"?>' : '',
               '<GeocodeResponse>' : '',
              '<status>OK</status>': '',
              '<result>': '',         
              '</result>':  '',
              '</GeocodeResponse>': '',
           
              ## fixes error of failed geocodes getting wrong addresses
              ### the STATUS: ZERO_RESULTS tag occurs only on geocode fail. 
              ## Use the value as the address           
              '<status>ZERO_RESULTS</status>' : '<formatted_address>ZERO_RESULTS</formatted_address>',           
            }  
     
        for old_value, new_value in repl.iteritems():                    
           line_item = str(line_item).replace(old_value, new_value)        
    
        return line_item     

   def transform_resultset(self, source_file, dest):
      ''' call find_replace() to clean up for each line in the XML file
         and create a new (CLEAN) file for use
      '''       
       #replace the "u'" character, enclose True and False in quotes, etc, push updated data to new file
      try:
          #todo: check if file exists, then delete b4 proceeding with below      
          with codecs.open(dest, 'wb', 'utf-8') as dest_file:               
            for line in fileinput.input(source_file):          
                  line = self.find_replace(line)                
                  dest_file.write(str(line))           
      except Exception as err:
         dest_file.close()
         print("Yikes!! ETL error - xml data cleansing failed  -  {}".format(err))
         return None
      finally:
            #clean up after urself, kid
            dest_file.close()    
            print("Stripping XML metadata.")      
            #os.remove(source_file)       

   def add_xml_header(self, input_file):
      '''add the tags <GeocodeResponse> and </GeocodeResponse> 
            to header and footer of to the file'''
      try:
           with codecs.open(input_file, 'r+', 'utf-8') as f:
               content = f.read()        
               #add the <GeocodeResponse> at beginning of file:
               f.seek(0, 0)              
               f.write("<GeocodeResponse>\n" + content)
   
               #now go to end of file and insert closing braces
               f.seek(0, 2)       
               f.write("</GeocodeResponse>")
      except Exception as err:
           print("Error: {}".format(err))
      finally:
               f.close()
               print("Success...XML parsing completed") 
      
      ### return input_file

   ###----Step 2 ---- ## return just the address and zip code, strip xml out

   def get_xml_nodes(self, xml_file):
      '''
         strips ALL the xml metadata/tags and returns only
         the address and the original record id from the 
         database associated with the address

         PARAMETERS:
            doc:  the .xml file containing all the Google
                  geocoded addresses.
      '''      
      try:
         for node in xml_file.getElementsByTagName("Record"):       
            #extract the record ids
            id = node.getElementsByTagName("VisitorDataID")
            for node2 in id:
               id = ""   
               for node3 in node2.childNodes:
                  if node3.nodeType == Node.TEXT_NODE:
                     id += node3.data
     
            #extract the related addresses
            L = node.getElementsByTagName("formatted_address")      
            for node2 in L:
               formatted_address = ""   
               for node3 in node2.childNodes:
                  if node3.nodeType == Node.TEXT_NODE:
                     formatted_address += node3.data
      
            ##map the database record ID to the addresses     
            self.mapping.append( (id, formatted_address) )  
      except Exception as err:
         print err.__doc__
      finally:
         print("\nGenerating address list \nVoila...\n")      
  
      return self.mapping
   ''' END: XML parsing - get formatted addresses'''
