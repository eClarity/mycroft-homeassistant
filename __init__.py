from os.path import dirname, join

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from requests import get, post
from fuzzywuzzy import fuzz
import json

__author__ = 'robconnolly'


class HomeAssistantClient(object):

    def __init__(self, host, password, port=8123, ssl=False):
        self.ssl = ssl
        if self.ssl:
            self.url = "https://%s:%d" % (host, port)
        else:
            self.url = "http://%s:%d" % (host, port)
        self.headers = {
            'x-ha-access': password,
            'Content-Type': 'application/json'
        }

    def find_entity(self, entity, types):
        if self.ssl:
            req = get("%s/api/states" % self.url, headers=self.headers, verify=False)
        else:
            req = get("%s/api/states" % self.url, headers=self.headers)

        if req.status_code == 200:
            best_score = 0
            best_entity = None
            for state in req.json():
                try:
                    if state['entity_id'].split(".")[0] in types:
                        score = fuzz.ratio(entity, state['attributes']['friendly_name'].lower())
                        if score > best_score:
                            best_score = score
                            best_entity = {"id": state['entity_id'], "name": state['attributes']['friendly_name']}
                except KeyError:
                    pass
            return best_entity

        return None

    def execute_service(self, domain, service, data):
        if self.ssl:
            post("%s/api/services/%s/%s" % (self.url, domain, service), headers=self.headers, data=json.dumps(data), verify=False)
        else:
            post("%s/api/services/%s/%s" % (self.url, domain, service), headers=self.headers, data=json.dumps(data))

# TODO - Localization
class HomeAssistantSkill(MycroftSkill):
    def __init__(self):
        super(HomeAssistantSkill, self).__init__(name="HomeAssistantSkill")
        self.ha = HomeAssistantClient(self.config.get('host'),
            self.config.get('password'), ssl=self.config.get('ssl', False))

    def initialize(self):
        self.load_vocab_files(join(dirname(__file__), 'vocab', 'en-us'))

        prefixes = ['turn', 'switch']
        self.__register_prefixed_regex(prefixes, "(?P<Action>on|off) (?P<Entity>.*)")

        intent = IntentBuilder("TurnOnOffIntent").require("TurnOnOffKeyword").require("Action").require("Entity").build()
        self.register_intent(intent, self.handle_intent)

    def __register_prefixed_regex(self, prefixes, suffix_regex):
        for prefix in prefixes:
            self.register_regex(prefix + ' ' + suffix_regex)

    def handle_intent(self, message):
        entity = message.data["Entity"]
        action = message.data["Action"]

        ha_entity = self.ha.find_entity(entity, ['light', 'switch', 'scene', 'input_boolean'])
        if ha_entity is None:
            self.speak("Sorry, I can't find the Home Assistant entity %s" % entity)
            return
        ha_data = {'entity_id': ha_entity['id']}

        if action == "on":
            self.speak("Turned on %s" % ha_entity['name'])
            self.ha.execute_service("homeassistant", "turn_on", ha_data)
        elif action == "off":
            self.speak("Turned of %s" % ha_entity['name'])
            self.ha.execute_service("homeassistant", "turn_off", ha_data)
        else:
            self.speak("I don't know what you want me to do.")

    def stop(self):
        pass


def create_skill():
    return HomeAssistantSkill()
