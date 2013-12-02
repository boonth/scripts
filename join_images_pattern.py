
# joins two sets of images together either horizontally or vertically
# accepts unix style pathname pattern expansion
# assumes the two patterns will resolve into the same base filenames
# optional pad amt
# if joining horizontally, first picture is left, second picture is right
# if joining vertically, first picture is top, second picture is bottom

import glob
import Image
import multiprocessing
import os
import sys

import join_images

# number of processes to use in parallel
num_procs = 8

def join(pattern1, pattern2, output_dir, mode, pad):

    start = time.time()

    files1 = glob.glob(pattern1)
    files2 = glob.glob(pattern2)

    files1.sort()
    files2.sort()

    # if the two file lists have different number of files, cut off the longer
    # one to match the length of the shorter one
    shorter = min(len(files1), len(files2))
    files1 = files1[:shorter]
    files2 = files2[:shorter]

    pool = multiprocessing.Pool(processes=num_procs)
    calls = []
    for file1, file2 in zip(files1, files2):
        output = os.path.basename(file1)
        output = os.path.join(output_dir, output)
        calls.append((file1, file2, output, mode, pad))

    for call in calls:
        pool.apply_async(join_images.join, args=call)

    pool.close()
    pool.join()

    print 'done! -- output written to', output_dir

    end = time.time()
    print 'total time is', (end - start), 'seconds'

def usage():
    print 'usage: <pattern1> <pattern2> <output dir> [\'h\'|\'v\'] [pad amt]'


if __name__ == '__main__':
    if len(sys.argv) < 4:
        usage()
    else:
        if len(sys.argv) == 4:
            # let the default be horizontal with zero pad
            join(sys.argv[1], sys.argv[2], sys.argv[3], 'h', 0)
        else:
            orientation = sys.argv[4].lower()
            if orientation == 'h' or orientation == 'v':
                pad = 0
                if len(sys.argv) > 5:
                    pad = int(sys.argv[5])
                join(sys.argv[1], sys.argv[2], sys.argv[3], orientation, pad)
            else:
                usage()
