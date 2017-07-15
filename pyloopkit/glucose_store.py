class GlucoseValue:
    def __init__(self, start_date, quantity):
        self.start_date = start_date
        self.quantity = quantity

    def as_dict(self):
        return dict(
            start_date=self.start_date.isoformat(),
            quantity=self.quantity,
            )


class GlucoseStore:
    """ GlucoseStore backed by Nightscout """
    def __init__(self, ns_client):
        self.ns_client = ns_client

    def sgv_to_glucose_value(self, sgv):
        return GlucoseValue(sgv.date, sgv.sgv)

    def get_glucose_values(self, start_date, end_date = None):
        query = {'count':0} # Don't limit by count
        if end_date:
            query['find[dateString][$lte]'] = end_date.isoformat()
        query['find[dateString][$gte]'] = start_date.isoformat()

        sgvs = self.ns_client.get_sgvs(query)
        sgvs.sort(key=lambda x: x.date)

        return [self.sgv_to_glucose_value(sgv) for sgv in sgvs]
