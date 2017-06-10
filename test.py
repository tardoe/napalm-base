from napalm_base import get_network_driver

import json


def pretty_print(dictionary):
    print(json.dumps(dictionary, sort_keys=True, indent=4))


eos_configuration = {
    'hostname': '127.0.0.1',
    'username': 'vagrant',
    'password': 'vagrant',
    'optional_args': {'port': 12443}
}

eos = get_network_driver("eos")
eos_device = eos(**eos_configuration)

eos_device.open()
pretty_print(eos_device.yang.config.get_openconfig_interfaces(candidate=True))
#  print(eos_device.yang.config.get_openconfig_network_instance())

print("# Raw translation")
print(eos_device.yang.config.translate())
print("-------------")

print("# Merge without changes, should be empty")
print(eos_device.yang.config.translate(merge=True))
print("-------------")

print("# Replace without changes, should be empty")
print(eos_device.yang.config.translate(replace=True))
print("-------------")


print("# Change a description")
eos_device.candidate.interfaces.interface["Ethernet1"].config.description = "This is a new description"  # noqa
pretty_print(eos_device.config.diff())
print("-------------")

print("# Merge change")
print(eos_device.yang.config.translate(merge=True))
print("-------------")

print("# Replace change")
replace_config = eos_device.yang.config.translate(replace=True)
print(replace_config)
print("-------------")

print("# Let's replace the current interfaces configuration from the device")
eos_device.load_merge_candidate(config=replace_config)
print(eos_device.compare_config())
eos_device.discard_config()
print("-------------")

eos_device.close()
