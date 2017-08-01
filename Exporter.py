# Written by Ben Scholer (06/15/2017) for The Schneider Corporation.
import pypyodbc as sql
import csv
import os

database = input("Enter database name, with quotes (\"WayneCountyIN\"): ")

# Locate the database on the servers.
finderConnection = sql.connect('Driver={SQL Server};'
                               'Server=tsc-gis-sql1;'
                               'Database=WebGIS;'
                               'uid=webgis;pwd=Figure This Out.')
finderCursor = finderConnection.cursor()
SQLCommand = "SELECT ReadServerID FROM TargetDatabases WHERE TargetDatabase = '" + database + "'"
finderCursor.execute(SQLCommand)
server = str(finderCursor.fetchone())[1:-2]
print("Database located on tsc-gis-sql" + server)

# Connect up to that database on the correct server
connection = sql.connect('Driver={SQL Server};'
                         'Server=tsc-gis-sql' + server + ';'
                                                         'Database=' + database + ';'
                                                                                  'uid=shopvac;pwd=sup3rsuck3r')
# Retrieve all the tables from that database
cursor = connection.cursor()
SQLCommand = "SELECT * FROM INFORMATION_SCHEMA.TABLES"
cursor.execute(SQLCommand)
tables = cursor.fetchall()

# If that database isn't in the export path, make a new folder.
if not os.path.exists(database):
    os.makedirs(database)

views = []
for table in tables:
    # Check if the table is a VIEW
    if table[3] == 'VIEW':
        # Add the name of the view to an array for later use.
        views += table[2]

print(table)
# for i in range (0, len(views)):
#     print(str(i) + " " + str(views[i]))
viewsToExportStr = input("Choose the views you would like to export, separated by commas, without spaces (1,3,4,5,7):")
viewsToExport = viewsToExportStr.split(",")
viewsToExport = map(int, viewsToExport)

for x in range(0, len(views)):
    if viewsToExport.index(x) != -1:
# Select all the columns for that table
        SQLCommand = "SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '" + views[x] + "'"
        cursor.execute(SQLCommand)
        columns = cursor.fetchall()
        tableData = []
        for column in columns:
            SQLCommand = "SELECT [" + column[3] + "] FROM " + views[x]
            # Execute
            # print(SQLCommand)
            cursor.execute(SQLCommand)
            data = cursor.fetchall()
            # Check if the item has the extra (,) around it, and get rid of it.
            # If there are single quotes, make them double
            for i in range (0, len(data)):
                if str(data[i]).startswith("("):
                    data[i] = str(data[i])[1:]
                if str(data[i]).endswith(",)"):
                    data[i] = str(data[i])[:-2]
                if str(data[i]).startswith("'"):
                    data[i] = '"' + str(data[i])[1:]
                if str(data[i]).endswith("'"):
                    data[i] = str(data[i])[:-1] + '"'
            # Add the field name to the data
            data.insert(0, column[3])
            tableData.append(data)

        # Rotate the data 90 degrees
        rotated = zip(*tableData[::-1])

        # Write it out to a file
        with open(database + '/' + table[2] + '.csv', 'w', newline = '') as f:
            writer = csv.writer(f)
            for row in rotated:
                writer.writerow(row)
# Tidy up
cursor.close()
connection.close()
