import re
import sys

full_file = sys.argv[1]
mono_file = sys.argv[2]

lines = []
with open(full_file) as f_full:
    for l in f_full:
        elts = l.strip().split()
        if len(elts) == 0:
            continue
        if len(elts) != 3:
            raise Exception(f"Elements are not valid {elts}")
        
        s = re.search("^[^-]+[-]([^+]+)\+.*", elts[2])
        if s:
            elts[2] = s.group(1)
        lines.append(elts)

with open(mono_file, "w") as f_mono:
    for l in lines:
        f_mono.write("\t".join(l))
        f_mono.write("\n")
