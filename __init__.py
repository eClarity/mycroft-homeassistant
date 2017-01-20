from os.path import dirname, join

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from requests import post
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

        # TODO: we should use the HA api to search for a matching entity
        ha_entity = {"entity_id": "light." + entity.replace(" ", "_")}
        print ha_entity

        if action == "on":
            self.speak("Turning on %s" % entity)
            self.ha.execute_service("light", "turn_on", ha_entity)
        elif action == "off":
            self.speak("Turning off %s" % entity)
            self.ha.execute_service("light", "turn_off", ha_entity)
        else:
            self.speak("I don't know what you want me to do.")

    def stop(self):
        pass


def create_skill():
    return HomeAssistantSkill()
