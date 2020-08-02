import logging
import re

logger = logging.getLogger(__name__)

WPA_FILENAME = r'/etc/wpa_supplicant/wpa_supplicant.conf'
WPA_FILENAME = r'./.test/wpa_supplicant.conf'
WPA_COUNTRY = "US"
WPA_GROUP = "netdev"


def get_wifi_config():
    """
    Generate a list of dictionaries from the wpa_supplicant.conf file.
    This uses regex to filter out the known fields for raspberry pi.
    """
    logger.info("Read WiFi config file: {0}".format(WPA_FILENAME))
    try:
        file = open(WPA_FILENAME, "r")
    except FileNotFoundError:
        logger.error("{0} doesn't exist.".format(WPA_FILENAME))
        return ""
    networks = []
    id = 0
    network = {}

    for line in file.readlines():
        logger.debug("Line is {0}".format(line.strip()))
        # Network block start
        if 'network=' in line:
            logger.debug("Found network block")
            # We save an id to start parsing the network block.
            network['id'] = id

        # This looks for specific lines and strips out only the value
        if 'id' in network:
            # ssid regex
            if re.search(
                r'^\s*ssid\=.*$',
                line
            ) is not None:
                # We need to strip out quotes amd whitespace
                network['ssid'] = line.strip().split('=')[1].replace('"', "")
            # psk regex
            elif re.search(
                r'^\s*psk\=.*$',
                line
            ) is not None:
                network['psk'] = line.strip().split('=')[1].replace('"', "")
            # priority regex
            elif re.search(
                r'^\s*priority\=.*$',
                line
            ) is not None:
                network['priority'] = line.strip().split('=')[1]
            # id_str regex
            elif re.search(
                r'^\s*id_str\=.*$',
                line
            ) is not None:
                network['id_str'] = line.strip().split('=')[1].replace('"', "")
            # End of network block
            elif '}' in line:
                networks.append(network)
                logger.info(
                    "Network {0} has been parsed".format(str(network['ssid']))
                )
                logger.debug(network)
                # Reset network block and increase id
                network = {}
                id += 1

    logger.info("Closing WiFi config file")
    file.close()
    return networks


def set_wifi_config(networks, country=WPA_COUNTRY, group=WPA_GROUP):
    """
    Save the wifi network array to a file.
    """
    logger.info("Saving WiFi configuration")
    data = []
    # Add the header for wpa_supplicant.conf
    data.append('country={0}\n'.format(str(country)))
    data.append(
        'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP={0}\n'.format(
            str(group)
        )
    )
    data.append('update_config=1\n')
    data.append('\n')
    # Loop through the networks
    for network in networks:
        data.append('network={\n')
        data.append('    ssid="' + network['ssid'] + '"\n')
        data.append('    psk="' + network['psk'] + '"\n')
        if 'priority' in network:
            data.append('    priority=' + network['priority'] + '\n')
        if 'id_str' in network:
            data.append('    id_str="' + network['id_str'] + '"\n')
        data.append('}\n')
        data.append('\n')

    try:
        file = open(WPA_FILENAME, "w")
        file.writelines(data)
        file.close()
    except FileNotFoundError:
        logger.error("There was a problem writing the file.")
    except PermissionError:
        logger.error("Permission error writing file")
