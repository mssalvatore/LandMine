# LandMine

LandMine is a simple IDS with a near-zero false positive rate that runs on a
dedicated host.

## Description

The mission of LandMine is to detect attackers as they move laterally (or pivot)
through a network. It does this by monitoring all network traffic on a dedicated
host. Because the host's only function is to run LandMine, any traffic it
detects can be assumed to be malicious. In this way, LandMine can detect some
malicious activity on the network with a near-zero false positive rate.

LandMine works by configuring [snort](https://snort.org) to alert on any inbound
or outbound traffic from the host. It then monitors snort's alert log and sends
an e-mail with the alert details.

## Project Status

Currently, LandMine is a script I threw together one afternoon to accomplish its
mission. It is in the process of being transformed into a more complete
solution. Some much needed improvements are:
* The replacement of some code with preexisting utilities where appropriate
  (i.e. sendmail and swatch)
* A solution to simplify configuration of the system as a whole
    * Code refactor to remove hard coded values and allow for configuration via
      a config file
* A mechanism for installation (deb, AppImage, Snap, etc.)

## Installation

TBD

### Dependencies

Snort

Python 3

pythondialog
