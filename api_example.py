from dataclasses import dataclass
import os

import ros_api
from jinja2 import Environment, FileSystemLoader, select_autoescape

FLOOR_ORDER = ['2.OG', '1.OG', 'EG', 'UG']

env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape()
)
template = env.get_template("template.html.jinja")

@dataclass
class FloorInfo:
  name: str
  count_24GHz: int
  count_5GHz: int

router = ros_api.Api('192.168.88.1', user=os.environ.get('MIKROTIK_USER'), password=os.environ.get('MIKROTIK_PASSWORD'))
interfaces = router.talk('/caps-man/interface/print')

floor_infos = []

for floor_name in FLOOR_ORDER:
  count_24GHz = 0
  count_5GHz = 0

  for interface in interfaces:
    interface_name = interface['name']
    registered_clients = int(interface['current-registered-clients'])

    if floor_name not in interface_name:
      continue

    if '2ghz' in interface_name:
      count_24GHz += registered_clients
    elif '5ghz' in interface_name:
      count_5GHz += registered_clients
    else:
      exit(-1)

  floor_infos.append(FloorInfo(floor_name, count_24GHz, count_5GHz))

print(template.render(floor_infos=floor_infos))
