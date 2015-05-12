#!/usr/bin/env python
import os
import sys

sys.path.append("../..")
import observer.ansible

print sys.argv

private_key="""-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEAtJiuarud5S4Y2quDeWyaS0UCQGQtfuSzzNhplFwujYnJGL65
e14REtv+UuHGymyr/SfkTrBd8vH5NI2UZ/4sZW13ieI/1d97OeVe2+ct0Y4BaFEI
3Hja6DIpsY3Q2cBQsWUwcQzbMIF9jIq8SzwR1zk8UtZi09fNxqjCchRPlBvbiLKX
g0/yirN237WbaKzK++8EPy3nuv83216MXHFFSjuxfICe/RhjaqMzVp7isSbv1suU
geyvNNzU71c/K13gTggdcIXeRQBiJYio2Sn3h2nsV6AFqFH4fjERxWG55Q4e3jeE
tWM/Dw+hqYKg/25UcmM862a6sUmuDCmM5S3VEQIDAQABAoIBACH88iZoNOki6c6N
pOq/Q7KSxD+2GtHc3PHacNRZHPHKUqxziJjtNS1lddHHaBBEr4GvdkpQ6v2ECLCZ
TKrdrSFRnsO2bukjbB+TSWz9byQXI7CsP4yuuhQlDK+7zuiMRyN7tcgw8TeJx0Uh
/xnxrjHhNbcpXeQcoz+WFzI9HFT1MEGmMS4Lyp/zLB/pmfY9h7V9d+EeRZDi78jq
Vir6MI6iCTa0T02dvHUFOg+wXLb0nb8V1xKDL+6cAJla7LzwoG8lTnvp5DSYCojI
5JrILYafeO8RbBV2GWmaE5mkHgeBkFZ+qZQ7K0MjR30Yh6tajB7P3+F/Max8FUgW
xLHr8AECgYEA2+o0ge3HtZcepEFBKKYnLTwoEpPCfLElWZHzUJYDz259s4JLsfak
tROANFEdsJUjpmWG52MCL+bgKFFOedDkt4p1jgcIneaHk0jvoU11wG7W3jZZVy1q
WjQNH5vDU+hg5tm/CREwm7lbUxR9Xuj9K63CNAAGp8KO7h2tOH8woIECgYEA0jrb
LUg30RxO3+vrq9dUYohrDRisk5zKXuRLfxRA+E+ruvZ7CctG2OpM+658/qZM/w95
7pOj6zz3//w7tAvH9erY+JOISnzaYKx04sYC1MfbFiFkq5j0gpuYm/MULDYNvFqr
NU2Buj4dW+ZB+SeficsQOqm5QeNxh1kgiDCs7JECgYEAjSLGCAzeesA9vhTTCI95
3SIaZbHGw9e8rLtqeHGOiHXU3nvksJYmJsAZK3pTn5xXgNbvuVhlcvCtM7LatntG
DjUiNMB22z+0CuZoRBE+XP3FkF84/yX6d2Goenyw4wzkA8QDQoJxu789yRgBTgQh
VwLw/AZ4PvoyWMdbAENApgECgYEAvFikosYP09XTyIPaKaOKY5iqqBoSC1GucSOB
jAG+T3k5dxB6nQS0nYQUomvqak7drqnT6O33Lrr5ySrW5nCjnmvgJZwvv+Rp1bDM
K5uRT8caPpJ+Wcp4TUdPi3BVA2MOHVDyEJg3AH/D1+DL/IgGQ/JcwOHsKt61iLhO
EBXj5zECgYEAk+HuwksUPkSxg/AiJGbapGDK6XGymEUzo2duWlnofRqGcZ3NT3bB
/kDI1KxQdlpODXSi4/BuTpbQiFOrzcEq5e5ytoMxlCHh3Fl3Jxl+JlgO21vAUvP6
4SET7Q/6LxmfBlCVRg0dXDwcfJLgbnWxyvprIcz4e0FSFVZTBs/6tFk=
-----END RSA PRIVATE KEY-----
"""

observer.ansible.run_template_ssh("test.yaml",
                                  {"sliver_name": "onlab_test405-378",
                                   "instance_id": "instance-0000004d",
                                   "hostname": "node67.washington.vicci.org",
                                   "private_key": private_key})

