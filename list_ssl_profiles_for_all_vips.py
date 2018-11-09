"""This module generates a list of all Virtual Servers with their associated SSL profiles."""

import csv
import time
import requests

# you may have to comment out the following two lines if running this code directly on the BIG-IP
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# update to the mgmt address of your target BIG-IP device (can be localhost)
HOST = "https://10.1.1.138"

# it is recommended to use token auth, basic auth used here for lab testing
HEADERS = {
    'Content-Type': "application/json",
    'cache-control': "no-cache",
    'Authorization': "Basic YWRtaW46YWRtaW4="
    }


print "Getting all serverssl profiles on the BIG-IP..."

# initialize an empty dictionary
SERVERSSL_DICT = dict()

# set the base URL for REST API
URL = HOST + "/mgmt/tm/ltm/profile/server-ssl"

# perform a GET request
RESPONSE = requests.request("GET", URL, headers=HEADERS, verify=False)

# parse the API RESPONSE and store the results
if RESPONSE.status_code == 200:
    for serverssl_profile in RESPONSE.json()['items']:
        SERVERSSL_DICT[serverssl_profile['name']] = serverssl_profile
else:
    print "ERROR: ", RESPONSE.status_code


print "Getting all clientssl profiles on the BIG-IP..."

# initialize an empty dictionary
CLIENTSSL_DICT = dict()

# set the base URL for REST API
URL = HOST + "/mgmt/tm/ltm/profile/client-ssl"

# perform a GET request
RESPONSE = requests.request("GET", URL, headers=HEADERS, verify=False)

# parse the API RESPONSE and store the results
if RESPONSE.status_code == 200:
    for clientssl_profile in RESPONSE.json()['items']:
        CLIENTSSL_DICT[clientssl_profile['name']] = clientssl_profile
else:
    print "ERROR: ", RESPONSE.status_code



def get_parents(profile_name):
    """This function recursively returns the parent profile of the input profile.

    Args:
        profile_name (str)

    """
    if profile_name in CLIENTSSL_DICT:
        try:
            # get the parent profile, converting URL to name
            parent_url = CLIENTSSL_DICT[profile_name]['defaultsFromReference']['link']
            parent_name = parent_url[parent_url.rfind('~')+1:parent_url.rfind('?')]
            string_to_return = ", " + parent_name + get_parents(parent_name)
            return string_to_return
        except KeyError: # profile has no parents
            return ""

    elif profile_name in SERVERSSL_DICT:
        try:
            # get the parent profile, converting URL to name
            parent_url = SERVERSSL_DICT[profile_name]['defaultsFromReference']['link']
            parent_name = parent_url[parent_url.rfind('~')+1:parent_url.rfind('?')]
            string_to_return = ", " + parent_name + get_parents(parent_name)
            return string_to_return
        except KeyError: # profile has no parents
            return ""


print "Getting all virtuals on the BIG-IP..."

# initialize an empty list to store the output and an index to track position
OUTPUT_LIST = list()
i = 0

# set the base URL for REST API
URL = HOST + "/mgmt/tm/ltm/virtual"

# perform a GET request
RESPONSE = requests.request("GET", URL, headers=HEADERS, verify=False)

# parse the API RESPONSE and store the results
if RESPONSE.status_code == 200:
    for virtual in RESPONSE.json()['items']:
        OUTPUT_LIST.append([virtual['name'], \
                            virtual['destination'][virtual['destination'].rfind('/')+1:]])

        # set the base URL to get all of the profiles associated with the virtual
        URL = HOST + virtual['selfLink'][17:]
        URL = URL[:URL.find('?')]
        URL = URL + "/profiles/"

        # perform a GET request
        RESPONSE1 = requests.request("GET", URL, headers=HEADERS, verify=False)

        # parse the API RESPONSE and store the results
        if RESPONSE1.status_code == 200:
            for profile in RESPONSE1.json()['items']:

                if profile['name'] in CLIENTSSL_DICT:
                    CLIENTSSL_PROFILES = profile['name'] + get_parents(profile['name'])
                    OUTPUT_LIST[i].append(CLIENTSSL_PROFILES)

            # looping twice because the results are in alphabetical order
            for profile in RESPONSE1.json()['items']:
                if profile['name'] in SERVERSSL_DICT:
                    SERVERSSL_PROFILES = profile['name'] + get_parents(profile['name'])
                    OUTPUT_LIST[i].append(SERVERSSL_PROFILES)

        i = i + 1

else:
    print "ERROR: ", RESPONSE.status_code

print "Writing to CSV..."
FILENAME = "ssl_profiles_" + time.strftime("%Y%m%d_%H%M%S") + ".csv"
OUTPUT = open(FILENAME, "a")
CSV_WRITER = csv.writer(OUTPUT)
CSV_WRITER.writerow(["Virtual Server Name", "Virtual Server Destination IP:Port", \
                     "SSL Profiles (Client)", "SSL Profiles (Server)"])

for line in OUTPUT_LIST:
    CSV_WRITER.writerow(line)

OUTPUT.close()
print "Done!"
