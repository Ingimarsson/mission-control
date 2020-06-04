from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve
from django.conf import settings

from django.http import HttpResponse

import os
import json
import cantools

from cantools.database import UnsupportedDatabaseFormatError

@login_required
def accumulator(request):
    """
    Renders the accumulator page.
    """
    return render(request, 'accumulator.html', {'name': 'Accumulator'})


@login_required
def dashboard(request):
    """
    Renders the dashboard.
    """
    return render(request, 'dashboard.html', {'name': 'Dashboard'})


@login_required
def sensors(request):
    """
    Reads the DBC file and render the sensors page.
    """
    table = []

    ns = 0
    nm = 0
    ne = 0

    try:
        db = cantools.database.load_file(settings.BASE_DIR + '/datalogger.dbc')
        ids = []

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

    except (UnsupportedDatabaseFormatError, FileNotFoundError):
        pass

    return render(request, 'sensors.html', {'name': 'Sensors', 'table': table, 'messages': nm, 'sensors': ns, 'error': ne})

@login_required
@csrf_exempt
def api_sensors_upload(request):
    """
    Accepts a file upload and writes the content to the DBC file.
    """
    if request.method == 'POST':
        with open('/home/spark/mission-control/datalogger.dbc', 'wb+') as destination:
            for chunk in request.FILES['file'].chunks():
                destination.write(chunk)

        return HttpResponse('ok')

