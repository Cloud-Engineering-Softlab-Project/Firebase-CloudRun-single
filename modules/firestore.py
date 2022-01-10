import datetime
import configuration

@configuration.measure_time
def query_energy_data(zone_code: [int], date_from: str, duration: int, join: bool, light: bool) -> [dict]:

    # Initialize dicts which will be used for join
    reference_zones = {}
    resolution_codes = {}

    # Refactor DateTimes from string to date object and calculate the "date_to"
    date_from = datetime.datetime.strptime(date_from, '%d-%m-%Y')
    date_to = date_from + datetime.timedelta(days=duration)

    # Query Data from Firestore
    data_ref = configuration.db.collection(u'total_load_data')
    query = data_ref \
        .where(u'entsoeAreaReference_FK', u'in', zone_code) \
        .where(u'DateTime', u'>=', date_from) \
        .where(u'DateTime', u'<=', date_to)
    # .order_by(u'time')
    results = query.stream()

    # Join energy data with information about resolution codes and reference zones
    final = []
    for result in results:
        doc = result.to_dict()

        if join:
            # Join Reference Zone (caching technique)
            zone_code = doc['entsoeAreaReference_FK']
            if zone_code not in reference_zones.keys():
                ref_zone_doc = configuration.db.collection('reference_zones').document(str(zone_code)).get().to_dict()
                reference_zones[zone_code] = ref_zone_doc
            doc['ReferenceZoneInfo'] = reference_zones[zone_code]

            # Join Resolution Codes (caching technique)
            resolution_code = doc['ResolutionCode_FK']
            if resolution_code not in resolution_codes.keys():
                res_code_doc = configuration.db.collection('resolution_codes').document(
                    str(resolution_code)).get().to_dict()
                resolution_codes[resolution_code] = res_code_doc
            doc['ResolutionCodeInfo'] = resolution_codes[resolution_code]

        if light:
            keys = ['TotalLoadValue',
                    'DateTime',
                    'ResolutionCode_FK',
                    'ResolutionCodeInfo',
                    'entsoeAreaReference_FK',
                    'ReferenceZoneInfo']
            doc = {k: v for k, v in doc.items() if k in keys}

        final.append(doc)

    return final

@configuration.measure_time
def query_ref_zones(time_added: str, country_fk: str, ref_zone_id: str) -> [dict]:

    # Refactor DateTimes from string to date object
    if time_added:
        time_added_obj = datetime.datetime.strptime(time_added, '%d-%m-%Y')

    country_fk = country_fk = int(country_fk) if country_fk else None

    # Get ref_zone with specific ID
    if ref_zone_id:
        doc_dict = configuration.db.collection(u'reference_zones').document(ref_zone_id).get().to_dict()
        return [doc_dict]

    # Query ref zones which they are added later than the  "time_added"
    elif time_added:
        data_ref = configuration.db.collection(u'reference_zones')
        query = data_ref \
            .where(u'Country_FK', u'==', country_fk) \
            .where(u'AreaRefAddedOn', u'>=', time_added_obj)

        results = query.stream()

    # Query ref zones with only Country_FK
    else:
        data_ref = configuration.db.collection(u'reference_zones')
        query = data_ref \
            .where(u'Country_FK', u'==', country_fk)

        results = query.stream()

    final = []
    for result in results:
        doc = result.to_dict()
        final.append(doc)

    return final
