# create a video from a stack of images
#
# Takes a list of input files, with the last argument being the output.
# Assumes that input files have a common prefix and suffix, and that
# in between, the only differences are numbers. Files are sorted by
# this number.
#
#


import argparse
import multiprocessing
import os
import shutil
import subprocess
import sys
import tempfile

# the encoder to use. they seem to basically be equivalent
encoder = 'ffmpeg'
#encoder = 'avconv'

# files are copied to a temporary location in parallel
default_num_procs = 8

# how fast the video plays
default_framerate = 50

# crf mean Constant Rate Factor, and denotes the video quality. values for
# crf range from 0 to 53 (0 being highest quality). sane values are from 18
# to 28. the normal default is 23.
default_crf = 15

def create_video(filenames, output, framerate=default_framerate, 
                 num_procs=default_num_procs, crf=default_crf):

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
    # we do this by reversing each string, finding the prefix, and
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
    print ''

    # create video
    template = prefix + '%' + 'd' + suffix
    template = os.path.join(temp_dir, template)

    # Note: the -pix_fmt yuv420p is used so that it plays on older video
    # players. if left out, it defaults to another pixel format that cannot be
    # played on macs at the moment. libx264 is also specified to ensure that
    # H.264 is used, for highest compatibility
    cmd = [encoder,
           '-r', str(framerate), 
           '-f', 'image2', 
           '-i', template, 
           '-pix_fmt', 'yuv420p', 
           '-c:v', 'libx264', 
           '-crf', str(crf),
           output]
    print '-'*70
    print ' '.join(cmd)
    print '-'*70
    print ''
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
                        metavar='N',
                        help='framerate, default=%i' % default_framerate)
    parser.add_argument('-np', type=int, 
                        default=default_num_procs, 
                        metavar='N',
                        help='number of procs (for parallel copying), default=%i' % default_num_procs)
    parser.add_argument('-crf', type=int, 
                        default=default_crf, 
                        metavar='N',
                        help='video quality, default=%i' % default_crf)

    args = parser.parse_args()

    create_video(args.input, args.output, args.framerate, args.np, args.crf)


