from datetime import datetime,timedelta

class CarbEntry:
    def __init__(self, start_date, quantity, absorption_time=None, food_type=None):
        self.start_date = start_date
        self.quantity = quantity
        self.absorption_time = absorption_time
        self.food_type = food_type

    def __repr__(self):
        str = "CarbEntry(%s %d %s %s)" % (self.start_date, self.quantity, self.absorption_time, self.food_type)
        return str.encode('utf-8')  # Support python 2.x

    def as_dict(self):
        return dict(
            start_date=self.start_date.isoformat(),
            quantity=self.quantity,
            absorption_time=self.absorption_time,
            food_type=self.food_type,
            )


class CarbStore:
    """ CarbStore backed by Nightscout """
    def __init__(self, ns_client):
        self.ns_client = ns_client

    def carb_treatment_to_dose(self, treatment):
        absorption = None
        if treatment.absorptionTime:
            absorption = timedelta(minutes=treatment.absorptionTime)
        return CarbEntry(treatment.timestamp, treatment.carbs, absorption, treatment.foodType)

    def get_carb_entries(self, start_date, end_date = None):
        query = {'count':0} # Don't limit by count
        if end_date:
            query['find[created_at][$lte]'] = end_date.isoformat()
        query['find[created_at][$gte]'] = start_date.isoformat()
        query['find[eventType][$eq]'] = "Meal Bolus"

        carb_treatments = self.ns_client.get_treatments(query)

        return [self.carb_treatment_to_dose(t) for t in carb_treatments]
