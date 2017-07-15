from napalm_base.utils import py23_compat

import re


def parse_indented_config(config, current_indent=0, previous_indent=0, nested=False):
    parsed = IndentedConfig()
    while True:
        if not config:
            break
        line = config.pop(0)
        last = line.lstrip()
        leading_spaces = len(line) - len(last)

        #  print("current_indent:{}, previous:{}, leading:{} - {}".format(
        #        current_indent, previous_indent, leading_spaces, line))

        if leading_spaces > current_indent:
            parsed[last] = parse_indented_config(config, leading_spaces, current_indent, True)
        elif leading_spaces < current_indent:
            config.insert(0, line)
            break
        else:
            if not nested:
                parsed[last] = parse_indented_config(config, leading_spaces, current_indent, True)
            else:
                config.insert(0, line)
                break

    return parsed


def _can_have_multiple(command):
    EXACT_MATCHES = [
        "interface",
        "router",
        "access-list",
        "policy-map",
        "ip prefix",
        "ipv6 prefix",
        "neighbor",
        "ip address",
        "ipv6 address",
    ]
    return any([command.startswith(e) for e in EXACT_MATCHES])


def _expand(d, action, indent):
    result = []
    for k, v in d.items():
        k = "{}{}".format(" " * indent * 2, k)
        result.append((action, k))
        result += _expand(v, action, indent+1)
    return result


def merge(running, candidate, negators, indent=0):
    result = []
    for command, subcommands in candidate.items():
        if any([command.startswith(n) for n in negators]):
            ncmd = " ".join(command.split(" ")[1:])
            remove = running.find(ncmd, exact=_can_have_multiple(ncmd))
            for r in remove:
                result.append(("remove", "{}{}".format(" " * indent * 2, r)))
                result += _expand(running[r], "remove", indent+1)
        elif command in running:
            r = merge(running[command], subcommands, negators, indent+1)
            if r:
                result.append(("change", command))
                result += r
        elif command not in running:
            result.append(("add", "{}{}".format(" " * indent * 2, command)))
            result += _expand(subcommands, "add", indent+1)

            remove = running.find(command, exact=_can_have_multiple(command))
            for r in remove:
                result.append(("remove", "{}{}".format(" " * indent * 2, r)))
                result += _expand(running[r], "remove", indent+1)

    return result


class IndentedConfig(object):

    def __init__(self, config=None, comments="!", negators=["no", "default"]):
        self.config = config if config is not None else ""

        if self.config:
            # let's get rid of empty lines and comments
            lines_no_blanks = [line for line in self.config.splitlines()
                               if line.strip() and not line.startswith(comments)]
            self.parsed = parse_indented_config(lines_no_blanks)
        else:
            self.parsed = {}
        self.negators = negators

    def items(self):
        return self.parsed.items()

    def keys(self):
        return self.parsed.keys()

    def values(self):
        return self.parsed.values()

    def __setitem__(self, item, value):
        self.parsed.__setitem__(item, value)

    def __getitem__(self, item):
        return self.parsed.__getitem__(item)

    def __contains__(self, key):
        return key in self.parsed

    def to_dict(self):
        result = {}
        for k, v in self.items():
            if v:
                result[k] = v.to_dict()
            else:
                result[k] = {}
        return result

    def find(self, command, exact):
        if not exact:
            cmd = " ".join(command.split(" ")[0:-1])
            command = cmd if cmd else command
        regex = re.compile("^{}.*".format(command))
        return [c for c in self.keys() if regex.match(c)]

    def diff(self, candidate):
        if isinstance(candidate, py23_compat.string_types):
            candidate = IndentedConfig(candidate)
        result = merge(self, candidate, self.negators)
        m = {
            "remove": "-",
            "add": "+",
            "change": " ",
        }
        return "\n".join(["{} {}".format(m[r[0]], r[1]) for r in result])
