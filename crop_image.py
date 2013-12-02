# crop an image so it has the same number of
# background pixels in each direction

# default pad value is 0
# default background is white

# in PIL (0, 0) is the upper left corner
# indexing is in between pixels, so 0 is before first pixel



import argparse
import Image
import numpy
import sys

default_pad = 0
default_background = (255, 255, 255)  # white


def crop(input, output, pad=default_pad, background=default_background):

    if pad < 0:
        print 'Warning! pad is less than 0, setting pad to 0'
        pad = 0

    print 'input:', input
    print 'pad:', pad
    print 'background:', background

    im = Image.open(input)

    # get the images as an array of pixel values, and mask out
    # the background pixels
    data = numpy.array(im.getdata())
    data = numpy.resize(data, [im.size[1], im.size[0], len(data[0])])
    data = numpy.ma.masked_equal(data, background)

    # find the first and last rows of the image which contain 
    # non-background pixels
    rows = [None, None]
    for row in range(data.shape[0]):
        if not numpy.ma.getmaskarray(data[row, :]).all():
            if rows[0] is None:
                rows[0] = row
            else:
                rows[1] = row

    # find the first and last columns of the image which contain 
    # non-background pixels
    cols = [None, None]
    for col in range(data.shape[1]):
        if not numpy.ma.getmaskarray(data[:, col]).all():
            if cols[0] is None:
                cols[0] = col
            else:
                cols[1] = col

    # add one to the ends to include the last row and column
    rows[1] += 1
    cols[1] += 1

    print 'active rows:', rows
    print 'active cols:', cols

    # crop to active portion of image
    box = (cols[0], rows[0], cols[1], rows[1])
    region = im.crop(box)

    # add in desired amount of padding on each side
    width = cols[1] - cols[0] + pad*2
    height = rows[1] - rows[0] + pad*2
    final_image = Image.new(im.mode, (width, height), background)

    box = (pad, pad)
    final_image.paste(region, box)
    final_image.save(output)

    print 'all done! -- output written to', output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crop an image so it has the same number of background pixels in each direction.')

    parser.add_argument('input', help='input filename')
    parser.add_argument('output', help='output filename')
    parser.add_argument('--pad', '-p', type=int, default=default_pad, 
                        metavar='amt', help='pad amount')
    parser.add_argument('--background', '-b', default=(default_background), 
                        type=int, nargs=3, metavar='0-255', 
                        help='background color (default white)')

    args = parser.parse_args()

    crop(args.input, args.output, args.pad, tuple(args.background))


