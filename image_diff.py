# compare two images. create a third image showing the difference between the
# two. in the diff image, black pixels means same color, and white pixels means
# different colors. can also optionally output a text file listing all the
# different pixels.

import Image
import sys



def diff(input1, input2, output, output_text):

    im1 = Image.open(input1)
    im2 = Image.open(input2)
    im = Image.new('RGB', im1.size)

    if output_text is not None:
        f = open(output_text, 'w')

    max_diff = 0
    count = 0
    for x in range(im1.size[0]):
        for y in range(im2.size[1]):
            p1 = im2.getpixel((x, y))
            p2 = im1.getpixel((x, y))
            if p1 != p2:
                im.putpixel((x, y), (255, 255, 255))
                count += 1

                difference = 0
                for i in range(3):
                    difference += abs(p1[i] - p2[i])
                max_diff = max(difference, max_diff)

                if output_text is not None:
                    f.write('-'*70 + '\n')
                    f.write('p1: %i %i %i %i\n' % 
                                           (p1[0], p1[1], p1[2], difference))
                    f.write('p2: %i %i %i %i\n' % 
                                           (p2[0], p2[1], p2[2], difference))
                    f.write('-'*70 + '\n')
            else:
                im.putpixel((x, y), (0, 0, 0))

    im.save(output)
    print 'done! -- output written to', output
    print count, 'pixels are different'
    print 'max difference is:', max_diff

    if output_text is not None:
        f.close()
        print 'output text written to:', output_text




if __name__ == '__main__':
    if len(sys.argv) < 4:
        print 'usage: <input1> <input2> <output> [output_text]'
    else:
        if len(sys.argv) == 4:
            diff(sys.argv[1], sys.argv[2], sys.argv[3], None)
        else:
            diff(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
