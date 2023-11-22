
import json
import requests
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import random
from matplotlib.path import Path
random.seed(17)
import statistics
import re
from collections import Counter
import os.path

raw = requests.get("https://dsl.richmond.edu/panorama/redlining/static/downloads/geojson/MIDetroit1939.geojson")
RedliningData = raw.json()

#print(RedliningData["features"][0])

class DetroitDistrict:
    def __init__(self, RandomLat=None, RandomLong=None, median_income=None, CensusTract=None, json_in=None):

        self.Coordinates = json_in["geometry"]["coordinates"]
        self.HolcGrade = json_in["properties"]["holc_grade"]

        if self.HolcGrade == "A":
            self.HolcColor = "darkgreen"

        elif self.HolcGrade == "B":
            self.HolcColor = "cornflowerblue"

        elif self.HolcGrade == "C":
            self.HolcColor = "gold"

        elif self.HolcGrade == "D":
            self.HolcColor = "maroon"

        self.name = json_in["properties"]["area_description_data"]["9"]
        self.qualitative_description = json_in["properties"]["area_description_data"]["8"]

        self.RandomLat = RandomLat
        self.RandomLong = RandomLong
        self.median_income = median_income
        self.CensusTract = CensusTract

    def __str__(self):
        return f'District Name: {self.name}, Coordinates: {self.Coordinates}, RandomLong: {self.RandomLong}, RandomLat: {self.RandomLat}, HolcGrade: {self.HolcGrade}, CensusTract: {self.CensusTract}, MedianIncome: {self.median_income}'


def remove_fillers(in_list):

    fillers = set(["the", "of", "is", "are", "and", "in", "to", "a", "for", "area", "on", "at", "this", "very", "all", "*see", "there", "with", "but", "as", "area.", "not"])
    return_list = []

    for word in in_list:
        if word.strip().lower() not in fillers:
            return_list.append(word)

    return return_list



Districts = [DetroitDistrict(json_in=data) for data in RedliningData["features"]]


fig, ax = plt.subplots()

for district in Districts:
    ax.add_patch(matplotlib.patches.Polygon(xy=district.Coordinates[0][0], facecolor=district.HolcColor, edgecolor="black"))
    ax.autoscale()
    plt.rcParams["figure.figsize"] = (15,15)

plt.show()



xgrid = np.arange(-83.5,-82.8,.004)
ygrid = np.arange(42.1, 42.6, .004)
#Assigns evenly spaced values within given range for both coordinates to xgrid, ygrid

xmesh, ymesh = np.meshgrid(xgrid,ygrid)
#Assigns coordinate matrices to xmesh and ymesh from xgrid, ygrid

points = np.vstack((xmesh.flatten(),ymesh.flatten())).T
#stacks arrays row wise


for j in Districts:
    p = Path(j.Coordinates[0][0])
    #Defines Path from coordinates

    grid = p.contains_points(points)
    #Returns whether the path contains the points defined above

    #print(j," : ", points[random.choice(list(np.where(grid)[0]))])
    #Prints District object and random point

    point = points[random.choice(list(np.where(grid)[0]))]
    #Select a random point from the 'points' list that is contained within the Path

    j.RandomLong = point[0]
    j.RandomLat = point[1]
    # Assigns the lat/lon of the point to the District object



for district in Districts:

    try:
        with open("District_Cache.json") as json_datafile:
            json_data = json.load(json_datafile)

            for json_district in json_data:
                if json_district["RandomLong"] == district.RandomLong and json_district["RandomLat"] ==  district.RandomLat:
                    district.CensusTract = json_district["CensusTract"]

    except FileNotFoundError:
        census_data = requests.get(f"https://geo.fcc.gov/api/census/area?lat={district.RandomLat}&lon={district.RandomLong}&censusYear=2010&format=json")
        census_data = census_data.json()
        census_tracts = census_data["results"][0]["block_fips"][5:11]
        district.CensusTract = census_tracts



census_key = "a6412bcda3469b76c4eadaed085da34110f1aca0"


for district in Districts:


    try:
        with open("District_Cache.json") as json_datafile:
            json_data = json.load(json_datafile)

            for json_district in json_data:
                if json_district["RandomLong"] == district.RandomLong and json_district["RandomLat"] ==  district.RandomLat:
                    district.median_income = json_district["median_income"]

    except FileNotFoundError:
        income_data = requests.get(f"https://api.census.gov/data/2018/acs/acs5?get=B19013_001E&for=tract:*&in=state:26&key={census_key}")
        income_data = income_data.json()

        for tract in income_data:
            if tract[3] == district.CensusTract and int(tract[0]) > 0:
                district.median_income = int(tract[0])

            elif tract[3] == district.CensusTract and int(tract[0]) < 0:
                district.median_income = 0


## Part 7

cache_list = []


for district in Districts:

    district_info = {
        "median_income": district.median_income,
        "RandomLong": district.RandomLong,
        "RandomLat": district.RandomLat,
        "CensusTract": district.CensusTract
    }

    cache_list.append(district_info)

json_cache = json.dumps(cache_list)

with open("District_Cache.json", "w") as outfile:
    outfile.write(json_cache)


## Part 8

A_districts = []
B_districts = []
C_districts = []
D_districts = []

A_district_incomes = []
B_district_incomes = []
C_district_incomes = []
D_district_incomes = []


for district in Districts:
    if district.HolcGrade == "A":
        A_districts.append(district)
        A_district_incomes.append(district.median_income)

    elif district.HolcGrade == "B":
        B_districts.append(district)
        B_district_incomes.append(district.median_income)


    elif district.HolcGrade == "C":
        C_districts.append(district)
        C_district_incomes.append(district.median_income)


    elif district.HolcGrade == "D":
        D_districts.append(district)
        D_district_incomes.append(district.median_income)


A_mean_income = round(statistics.mean(A_district_incomes))
B_mean_income = round(statistics.mean(B_district_incomes))
C_mean_income = round(statistics.mean(C_district_incomes))
D_mean_income = round(statistics.mean(D_district_incomes))

A_median_income = statistics.median(A_district_incomes)
B_median_income = statistics.median(B_district_incomes)
C_median_income = statistics.median(C_district_incomes)
D_median_income = statistics.median(D_district_incomes)

#print(A_mean_income,B_mean_income, C_mean_income, D_mean_income)



## Part 9

A_string = ""
B_string = ""
C_string = ""
D_string = ""


for district in A_districts:
    A_string = A_string + " " + district.qualitative_description

for district in B_districts:
    B_string = B_string + " " + district.qualitative_description

for district in C_districts:
    C_string = C_string + " " + district.qualitative_description

for district in D_districts:
    D_string = D_string + " " + district.qualitative_description


A_wordlist = re.split(r"\s+", A_string)
B_wordlist = re.split(r"\s+", B_string)
C_wordlist = re.split(r"\s+", C_string)
D_wordlist = re.split(r"\s+", D_string)

A_wordlist = remove_fillers(A_wordlist)
B_wordlist = remove_fillers(B_wordlist)
C_wordlist = remove_fillers(C_wordlist)
D_wordlist = remove_fillers(D_wordlist)

A_counter = Counter(A_wordlist)
B_counter = Counter(B_wordlist)
C_counter = Counter(C_wordlist)
D_counter = Counter(D_wordlist)

A_mostcommon = A_counter.most_common(10)
B_mostcommon = B_counter.most_common(10)
C_mostcommon = C_counter.most_common(10)
D_mostcommon = D_counter.most_common(10)


#print(A_mostcommon, B_mostcommon, C_mostcommon, D_mostcommon)









