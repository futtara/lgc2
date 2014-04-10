#!/usr/bin/env python

import os, sys
from bottle import Bottle, request
from bottle import hook, response, route 

import apiquery

application = Bottle()
app = application
#app.DEBUG = True

@app.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'

#--------------- Define needed routes -------------------

@app.route('/')
def index():
    return  '<p>Data server for the <a href="http://data.msulocalgov.net">Montana Local Government Center Data Portal</a></p>'

@app.route('/data/<format>/<type>')
@app.route('/data/<format>/<type>/<name>')
@app.route('/data/<format>/<type>/<name>/year/<year>')
@app.route('/data/<format>/<type>/<name>/year/<year>/fields/<fields>')
@app.route('/data/<format>/<type>/<name>/fields/<fields>')
def get_the_data(format='', type='', name='', year='', fields=''):
    data = query.get_data(format, type, name, year, fields)
    return data

#---------- Main method for local developement ----------

def main():
    #data = query.get_data('json', 'city', 'all', '2010', 'all')
    data = query.get_data('json', 'county', 'all', '2009', 'Income')
    print(data)
    return data

if __name__ == '__main__':
    main()

