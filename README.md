# check\_unifi.py

## Overview

`check_unifi.py` is a Python script that monitors UniFi devices via the UniFi API (auth via API-KEY) on a Unifi Cloud Controller. It is designed for integration with monitoring systems such as Icinga, Nagios, or similar tools.

## Features

- Retrieves device statistics (CPU and memory usage) from a UniFi Cloud Controller.
- Supports warning and critical thresholds for monitoring.
- Provides structured output for monitoring tools.
- Uses API authentication for secure communication.

## Requirements

- Python 3
- `requests` library (can be installed via `pip install requests`)


# Guide to Generating a UniFi API Key

This guide explains how to generate an API key for the UniFi Cloud Controller API.

## Prerequisites
- Access to a UniFi Controller (Cloud Key, Dream Machine, or Cloud Gateway)
- Administrator privileges for the UniFi Controller

## Steps to Generate the API Key

### 1. Logging into the UniFi Controller
1. Open your web browser and navigate to the UniFi Cloud Console.
   - Cloud controller: `https://unifi.ui.com`
2. Log in with your administrator account.

### 2. Accessing API Settings
1. Navigate to the **Settings** menu.
2. Look for the **System** section.
3. Scroll down to **API Keys** or **API Access**.

### 3. Generating the API Key
1. Click on **Generate New API Key**.
2. If required, select the permissions for the API key (e.g., read-only or full admin access).
3. Confirm the key generation.
4. Copy the generated API key and store it securely.  
   **Note:** The key may not be displayed again after leaving the page.

### 4. Using the API Key

The API key can now be used for HTTP requests to the UniFi API. Example request using `curl`:

```bash
curl -k -X GET 'https://<Unifi Controller IP Address>/proxy/network/integrations/v1/sites' \
 -H 'X-API-KEY: <API-KEY>' \
 -H 'Accept: application/json'

```

### 5. Security Recommendations
- Do not share your API key with third parties.


## Additional Resources
- [UniFi API Documentation](https://ubntwiki.com/UniFi_API)
- [Official UniFi Community](https://community.ui.com/)

If you have further questions, reach out to the UniFi community.




## Installation

### Clone Repository

```sh
git clone https://github.com/chr0w94/check_unifi.py.git
cd check_unifi.py
mv check_unifi.py /usr/lib/nagios/plugins
```

## Usage

Run the script with the following parameters:

```sh
check_unifi.py -i <Unifi Controller IP-Addr> -a <Unifi API-Key> -s <Unifi Site-Name> -m <MODE> -d <Unifi Device MAC-Addr> -w <WARN Level> -c <CRIT LEVEL>
```

### Options

| Option | Description                                            |
| ------ | ------------------------------------------------------ |
| `-h`   | Show help message                                      |
| `-i`   | UniFi Controller IP Address                            |
| `-a`   | UniFi API Key                                          |
| `-s`   | UniFi Site Name (default: `Default`)                   |
| `-m`   | Monitoring mode (`cpu` or `memory`)                    |
| `-d`   | UniFi Device MAC Address (Format: `00:11:22:33:44:55`) |
| `-w`   | Warning threshold (percentage)                         |
| `-c`   | Critical threshold (percentage)                        |

### Example

```sh
check_unifi.py -i 192.168.2.1 -a Ua7t6TuB9p1q8UgVaatm4aiwobasfh12o9 -s MySite -m cpu -d 0c:ea:16:61:41:e9 -w 80 -c 90
```

## Exit Codes

| Code | Meaning                                                                          |
| ---- | -------------------------------------------------------------------------------- |
| `0`  | OK - Utilization is below the warning level.                                     |
| `1`  | WARNING - Utilization exceeds the warning level but is below the critical level. |
| `2`  | CRITICAL - Utilization exceeds the critical level.                               |

## Integration in Icinga2

### unifi-commands.conf
```sh
object CheckCommand "unifi" {
        import "plugin-check-command"

        command = [ PluginDir + "/check_unifi.py" ]

        arguments = {
                "-i" = {
                        value = "$unifi_controller$"
                        required = true
                        description = "IP-Addr Unifi Controller"
                }
                "-a" = {
                        value = "$unifi_api_key$"
                        required = true
                        description = "Unifi API Key"
                }
                "-s" = {
                        value = "$unifi_site_name$"
                        description = "Unifi Site Name. Default is 'Default'"
                }
                "-m" = {
                        value = "$unifi_mode$"
                        required = true
                        description = "Unifi Mode eq. cpu or memory"
                }
                "-d" = {
                        value = "$unifi_device$"
                        required = true
                        description = "Unifi device mac addr"
                }

                "-w" = {
                        value = "$unifi_warn_level$"
                        required = true
                        description = "WARNING Level eq. 80"
                }
                "-c" = {
                        value = "$unifi_crit_level$"
                        required = true
                        description = "CRITICAL Level eq. 90"
                }
        }
}
```

### templates.conf
```sh
template Host "unifi-host" {
  import "generic-host"

  vars.unifi_controller = "<Controller IP-Address>"
  vars.unifi_api_key = "<API-KEY>"
}

template Service "unifi-service" {
  import "generic-service"

  check_command = "unifi"
}
```

### unifi-services.conf
```sh
apply Service "unifi_cpu" {
  import "unifi-service"

  vars.unifi_mode = "cpu"

  vars.unifi_warn_level = 70
  vars.unifi_crit_level = 90

  assign where host.vars.unifi_device
}

apply Service "unifi_memory" {
  import "unifi-service"

  vars.unifi_mode = "memory"

  vars.unifi_warn_level = 80
  vars.unifi_crit_level = 90

  assign where host.vars.unifi_device
}
```

### unifi-hosts.conf
```sh
object Host "unifi-gw" {
        import "unifi-host"
        display_name = "Unifi Cloud Gateway Ultra"
        address = "<DEVICE-IP-Address>"
        vars.unifi_device = "<DEVICE-MAC-Address>"
}

object Host "unifi-U7Pro-AP" {
        import "unifi-host"
        display_name = "Unifi U7 Pro AccessPoint"
        address = "<DEVICE-IP-Address>"
        vars.unifi_device = "<DEVICE-MAC-Address>"
}
```


## License

This project is licensed under the GNU General Public License v2.0 or later. See the [LICENSE](LICENSE) file for details.

## Author

Developed by chr0w94.

