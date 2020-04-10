import cantools
import json

db = cantools.database.load_file('datalogger.dbc')

signals = {}

for mess in db.messages:
    for sign in mess.signals:
        path = sign.comment.split("/")

        if path[1] not in signals:
            signals[path[1]] = {
                'name': path[1], 
                'objpath': path[1], 
                'measurements': []
            }

        signals[path[1]]['measurements'].append({
            'name': "_".join(path[2:]),
            'topic': sign.comment,
            'objpath': path[1] + "." + "_".join(path[2:]),
            'options': {'units': 'volts', 'format': 'float'}
        })

print(json.dumps(list(signals.values())))
