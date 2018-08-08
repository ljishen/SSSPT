# SSSPT
Ansible playbook that complies with Solid State Storage (SSS) Performance Test Specification (PTS) v2.0.1

**Specification** https://www.snia.org/tech_activities/standards/curr_standards/pts


### Requirements

- `ansible >= 2.5` on control machine


### Usage


```bash
git clone https://github.com/ljishen/SSSPT.git

# command is required to run within this dir so that ansible-playbook can see ansible.cfg
cd SSSPT

# Modify the hosts and the corresponding device under test (DUT)
vim hosts

# run tests
ansible-playbook playbooks/main.yml --tags TESTS [-v]

# TESTS can be any combinations of [throughput, iops] separated by comma.
# E.g. ansible-playbook playbooks/main.yml --tags "throughput,iops"
#
# Options:
#   -v  Show debug messages while running playbook
```
