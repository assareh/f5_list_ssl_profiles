# f5_list_ssl_profiles

The intent of this script is to generate a report of all virtual servers on the BIG-IP system, with their Client and Server SSL profiles. 

The script can be run on the BIG-IP directly or from an external system. 

The script will generate a csv file formatted like so:

Virtual Server Name	| Virtual Server Destination IP:Port | SSL Profiles (Client) | SSL Profiles (Server)

SSL Profiles will be shown with their parent relationships, like so:

serverssl-insecure-compatible, serverssl
