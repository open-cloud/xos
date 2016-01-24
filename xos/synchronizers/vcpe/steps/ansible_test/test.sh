#! /bin/bash
ansible-playbook --private-key /home/smbaker/.ssh/id_rsa -i ./inventory.txt test.yaml
