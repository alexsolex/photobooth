# -*- coding: utf-8 -*-
#
# Customize this to create the photomontage you love
#
from PIL import Image
# Size of the final picture montage
OUTPIC_SIZE         = (1090  ,800 )
# topleft photo offset (Horizontal,Vertical)
OUTPIC_PHOTO_OFFSET = (225,106 ) 
# background and stickers file names
BACKGROUND_FILENAME = 'background.png'
STICKERS_FILENAME   = 'stickers.png'


def make_montage(infile):
    """Create the photo montage and put the infile filename in the montage.
    Return a PIL image of the montage
    """

    #create a blank image
    blank = Image.new("RGB", OUTPIC_SIZE ,(25,23,24,255))

    #paste the background
    bg = Image.open(BACKGROUND_FILENAME)
    blank.paste(bg,(0,0))
    
    #paste the raw picture
    im = Image.open(infile)
    
    # past on background
    blank.paste(im,OUTPIC_PHOTO_OFFSET)

    #paste the stickers layer on the pic (a transparent png)
    stickers = Image.open(STICKERS_FILENAME)
    blank.paste(stickers,(0,0),stickers)

    return blank