# f5_list_ssl_profiles

The intent of this script is to generate a report of all virtual servers on the BIG-IP system, with their Client and Server SSL profiles. 

There are two versions of the script:

**list_ssl_profiles_for_all_vips.py**
- uses the Requests library and the iControl REST API
- can be run on an external system
- can be run on a BIG-IP out of the box

**list_ssl_profiles_for_all_vips_f5_sdk.py**
- leverages the F5 Python SDK and is considerably simpler
- can be run on an external system
- can be run on a BIG-IP if you've manually installed the SDK

The script will generate a csv file formatted like so:

Virtual Server Name	| Virtual Server Destination IP:Port | SSL Profiles (Client) | SSL Profiles (Server)

SSL Profiles will be shown with their parent relationships, like so:

serverssl-insecure-compatible, serverssl
