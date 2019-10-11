from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve

from django.http import HttpResponse

from .models import Data, Track

from math import sin, cos, sqrt, atan2, radians
from datetime import datetime
import paho.mqtt.client as mqtt
import json
import cantools
import os

@login_required
def dashboard(request):
    entries = Track.objects.all()

    return render(request, 'dashboard.html', {'name': 'Dashboard', 'tracks': entries})

@login_required
def data(request):
    entries = Data.objects.all().order_by('-id')

    return render(request, 'data.html', {'name': 'Data', 'entries': entries})

@login_required
def tracks(request):
    entries = Track.objects.all()

    return render(request, 'tracks.html', {'name': 'Tracks', 'entries': entries})

@login_required
def accumulator(request):
    return render(request, 'accumulator.html', {'name': 'Accumulator'})

@login_required
def sensors(request):
    db = cantools.database.load_file('/home/spark/mission-control/datalogger.dbc')
    ids = []
    table = []

    ns = 0
    nm = 0
    ne = 0

    for mess in db.messages:
        ids.append(mess.frame_id)
    
    ids.sort()

    for i in ids:
        mess = db.get_message_by_frame_id(i)
        s = []
        for sign in mess.signals:
            s.append({'name': sign.name, 'length': sign.length, 'is_signed': sign.is_signed, 'is_float': sign.is_float, 'byte_order': (sign.byte_order == 'big_endian'), 'path': sign.comment})
            if sign.comment == None:
                ne += 1
            elif sign.comment.count('/') < 2:
                ne += 1

            ns += 1

        nm += 1

        table.append({'id': hex(mess.frame_id), 'name': mess.name, 'signals': s})

    return render(request, 'sensors.html', {'name': 'Sensors', 'table': table, 'messages': nm, 'sensors': ns, 'error': ne})

@login_required
def data_get(request, id):
    entry = Data.objects.get(pk=id)
    
    filepath = entry.filename

    return serve(request, os.path.basename(filepath), os.path.dirname(filepath))

@login_required
def api_track(request, id):
    entry = Track.objects.get(pk=id)

    data = json.loads(entry.points)
    data['name'] = entry.name

    return HttpResponse(json.dumps(data))

@login_required
@csrf_exempt
def api_recording_start(request):
    data = Data.objects.create()

    if request.POST['track'] != 0:
        print(request.POST['track'])
        data.track_id = request.POST['track']

    data.driver = request.POST['driver']
    data.comment = request.POST['comment']
    data.filename = datetime.now().strftime('%Y%m%d_%H%M%S.csv')

    data.save()

    # Send MQTT command to start recording
    client = mqtt.Client()

    client.username_pw_set('spark', 'spark')
    client.connect("localhost", 1883, 60)
    cmd = json.dumps({'recording': 1, 'filename': data.filename, 'track': data.track.id})
    
    client.publish('control/recording', cmd)
    client.disconnect()

    return HttpResponse('ok')

@login_required
@csrf_exempt
def api_recording_stop(request):
    # Send MQTT command to stop recording
    client = mqtt.Client()

    client.username_pw_set('spark', 'spark')
    client.connect("localhost", 1883, 60)
    cmd = json.dumps({'recording': 0})
    
    client.publish('control/recording', cmd)
    client.disconnect()

    return HttpResponse('ok')

@login_required
@csrf_exempt
def api_track_add(request):
    data = Track.objects.create()

    points = json.loads(request.POST['points'])['track']

    distance = 0

    for p in range(1, len(points)):
        dlon = radians(points[p][0]) - radians(points[p-1][0])
        dlat = radians(points[p][1]) - radians(points[p-1][1])

        a = sin(dlat / 2)**2 + cos(points[p-1][1]) * cos(points[p][1]) * sin(dlon / 2)**2
        distance += 2 * 6373 * atan2(sqrt(a), sqrt(1 - a))

    data.name = request.POST['name']
    data.points = request.POST['points']
    data.size = len(points)
    data.distance = round(distance,2)

    data.save()

    return HttpResponse('ok')


@login_required
@csrf_exempt
def api_track_edit(request, id):
    data = Track.objects.get(pk=id)

    points = json.loads(request.POST['points'])['track']

    distance = 0

    for p in range(1, len(points)):
        dlon = radians(points[p][0]) - radians(points[p-1][0])
        dlat = radians(points[p][1]) - radians(points[p-1][1])

        a = sin(dlat / 2)**2 + cos(points[p-1][1]) * cos(points[p][1]) * sin(dlon / 2)**2
        distance += 2 * 6373 * atan2(sqrt(a), sqrt(1 - a))

    data.name = request.POST['name']
    data.points = request.POST['points']
    data.size = len(points)
    data.distance = round(distance,2)

    data.save()

    return HttpResponse('ok')

@login_required
@csrf_exempt
def api_sensors_upload(request):
    if request.method == 'POST':
        with open('/home/spark/mission-control/datalogger.dbc', 'wb+') as destination:
            for chunk in request.FILES['file'].chunks():
                destination.write(chunk)

        return HttpResponse('ok')
