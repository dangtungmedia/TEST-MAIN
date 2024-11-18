import json
from datetime import datetime

# Define the base JSON structure
data = {
    "url-sever": "https://autospamnews.com",
    "timeupload": 0,
    "profiles": [],
    "ip_address": "148.251.40.198:pqFHM"
}

# Generate 60 profiles
for i in range(1, 61):
    profile = {
        "name": f"k{i}",
        "path_profile": "",
        "uploadsToday": 0,
        "lastUploadTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "uploadLimitPerDay": 6
    }
    data["profiles"].append(profile)

# Save to JSON file
with open("profiles_config.json", "w") as json_file:
    json.dump(data, json_file, indent=4)

print("JSON file 'profiles_config.json' created successfully!")
