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
    data = ff.read(4)
    if len(data) < 4: raise EOFError
    return int.from_bytes(data, 'little') & 0xFFFFFFFF

def ismatch(fn):
    return any(fnmatch.fnmatch(fn, pat) for pat in opts.files or ['*'])

count = readint()
print('archive contains', count - 1, 'files')
if count <= 0 or count > 1048576:
    print('archive appears invalid, exiting')
    sys.exit(1)
if count == 1: # could be a valid empty archive ¯\_(ツ)_/¯
    sys.exit(0)

lst = []
for i in range(count):
    offset = readint()
    name = ff.read(13).decode('oem').strip('\0')
    if len(name) > 12:
        print('archive appears invalid, exiting')
        sys.exit(1)
    if lst:
        offset1, name1 = lst[-1]
        if offset1 > offset:
            print('archive appears invalid, exiting')
            sys.exit(1)
        if ismatch(name1):
            print(name1, offset-offset1)
    lst.append((offset, name))
if(lst[-1][1] != ''):
    print('unexpected filename', lst[-1][1], 'for final directory entry')

for ((offset, name), (offset2, _)) in zip(lst, lst[1:]):
    size = offset2-offset
    if opts.mode == 'x':
        #ff.seek(offset)
        if '/' in name or '\\' in name:
            name = name.replace('/', '_').replace('\\', '_')
        data = ff.read(offset2-offset)
        if ismatch(name):
            with open(name, 'wb') as of:
                of.write(data)
