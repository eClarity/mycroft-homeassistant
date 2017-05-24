# Home Assistant Skill for Mycroft

based off the original code from https://github.com/BongoEADGC6/mycroft-home-assistant, spun off my own version since they seem to be inactive.

This is a skill to add [Home Assistant](https://home-assistant.io) support to
[Mycroft](https://mycroft.ai). Currently is supports turning on and off several
entity types (`light`, `switch`, `scene`, `groups` and `input_boolean`).

## Support/Help
You can always find me in the mycroft slack channel here, http://mycroft-ai-slack-invite.herokuapp.com/

## Installation

Clone the repository into your `~/.mycroft/skills` directory. Then install the
dependencies inside your mycroft virtual environment:

If on picroft just skip the workon part and the directory will be /opt/mycroft/skills

```
cd ~/.mycroft/skills
git clone https://github.com/btotharye/mycroft-homeassistant HomeAssistantSkill
workon mycroft
cd HomeAssistantSkill
pip install -r requirements.txt
```



## Configuration

Add a block to your `~/.mycroft/mycroft.conf` file like this:

```
  "HomeAssistantSkill": {
    "host": "hass.mylan.net",
    "password": "mysupersecrethasspass",
    "ssl": true|false
  }
```

NOTE: SSL support is currently secure as it does verify the cert.

You will then need to restart mycroft.

## Usage

Say something like "Hey Mycroft, turn on living room lights". Currently available commands
are "turn on" and "turn off". Matching to Home Assistant entity names is done by scanning
the HA API and looking for the closest matching friendly name. The matching is fuzzy (thanks
to the `fuzzywuzzy` module) so it should find the right entity most of the time, even if Mycroft
didn't quite get what you said.  I have further expanded this to also look at groups as well as lights.  This way if you say turn on the office light, it will do the group and not just 1 light, this can easily be modified to your preference by just removing group's from the fuzzy logic in the code.


Example Code:
So in the code in this section you can just remove group, etc to your liking for the lighting.  I will eventually set this up as variables you set in your config file soon.

```
def handle_lighting_intent(self, message):
        entity = message.data["Entity"]
        action = message.data["Action"]
        LOGGER.debug("Entity: %s" % entity)
        LOGGER.debug("Action: %s" % action)
        ha_entity = self.ha.find_entity(entity, ['group','light', 'switch', 'scene', 'input_boolean'])
        if ha_entity is None:
            #self.speak("Sorry, I can't find the Home Assistant entity %s" % entity)
            self.speak_dialog('homeassistant.device.unknown', data={"dev_name": ha_entity['dev_name']})
            return
        ha_data = {'entity_id': ha_entity['id']}
```


## Supported Phrases/Entities
Currently the phrases are:
* Ask home assistant where is brian (Brian is a sensor for home/not home)
* Ask home assistant what is the weather (it would be another sensor called weather or fuzzy matched to it)
* Turn on office (Can be a group, light, switch)
* Turn off office (Can be a group, light, switch)
 

## TODO
 * New intent for scene activation, e.g. "Mycroft, activate scene..."
 * Script intents processing
 * New intent for opening/closing cover entities
 * New intent for locking/unlocking lock entities (with added security?)
 * New intent for thermostat values, raising, etc.
 * ...

## Contributing

All contributions welcome:

 * Fork
 * Write code
 * Submit merge request

## Licence

See [`LICENCE`](https://gitlab.com/robconnolly/mycroft-home-assistant/blob/master/LICENSE).

