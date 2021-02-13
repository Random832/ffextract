import sys
import os
import argparse
import fnmatch

parser = argparse.ArgumentParser(description='Extract a DirectX FastFile Archive.')
parser.add_argument('-x', '--extract', dest='mode', action='store_const', const='x', default='t')
parser.add_argument('-t', '--list', dest='mode', action='store_const', const='t', default='t')
parser.add_argument('-f', '--file', dest='archive', type=str, metavar='ARCHIVE.FF')
parser.add_argument('-C', '--directory', dest='dir', type=str)
#parser.add_argument('-v', '--verbose', dest='verbose', action='store_true')
parser.add_argument('files', metavar='FILES', type=str, nargs='*',
                    help='The files within the archive to extract')
opts = parser.parse_args()

fname = opts.archive
ff = open(fname, 'rb')

if opts.dir:
    os.makedirs(opts.dir, exist_ok=True)
    os.chdir(opts.dir)

def readint():
    return int.from_bytes(ff.read(4), 'little')

count = readint()
lst = []
for i in range(count-1):
    offset = readint()
    name = ff.read(13).decode('oem').strip('\0')
    if '/' in name or '\\' in name:
        name = name.replace('/', '_').replace('\\', '_')
    lst.append((offset, name))
eoffset = readint()
lst.append((eoffset, None))

def ismatch(fn):
    return any(fnmatch.fnmatch(fn, pat) for pat in opts.files or ['*'])

for ((offset, name), (offset2, _)) in zip(lst, lst[1:]):
    size = offset2-offset
    if ismatch(name):
        print(name, size)
    if opts.mode == 'x':
        #ff.seek(offset)
        data = ff.read(offset2-offset)
        if ismatch(name):
            with open(name, 'wb') as of:
                of.write(data)
