import datetime

from flask import request
from flask_restx import Resource, abort
from random import randrange

import configuration
from modules import firestore

class EnergyData(Resource):

    @configuration.measure_time
    def post(self):

        # Initialize global times keeper
        configuration.times = {}

        # Get parameters
        payload = request.json
        zone_codes = payload['zone_codes']
        date_from = payload['date_from']
        duration = payload['duration']
        join = payload['join']
        light = payload['light']

        # Get data
        data = firestore.query_energy_data(zone_codes, date_from, duration, join, light)

        # Make them JSON serializable
        for i in range(len(data)):
            doc = data[i]

            # Refactor datetime from str to date-objects
            datetime_keys = ['EntityCreatedAt', 'EntityModifiedAt', 'DateTime', 'UpdateTime']
            for key in datetime_keys:
                if key in doc.keys():
                    data[i][key] = str(doc[key])

            if payload['join']:
                data[i]['ReferenceZoneInfo']['AreaRefAddedOn'] = str(doc['ReferenceZoneInfo']['AreaRefAddedOn'])
                data[i]['ResolutionCodeInfo']['EntityCreatedAt'] = str(doc['ResolutionCodeInfo']['EntityCreatedAt'])
                data[i]['ResolutionCodeInfo']['EntityModifiedAt'] = str(doc['ResolutionCodeInfo']['EntityModifiedAt'])

        return {
            'times': configuration.times,
            'parameters': payload,
            'len_of_data': len(data),
            'data': data
        }

    @configuration.measure_time
    def get(self):

        # Initialize global times keeper
        configuration.times = {}

        # Get query parameters
        zone_code = request.args.get('zone_code', default=None, type=str)
        date_from = request.args.get('date_from', default='01-10-2020', type=str)
        duration = request.args.get('duration', default='10', type=str)

        if zone_code is None:
            abort(400, f"Zone Code needed.", statusCode=400)

        # Get data
        data = firestore.query_energy_data([int(zone_code)], date_from, int(duration), False, True)

        # Make them JSON serializable
        for i in range(len(data)):
            doc = data[i]

            # Refactor datetime from str to date-objects
            datetime_keys = ['EntityCreatedAt', 'EntityModifiedAt', 'DateTime', 'UpdateTime']
            for key in datetime_keys:
                if key in doc.keys():
                    data[i][key] = str(doc[key])

        return {
            'times': configuration.times,
            'parameters': {
                'zone_code': zone_code,
                'date_from': date_from,
                'duration': duration
            },
            'len_of_data': len(data),
            'data': data
        }

class ReferenceZones(Resource):

    @configuration.measure_time
    def get(self):

        # Initialize global times keeper
        configuration.times = {}

        # Get query parameters
        time_added = request.args.get('time_added', default=None, type=str)
        country_fk = request.args.get('country_fk', default=None, type=str)
        ref_zone_id = request.args.get('ref_zone_id', default=None, type=str)

        # Get data
        data = firestore.query_ref_zones(time_added, country_fk, ref_zone_id)

        # Make them JSON serializable
        for i in range(len(data)):
            doc = data[i]

            # Refactor datetime from str to date-objects
            datetime_keys = ['AreaRefAddedOn']
            for key in datetime_keys:
                if key in doc.keys():
                    data[i][key] = str(doc[key])

        return {
            'times': configuration.times,
            'len_of_data': len(data),
            'data': data
        }

    @configuration.measure_time
    def post(self):

        # Initialize global times keeper
        configuration.times = {}

        # Get query parameters
        ref_zone_id = request.args.get('ref_zone_id', default=None, type=str)

        # Generate ref_zone_id
        if ref_zone_id is None:
            ref_zone_id = str(randrange(410, 1000))

        # Check ID
        doc = configuration.db.collection('reference_zones').document(ref_zone_id).get()
        if doc.exists:
            abort(400, f"Reference Zone with ID {ref_zone_id} already exists.", statusCode=400)

        # Write dummy document
        else:
            new_doc = {
                "AreaRefAbbrev": "GREEK TESTING",
                "Country_FK": randrange(50, 100),
                "Id": int(ref_zone_id),
                "eicFunctionName_FK": None,
                "AreaTypeCode_FK": randrange(0, 100),
                "AreaRefAddedOn": datetime.datetime.now(),
                "MapCode_FK": randrange(0, 100),
                "AreaRefName": "[NEW] /GREEK",
                "AreaCode_eic_FK": None
            }
            configuration.db.collection('reference_zones').document(ref_zone_id).set(new_doc)

            return {
                "times": configuration.times,
                "ref_zone_id": ref_zone_id
            }

    @configuration.measure_time
    def delete(self):

        # Initialize global times keeper
        configuration.times = {}

        # Get query parameters
        ref_zone_id = request.args.get('ref_zone_id', default=None, type=str)

        # Generate ref_zone_id
        if ref_zone_id is None:
            ref_zone_id = str(randrange(100, 1000))

        # Check ID
        doc = configuration.db.collection('reference_zones').document(ref_zone_id).get()
        if not doc.exists:
            abort(400, f"Reference Zone with ID {ref_zone_id} does not exist.", statusCode=400)
        else:
            if doc.to_dict()['AreaRefAbbrev'] != "GREEK TESTING":
                abort(400, f"Reference Zone with ID {ref_zone_id} cannot be deleted.", statusCode=400)

        # Delete document
        configuration.db.collection('reference_zones').document(ref_zone_id).delete()

        return {
            "times": configuration.times,
            "ref_zone_id": ref_zone_id
        }
