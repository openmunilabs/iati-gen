# -*- coding: utf-8 -*-
import csv

from string import Template

from datetime import datetime
timestamp=datetime.now().replace(microsecond=0).isoformat()

countries={}

#load list of country names and their codes
f=open("source/countrycodes.csv","rU")

csvreader = csv.reader(f, delimiter=',', quotechar='"')
for i, row in enumerate(csvreader):
	code2, code3, countryname=row[0], row[1], row[2]
	if i!=0:
		countries[countryname.split(",")[0].upper()]={"code2":code2, "code3":code3, "countryname":countryname}

f.close()

#load list of lat/lon for countries
f=open("source/country_latlon.csv","rU")

csvreader = csv.reader(f, delimiter=',', quotechar='"')
for i, row in enumerate(csvreader):
	code2, lat, lon=row[0], row[1], row[2]
	if i!=0:
		for country in countries:
			if countries[country]["code2"]==code2:
				countries[country]["lat"]=lat
				countries[country]["lon"]=lon

f.close()

#print countries

#import sys
#sys.exit(0)

#load list of compacts and start/end dates
f=open("source/compacts_details.csv","rU")

compacts={}

csvreader = csv.reader(f, delimiter=',', quotechar='"')
for i, row in enumerate(csvreader):
	#Organizational Unit,Compact Code,Original Compact Amount,Current Compact Amount,Compact Signing,Entry into Force,Compact Closure,Notes
	if i!=0:
		compact, country, code, eif, closure=row[0], row[1], row[2], row[6], row[7]
		compacts[code]={"compact":compact, "eif":eif, "closure":closure, "country":country}

f.close()

#load list of lat/lon for countries
f=open("source/country_latlon.csv","rU")

csvreader = csv.reader(f, delimiter=',', quotechar='"')
for i, row in enumerate(csvreader):
	code2, lat, lon=row[0], row[1], row[2]
	if i!=0:
		for country in countries:
			if countries[country]["code2"]==code2:
				countries[country]["lat"]=lat
				countries[country]["lon"]=lon

f.close()

#print countries

import codecs

f = codecs.open("data/finance.csv", 'r', encoding='latin1')

mcc_id="US-18" # which one is actual ID?
mcc_id="US-USG-MCC-18"

def fiscal_date(date):
	#translates "Fiscal Year, Fiscal Quarter" into ISO date for the start date of the quarter
	try:
		fy,fq=date.split(',')
		fy=fy.strip()
		fq=fq.strip()
		
		fy=fy[3:]
		fy=int(fy)
		
		if fq=="FQ 1":
			return str(fy-1)+"-"+"09-01"
		elif fq=="FQ 2":
			return str(fy-1)+"-"+"12-01"
		elif fq=="FQ 3":
			return str(fy)+"-"+"03-01"
		elif fq=="FQ 4":
			return str(fy)+"-"+"06-01"
		else:
			return "n/a"
	except:
		return "n/a"

#Region,Fund,CountryID,Country,ProjectID,Project,ActivityID,Activity,DAC CODE,DACName,FY,FQ,Disbursement,Obligation
# header for finance.csv

#generate hierachy of projects

fin={}

for i, line in enumerate(f):
	line=line.rstrip('\n').split(",")
	if i==0:
		continue
	if i>0:

		region=line[0].strip()
		fund=line[1].strip()
		country_id=line[2].strip()
		country=line[3].strip()
		project_id=line[4].strip()
		project=line[5].strip()
		activity_id=line[6].strip()
		activity=line[7].strip()
		dac_code=line[8].strip()
		dac_name=line[9].strip()
		fy=line[10].strip()
		fq=line[11].strip()
		disbursement=line[12].strip()
		obligation=line[13].strip()

		if fund not in fin.keys():
				fin[fund]={}

		if country_id not in fin[fund].keys():
			fin[fund][country_id]={}
			fin[fund][country_id]["country"]=country
			fin[fund][country_id]["projects"]={}

		if project_id not in fin[fund][country_id].keys():
			fin[fund][country_id]["projects"][project_id]={}
			fin[fund][country_id]["projects"][project_id]["project"]=project
			fin[fund][country_id]["projects"][project_id]["activities"]={}

		if activity_id not in fin[fund][country_id]["projects"][project_id].keys():
			fin[fund][country_id]["projects"][project_id]["activities"][activity_id]={}
			fin[fund][country_id]["projects"][project_id]["activities"][activity_id]["activity"]=activity
			fin[fund][country_id]["projects"][project_id]["activities"][activity_id]["dac_code"]=dac_code
			fin[fund][country_id]["projects"][project_id]["activities"][activity_id]["dac_name"]=dac_name

			fin[fund][country_id]["projects"][project_id]["activities"][activity_id]["transactions"]=[]

		#FY,FQ,Disbursement,Obligation
		transaction={"fy":fy,"fq":fq, "disbursement":disbursement, "obligation":obligation}

		fin[fund][country_id]["projects"][project_id]["activities"][activity_id]["transactions"].append(transaction)

import json

fo=open("dump.json","w")
fo.write(json.dumps(fin, indent=4))
fo.close()


"""
for fund in fin:
	#print fund
	for country in fin[fund]:
		#print "     ", country, " ", fin[fund][country]["country"]
		for project in fin[fund][country]["projects"]:
			#print "               ", fin[fund][country]["projects"][project]["project"]
"""


header_t="""<?xml version="1.0"?>
<iati-activities generated-datetime="%s" version="1.0">"""

footer_t="""
</iati-activities>"""

compact_t=Template("""
	<iati-activity default-currency="USD" xml:lang="en">
		<reporting-org ref="$orgid" type="10">Millennium Challenge Corporation</reporting-org>

		<default-flow-type code="10">ODA</default-flow-type>
		<iati-identifier>$iatiid</iati-identifier>
		<title>$title</title>

		<recipient-country code="$countrycode">$countryname</recipient-country>

		<participating-org ref="US" role="funding" type="10">United States of America</participating-org>
		<participating-org ref="$orgid" role="extending" type="10">Millennium Challenge Corporation</participating-org>
		<participating-org role="implementing">$implorgid</participating-org>

		<default-finance-type code="110">Aid grant excluding debt reorganisation</default-finance-type>

		<collaboration-type code="1">Bilateral</collaboration-type>

		<activity-date iso-date="$startdate" type="start-actual">$startdate</activity-date>
		<activity-date iso-date="$enddate" type="end-planned">$enddate</activity-date>

		<default-aid-type code="C01">Project-type interventions</default-aid-type>
		<default-tied-status code="5">Untied</default-tied-status>
		<activity-status code="2">Implementation</activity-status>
		$relatedactivities
		<location>
		    <location-type code="PCL"/>
		    <name xml:lang="en"></name>
		    <description>$countryname</description>
		    <administrative country="$countrycode">$countryname</administrative>
		    <coordinates latitude="$lat" longitude="$lon" precision="9"/>
		</location>
	</iati-activity>
""")

project_t=Template("""
	<iati-activity default-currency="USD" xml:lang="en">
		<reporting-org ref="$orgid" type="10">Millennium Challenge Corporation</reporting-org>

		<default-flow-type code="10">ODA</default-flow-type>
		<iati-identifier>$iatiid</iati-identifier>
		<title>$title</title>

		<recipient-country code="$countrycode">$countryname</recipient-country>

		<participating-org ref="US" role="funding" type="10">United States of America</participating-org>
		<participating-org ref="$orgid" role="extending" type="10">Millennium Challenge Corporation</participating-org>
		<participating-org role="implementing">$implorgid</participating-org>

		<default-finance-type code="110">Aid grant excluding debt reorganisation</default-finance-type>

		<collaboration-type code="1">Bilateral</collaboration-type>

		<activity-date iso-date="$startdate" type="start-actual">$startdate</activity-date>
		<activity-date iso-date="$enddate" type="end-planned">$enddate</activity-date>

		<default-aid-type code="C01">Project-type interventions</default-aid-type>
		<default-tied-status code="5">Untied</default-tied-status>
		<activity-status code="2">Implementation</activity-status>
		$relatedactivities
	</iati-activity>
""")

activity_t=Template("""
	<iati-activity default-currency="USD" xml:lang="en">
		<reporting-org ref="$orgid" type="10">Millennium Challenge Corporation</reporting-org>

		<default-flow-type code="10">ODA</default-flow-type>
		<iati-identifier>$iatiid</iati-identifier>
		<title>$title</title>

		<recipient-country code="$countrycode">$countryname</recipient-country>

		<participating-org ref="US" role="funding" type="10">United States of America</participating-org>
		<participating-org ref="$orgid" role="extending" type="10">Millennium Challenge Corporation</participating-org>
		<participating-org role="implementing">$implorgid</participating-org>

		<default-finance-type code="110">Aid grant excluding debt reorganisation</default-finance-type>

		<collaboration-type code="1">Bilateral</collaboration-type>

		<activity-date iso-date="$startdate" type="start-actual">$startdate</activity-date>
		<activity-date iso-date="$enddate" type="end-planned">$enddate</activity-date>

		<default-aid-type code="C01">Project-type interventions</default-aid-type>
		<default-tied-status code="5">Untied</default-tied-status>
		<activity-status code="2">Implementation</activity-status>

		$relatedactivities
		$transactions
	</iati-activity>
""")

transaction_t=Template("""
		<transaction>
			<transaction-date iso-date="$date">$date</transaction-date>
			<transaction-type code="$code">$type</transaction-type>
			<value value-date="$date">$amount</value>
		</transaction>""")


result_t=Template("""
		<result>
			<title></title>
			<description></description>
			<indicator>
				<title></title>
				<description></description>
				<baseline>
					<value></value>
					<period>
						<preiod-start></period-start>
						<period-end></period-end>
					</period>
				</baseline>
				<actual>
					<value></value>
				</actual>
				<measure aggregation-status="" ascending="">
					<type></type>
				</measure>
			</indicator>
		</result>""")


fo=open("output/mcc-activities.xml", 'w')

fo.write(header_t % (timestamp))

#Region,Fund,CountryID,Country,ProjectID,Project,ActivityID,Activity,DAC CODE,DACName,FY,FQ,Disbursement,Obligation
# header for finance.csv


for country_id in fin["Compact"]:
	#print country_id

	country=fin["Compact"][country_id]["country"]
	orgid=mcc_id
	iatiid=mcc_id+"-"+country_id
	implorgid=country_id+"-MCA"
	title=country+" Compact"
	countrycode=country_id #update to ISO2 code later
	countryname=country

	if country_id=="KEN":
		continue

	if country_id!="NA":
		eif=compacts[country_id]["eif"]
		closure=compacts[country_id]["closure"]
	else:
		eif=""
		closure=""

	print countryname
	try:
		lat=countries[countryname.upper()]["lat"] #add geocoded lat/lon for country
		lon=countries[countryname.upper()]["lon"]
	except:
		lat=0
		lon=0

	relatedactivities=""
	for project_id in fin["Compact"][country_id]["projects"]:
		iatiid2=iatiid+"-"+project_id
		iatiid2=iatiid2.replace("&"," AND ")
		title2=fin["Compact"][country_id]["projects"][project_id]["project"]
		title2 = title2.replace("&", " AND ")

		related_child=Template("""
			<related-activity ref="$ref" type="2">$name</related-activity>""")
		params={"ref":iatiid2, #encode &amp;
				"name":title2}
		relatedactivities=relatedactivities+related_child.substitute(params)

		related_parent=Template("""
			<related-activity ref="$ref" type="1">$name</related-activity>""")

		
		project_relatedactivities=related_parent.substitute({"ref":iatiid, "name":title})

		for activity_id in fin["Compact"][country_id]["projects"][project_id]["activities"]:
			iatiid3=iatiid2+"-"+activity_id
			title3=fin["Compact"][country_id]["projects"][project_id]["activities"][activity_id]["activity"]
			title3=title3.replace("&", " AND ")
			project_relatedactivities=project_relatedactivities+related_child.substitute({"ref":iatiid3, "name":title3})

			activity_relatedactivities=related_parent.substitute({"ref":iatiid2, "name":title2})

			transactions=""
			for transaction in fin["Compact"][country_id]["projects"][project_id]["activities"][activity_id]["transactions"]:
				#print fin["Compact"][country_id]["projects"][project_id]["activities"][activity_id]["transactions"]
				trans=transaction
				transactions=transactions+transaction_t.substitute({"date":fiscal_date(trans["fy"]+","+trans["fq"]),"code":"C","type":"Commitment","amount":trans["obligation"]})
				transactions=transactions+transaction_t.substitute({"date":fiscal_date(trans["fy"]+","+trans["fq"]),"code":"D","type":"Disbursement","amount":trans["disbursement"]})

			params3={"orgid":orgid,
					"implorgid":implorgid,
					"title":title3,
					"relatedactivities":activity_relatedactivities,
					"countrycode":countrycode,
					"countryname":countryname,
					"iatiid":iatiid3,
					"transactions":transactions,
					"startdate":eif,
					"enddate":closure}
			fo.write(activity_t.substitute(params3))



		params2={"orgid":orgid,
				"implorgid":implorgid,
				"title":title2,
				"relatedactivities":project_relatedactivities,
				"countrycode":countrycode,
				"countryname":countryname,
				"iatiid":iatiid2,
				"startdate":eif,
				"enddate":closure}
		fo.write(project_t.substitute(params2))

	params={"orgid":orgid,
			"implorgid":implorgid,
			"title":title,
			"relatedactivities":relatedactivities,
			"countrycode":countrycode,
			"countryname":countryname,
			"iatiid":iatiid,
			"lat":lat,
			"lon":lon,
			"startdate":eif,
			"enddate":closure}
	fo.write(compact_t.substitute(params))

import sys
sys.exit(0)


fo.write(footer_t)

fo.close()
