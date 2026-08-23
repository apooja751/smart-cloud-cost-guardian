import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, chr(39)+chr(119)+chr(39), encoding=chr(39)+chr(117)+chr(116)+chr(102)+chr(45)+chr(56)+chr(39)) as out:
        out.write(content)
    print(chr(39)+chr(87)+chr(114)+chr(111)+chr(116)+chr(101)+chr(58)+chr(39), path)
