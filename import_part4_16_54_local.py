import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from core.models import ListeningPartMaterial

DATA = {
    16: "https://drive.google.com/file/d/13ZaotiJqGRlFfrt2QZGhs1Yhbxefzn4o/view?usp=drivesdk",
    17: "https://drive.google.com/file/d/17UijlOVZvitTKx1E-bIdV9BG2E7UTQwz/view?usp=drivesdk",
    18: "https://drive.google.com/file/d/1x9zeYyVD4cbAwFE2b1ZaiEtgz_OAcyQK/view?usp=drivesdk",
    19: "https://drive.google.com/file/d/1bLnosuEItzQkEp7epleTRDTPSHGxhgFy/view?usp=drivesdk",
    20: "https://drive.google.com/file/d/1RNK4cB8u97DfROe1VZLk2_nF6N1IqAMR/view?usp=drivesdk",
    21: "https://drive.google.com/file/d/1kiIIg-j3kJccnsG8byxOpjEoz81uP0Xd/view?usp=drivesdk",
    22: "https://drive.google.com/file/d/1fOHhKng39mnPRkjhSmIoBf-dJQdyKcJe/view?usp=drivesdk",
    23: "https://drive.google.com/file/d/16j9uEc2cirbVQO18onChwwHTVohnMfJ9/view?usp=drivesdk",
    24: "https://drive.google.com/file/d/1_E47DoBMCfd2QuKkIkPu8a_bHLXp9s1r/view?usp=drivesdk",
    25: "https://drive.google.com/file/d/1ls94H4-7fUxkuC83tJBFB6cXf94NeZOj/view?usp=drivesdk",
    26: "https://drive.google.com/file/d/1upq0w86daNSY_KAV0tPsB98wqOPYMzCT/view?usp=drivesdk",
    27: "https://drive.google.com/file/d/1cjrYcvjUFMMHjt80vr0oPxAu7Ft1HG-N/view?usp=drivesdk",
    28: "https://drive.google.com/file/d/1M6lRB5jgBj_t2zCpHOXdexI9f5XGwutG/view?usp=drivesdk",
    29: "https://drive.google.com/file/d/1c4pmCdm5oTtBySvw3A4OU6-9xsmygSFM/view?usp=drivesdk",
    30: "https://drive.google.com/file/d/1IkFFp6VO1Iy7j9kSzZEcBphl52QMxtzO/view?usp=drivesdk",
    31: "https://drive.google.com/file/d/1ckMUe6tPSyf7xzzDt30IT_tOI_IRjM4u/view?usp=drivesdk",
    32: "https://drive.google.com/file/d/160WuB4e1ZyDT3MVE3hmlpbzrURChH9Yd/view?usp=drivesdk",
    33: "https://drive.google.com/file/d/1kUHE_SDNzL9V-nhiSmHxLjDnEvhtQQuC/view?usp=drivesdk",
    34: "https://drive.google.com/file/d/1juMOVz6C1tWVk42HpAugEL3Kuc8bUjLG/view?usp=drivesdk",
    35: "https://drive.google.com/file/d/1wfNmvtvA970VRBgBxIMjs0I1LF5uBDHf/view?usp=drivesdk",
    36: "https://drive.google.com/file/d/14G2eu4TDFirXllwvZo6hR4doFvTDX_BU/view?usp=drivesdk",
    37: "https://drive.google.com/file/d/14BuLteu581uGUTBmPK-YvCcEmuw5oBWy/view?usp=drivesdk",
    38: "https://drive.google.com/file/d/1JZHivYN6Ehnx9kr6LqLv0karKDaGpW39/view?usp=drivesdk",
    39: "https://drive.google.com/file/d/1Bavr7qt7NQy7OgtdkbeoanpmWzc0qCA1/view?usp=drivesdk",
    40: "https://drive.google.com/file/d/1qtHyibBt2AkL0TSpAL8OWU_dLm49C3et/view?usp=drivesdk",
    41: "https://drive.google.com/file/d/1iCzi74fcu1zAQLmymclVrygophpaKMX4/view?usp=drivesdk",
    42: "https://drive.google.com/file/d/11Z0WdA8lEvC8eymJ5U-74f8b_hnghzOV/view?usp=drivesdk",
    43: "https://drive.google.com/file/d/11p8o8k4ebrDd69mq-2WXZgiYkqrSYtmj/view?usp=drivesdk",
    44: "https://drive.google.com/file/d/1j2plpeS1KI4UgPbL8v6lnGf1iIAG7pij/view?usp=drivesdk",
    45: "https://drive.google.com/file/d/1jAIyecmw3p3a-Jtog6mMo_LZuu4uGKyT/view?usp=drivesdk",
    46: "https://drive.google.com/file/d/1ic_TuyPV4pqjnmZE8yh9H1Q6kJGXv58I/view?usp=drivesdk",
    47: "https://drive.google.com/file/d/1aDMcaYTVNDOgos8J_2OaDG-nA-gE7GX8/view?usp=drivesdk",
    48: "https://drive.google.com/file/d/1JdBDAjQG56dn8fbL7mtwBuVun37CN02R/view?usp=drivesdk",
    49: "https://drive.google.com/file/d/1Y2WXPFdSdFhMA6nLTz8bF372pveKFQ1A/view?usp=drivesdk",
    50: "https://drive.google.com/file/d/1BtNXxbW0NEy7cWkg2gZ6IW0mx3TzuFVH/view?usp=drivesdk",
    51: "https://drive.google.com/file/d/1PbD0azpnbMVgDalv082gAHTzdXME6anV/view?usp=drivesdk",
    52: "https://drive.google.com/file/d/15gRV_gdOU5UXM-gcPn9LWRaJRwuUPj72/view?usp=drivesdk",
    53: "https://drive.google.com/file/d/1JnYcLv39bYnW3xhYnpVw_ew-KhgyP4Qr/view?usp=drivesdk",
    54: "https://drive.google.com/file/d/161VQLvPvkCXJhYSiZym9XU_7CMLgLcv4/view?usp=drivesdk",
}

materials = list(ListeningPartMaterial.objects.filter(part=4).order_by("id"))

print(f"Local Part 4 materials found: {len(materials)}")

for number, url in DATA.items():
    material = materials[number - 1]
    material.audio_url = url
    material.save(update_fields=["audio_url"])
    print(f"OK {number}: {material.title}")

print("DONE: Updated local Part 4 audio rows 16-54.")
