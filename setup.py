import deezerArl
import json

ARL = deezerArl.get_arl()
with open("config.json") as json_data_file:
    config = json.load(json_data_file)

config["arl"] = ARL

with open("config.json", "w") as json_data_file:
    json_data_file.write(json.dumps(config, indent=2))
