#!/usr/bin/env python

import os
import re
import collections
import glob

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

# Start process the legacy help file.
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
def split_sec(help_str):
    secs = collections.OrderedDict()
    
    p_sec_bgn = re.compile('Cell\[CellGroupData')
    p_sec_title = re.compile('"(.+)?", "Section"')

    m_sec_title = list(p_sec_title.finditer(help_str))

    for i in range(len(m_sec_title)):
        m_bgn = p_sec_bgn.search(help_str, 
                                   m_sec_title[i].span()[0] - 100)
        bgn = m_bgn.span()[0]

        if i == len(m_sec_title) - 1:
            end = -1
        else:
            m_end = p_sec_bgn.search(help_str, 
                                       m_sec_title[i+1].span()[0] - 100)
            end = m_end.span()[0]
            
        secs[m_sec_title[i].group(1)] = help_str[bgn:end]
    
    return secs
    
secs = split_sec(legacy_help)

def parse_func_idx(help_str):
    subsec = collections.OrderedDict()
    p_subsec = re.compile('Cell\["(.+)", "Subsection",')
    p_func = re.compile('ButtonBox\["(.+)"')
    m_subsec = list(p_subsec.finditer(help_str))
    for i in range(len(m_subsec) - 1):
        bgn = m_subsec[i].span()[1]
        end = m_subsec[i+1].span()[0]
        m_func = p_func.findall(help_str, bgn, end)
        subsec[m_subsec[i].group(1)] = m_func

    bgn = m_subsec[-1].span()[1]
    end = -1 # bgn + re.search('"Section"', help_str[bgn:]).span()[0]
    m_func = p_func.findall(help_str, bgn, end)
    subsec[m_subsec[-1].group(1)] = m_func

    return subsec

secs['Index of Functions'] = parse_func_idx(secs['Index of Functions'])

def closing(title):
    name = None
    if title[0] == '\\':
        name = title[4:-4].split('\n')[1]
    else:
        name = title

    former='''ScreenStyleEnvironment->"Working",
WindowTitle->"'''
    latter='''",
TaggingRules->{
 "ModificationHighlight" -> False, "ColorType" -> "GuideColor", "LinkTrails" -> 
  GridBox[{{\
      RowBox[{
        ButtonBox[
        "Wolfram Language", ButtonData -> "paclet:guide/WolframRoot", 
         BaseStyle -> {"Link", "DockedLinkTrail"}]}]}}, ColumnAlignments -> 
    Left], "ExampleCounter" -> 1, "NeedPlatMsgIn" -> None, "RootCaptions" -> 
  "", "SearchTextTranslated" -> ""},
StyleDefinitions->Notebook[{
   Cell[
    StyleData[
    StyleDefinitions -> 
     FrontEnd`FileName[{"Wolfram"}, "Reference.nb", CharacterEncoding -> 
       "UTF-8"]]], 
   Cell[
    StyleData["Input"], CellContext -> "Global`"]}, Visible -> False, 
    StyleDefinitions -> "PrivateStylesheetFormatting.nb"]'''
    return ''.join([former, name, latter])

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
        
        # Exclude tailing ','
        end_idx = content.rfind(',')
        func_desc[name] = '\n'.join(['Notebook[{', content[:end_idx], '},', closing(name), ']', ''])

    name = m[i+1].group(1)
    begin = list(p1.finditer(help_str, m[i+1].span()[0] - 100, m[i+1].span()[0]))[-1].span()[0]
    end = help_str.find('AutoGeneratedPackage')
    content = help_str[begin:end]
    end_idx = content.rfind('Open')
    func_desc[name] = '\n'.join(['Notebook[{', content[:end_idx], closing(name), ']', ''])

    return func_desc

secs['Variables and Macros'] = parse_func_desc(secs['Variables and Macros'])

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

generate_func_help(secs['Variables and Macros'])

# print(secs['About the Package'])

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

# Generate a function category from BrowserCategories.m
def parse_category(cat_str):
    cat = collections.OrderedDict()

    m_start = re.search('Item\[Delimiter\],', cat_str)
    cat_str = cat_str[m_start.span()[1]:]
    m_cat = list(re.finditer('BrowserCategory\["(.+)",', cat_str))

    p = re.compile('Item\["(.+)",')
    for i in range(len(m_cat)):
        bgn = m_cat[i].span()[1]
        if i == len(m_cat) - 1:
            end = len(cat_str)
        else:
            end = m_cat[i+1].span()[0]

        cat[m_cat[i].group(1)] = p.findall(cat_str, bgn, end)
        
    return cat

fname = os.path.join(doc_en, 'BrowserCategories.m')
with open(fname) as f:
    cat_str = f.read()
cat = parse_category(cat_str)

def gen_func_lst_cell(func_lst):
    header = 'Cell[TextData[{'
    footer = '}], "Text"]'
    sep = \
''',
 "\[NonBreakingSpace]",
 StyleBox["\[MediumSpace]\[FilledVerySmallSquare]\[MediumSpace]"],
 " ",
'''
    template = \
'''ButtonBox["{SYMBOL}",
  BaseStyle->{{
   "Link", FontFamily -> "Courier New", FontColor -> 
    RGBColor[0.269993, 0.308507, 0.6]}},
  ButtonData->"paclet:SymbolicComputing/ref/{SYMBOL}"]
'''
    data = [template.format(SYMBOL=f) for f in func_lst]
    cell = header + sep.join(data) + footer

    return cell

# Generate a guide file.
fname = os.path.join(doc_en, 'Guides', 'SymbolicComputingPackage.nb')

with open(fname, 'w') as f:
    f.write('Notebook[{\n')
    f.write(secs['About the Package'])
    f.write(secs['Author'])
    f.write(secs['Copyright'])
    f.write(secs['Disclaimer'])
    f.write(secs['Distribution Policy'])
    f.write(secs['Version Compatibility'])
    f.write(secs['How to Start'])
    
    f.write('Cell[CellGroupData[{')
    f.write('Cell["Functions", "Section"],')

    for k in cat:
        f.write('Cell["{}", "Subsection"],'.format(k))
        f.write(gen_func_lst_cell(cat[k]))
        if k != 'W': f.write(',')

    f.write('}, Open  ]]')

    f.write(''.join(['},', closing("SymbolicComputing Package"), ']']))

# List up reference pages
ref_path = os.path.join(doc_en, 'ReferencePages', 'Symbols', '*')
ref_lst = glob.glob(ref_path)
ref_pat = re.compile('.+(ReferencePages.+)\.nb')
ref_lst = [ref_pat.search(i).group(1) for i in ref_lst]
ref_str = '"' + '",\n                "'.join(ref_lst) + '"'

# Generate PacletInfo.m
template = \
'''Paclet[
    Name -> {NAME},
    Version -> {VER},
    MathematicaVersion -> "9+",
    Extensions -> {{
        {{
            "Application",
            Root -> "SymbolicComputing",
            Context -> "SymbolicComputing`"
                }},
        {{
            "Documentation",
            Language -> "English", 
            LinkBase -> "SymbolicComputing",
            Resources -> {{
                "Guides/SymbolicComputingPackage"
      	        }}
            }},
        {{
            "Documentation",
            Language -> "English", 
            LinkBase -> "SymbolicComputing",
            Resources -> {{
                {REFERENCE}
      	        }}
            }}
    }}
]
'''

with open(os.path.join(base, 'PacletInfo.m'), 'w') as f:
    f.write(template.format(NAME=name, VER=ver, REFERENCE=ref_str))
    
