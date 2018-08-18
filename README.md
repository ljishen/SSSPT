# SSSPT

Ansible playbook that complies with Solid State Storage (SSS) Performance Test Specification (PTS) v2.0.1

**Specification:** https://www.snia.org/tech_activities/standards/curr_standards/pts


## Requirements on Control Machine

- `ansible >= 2.5`
<!---
need to install "jmespath" prior to running json_query filter
https://github.com/elastic/ansible-elasticsearch/issues/321

Flag python-jmespath as PPA dependency
https://github.com/ansible/ansible/issues/24319
--->
- `jmespath >= 0.9.3` (`apt-get install python-jmespath`)


## Usage

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
