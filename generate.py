#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import sys
import os
import errno

proxy = sys.argv[1]
tftp = proxy
csv_file = open(sys.argv[2], 'rt')

try:
    #detect delimiter
    dialect = csv.Sniffer().sniff(csv_file.read(1024))
    csv_file.seek(0)
    #detect header
    header = csv.Sniffer().has_header(csv_file.read(1024))
    csv_file.seek(0)
    reader = csv.reader(csv_file, dialect)
    #skip the first line if header found
    if header:
        next(reader, None)
    #phonebook XML start
    phonebook="<CiscoIPPhoneDirectory>\n<Title>Adresář</Title>"

    #iterate CSV
    for row in reader:
        filedata = None
        #map columns
        sn = row[0]
        num = row[1]
        pswd = row[2]
        name = row[3]
        template = row[4]

        template = "{}.xml".format(template)

        outfile = "./output/spa{}.xml".format(sn)
        #create output directory if not exists
        if not os.path.exists(os.path.dirname(outfile)):
            try:
                os.makedirs(os.path.dirname(outfile))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        #phonebook record
        phonebook += "\n<DirectoryEntry><Name>{}</Name><Telephone>{}</Telephone></DirectoryEntry>".format(name,num)

        #parse template
        with open(template, 'r') as file :

          filedata = file.read()
          #replace fields with values
          filedata = filedata.replace('##NUM##', num)
          filedata = filedata.replace('##PASS##', pswd)
          filedata = filedata.replace('##NAME##', name)
          filedata = filedata.replace('##PROXY##', proxy)
          filedata = filedata.replace('##TFTP##', tftp)

          #write output config file for device
          with open(outfile, 'w') as file:
            file.write(filedata)
          print("{}: {} [{}]").format(sn, num, name)

    #phonebook XML end + write to file
    phonebook += "\n</CiscoIPPhoneDirectory>"
    with open("./output/directory.xml", 'w') as file:
        file.write(phonebook)

    #generate provisioning models configs
    models = ['spa301','spa501G','spa502G','spa504G','spa508G','spa509G','spa512G','spa514G']
    for model in models:
        outfile = "./output/{}.xml".format(model)
        with open(outfile, 'w') as file:
            conf = """
            <flat-profile>
            <Resync_On_Reset>Yes</Resync_On_Reset>
            <Resync_Periodic>10</Resync_Periodic>
            <Profile_Rule>tftp://{}/spa$MA.xml</Profile_Rule>
            </flat-profile>""".format(tftp)
            file.write(conf)

finally:
    csv_file.close()


