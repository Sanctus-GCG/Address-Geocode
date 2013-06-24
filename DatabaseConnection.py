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
import pyodbc as odbc

class DatabaseConnection:
   def __init__(self):
      '''
            Should be treated as non-public
            docs.python.org (9.6. Private Variables and Class-local References)

             creates a connection to database 
               and initializes SQL query
      '''   
      self.server = 'LOCALHOST'  ###'Server Name' 
      self.database = 'MyDatabase'      ## Database Name 
      self.connStr = 'DRIVER=%s;SERVER=%s;DATABASE=%s;Trusted_Connection=%s' % ('{SQL Server}', self.server, self.database, 'yes')  
      self.conn = odbc.connect(self.connStr)
      self.dbCursor = self.conn.cursor()      

   def sql_select(self):
      '''get data from sql database using the query below'''
   
      db_link = self.dbCursor #__dbconnect()   
      sql_sproc = '''EXEC dbo.Clean_RawData;'''     
      # parameters below are 0 and '' (empty field)            
      ## SELECT...WHERE IsGeocoded = 0
         ## ie only pull those records that have not been geocoded   
      sql_query = '''EXEC dbo.get_addresses ? '''

      # call sproc and commit the changes or lose it all
      db_link.execute(sql_sproc)   
      db_link.commit()   
      sql_results  = db_link.execute(sql_query, 0)  

      ## if no rows are returned
      # then clean up after yourself, kid!!      
      if sql_results.rowcount == 0:        
         return None   
  
      return sql_results
   
   #write the new geocoded addresses back to sql databas
   def sql_insert(self, address_list):   
      '''
         Inserts the newly geocoded address back into the database

         PARAMETERS:
            address_list:  a list of address tuples (ID, Address) in the form below:
               eg my_addresslist = [ ('1049', '111 Lincoln St, Denver CO 80204'), ('1045', '100 Broadway St, Denver CO 80125') ]
      '''
      db_link = self.conn
      db_cursor = self.dbCursor
      sql_query = ''' EXEC dbo.insert_after_geocode ?, ?''' 

      try:               
         #iterate through the list and insert each id and address into the sql table
         for addresses in range( len(address_list) ):   
            ## the record (address) id is                   address_list[record number][0]
            ## the actual goecoded address is found at      address_list[record number][1]            
            db_cursor.execute(sql_query, address_list[addresses][0], address_list[addresses][1] )             
            ##commit the database changes!!
            db_link.commit()    
            #inserted = db_cursor.execute(sql_query).rowcount
            print(address_list[addresses][0], address_list[addresses][1])                     
         ## end for         
      except Exception as err:
         print("Error526C Insert error: {}".format(err))
      ###   end try..except

   def sql_update(self):   
      '''
         updates from the staging "temp" table:
         populates the geocodedaddresses field in the production table,
         gets the "Address1" from the geocodedAddress
          and set the IsGeocoded flag to 1
      '''
      db_link = self.conn
      db_cursor = self.dbCursor
      sql_query = ''' EXEC dbo.update_after_geocode ?, ?, ? '''   ###{}, '', '' '''.format(0)
      try:         
         #run the query and commit the database changes
         db_cursor.execute(sql_query, 0, '', '')      
         db_link.commit()          
         print('Mission Accomplished!')         
      except Exception as err:
         print("Error526D Update error at {}".format(err.__doc__))
      ###   end try..except
   
   def get_eMerge(self):
      '''
         pulls required eMerge fields from the
         VisitorData table and writes to
         .csv and .xlsx files
      '''
      pass

   def close_connection(self):

      ''' closes the database connection    
         In CPython, connections are automatically closed when they are deleted,
         but you should call this if the connection is referenced in more than one place. 
      '''
      self.conn.close()
