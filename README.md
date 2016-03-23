# SC-Help-Converter

Help Migration Script of 'Symbolic Computing Package for Mathematica.'

Symbolic Computing Package for Mathematica (SCPM) is a third party package for Wolfram Mathematica. SCPM has a homepage, http://symbcomp.gist.ac.kr/ and you can find the download and installation instructions. It provides a quite complete set of functions to manupulate and evaluate equations. Though SCPM provides a good user documents, it uses the old-styled help platform which is called a 'Help Browser.' 

It seems that Wolfram Research wants to deprecate the 'Help Browser'. On Linux, the Help Browers invokes many problems, such as, memory leak, segmantation fault, and you can hardly get help about this problem from Wolfram Research.

This script converts the user documentation of SCPM to the new 'Documentation Center' style.

# Usage
Before execute this script, you need to install SCPM properly. Please, follow instructions on http://symbcomp.gist.ac.kr/. Then, execute the following script.
```bash
python converter.py
```

## License
This conversion script follows GPLv3. SCPM follows its own license.

