import os.path
import configparser
import json
import requests.auth

PATH = "/etc/gandi-ddns.cfg"
API = "https://api.gandi.net/v5/livedns"


def get_ipv4():
    try:
        return requests.get("https://api.ipify.org", timeout=5).text
    except Exception:
        print("Error getting this computers IP address. Exiting now ...")
        exit(1)


def main():
    # load config file
    if not os.path.exists(PATH):
        print("Config file under '/etc/gandi-ddns.cfg' is missing. Exiting now ...")
        exit(1)
    config = configparser.ConfigParser()
    try:
        config.read(PATH)
    except Exception:
        print("Failed to open the config file under '/etc/gandi-ddns.cfg'. Exiting now ...")
        exit(1)

    # get this computers external ipv4 address
    ip = get_ipv4()

    for fqdn in config.sections():
        try:
            apikey = config[fqdn]['apikey']
            aname = config[fqdn]['aname']
            ttl = config[fqdn]['ttl']
        except Exception:
            print("Config file is missing parameters in section '" + fqdn + "'. Skipping this section ...")
            continue

        # check for a single domain's record, by name and type
        exists = requests.get(API + "/domains/" + fqdn + "/records/" + aname + "/" + "A",
                              headers={"Authorization": "Apikey " + apikey})
        # if record does not exist create it
        if exists.status_code == 404:
            # construct payload to update record
            data = json.dumps({'rrset_values': [ip], 'rrset_ttl': ttl})
            # create new record
            new = requests.post(API + "/domains/" + fqdn + "/records/" + aname + "/" + "A",
                                data=data, headers={"Authorization": "Apikey " + apikey})
            print(new.status_code)
            if new.status_code != 200:
                print("Failed to update A record for " + aname + "." + fqdn + ". Skipping this section ...")
                continue

        # if record already exists check if ip and ttl are correct
        if exists.status_code == 200:
            # decode json payload
            response = json.loads(exists.text)
            if not (response["rrset_ttl"] == int(ttl) and response["rrset_values"][0] == ip and len(
                    response["rrset_values"]) == 1):
                # construct payload to update record
                data = json.dumps({'rrset_values': [ip], 'rrset_ttl': ttl})
                # now we overrride the old record with new parameters
                replace = requests.put(API + "/domains/" + fqdn + "/records/" + aname + "/" + "A", data=data,
                                       headers={"Authorization": "Apikey " + apikey})
                if replace.status_code == 201:
                    print("Creating record for " + aname + "." + fqdn + " was successful.")
                    continue
                else:
                    print("Creating record for " + aname + "." + fqdn + " failed with error code " + str(
                        replace.status_code))
                    continue
            else:
                print("Parameters of the record for " + aname + "." + fqdn + " are up-to-date. Nothing to do.")
                continue
        # handle case if name/type pair did exist, but could not be changed
        print("Failed to update A record for " + aname + "." + fqdn + ". With error code " + str(exists.status_code)
              + ".")


if __name__ == '__main__':
    main()
