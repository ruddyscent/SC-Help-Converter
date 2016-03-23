#!/usr/bin/env python

import os
import re
import collections

name = '"Symbolic Computing Package for Mathematica"'
ver = '"3.1.2016.1.27"'
home = os.path.expanduser('~')
base = os.path.join(home, '.Mathematica', 'Applications' , 'SymbolicComputing')
doc_en = os.path.join(base, 'Documentation', 'English')
help = os.path.join(doc_en, 'SymbolicComputingHelp10.3.nb')

# Make directory structures
newpath = [os.path.join(doc_en, 'Guides'), 
           os.path.join(doc_en, 'Tutorials'),  
           os.path.join(doc_en, 'ReferencePages', 'Symbols')]
for p in newpath:
    if not os.path.exists(p):
        os.makedirs(p)

with open(help, 'r') as f:
    legacy_help = f.read()

# Select just Notebook Content
str_m = re.search('\(\* Beginning of Notebook Content \*\)', legacy_help, re.DOTALL)
end_m = re.search('\(\* End of Notebook Content \*\)', legacy_help, re.DOTALL)
legacy_help = legacy_help[str_m.span()[0] - 1: end_m.span()[1]]

# Translate link anchors to page links
def linkrepl(match):
    "Return new type of link"

    template = \
'''ButtonBox["{SYMBOL}",
  BaseStyle->{{
   "Link", FontFamily -> "Courier New", FontColor -> 
    RGBColor[0.269993, 0.308507, 0.6]}},
  ButtonData->"paclet:SymbolicComputing/ref/{SYMBOL}"]'''

    return template.format(SYMBOL=match.group(1))

p_link = re.compile('ButtonBox\["(\w+?)",[\sA-Za-z]+?->".+?\]', re.DOTALL)
# p = re.compile('ButtonBox\["(.+?)\".*?\]', re.DOTALL)
# legacy_help = re.sub('ButtonBox\["(.+?)\".*?\]', linkrepl, legacy_help, re.DOTALL)

# Split sections.
def find_sec_start(help_str):
    secs = []
    p = re.compile('Cell\[CellGroupData')

    m = re.finditer('"Section",', help_str, re.DOTALL)
    begin = 0
    for i in m:
        end = i.span()[0]
        m1 = p.search(help_str, begin, end)
        secs.append(m1.span()[0])
        begin = i.span()[1]
        
    return secs
    
sec_start = find_sec_start(legacy_help)

def find_sec_title(help_str, sec_start):
    secs = collections.OrderedDict()
    p = re.compile('"([\w\s]+)"')
    for i in range(len(sec_start) - 1):
        m = p.search(help_str, sec_start[i])
        secs[m.group(1)] = help_str[sec_start[i]: sec_start[i + 1] - 1]
    
    m = p.search(help_str, sec_start[-1])
    secs[m.group()] = help_str[sec_start[-1]: - 1]
    
    return secs

secs = find_sec_title(legacy_help, sec_start)

def parse_func_idx(help_str):
    subsec = collections.OrderedDict()
    p_subsec = re.compile('Cell\["(.+)", "Subsection",')
    p_func = re.compile('ButtonBox\["(.+)"')
    m_subsec = list(p_subsec.finditer(help_str))
    for i in range(len(m_subsec) - 1):
        begin = m_subsec[i].span()[1]
        end = m_subsec[i+1].span()[0]
        m_func = p_func.findall(help_str, begin, end)
        subsec[m_subsec[i].group(1)] = m_func

    begin = m_subsec[-1].span()[1]
    end = begin + re.search('"Section"', help_str[begin:]).span()[0]
    m_func = p_func.findall(help_str, begin, end)
    subsec[m_subsec[-1].group(1)] = m_func

    return subsec

secs['"Index of Functions"'] = parse_func_idx(secs['"Index of Functions"'])

def parse_func_desc(help_str):
    func_desc = {}
    m = re.search('Variables and Macros', help_str)
    begin = m.span()[0]
    
    p = re.compile('Cell\["([\S\n]+?)", "ObjectName"', re.DOTALL)
    p1 = re.compile('Cell\[CellGroupData\[{')
    m = list(p.finditer(help_str, begin))
    for i in range(len(m) - 1):
        name = m[i].group(1)
        begin = list(p1.finditer(help_str, m[i].span()[0] - 100, m[i].span()[0]))[-1].span()[0]
        end = list(p1.finditer(help_str, m[i].span()[0] - 100, m[i+1].span()[0]))[-1].span()[0]
        content = help_str[begin:end]
        
        content = p_link.sub(linkrepl, content)

        # Exclude tailing ','
        end_idx = content.rfind(',')
        func_desc[name] = '\n'.join(['Notebook[{', content[:end_idx], '}]', ''])

    return func_desc

func_desc = parse_func_desc(legacy_help)

def generate_func_help(func_desc):
    for item in func_desc.items():
        name = item[0]
        if name[0] == '\\':
            name = name[4:-4].split('\n')
        else:
            name = [name]
        loc = os.path.join(doc_en, 'ReferencePages', 'Symbols')
        
        for n in name:
            fname = os.path.join(loc, n + '.nb')
            with open(fname, 'w') as f:
                f.write(item[1])

generate_func_help(func_desc)

print(secs['About the Package'])

# # Separate the entire help to Cell-based blocks.
# re.finditer('Cell[CellGroupData\[{\n\nCell["\<\\n(\w+?).+?\],\n', legacy_help_mod, re.DOTALL)
# for i in m:
#     print(i.group())

# # Separate the entire help to Cell based blocks.
# m = re.search('\(\* Beginning of Notebook Content \*\)', legacy_help_mod)
# preamble = legacy_help_mod[0:m.start()]

# m = re.search('Notebook\[{', legacy_help_mod)
# m = re.finditer('Cell\[CellGroupData\[.*?\]\n', legacy_help_mod[m.end():], re.DOTALL)
# for i in m:
#     print(i.group())

# Generate a preamble file.
fname = os.path.join(doc_en, 'Guides', 'Preambles.nb')
end_idx = 0

for i, line in enumerate(legacy_help):
    if 'Variables and Macros' in line:
        end_idx = i - 3
        break

with open(fname, 'w') as f:
    for i in range(end_idx - 1):
        f.write(legacy_help[i])

    f.write(legacy_help[end_idx - 1][0:-2])
    f.write('}]')

# contents = {}
# # '"ReferencePages/Symbols/AFunction"'

template = \
'''Paclet[
    Name -> {NAME},
    Version -> {VER},
    MathematicaVersion -> "8+",
    Extensions -> {{
        {{
            "Documentation",
            Language -> "English", 
            LinkBase -> "SymbolicComputing",
            Resources -> {{
                "Guides/Preambles"
      	        }}
            }}
    }}
]
'''


with open(os.path.join(base, 'PacletInfo.m'), 'w') as f:
    f.write(template.format(NAME=name, VER=ver))
    
