#!/usr/bin/env python3

#program pulls in the last hour of wireless client failures depending on the network requested. Goes from the current time and then coverts to epoch and then subtracts 60 minutes
#You can invoke the program with the following from a command line:
#export FLASK_APP=wireless_failure.py
#flask run --host=0.0.0.0

import requests
import cred
from pprint import pprint
from flask import Flask, render_template, redirect, flash, Markup
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField, validators

#custom variables for the program imported from the cred.py file located in the same directory
key = cred.key
org = cred.org

#Main URL for the Meraki Platform
dashboard = "https://dashboard.meraki.com/api/v0"
#api token and other data that needs to be uploaded in the header
headers = {'X-Cisco-Meraki-API-Key': (key), 'Content-Type': 'application/json'}

#Query the networks in the Organization and then list them so that you can choose which one to look at for wirless client failures

networksinorg_url = dashboard + '/organizations/%s/networks' % cred.org
networksinorg_get = requests.get(networksinorg_url, headers=headers)
networksinorg_get_json = networksinorg_get.json()

#BUILD FORM FIELDS AND POPULATE DROPDOWN 
class wireless_errors(FlaskForm):
    #NETWORK DROPDOWN
    networks = networksinorg_get_json
    cleannetworks = []
    for network in networks:
        for key, value in network.items():
            if key == 'id':
                net_id = value
            elif key == 'name':
                net_name = value
            else:
                continue
        cleannetworks.append([net_id,net_name])
    cleannetworks.sort(key=lambda x:x[1])
    cleannetworks.insert(0, [None, '* Choose...'])
    networkField = SelectField(u'Network Name', choices = cleannetworks)
    submitField = SubmitField('Submit')

#MAIN PROGRAM
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Ikarem123'

@app.route('/', methods=['GET', 'POST'])
def provision():
    form = wireless_errors()
    if form.validate_on_submit():
        message = []
        postNetwork = form.networkField.data

        #fully formed URL
        wireless_failures_url = dashboard + '/networks/%s/failedConnections?timespan=3600' % postNetwork

        #get request
        wireless_failures_get = requests.get(wireless_failures_url, headers=headers)
        wireless_failures_json = wireless_failures_get.json()

        #return the data for the submit page
        for data in wireless_failures_json:
            flash("Client MAC: " + data["clientMac"] + " Failure Step: " + data["failureStep"] + " Failure: " + data["type"])
            
        return redirect('/submit')

        
    return render_template('index.html', title='Meraki Device Provisioning', form=form)

@app.route('/submit')
def submit():
   return render_template('submit.html')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')