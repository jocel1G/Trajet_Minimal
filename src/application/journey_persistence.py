class JourneyPersistence:
    def __init__(self, persistence):
        self.persistence = persistence

    def save_journey(self, journey):
        for location in journey.locations:
            self.persistence.save_location(location)
        self.persistence.save_journey(journey)

    def save_result(self, result):
        self.persistence.save_result(result)

    def load_journey(self, journey_id):
        return self.persistence.get_journey(journey_id)

    def list_journeys(self):
        return self.persistence.list_journeys()

    def load_result(self, result_id):
        return self.persistence.get_result(result_id)
