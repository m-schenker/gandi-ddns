# gandi-ddns

This is a minimal script that dynamically updates DNS A records for domains, and/or subdomains, that are hosted with the registrar [Gandi](https://www.gandi.net/).

## Requirements
1. python
2. python-requests

## Configuration
The script is controlled via a configuration file, `/etc/gandi-ddns.cfg`, that is to be written in an INI files manner.
Attached you will find a sample configuration file. Just set the script to be executed in regular intervals, smaller than the shortest specified ttl, via a cron job or a systemd timer.

    [domain.com]
    apikey=<insert your Gandi API key>
    aname=@
    ttl=1800

    [domain.com]
    apikey=<insert your Gandi API key>
    aname=www
    ttl=900

    [anotherdomain.fr]
    apikey=<insert your Gandi API key>
    aname=blog
    ttl=3600
    
The script is verbose and will print to stout telling you what is wrong if an update operation failed.
