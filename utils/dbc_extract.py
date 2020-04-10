import cantools
from pprint import pprint

db = cantools.database.load_file('datalogger.dbc')


#message = db.get_message_by_name('AMSValues1')
#pprint(message.signals)

for mess in db.messages:
    for sign in mess.signals:
        sign.comment = "spark/"

heatCount = 0
voltCount = 0

for mess in db.messages:
    #what component this signal belongs to
    parts = ["AMS", "Bat", "Coo", "Das", "Dat", "dSp", "Ene", "Jun", "MC_"]
    groups = ['accumulator', 'accumulator', 'cooling', 'dashboard', 'datalogger', 'dspace', 'energymeter', 'junction', 'mc']
    part = mess.name[0:3]

    for idx,i in enumerate(parts):
        if part == i:
            for sign in mess.signals:
                sign.comment+=groups[idx]+"/"

                if part == "Bat":
                    if len(sign.name) > 7:
                        if sign.name[0:7] == "Voltage":
                            voltCount += 1
                            sign.comment+="voltage/"+str(voltCount)
                    else:
                        heatCount += 1
                        sign.comment+="temperature/" + str(heatCount)

                else:
                    sign.comment+=mess.name.lower().replace(groups[idx],'').replace('_', '') + "/" + sign.name.lower()


    #what group the signal belongs to
    

for mess in db.messages:
    for sing in mess.signals:
        print(sing.comment)
cantools.database.dump_file(db, 'datalogger.dbc')

