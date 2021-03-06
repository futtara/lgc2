# Output json from DB query

import os, sys, json
from urllib import parse
#from ordereddict import OrderedDict
from collections import OrderedDict
from copy import deepcopy

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

myhost = os.environ['OPENSHIFT_MYSQL_DB_HOST']
myport = os.environ['OPENSHIFT_MYSQL_DB_PORT']
myuser = os.environ['OPENSHIFT_MYSQL_DB_USERNAME']
mypw = os.environ['OPENSHIFT_MYSQL_DB_PASSWORD']
mydb = 'lgc'

def get_sql(type, name, year, fields):

    sql = "SELECT * FROM info2 WHERE "
    #sql = "SELECT * FROM info WHERE "

    if type.lower() == 'county':
        sql += "type='County' "
    else:
        sql += "type='City' "

    if len(name) > 0 and name.lower() != 'all':
        name = parse.unquote_plus(name)
        #name = name.replace('+', ' ');
        quoted_names = "','".join(name.split(','))
        sql += "AND name IN ('%s') " % (quoted_names)

    if len(year) > 0 and year.lower() == 'all':
        sql += "AND year>1990 "

    if len(year) > 0 and year.lower() != 'all':
        if year.lower() == 'all_from_1974':
            sql += "AND year>=1974 "
        else:
            quoted_years = "','".join(year.split(','))
            sql += "AND year IN ('%s') " % (quoted_years)

    if len(fields) > 0 and fields.lower() != 'all':
        fields = parse.unquote_plus(fields)
        #fields = fields.replace('+', ' ');
        quoted_fields = "','".join(fields.split(','))
        sql += "AND label IN ('%s') " % (quoted_fields)

    sql += "AND authority>0 AND value IS NOT NULL "
    sql += "ORDER BY year, name, label, authority DESC "

    print(sql)
    return (sql)

# Handle number formatting, especially rounding errors
def niceFormat(entry):
    try:
        n = float(entry)
        n10 = 10 * n
        if n10 != int(n10):
            return round(100 * n)/100
        elif n != int(n):
            return round(n10)/10
        else:
            return entry
    except ValueError:
        return entry

def get_data(format, type, name, year, fields):
    conn = pymysql.connect(host=myhost, user=myuser, passwd=mypw, db=mydb, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
     
    sql = get_sql(type, name, year, fields)
    cursor.execute(sql)
     
    # lists and tuples become arrays, dictionaries become objects
    all_data = OrderedDict()
    data_row = OrderedDict()
    year_array = OrderedDict()

    rows = cursor.fetchall()

  # Prepare to read data, if available
    try:
        the_year = rows[0]['year']
        the_name = rows[0]['name']
    except IndexError:
        e = sys.exc_info()[0]
        print("Error: %s" % e)

        conn.close()
        result = { 'error': 'No data available for this request' }
        return json.dumps(result)

    last_row_name = 0
    last_row_year = 0
    last_row_label = 0
    for row in rows:
        # Ignore duplicate info (single type in query)
        if row['name'] == last_row_name:
            if row['year'] == last_row_year:
                if row['label'] == last_row_label:
                    continue

        # Group by year
        if row['year'] == the_year:
            # Group by county or city name
            if row['name'] == the_name:
                data_row[row['label']] = niceFormat(row['value'])
            else:
                # Append existing county data
                year_array[the_name] = data_row.copy()

                # Start new county or city name
                data_row.clear()
                data_row[row['label']] = niceFormat(row['value'])
                the_name = row['name']
        else:
            # Append existing county or city data
            year_array[the_name] = data_row.copy()
            # Append existing year data
            all_data[the_year] = deepcopy(year_array);

            # Start new year and county or city name
            year_array.clear()
            data_row.clear()
            data_row[row['label']] = niceFormat(row['value'])

            the_name = row['name']
            the_year = row['year']

        # Keep track of data seen
        last_row_name = 0
        last_row_year = 0
        last_row_label = 0

    # Handle last data item
    # Append existing county or city data
    year_array[the_name] = data_row.copy()
    # Append existing year data
    all_data[the_year] = deepcopy(year_array);

    conn.close()
    json_data = json.dumps(all_data)
    return (json_data)

#---------- Main method for local developement ----------

def main():
    #all_data = get_data('json', 'city', 'all', '2010', 'all')
    all_data = get_data('json', 'county', 'all', '2009', 'Income')
    print(all_data)

if __name__ == '__main__':
    main()
