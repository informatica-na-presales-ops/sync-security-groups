import ipaddress
import re
import requests

txt = 'http://asnetadmin.informatica.com/aws/PAN.txt'
html = 'http://asnetadmin.informatica.com/aws/geo.php'

txt_response = requests.get(txt)
txt_response.raise_for_status()
txt_ips = set(txt_response.text.splitlines())

def is_ip(token):
    try:
        _ = ipaddress.ip_address(token)
        return True
    except ValueError:
        return False

html_response = requests.get(html)
html_response.raise_for_status()
tokens = set(re.split(r'</?td>', html_response.text))
html_ips = set([t for t in tokens if is_ip(t)])

print('In txt list but not html:', txt_ips - html_ips)
print('In html list but not txt:', html_ips - txt_ips)
