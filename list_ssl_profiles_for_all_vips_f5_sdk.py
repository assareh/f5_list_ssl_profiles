"""This module generates a list of all Virtual Servers with their associated SSL profiles."""

import csv
import time

from f5.bigip import ManagementRoot

# Connect to the BigIP
MGMT = ManagementRoot("10.1.1.138", "admin", "admin")

print "Getting all serverssl profiles on the BIG-IP..."

# initialize an empty dictionary
SERVERSSL_DICT = dict()

SERVERSSL_COLLECTION = MGMT.tm.ltm.profile.server_ssls.get_collection()
SERVERSSL_PROFILES = MGMT.tm.ltm.profile.server_ssls

for serverssl_profile in SERVERSSL_COLLECTION:
    SERVERSSL_DICT[serverssl_profile.name] = serverssl_profile

print "Getting all clientssl profiles on the BIG-IP..."

# initialize an empty dictionary
CLIENTSSL_DICT = dict()

CLIENTSSL_COLLECTION = MGMT.tm.ltm.profile.client_ssls.get_collection()
CLIENTSSL_PROFILES = MGMT.tm.ltm.profile.client_ssls

for clientssl_profile in CLIENTSSL_COLLECTION:
    CLIENTSSL_DICT[clientssl_profile.name] = clientssl_profile


def get_parents(profile_name):
    """This function recursively returns the parent profile of the input profile.

    Args:
        profile_name (str)

    """
    if profile_name in CLIENTSSL_DICT:
        try:
            # get the parent profile, converting URL to name
            parent_url = CLIENTSSL_DICT[profile_name].defaultsFromReference['link']
            parent_name = parent_url[parent_url.rfind('~')+1:parent_url.rfind('?')]
            string_to_return = ", " + parent_name + get_parents(parent_name)
            return string_to_return
        except AttributeError: # profile has no parents
            return ""

    elif profile_name in SERVERSSL_DICT:
        try:
            # get the parent profile, converting URL to name
            parent_url = SERVERSSL_DICT[profile_name].defaultsFromReference['link']
            parent_name = parent_url[parent_url.rfind('~')+1:parent_url.rfind('?')]
            string_to_return = ", " + parent_name + get_parents(parent_name)
            return string_to_return
        except AttributeError: # profile has no parents
            return ""


print "Getting all virtuals on the BIG-IP..."

# initialize an empty list to store the output and an index to track position
OUTPUT_LIST = list()
i = 0

for virtual in MGMT.tm.ltm.virtuals.get_collection():
    OUTPUT_LIST.append([virtual.name, \
                            virtual.destination[virtual.destination.rfind('/')+1:]])

    virt = MGMT.tm.ltm.virtuals.virtual.load(partition=virtual.partition, name=virtual.name)
    for profile in virt.profiles_s.get_collection():
        if profile.name in CLIENTSSL_DICT:
            CLIENTSSL_PROFILES_STRING = profile.name + get_parents(profile.name)
            OUTPUT_LIST[i].append(CLIENTSSL_PROFILES_STRING)

    # looping twice because the results are in alphabetical order
    for profile in virt.profiles_s.get_collection():
        if profile.name in SERVERSSL_DICT:
            SERVERSSL_PROFILES_STRING = profile.name + get_parents(profile.name)
            OUTPUT_LIST[i].append(SERVERSSL_PROFILES_STRING)

    i = i + 1


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
