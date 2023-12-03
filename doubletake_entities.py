import appdaemon.plugins.hass.hassapi as hass
import json

entity_template = 'sensor.face_person_{}'
wildcard = 'double-take/matches/+'
RESET_DELAY = 20
NOT_PRESET_STATE = 'Not present'
UNKNOWN_ZONE_STATE = 'Undefined zone'

class DoubleTakeEntities(hass.Hass): 
    def initialize(self):
        self.mqtt = self.get_plugin_api("MQTT")
        self.mqtt.listen_event(self.process_received_msg, "MQTT_MESSAGE", wildcard=wildcard, namespace='mqtt')

    def process_received_msg(self, message, topic, namespace):
        payload_d = json.loads(topic.get('payload', '{}'))
        entity = entity_template.format(payload_d.get('match').get('name'))
        zone = ', '.join(payload_d.get('zones', [UNKNOWN_ZONE_STATE]))
        attrs = {}
        attrs['camera'] = payload_d.get('camera')
        attrs['confidence'] = payload_d.get('match', {}).get('confidence')
        attrs['filename'] = payload_d.get('match', {}).get('filename')
        self.set_state(entity, state=zone, attributes=attrs)
        self.run_in(self.reset_state, delay=RESET_DELAY, entity=entity)

    def reset_state(self, kwargs):
        self.set_state(kwargs.get('entity'), state=NOT_PRESET_STATE, attributes={})
        

'''
        #self.log(payload_d)
        # 2023-12-03 20:19:42.726953 INFO doubletake: {'id': '1701631166.089221-d5foau', 'duration': 3.21, 'timestamp': '2023-12-03T19:19:42.125Z', 'attempts': 6, 'camera': 'yi_cam1', 'zones': ['dnevna_sredina'], 'match': {'name': 'tom', 'confidence': 86.12, 'match': True, 'box': {'top': 160, 'left': 538, 'width': 106, 'height': 142}, 'type': 'latest', 'duration': 0.15, 'detector': 'compreface', 'filename': 'e4bf4202-8af6-4486-874a-078f929c61c6.jpg', 'base64': None}}
'''