#!/usr/bin/env python3

import os, gzip
from csv import DictReader
from geopy.distance import geodesic

class Airport(object):
    __slots__ = ['ident', 'name', 'type', 'latitude', 'longitude', 'elevation', 'continent', 'country', 'iata', 'icao', 'frequencies']
    def __init__(self, ident, name, type, latitude, longitude, elevation, continent, country, iata, icao):
        self.ident = ident
        self.name = name
        self.type = type
        # location data
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.elevation = elevation
        self.continent = continent
        self.country = country
        # coding
        self.iata = iata
        self.icao = icao
    def __eq__(self, other):
        if not isinstance(other, Airport):
            return False
        return True
    def __hash__(self):
        return self.iata
    def getFrequencies(self):
        try:
            if self.frequencies:
                return self.frequencies
        except AttributeError:
            self.frequencies = OurAirports().getFrequencies(self)
            return self.frequencies

class Frequency(object):
    __slots__ = ['airport', 'type', 'description', 'frequency']
    def __init__(self, airport, type, description, frequency):
        self.airport = airport
        self.type = type
        self.description = description
        self.frequency = frequency
    def __eq__(self, other):
        if not isinstance(other, Frequency):
            return False
        return True

class OurAirports:

    def __init__(self):
        self.airports = []
        self.frequencies = []
        self.dir = os.path.dirname(os.path.realpath(__file__))
        with gzip.open('{}/data/airports.csv.gz'.format(self.dir), mode='rt') as f:
            reader = DictReader(f)
            for row in reader:
                self.airports.append(
                    Airport(
                        row['ident'],
                        row['name'],
                        row['type'],
                        row['latitude_deg'],
                        row['longitude_deg'],
                        row['elevation_ft'],
                        row['continent'],
                        row['iso_country'],
                        row['iata_code'],
                        row['gps_code']
                    )
                )
        with gzip.open('{}/data/frequencies.csv.gz'.format(self.dir), mode='rt') as f:
            reader = DictReader(f)
            for row in reader:
                self.frequencies.append(
                    Frequency(
                        row['airport_ident'],
                        row['type'],
                        row['description'],
                        row['frequency_mhz'],
                    )
                )

    def getAirportsByIdent(self, ident):
        return [x for x in self.airports if x.ident == ident]
    
    def getAirportsByType(self, type):
        if not type in ["closed_airport", "heliport", "large_airport", "medium_airport", "seaplane_base", "small_airport"]:
            return []
        return [x for x in self.airports if x.type == type]

    def getAirportsByICAO(self, icao):
        return [x for x in self.airports if x.icao == icao]

    def getAirportsByIATA(self, iata):
        return [x for x in self.airports if x.iata == iata]

    def getAirportsByDistance(self, lat, lon, distance):
        lat_float = float(lat)
        lon_float = float(lon)
        bounding_box_degree_tolerance = math.ceil(distance / 69) * 2
        airports_in_bounding_box = [x for x in self.airports if abs(x.latitude - lat_float) <= bounding_box_degree_tolerance and abs(x.longitude - lon_float) <= bounding_box_degree_tolerance]
        airports_with_distances = [(x, geodesic((x.latitude, x.longitude), (lat_float, lon_float)).miles) for x in airports_in_bounding_box]
        filtered_sorted_airports = sorted(((x, d) for x, d in airports_with_distances if d < distance), key=lambda x: x[1])
        return [x for x, d in filtered_sorted_airports]

    def getFrequencies(self, airport):
        if not isinstance(airport, Airport):
            return False
        return [x for x in self.frequencies if x.airport == airport.ident]