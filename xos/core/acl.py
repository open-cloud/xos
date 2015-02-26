from fnmatch import fnmatch

"""
    A General-purpose ACL mechanism.

    [allow | deny] <type_of_object> <text_pattern>

    "allow all" and "deny all" are shorthand for allowing or denying all objects.
    Lines are executed from top to bottom until a match was found, typical
    iptables style. An implicit 'deny all' exists at the bottom of the list.

    For example,
    allow site Max Planck Institute
    deny site Arizona
    allow region US
    deny user scott@onlab.us
    allow user *@onlab.us
"""
class ACLValidationError(Exception): pass

class AccessControlList:
    def __init__(self, aclText=None):
        self.rules = []
        if aclText:
            self.import_text(aclText)

    def import_text(self, aclText):
        # allow either newline or ';' to separate rules
        aclText = aclText.replace("\n", ";")
        for line in aclText.split(";"):
            line = line.strip()
            if line.startswith("#"):
                continue

            if line=="":
                continue

            parts = line.split()

            if len(parts)==2 and (parts[1]=="all"):
                # "allow all" has no pattern
                parts = (parts[0], parts[1], "")

            if len(parts)!=3:
                raise ACLValidationError(line)

            (action, object, pattern) = parts

            if action not in ["allow", "deny"]:
                raise ACLValidationError(line)

            if object not in ["site", "user", "all"]:
                raise ACLValidationError(line)

            self.rules.append( (action, object, pattern) )

    def __str__(self):
        lines = []
        for rule in self.rules:
            lines.append( " ".join(rule) )
        return ";\n".join(lines)

    def test(self, user, site=None):
        for rule in self.rules:
            if self.match_rule(rule, user):
                return rule[0]
        return "deny"

    def match_rule(self, rule, user, site=None):
        (action, object, pattern) = rule

        if (site==None):
            site = user.site

        if (object == "site"):
            if fnmatch(site.name, pattern):
                return True
        elif (object == "user"):
            if fnmatch(user.email, pattern):
                return True
        elif (object == "all"):
            return True

        return False


if __name__ == '__main__':
    # self-test

    class fakesite:
        def __init__(self, siteName):
            self.name = siteName

    class fakeuser:
        def __init__(self, email, siteName):
            self.email = email
            self.site = fakesite(siteName)

    u_scott = fakeuser("scott@onlab.us", "ON.Lab")
    u_bill = fakeuser("bill@onlab.us", "ON.Lab")
    u_andy = fakeuser("acb@cs.princeton.edu", "Princeton")
    u_john = fakeuser("jhh@cs.arizona.edu", "Arizona")
    u_hacker = fakeuser("somehacker@foo.com", "Not A Real Site")

    # check the "deny all" rule
    acl = AccessControlList("deny all")
    assert(acl.test(u_scott) == "deny")

    # a blank ACL results in "deny all"
    acl = AccessControlList("")
    assert(acl.test(u_scott) == "deny")

    # check the "allow all" rule
    acl = AccessControlList("allow all")
    assert(acl.test(u_scott) == "allow")

    # allow only one site
    acl = AccessControlList("allow site ON.Lab")
    assert(acl.test(u_scott) == "allow")
    assert(acl.test(u_andy) == "deny")

    # some complicated ACL
    acl = AccessControlList("""allow site Princeton
                 allow user *@cs.arizona.edu
                 deny site Arizona
                 deny user scott@onlab.us
                 allow site ON.Lab""")

    assert(acl.test(u_scott) == "deny")
    assert(acl.test(u_bill) == "allow")
    assert(acl.test(u_andy) == "allow")
    assert(acl.test(u_john) == "allow")
    assert(acl.test(u_hacker) == "deny")

    print acl

