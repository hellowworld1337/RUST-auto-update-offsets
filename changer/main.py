import re
from pprint import pprint

pattern = re.compile("constexpr auto (\w+) = (\w+);")
offsets_file = open("offsets.h", "r", encoding="utf-8").read()

namespaces = {}

for data in re.findall("namespace (\w+) {([^}]*)};", offsets_file):
    if data[0] != "O":
        namespaces[data[0]] = dict(pattern.findall(data[1]))

print(f"Loaded namespaces: {len(namespaces)}")
dump = open("dump.cs", "r").readlines()
new_namespaces = {}
current_class = None

for ind, line in enumerate(dump):

    for namespace in namespaces.copy():
        if len(list(namespaces[namespace])) == 0:
            del namespaces[namespace]

    if len(namespaces) == 0:
        break

    temp = re.findall("(struct|class) (\w+)", line)
    is_class_line = False
    if len(temp) != 0:
        is_class_line = True
        current_class = temp[0][1]
    if current_class is None or is_class_line:
        continue
    offset = None

    if current_class not in namespaces:
        current_class = None
        continue

    if "//" in line:
        temp_offset = re.findall("Offset: (\w+)", line)
        if len(temp_offset) == 0:
            temp_offset = re.findall("// (\w+)", line)
        if len(temp_offset) == 0:
            continue
        offset = temp_offset[0]
    else:
        temp_offset = re.findall("Offset: (\w+)", dump[ind - 1])
        if len(temp_offset) == 0:
            continue
        offset = temp_offset[0]

    for offset_name, offset_value in namespaces[current_class].copy().items():
        if offset_name in line:
            print(f"[{current_class}] Set {offset_value} to {offset} ({offset_name})")
            offsets_file = offsets_file.replace(f"{offset_name} = {offset_value}", f"{offset_name} = {offset}")
            if current_class not in new_namespaces:
                new_namespaces[current_class] = {}
            new_namespaces[current_class][offset_name] = offset
            del namespaces[current_class][offset_name]

print(f"New namespaces -> {len(new_namespaces)}")
print(f"New offsets -> {sum([len(new_offsets.values()) for new_offsets in new_namespaces.values()])}")

with open("offsets_new.h", "w", encoding="utf-8") as file:
    file.write(offsets_file)
