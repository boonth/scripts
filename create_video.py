# create a video from a stack of images
#
# assume that input_template will result in a list of filenames that have
# a common prefix and suffix, and are differentiated by increasing numbering
#


import argparse
import multiprocessing
import os
import shutil
import subprocess
import sys
import tempfile

default_num_procs = 8
default_framerate = 50
encoder = 'avconv'

def create_video(filenames, output, framerate=default_framerate, 
                 num_procs=default_num_procs):

    if len(filenames) == 0:
        print "Error! No filenames given"
        print 'Aborting...'
        return

    # find the base filenames
    base_filenames = [os.path.basename(x) for x in filenames]

    # find the longest common prefix among filenames
    prefix = os.path.commonprefix(base_filenames)
    print 'prefix:', prefix

    # find the longest common suffix among filenames.
    # we do this be reversing each string, finding the prefix, and
    # reversing the prefix to get the final suffix.
    filenames_reverse = [x[::-1] for x in base_filenames]
    suffix = os.path.commonprefix(filenames_reverse)
    suffix = suffix[::-1]
    print 'suffix:', suffix

    # get a list of all numbers, which we assume is what we'll get when
    # the prefix and suffix is stripped off each filename.
    numbers = [int(x[len(prefix):x.rfind(suffix)]) for x in base_filenames]
    #print 'numbers:', numbers

    # sort filenames by their numbers
    filenames = zip(numbers, filenames)
    filenames.sort()
    filenames = [x[1] for x in filenames]

    # create a reordered list of filenames, such that the numbering starts
    # at 0 and increases by 1. create a new list of filenames with these
    # new numbers.
    ordered = []
    for i in range(len(numbers)):
        ordered.append(prefix + str(i) + suffix)

    # create a temporary directory where images can be copied with with thier
    # ordered filename
    temp_dir = tempfile.mkdtemp()

    # add in path to temp dir
    ordered = [os.path.join(temp_dir, x) for x in ordered]

    # copy images to temp dir with new ordered filename
    pool = multiprocessing.Pool(processes=num_procs)
    print 'copying images...'
    for filename, new_filename in zip(filenames, ordered):
        pool.apply_async(shutil.copyfile, args=(filename, new_filename))
    pool.close()
    pool.join()
    print 'done copying images...'

    # create video
    template = prefix + '%' + 'd' + suffix
    template = os.path.join(temp_dir, template)
    cmd = [encoder, '-r', str(framerate), 
           '-f', 'image2', 
           '-i', template, 
           '-qscale', '1', output]
    print '-'*70
    print ' '.join(cmd)
    print '-'*70
    subprocess.call(cmd)
    print ''


    # cleanup
    shutil.rmtree(temp_dir)

    print 'all done! -- output written to', output
    print ''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a video from a stack of images.')

    parser.add_argument('input', nargs='+', 
                        help='input filenames')
    parser.add_argument('output', help='output video filename (*.mp4)')
    parser.add_argument('--framerate', '-r', type=int, 
                        default=default_framerate, 
                        metavar='N', help='framerate')
    parser.add_argument('-np', type=int, 
                        default=default_num_procs, 
                        metavar='N', help='number of procs')

    args = parser.parse_args()

    create_video(args.input, args.output, args.framerate, args.np)


