AddressGeocode
==============

Returns zip codes for USA, Canada, China, UK addresses from a batch/list in a csv, .txt file or SQL Server database

**Dependencies**
- Temboo account (www.temboo.com)
- pyodbc (http://code.google.com/p/pyodbc/)

**Input**

List of addresses in a .csv file or SQL Server database in the format:
- “123 Main Street, New York, NY”
- “3000 Broadway St, Louisville, IL”
- “789 Elm Street, Los Angeles, CA”

**Output**
- “1234 Main Street, New York, NY 10044”
- “3000 Broadway St, Louisville, IL 62858”
- “789 Elm Street, Los Angeles, CA 90065”
