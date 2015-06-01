import requests
import logging
import json
import sys

""" format of settings

    ["settings"]
        ["watershed"]
        ["rating"]
        ["categories"]
        ["blocklist"]
        ["allowlist"]

    ["users"]
        array
            ["account_id"] - 58
            ["reporting"] - False
            ["name"] - Scott1
            ["devices"]
            ["settings"] -
                ["watershed"]
                ["rating"]
                ["categories"]
                ["blocklist"]
                ["allowlist"]

    ["devices"]
        array
            ["username"] - "Scott1" or "" if whole-house
            ["uuid"] - empty
            ["mac_address"] - mac address as hex digits in ascii
            ["type"] - "laptop"
            ["name"] - human readable name of device ("Scott's laptop")
            ["settings"]
                 ["watershed"]
                     array
                         array
                             ["rating"]
                             ["category"]
                 ["rating"] - ["G" | "NONE"]
                 ["categories"] - list of categories set by rating
                 ["blocklist"] - []
                 ["allowlist"] - []
"""


class BBS:
    level_map = {"PG_13": "PG-13",
                 None: "NONE"}

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.api = "https://www.broadbandshield.com/api"
        self.session = None
        self.settings = None

    def login(self):
        self.session = requests.Session()
        r = self.session.post(self.api + "/login", data = json.dumps({"email": self.username, "password": self.password}))
        if (r.status_code != 200):
            raise BBS_Failure("Failed to login (%d)" % r.status_code)

    def get_account(self):
        if not self.session:
            self.login()

        r = self.session.get(self.api + "/account")
        if (r.status_code != 200):
            raise BBS_Failure("Failed to get account settings (%d)" % r.status_code)
        self.settings = r.json()

        return self.settings

    def post_account(self):
        if not self.settings:
             raise XOSProgrammingError("no settings to post")

        r = self.session.post(self.api + "/account/settings", data= json.dumps(self.settings))
        if (r.status_code != 200):
            raise BBS_Failure("Failed to set account settings (%d)" % r.status_code)

    def add_device(self, name, mac, type="tablet", username=""):
        data = {"name": name, "mac_address": mac, "type": type, "username": username}
        r = self.session.post(self.api + "/device", data = json.dumps(data))
        if (r.status_code != 200):
            raise BBS_Failure("Failed to add device (%d)" % r.status_code)

    def delete_device(self, data):
        r = self.session.delete(self.api + "/device", data = json.dumps(data))
        if (r.status_code != 200):
            raise BBS_Failure("Failed to delete device (%d)" % r.status_code)

    def add_user(self, name, rating="NONE", categories=[]):
        data = {"name": name, "settings": {"rating": rating, "categories": categories}}
        r = self.session.post(self.api + "/users", data = json.dumps(data))
        if (r.status_code != 200):
            raise BBS_Failure("Failed to add user (%d)" % r.status_code)

    def delete_user(self, data):
        r = self.session.delete(self.api + "/users", data = json.dumps(data))
        if (r.status_code != 200):
            raise BBS_Failure("Failed to delete user (%d)" % r.status_code)

    def clear_users_and_devices(self):
        if not self.settings:
            self.get_account()

        for device in self.settings["devices"]:
            self.delete_device(device)

        for user in self.settings["users"]:
            self.delete_user(user)

    def get_whole_home_level(self):
        if not self.settings:
            self.get_account()

        return self.settings["settings"]["rating"]

    def sync(self, whole_home_level, users):
        if not self.settings:
            self.get_account()

        vcpe_users = {}
        for user in users:
            user = user.copy()
            user["level"] = self.level_map.get(user["level"], user["level"])
            user["mac"] = user.get("mac", "")
            vcpe_users[user["name"]] = user

        whole_home_level = self.level_map.get(whole_home_level, whole_home_level)

        if (whole_home_level != self.settings["settings"]["rating"]):
            print "*** set whole_home", whole_home_level, "***"
            self.settings["settings"]["rating"] = whole_home_level
            self.post_account()

        bbs_usernames = [bbs_user["name"] for bbs_user in self.settings["users"]]
        bbs_devicenames = [bbs_device["name"] for bbs_device in self.settings["devices"]]

        add_users = []
        add_devices = []
        delete_users = []
        delete_devices = []

        for bbs_user in self.settings["users"]:
             bbs_username = bbs_user["name"]
             if bbs_username in vcpe_users.keys():
                 vcpe_user = vcpe_users[bbs_username]
                 if bbs_user["settings"]["rating"] != vcpe_user["level"]:
                     print "set user", vcpe_user["name"], "rating", vcpe_user["level"]
                     #bbs_user["settings"]["rating"] = vcpe_user["level"]
                     # add can be used as an update
                     add_users.append(vcpe_user)
             else:
                 delete_users.append(bbs_user)

        for bbs_device in self.settings["devices"]:
             bbs_devicename = bbs_device["name"]
             if bbs_devicename in vcpe_users.keys():
                 vcpe_user = vcpe_users[bbs_devicename]
                 if bbs_device["mac_address"] != vcpe_user["mac"]:
                     print "set device", vcpe_user["name"], "mac", vcpe_user["mac"]
                     #bbs_device["mac_address"] = vcpe_user["mac"]
                     # add of a device can't be used as an update, as you'll end
                     # up with two of them.
                     delete_devices.append(bbs_device)
                     add_devices.append(vcpe_user)
             else:
                 delete_devices.append(bbs_device)

        for (username, user) in vcpe_users.iteritems():
            if not username in bbs_usernames:
                add_users.append(user)
            if not username in bbs_devicenames:
                add_devices.append(user)

        for bbs_user in delete_users:
            print "delete user", bbs_user["name"]
            self.delete_user(bbs_user)

        for bbs_device in delete_devices:
            print "delete device", bbs_device["name"]
            self.delete_device(bbs_device)

        for vcpe_user in add_users:
            print "add user", vcpe_user["name"], "level", vcpe_user["level"]
            self.add_user(vcpe_user["name"], vcpe_user["level"])

        for vcpe_user in add_devices:
            print "add device", vcpe_user["name"], "mac", vcpe_user["mac"]
            self.add_device(vcpe_user["name"], vcpe_user["mac"], "tablet", vcpe_user["name"])

    def get_whole_home_rating(self):
        return self.settings["settings"]["rating"]

    def get_user(self, name):
        for user in self.settings["users"]:
            if user["name"]==name:
                return user
        return None

    def get_device(self, name):
        for device in self.settings["devices"]:
             if device["name"]==name:
                 return device
        return None

    def dump(self):
        if not self.settings:
            self.get_account()

        print "whole_home_rating:", self.settings["settings"]["rating"]
        print "users:"
        for user in self.settings["users"]:
            print "  user", user["name"], "rating", user["settings"]["rating"]

        print "devices:"
        for device in self.settings["devices"]:
            print "  device", device["name"], "user", device["username"], "rating", device["settings"]["rating"], "mac", device["mac_address"]

def self_test():
    if len(sys.argv)!=3:
        print "syntax: broadbandshield.py <email> <password>"
        sys.exit(-1)

    bbs = BBS(sys.argv[1], sys.argv[2])

    print "*** initial ***"
    bbs.dump()

    open("bbs.json","w").write(json.dumps(bbs.settings))

    # delete everything
    bbs.settings["rating"] = "R"
    bbs.post_account()
    bbs.clear_users_and_devices()

    print "*** cleared ***"
    bbs.settings=None
    bbs.dump()

    users = [{"name": "Moms pc", "level": "R", "mac": "010203040506"},
             {"name": "Dads pc", "level": "R", "mac": "010203040507"},
             {"name": "Jacks ipad", "level": "PG", "mac": "010203040508"},
             {"name": "Jills iphone", "level": "G", "mac": "010203040509"}]

    print "*** syncing mom-R, Dad-R, jack-PG, Jill-G, wholehome-PG-13 ***"

    bbs.settings = None
    bbs.sync("PG-13", users)

    print "*** after sync ***"
    bbs.settings=None
    bbs.dump()
    assert(bbs.get_whole_home_rating() == "PG-13")
    assert(bbs.get_user("Moms pc")["settings"]["rating"] == "R")
    assert(bbs.get_user("Dads pc")["settings"]["rating"] == "R")
    assert(bbs.get_user("Jacks ipad")["settings"]["rating"] == "PG")
    assert(bbs.get_user("Jills iphone")["settings"]["rating"] == "G")
    assert(bbs.get_device("Moms pc")["mac_address"] == "010203040506")
    assert(bbs.get_device("Dads pc")["mac_address"] == "010203040507")
    assert(bbs.get_device("Jacks ipad")["mac_address"] == "010203040508")
    assert(bbs.get_device("Jills iphone")["mac_address"] == "010203040509")

    print "*** update whole home level ***"
    bbs.settings=None
    bbs.get_account()
    bbs.settings["settings"]["rating"] = "PG"
    bbs.post_account()

    print "*** after sync ***"
    bbs.settings=None
    bbs.dump()
    assert(bbs.get_whole_home_rating() == "PG")
    assert(bbs.get_user("Moms pc")["settings"]["rating"] == "R")
    assert(bbs.get_user("Dads pc")["settings"]["rating"] == "R")
    assert(bbs.get_user("Jacks ipad")["settings"]["rating"] == "PG")
    assert(bbs.get_user("Jills iphone")["settings"]["rating"] == "G")
    assert(bbs.get_device("Moms pc")["mac_address"] == "010203040506")
    assert(bbs.get_device("Dads pc")["mac_address"] == "010203040507")
    assert(bbs.get_device("Jacks ipad")["mac_address"] == "010203040508")
    assert(bbs.get_device("Jills iphone")["mac_address"] == "010203040509")

    print "*** delete dad, change moms IP, change jills level to PG, change whole home to PG-13 ***"
    users = [{"name": "Moms pc", "level": "R", "mac": "010203040511"},
             {"name": "Jacks ipad", "level": "PG", "mac": "010203040508"},
             {"name": "Jills iphone", "level": "PG", "mac": "010203040509"}]

    bbs.settings = None
    bbs.sync("PG-13", users)

    print "*** after sync ***"
    bbs.settings=None
    bbs.dump()
    assert(bbs.get_whole_home_rating() == "PG-13")
    assert(bbs.get_user("Moms pc")["settings"]["rating"] == "R")
    assert(bbs.get_user("Dads pc") == None)
    assert(bbs.get_user("Jacks ipad")["settings"]["rating"] == "PG")
    assert(bbs.get_user("Jills iphone")["settings"]["rating"] == "PG")
    assert(bbs.get_device("Moms pc")["mac_address"] == "010203040511")
    assert(bbs.get_device("Dads pc") == None)
    assert(bbs.get_device("Jacks ipad")["mac_address"] == "010203040508")

    print "add dad's laptop"
    users = [{"name": "Moms pc", "level": "R", "mac": "010203040511"},
             {"name": "Dads laptop", "level": "PG-13", "mac": "010203040512"},
             {"name": "Jacks ipad", "level": "PG", "mac": "010203040508"},
             {"name": "Jills iphone", "level": "PG", "mac": "010203040509"}]

    bbs.settings = None
    bbs.sync("PG-13", users)

    print "*** after sync ***"
    bbs.settings=None
    bbs.dump()
    assert(bbs.get_whole_home_rating() == "PG-13")
    assert(bbs.get_user("Moms pc")["settings"]["rating"] == "R")
    assert(bbs.get_user("Dads pc") == None)
    assert(bbs.get_user("Dads laptop")["settings"]["rating"] == "PG-13")
    assert(bbs.get_user("Jacks ipad")["settings"]["rating"] == "PG")
    assert(bbs.get_user("Jills iphone")["settings"]["rating"] == "PG")
    assert(bbs.get_device("Moms pc")["mac_address"] == "010203040511")
    assert(bbs.get_device("Dads pc") == None)
    assert(bbs.get_device("Dads laptop")["mac_address"] == "010203040512")
    assert(bbs.get_device("Jacks ipad")["mac_address"] == "010203040508")

    #bbs.add_user("tom", "G", [u'PORNOGRAPHY', u'ADULT', u'ILLEGAL', u'WEAPONS', u'DRUGS', u'GAMBLING', u'SOCIAL', u'CYBERBULLY', u'GAMES', u'ANONYMIZERS', u'SUICIDE', u'MALWARE'])
    #bbs.add_device(name="tom's iphone", mac="010203040506", type="tablet", username="tom")

def main():
    self_test()

if __name__ == "__main__":
    main()


