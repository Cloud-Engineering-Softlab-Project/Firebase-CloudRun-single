from flask_restx import Resource

import configuration

class HardSleep(Resource):

    @configuration.measure_time
    def get(self):

        # Initialize global times keeper
        configuration.times = {}

        a = 0
        for i in range(3000):
            for j in range(10000):
                a += i * j

        return {
            'times': configuration.times
        }

class SoftSleep(Resource):

    @configuration.measure_time
    def get(self):

        # Initialize global times keeper
        configuration.times = {}

        a = 0
        for i in range(1000):
            for j in range(10000):
                a += i * j

        return {
            'times': configuration.times
        }
