
# joins two image together either vertically or horizontally.
# optional pad amt
# if joining horizontally, first picture is left, second picture is right
# if joining vertically, first picture is top, second picture is bottom

import sys
import Image



def join(input1, input2, output, mode, pad):

    im1 = Image.open(input1)
    im2 = Image.open(input2)
        
    if mode.lower() == 'h':
        # join horizontally
        width = im1.size[0] + im2.size[0] + pad
        height = max(im1.size[1], im2.size[1])
        im = Image.new('RGB', (width, height))

        im.paste(im1, (0, 0))
        im.paste(im2, (im1.size[0] + pad, 0))
    elif mode.lower() == 'v':
        # join vertically
        width = max(im1.size[0], im2.size[0])
        height = im1.size[1] + im2.size[1] + pad
        im = Image.new('RGB', (width, height))

        im.paste(im1, (0, 0))
        im.paste(im2, (0, im1.size[1] + pad))

    im.save(output)

    #print 'output written to', output

def usage():
    print 'usage: <input1> <input2> <output> [\'h\'|\'v\'] [pad amt]'


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
