This repository gathers scripts to use [Scaleway](https://console.scaleway.com/) services. API documentation is available at [developers.scaleway.com](https://developers.scaleway.com/) and the web console at [console.scaleway.com](https://console.scaleway.com/).

If you don't have an account, please [register](https://console.scaleway.com/register)!


# Account and billing

Account and billing APIs manage your user profile, credentials, invoices and so on.

* [ssh_keys.py](account/ssh_keys.py): list, add or remove SSH keys from your account.


# Instances

Instances APIs manage your servers, volumes, IP addresses, snapshots and so on.

* [list_instances.py](instances/list_instances.py): learn how to list instances and consume API pagination.
* [marketplace.go](instances/marketplace.go): query the marketplace API to retrieve image identifiers.
