# -*- coding: utf-8 -*-

import pygame
import pygame.camera
from pygame.locals import *
import time,random,datetime
import shutil,os.path
from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageFont
import socket
import fcntl
import struct
import config
import facebook
import piexif
#TODO
# - ajouter une option pour permettre de ne pas activer le slideshow
# - ajouter un timeout pour lancer le slideshow sur l'accueil 
# - Faire un système de lancement automatique de la prise de vue (pour attirer l'attention avec les flash)
# - terminer la factorisation des paramètres
# - améliorer la configuration (wifi, ...)
#DONE
# - design global
# - compte à rebour sur les différentes étapes
# - grossir le logo
# - appui sur A lors du compte à rebour pour revenir à la préparation
# - prévoir l'absence de réseau
# - ajouter le logo hackardenes sur le polaroid
# - réduire le polaroid pour ne pas perdre en qualité sur la photo
# - réparer le décompte avant abandon de la photo

############################################################################################
#  CONFIGURATION                                                                           #
############################################################################################

# Pour envoyer les tweets sans les messages 'officiels' (True : le message est basique / False : le message est aléatoire parmis les messages configurés)
TEST = False 

# Mode Debug : DEBUG = True pour ne pas envoyer de tweet du tout / False pour envoyer des Tweets
DEBUG = False

# Transform the picture into a polaroid photographe
RENDER_AS_POLAROID = True

# use a white background to act like a flash when shooting picture
USE_SCREEN_AS_FLASH = False

# Run the booth in full screen
RUN_FULLSCREEN = True

# if not full screen, size of the window
WINDOWED_MODE_SIZE = (800,800)

# use GPIO for button and/or flash
USE_GPIO = True

# Camera settings 
HFLIP = False
VFLIP = True

# FIN DE LA CONFIGURATION
#######################################################

# QRcode temporaire
QRCODE_FILENAME = "_temporaryQRCode.jpg"
# Nom des fichiers temporaires
TEMPORARY_FILENAME = "_temporary.jpg"
# polaroid filename
POLA_FILENAME = "_pola"+TEMPORARY_FILENAME #+".png"
# TODO : modifier le chemin et distinguer la photo prise de la photo générée
#TEMP_SHOOT_FILENAME = "shoot.jpg" #photo prise brut
#TEMP_PICTURE_FILENAME = "temporary.jpg" #photo travaillée

    
# imports facultatifs selon les options
if config.DROPBOX_UPLOAD:
    import dropbox
    dbx = dropbox.Dropbox(config.dropboxToken)
    if config.SHOW_DROPBOX_QRCODE:
        import qrcode

if config.SEND_ON_TWITTER:
    # clean the bad messages
    for m in config.Tweets_msgs:
        if len(m) > 117:
            print u"Suppression du message \"{0}\" car il dépasse la taille maxi".format(m)
            config.Tweets_msgs.remove(m)
    #check if list contain any message
    if len(config.Tweets_msgs)==0:
        raise Exception("ERROR : message for twitter are not correct")
    # import twitter python library
    from twython import Twython

FLASH_ON = True #False : interrupteur normalement fermé / True : interrupteur normalement ouvert
FLASH_OFF = not FLASH_ON
    
if USE_GPIO: #TODO : ajouter de l'électronique pour les boutons et un flash
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BOARD) # use board pin numbers
    # define pin #7 as input pin
    pin_buttonA = 7
    pin_buttonB = 8
    led1_pin    = 15 # LED 1
    GPIO.setup(led1_pin,GPIO.OUT) # LED 1
    GPIO.output(led1_pin, FLASH_OFF) #prepare off
    GPIO.setup(pin_buttonA, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
    GPIO.setup(pin_buttonB, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

# initialisations
pygame.init()
pygame.camera.init()
clock = pygame.time.Clock()

# Variables
frame_rate = 50

# pré-chargement des images en cache pour pygame
image_cache = {}
def get_image(key):
    """Pre-chargement des images pour améliorer les perf"""
    if not key in image_cache:
        image = pygame.image.load(key)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
        image_cache[key] = image
    return image_cache[key]

def make_polaroid(infile, outfile):
    import PhotoMontage
    montage = PhotoMontage.make_montage(infile)

    #create exif datas
    zeroth_ifd = {piexif.ImageIFD.Make: u"PiCamera HackArdennes",
                  piexif.ImageIFD.Software: u"Photobooth HackArdennes"
                  }
    exif_ifd = {piexif.ExifIFD.DateTimeOriginal: datetime.datetime.today().strftime('%Y:%m:%d %H:%M:%S'),
                piexif.ExifIFD.UserComment: config.PICTURE_EXIF_COMMENT}
    exif_dict = {"0th":zeroth_ifd, "Exif":exif_ifd}
    exif_bytes = piexif.dump(exif_dict)
    
    #Save as good quality ;) with exif metadatas
    montage.save(outfile, 'JPEG', subsampling=0, quality=100, exif=exif_bytes)   

def getATweet():
    """return a random choice for tweets"""
    return random.choice(config.Tweets_msgs)

def Tweet(message, picturefile):
    """Send the message as a Status with the picture"""
    print u"tweeting <<{0}>> with file '{1}'...".format(message,picturefile)
    if not DEBUG:
        twitter = Twython(config.apiKey,config.apiSecret,config.accessToken,config.accessTokenSecret)
        image_open = open(picturefile)
        image_ids = twitter.upload_media(media=image_open)
        tweetmsg = message
        if TEST:
            tweetmsg = "Photo envoyée le {0} #photobooth".format(time.strftime("%d/%m/%Y à %H:%M:%S"))

    try:	
        twitter.update_status(status = tweetmsg,media_ids = image_ids['media_id'])
    except Exception as e:
        print e.message

    print "done !"
 
def send_pic_FB(filename,message="Envoi automatique depuis le photobooth HackArdennes"):
    """send the picture 'filename' on the facebook album with the 'message' text""" 
    graph = facebook.GraphAPI(config.FB_ACCESS_TOKEN)
    print("Adding %s to the album ID#%s."%(filename,config.FB_ALBUM_ID))
    graph.put_photo(image       = open(filename, 'rb'),
                    album_path  = config.FB_ALBUM_ID + "/photos",
                    message     = message
                    )
      
def dbxUpload( fullname, folder, subfolder, name, overwrite=False):
    """Upload a file .

    Return the request response, or None in case of error.
    """
    path = '/%s/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'), name)
    while '//' in path:
        path = path.replace('//', '/')
    mode = (dropbox.files.WriteMode.overwrite
            if overwrite
            else dropbox.files.WriteMode.add)
    mtime = os.path.getmtime(fullname)
    with open(fullname, 'rb') as f:
        data = f.read()
    #with stopwatch('upload %d bytes' % len(data)):
    try:
        res = dbx.files_upload(
            data, path, mode,
            client_modified=datetime.datetime(*time.gmtime(mtime)[:6]),
            mute=True)
    except dropbox.exceptions.ApiError as err:
        print('*** API error', err)
        return None
    print('uploaded as', res.name.encode('utf8'))
    return res



test_server = 'www.google.fr'
def is_connected():
    connected = False
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((test_server, 80))
        connected = True
    except:
        print Exception
    return connected  

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


class Colors():
    BLACK           = (0, 0, 0)
    WHITE           = (255,255,255)
    PANTONE_339C    = (0, 179, 136)
    BLUE_TWITTER    = (85, 172, 238)
    BROWN           = (202,171,111)

class Status():
    INIT    = 0 # initialisation : first run
    WAIT    = 1 # waiting for user interaction
    READY   = 2 # user made interaction : waiting to shoot
    SHOOT   = 3 # shooting in progress
    APPROVE = 4 # shooting ended : display pics for approval
    SAVE    = 5 # saving pic in the folder
    UPDBX   = 6 # upload the pic to dropbox
    TWEET   = 7 # send the pic to twitter
    SEND    = 8 # pics approved : send it (twitter, mail, tumblr ...)
    SENT    = 9 # the pic has been sent
    SLIDESHOW = 10 # show a slide show

class TextRectException:
    def __init__(self, message = None):
        self.message = message
    def __str__(self):
        return self.message

def render_textrect(string, font, rect, text_color, background_color, transparent = False, justification=0):
    """Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Takes the following arguments:

    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rectstyle giving the size of the surface requested.
    text_color - a three-byte tuple of the rgb value of the
                 text color. ex (0, 0, 0) = BLACK
    background_color - a three-byte tuple of the rgb value of the surface.
    justification - 0 (default) left-justified
                    1 horizontally centered
                    2 right-justified

    Returns the following values:

    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """
    
    final_lines = []

    requested_lines = string.splitlines()

    # Create a series of lines that will fit on the provided
    # rectangle.

    for requested_line in requested_lines:
        if font.size(requested_line)[0] > rect.width:
            words = requested_line.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise TextRectException, "The word " + word + " is too long to fit in the rect passed."
            # Start a new line
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                # Build the line while the words fit.    
                if font.size(test_line)[0] < rect.width:
                    accumulated_line = test_line 
                else: 
                    final_lines.append(accumulated_line) 
                    accumulated_line = word + " " 
            final_lines.append(accumulated_line)
        else: 
            final_lines.append(requested_line) 

    # Let's try to write the text out on the surface.

    surface = pygame.Surface(rect.size) 
    surface.fill(background_color) 
    if transparent:
        surface.set_colorkey(background_color) #transparency

    accumulated_height = 0 
    for line in final_lines: 
        if accumulated_height + font.size(line)[1] >= rect.height:
            raise TextRectException, "Once word-wrapped, the text string was too tall to fit in the rect."
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            if justification == 0:
                surface.blit(tempsurface, (0, accumulated_height))
            elif justification == 1:
                surface.blit(tempsurface, ((rect.width - tempsurface.get_width()) / 2, accumulated_height))
            elif justification == 2:
                surface.blit(tempsurface, (rect.width - tempsurface.get_width(), accumulated_height))
            else:
                raise TextRectException, "Invalid justification argument: " + str(justification)
        accumulated_height += font.size(line)[1]
    margin = 10
    surface_final = pygame.Surface((surface.get_width()+(margin*2),accumulated_height+(margin*2)))
    surface_final.fill(background_color)
    if transparent:
        surface_final.set_colorkey(background_color) #transparency
    surface_final.blit(surface,(margin,margin))
    return surface_final

class Capture(object):
    def __init__(self):
        self.size = (640,640)
        # create a display surface. standard pygame stuff
        if RUN_FULLSCREEN:
            self.display = pygame.display.set_mode((0,0),FULLSCREEN)
        else:
            self.display = pygame.display.set_mode(WINDOWED_MODE_SIZE)

        # don't want to see the mouse pointer
        pygame.mouse.set_visible(False)

        # this is the same as what we saw before
        self.clist = pygame.camera.list_cameras()
        if not self.clist:
            raise ValueError("Sorry, no cameras detected.")
        self.cam = pygame.camera.Camera(self.clist[0], self.size)
        self.cam.start()
        self.cam.set_controls(vflip=VFLIP,hflip=HFLIP)#vflip hflip
        
        # create a surface to capture to.  for performance purposes
        # bit depth is the same as that of the display surface.
        self.snapshot = pygame.surface.Surface(self.size, 0, self.display)
        #self.snapshot = pygame.surface.Surface()

        self.font50 = pygame.font.Font(config.FONT_FILE, 50)
        self.font30 = pygame.font.Font(config.FONT_FILE, 30)
        self.font40 = pygame.font.Font(config.FONT_FILE, 40)

        self.font_timer = pygame.font.Font(config.COUNTDOWN_FONT_FILE,150)
        self.message = "OK"

        self.status = Status.INIT
        self.NextStatus = Status.INIT
        self.frame_count = 0

        self.flash = False # used for flashing during the shoot
        self.tweet_msg = ""
        self.time_shoot = "" 
        self.canceled = False
        self.newFilename = None

        self.USEREVENT_TIMEOUT_GLOBAL   = USEREVENT + 1
        self.USEREVENT_TIMEOUT_APPROVAL = USEREVENT + 2
        self.USEREVENT_SECOND           = USEREVENT + 3
        self.USEREVENT_BTNA             = USEREVENT + 4
        self.USEREVENT_BTNB             = USEREVENT + 5
        self.USEREVENT_TIMEOUT_SLIDE    = USEREVENT + 6
        
        self.ticks = 0

        # pre-load the images to speed-up
        for image in [config.OWNER_LOGO]:
            get_image(image)

        # init a picture for slideshow
        self.change_slide()

        #EVENTS FOR THE GPIO
        if USE_GPIO:
            self.start_event_detection()

    def btn_pushed(self,channel):
        """a button on GPIO has been pushed"""
        #time.sleep(0.4)
        #if GPIO.input(channel):
        if channel == pin_buttonA:
            print "pushed 'A' button",channel
            pygame.event.post(pygame.event.Event(self.USEREVENT_BTNA))
        elif channel == pin_buttonB:
            print "pushed 'B' button",channel
            pygame.event.post(pygame.event.Event(self.USEREVENT_BTNB))
        else:
            print "unknown button pushed"

    def start_event_detection(self):
        if USE_GPIO:
            GPIO.add_event_detect(pin_buttonA, GPIO.FALLING, callback=self.btn_pushed, bouncetime=400)
            #GPIO.add_event_detect(pin_buttonA, GPIO.FALLING, bouncetime=600)
            GPIO.add_event_detect(pin_buttonB, GPIO.FALLING, callback=self.btn_pushed, bouncetime=400)
            #GPIO.add_event_detect(pin_buttonB, GPIO.FALLING, bouncetime=600)

    def stop_event_detection(self):
        if USE_GPIO:
            GPIO.remove_event_detect(pin_buttonA)
            GPIO.remove_event_detect(pin_buttonB)

    def start_timer(self,  seconds = 5):
        self.ticks = seconds
        pygame.time.set_timer(self.USEREVENT_SECOND,1000)

    def stop_timer(self):
        #self.ticks = 0;
        pygame.time.set_timer(self.USEREVENT_SECOND,0)

    def tick_timer(self):
        if self.ticks > 0:
            self.ticks -= 1

    #def load_image(self,file_name, colorkey=False, image_directory='images'):
    #    'Loads an image, file_name, from image_directory, for use in pygame'
    #    file = os.path.join(image_directory, file_name)
    #    _image = get_image(file).convert() #pygame.image.load(file)
    #    if colorkey:
    #        if colorkey == -1: 
    #        # If the color key is -1, set it to color of upper left corner
    #            colorkey = _image.get_at((0, 0))
    #        _image.set_colorkey(colorkey)
    #        _image = _image.convert()
    #    else: # If there is no colorkey, preserve the image's alpha per pixel.
    #        _image = _image.convert_alpha()
    #    return _image

    def draw_snapshot(self):
        # if you don't want to tie the framerate to the camera, you can check 
        # if the camera has an image ready.  note that while this works
        # on most cameras, some will never return true.
        if self.cam.query_image():
            self.snapshot = self.cam.get_image(self.snapshot)

        snap_rect = self.snapshot.get_rect()
        snap_x = self.display.get_width() / 2 - snap_rect.width / 2
        snap_y = self.display.get_height() / 2 - snap_rect.height / 2
        self.display.blit(self.snapshot, (snap_x,snap_y))


    def show_pic(self):
        img=get_image(TEMPORARY_FILENAME)

        snap_rect = img.get_rect()
        snap_x = self.display.get_width() / 2 - snap_rect.width / 2
        snap_y = self.display.get_height() / 2 - snap_rect.height / 2
        
        img = pygame.transform.scale(img,self.size)
        self.display.blit(img,(snap_x,snap_y))
        
    def show_polaroid(self):
        img=pygame.image.load(POLA_FILENAME) #don't use cache here as the pic change each time
        ratio = 1 
        rotation = 0
        img = pygame.transform.rotozoom(img,
                                        rotation,  # rotation
                                        ratio  # ratio
                                        )
        snap_rect = img.get_rect()
        snap_x = self.display.get_width() / 2 - snap_rect.width / 2
        snap_y = self.display.get_height() / 2 - snap_rect.height / 2
        
        self.display.blit(img,(snap_x ,snap_y + 75))
        
    def show_tweet_msg(self):
        text_rect = pygame.Rect((0, 0, 600, 150))
        
        #transform the message in a multiline form
        rendered_text = render_textrect(self.tweet_msg, self.font30, text_rect, 
                                        Colors.WHITE,           # font  color
                                        Colors.BLUE_TWITTER,    # background color
                                        False,                  # not transparent
                                        1                       # centered
                                        )
        # rotate the text
        #rendered_text = pygame.transform.rotozoom(rendered_text,-3,1)
        
        text_rect = rendered_text.get_rect()
        text_x = self.display.get_width() / 2 - text_rect.width / 2
        #text_y = self.display.get_height() / 2 - text_rect.height / 2 
        text_y = 120
        self.display.blit(rendered_text, [text_x  , text_y])
        
     
    def show_logo(self):
        '''Display the logo at the bottom of the screen
        '''
        logo = get_image(config.OWNER_LOGO)
        logo_rect = logo.get_rect()
        
        logo_x = self.display.get_width() / 2 - logo_rect.width / 2
        logo_y = self.display.get_height() - logo_rect.height
       
        self.display.blit(logo, (logo_x,logo_y))

    def show_message( self, tcolor = config.GLOBAL_FONT_COLOR , vmiddle = False):
        '''
        Display the top message
        '''
        #text = self.font50.render(self.message, True, tcolor)
        #text_rect = text.get_rect()
        height=180
        if vmiddle:
            height = 300
        text_rect = pygame.Rect((0, 0, self.display.get_width(), height))
        text = render_textrect(self.message, self.font40, text_rect, 
                                tcolor,                     # font color
                                config.BACKGROUND_COLOR,    # background color
                                True,                       # transparent background
                                1                           # centered
                                )
        
        text_x = self.display.get_width() / 2 - text_rect.width / 2
        text_y = 0
        if vmiddle:
            text_y = self.display.get_height() / 2 - text_rect.height / 2
            
        self.display.blit(text, [text_x, text_y])

    def show_message_sent(self):
        height=300
        text_rect = pygame.Rect((0, 0, self.display.get_width(), height))
        text = render_textrect(self.message, self.font40, text_rect, 
                                config.GLOBAL_FONT_COLOR,           # white font
                                config.BACKGROUND_COLOR,    # green background
                                True,                   # transparent background
                                1                       # centered
                                )
        
        text_x = self.display.get_width() / 2 - text_rect.width / 2
        text_y = 0
            
        self.display.blit(text, [text_x, text_y])

    def show_counter(self):
        text = self.font_timer.render(self.message, True, config.COUNTDOWN_FONT_COLOR)
        text_rect = text.get_rect()
        text_x = self.display.get_width() / 2 - text_rect.width / 2
        text_y = self.display.get_height() / 2 - text_rect.height / 2
        if self.ticks == 0:
            text = pygame.transform.rotate(text,-90)
        self.display.blit(text, [text_x, text_y])

    def show_wait_screen(self):
        text_rect = pygame.Rect((0, 0, self.display.get_width(), 600))
        text = render_textrect(self.message, self.font50, text_rect, 
                                config.GLOBAL_FONT_COLOR,           # white font
                                config.BACKGROUND_COLOR,           # green background
                                True,                   # transparent background
                                1                       # centered
                                )
        text_x = self.display.get_width() / 2 - text_rect.width / 2
        text_y = self.display.get_height() / 2 - text_rect.height / 2
        self.display.blit(text, [text_x, text_y])
    
    def show_slide(self):
        if self.CurrentSlide:
            img=get_image(self.CurrentSlide) 
            ratio = 1 
            rotation = 0
            surface = pygame.transform.rotozoom(img,
                                            rotation,  # rotation
                                            ratio  # ratio
                                            )
            snap_rect = surface.get_rect() 
            
        else:
            snap_rect = pygame.Rect((0, 0, self.display.get_width(), 600))
            surface = render_textrect(u"Aucune image à afficher",
                                      self.font50, snap_rect, 
                                      config.GLOBAL_FONT_COLOR,           # white font
                                      config.BACKGROUND_COLOR,           # green background
                                      True,                   # transparent background
                                      1                       # centered
                                      )
        snap_x = self.display.get_width() / 2 - snap_rect.width / 2
        snap_y = self.display.get_height() / 2 - snap_rect.height / 2
        self.display.blit(surface,(snap_x ,snap_y ))

    def get_and_flip(self):
        # background :set white to mimic a flash
        backcolor = config.BACKGROUND_COLOR
        if self.flash :#and self.ticks<3:
            GPIO.output(led1_pin, FLASH_ON)
            if USE_SCREEN_AS_FLASH:
                backcolor = Colors.WHITE
                
        else:
            GPIO.output(led1_pin, FLASH_OFF )
            if USE_SCREEN_AS_FLASH:
                backcolor = Colors.WHITE
        self.display.fill(backcolor)
            
        if self.status == Status.INIT:
            self.show_wait_screen()
            pass
        elif self.status == Status.WAIT:
            self.show_wait_screen()
            self.show_logo()
        elif self.status == Status.READY:
            self.draw_snapshot()
            self.show_message()
            self.show_logo()
        elif self.status == Status.SHOOT:
            if self.NextStatus != Status.APPROVE: #self.ticks > 0 :
                self.draw_snapshot()
                self.show_counter()
            self.show_logo()

        elif self.status == Status.APPROVE:
            self.show_message()
            if RENDER_AS_POLAROID:
                self.show_polaroid()
            else:
                self.show_pic()
                self.show_logo()
            #self.show_tweet_msg()
        elif self.status == Status.SEND:
            self.show_message()
            self.show_logo()       
        elif self.status == Status.SAVE:
            self.show_message(vmiddle = True)
            self.show_logo()
        elif self.status == Status.TWEET:
            self.show_message(vmiddle = True)
            self.show_logo()
        elif self.status == Status.UPDBX:
            self.show_message(vmiddle = True)
            self.show_logo()
        elif self.status == Status.SENT:
            self.show_message_sent()
            self.show_polaroid()
        elif self.status == Status.SLIDESHOW:
            self.show_slide()
     
        pygame.display.flip()

    def change_slide(self):
        #Get a list of file
        list_pics = []
        for f in os.listdir(config.PHOTOS_PATH):
            fn = os.path.join( config.PHOTOS_PATH , f)
            if os.stat(fn).st_size > 0 and not os.path.isdir(fn):
                list_pics.append(fn)
        #pickup a random one
        if len(list_pics) > 0 :
            picture = random.choice(list_pics) 
        else:
            picture = None

        #use it for display
        print("slideshow : Change picture : %s file"%picture)
        self.CurrentSlide = picture

    def time_is_out(self,IdUserEvent):
        #clear the timer
        pygame.time.set_timer(IdUserEvent,0)#1000 * config.TIMEOUT_NO_ACTION
        #should go back to wait status
        self.NextStatus = Status.WAIT
        
    def main(self):
        going = True
        while going:
            events = pygame.event.get()
            PUSHB = False
            PUSHA = False
            
            for e in events:
                if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                    # close the camera safely
                    time.sleep(0.5)
                    self.cam.stop()
                    going = False

                if e.type == self.USEREVENT_TIMEOUT_GLOBAL:
                    print "End of global timeout"
                    self.time_is_out(self.USEREVENT_TIMEOUT_GLOBAL)

                if e.type == self.USEREVENT_TIMEOUT_APPROVAL :
                    print "End of approuval timeout"
                    self.time_is_out(self.USEREVENT_TIMEOUT_APPROVAL)

                if e.type == self.USEREVENT_TIMEOUT_SLIDE:
                    self.change_slide()
                    if self.status == Status.SLIDESHOW:
                        #Restart timer for next slide
                        pygame.time.set_timer(self.USEREVENT_TIMEOUT_SLIDE,1000 * config.TIMEOUT_NEXT_SLIDE)

                if e.type == self.USEREVENT_SECOND :
                    self.tick_timer()
                    if self.ticks==0:
                        print "End of countdown"
                        self.stop_timer()
                

                if e.type in [KEYDOWN,self.USEREVENT_BTNA,self.USEREVENT_BTNB] or PUSHB or PUSHA :
                    #reset the timout every time a key is pressed
                    pygame.time.set_timer(self.USEREVENT_TIMEOUT_GLOBAL,1000 * config.TIMEOUT_NO_ACTION)

                    #
                    # 'A' button in the events
                    #

                    if (e.type == KEYDOWN and e.key == K_a) or e.type == self.USEREVENT_BTNA or PUSHA:
                        if self.status == Status.WAIT:
                            #on démarre le shoot
                            self.start_timer(config.TIME_BEFORE_SHOOT)
                            self.flash = True
                            self.NextStatus = Status.SHOOT
                            
                        elif self.status == Status.READY:
                            self.start_timer(config.TIME_BEFORE_SHOOT)
                            self.flash = True
                            self.NextStatus = Status.SHOOT
                        
                        elif self.status == Status.SHOOT:
                            self.NextStatus = Status.WAIT
                            #avant de couper le flash on arrête les events
                            self.stop_event_detection()
                            #on abandonne le flash
                            self.flash = False
                            self.stop_timer()
                            self.get_and_flip()
                            time.sleep(0.4)
                            self.start_event_detection()

                        elif self.status == Status.APPROVE:
                            pygame.time.set_timer(self.USEREVENT_TIMEOUT_APPROVAL,0)
                            self.stop_timer()
                            self.NextStatus = Status.WAIT

                        elif self.status == Status.SEND:
                            self.NextStatus = Status.WAIT

                        elif self.status == Status.SENT:
                            self.NextStatus = Status.WAIT
                        
                        elif self.status == Status.SLIDESHOW:
                            self.NextStatus = Status.WAIT
                            pygame.time.set_timer(self.USEREVENT_TIMEOUT_SLIDE,0)
                    #
                    # 'B' button in the Events
                    #
                        
                    if (e.type == KEYDOWN and e.key == K_b) or e.type == self.USEREVENT_BTNB or PUSHB:
                        if self.status == Status.APPROVE:
                            if self.canceled == False:
                                self.NextStatus = Status.SEND
                                pygame.time.set_timer(self.USEREVENT_TIMEOUT_APPROVAL,0)    # arrêt du timer d'approbation
                                pygame.time.set_timer(self.USEREVENT_TIMEOUT_GLOBAL,0)      # arrêt du timer global d'annulation
                            
                        elif self.status == Status.SLIDESHOW:
                            self.NextStatus = Status.WAIT
                            pygame.time.set_timer(self.USEREVENT_TIMEOUT_SLIDE,0)

                        elif config.USE_SLIDESHOW and self.status in [ Status.WAIT, Status.READY, Status.SENT]:
                            self.NextStatus = Status.SLIDESHOW
                            pygame.time.set_timer(self.USEREVENT_TIMEOUT_SLIDE,1000 * config.TIMEOUT_NEXT_SLIDE)
                            pygame.time.set_timer(self.USEREVENT_TIMEOUT_GLOBAL,0)      # arrêt du timer global d'annulation

                            
            #
            # GESTION DES ETAPES
            #

            # INITIALISATION                 
            if self.status == Status.INIT:
                if (config.DISPLAY_IP_ADDRESS):
                    try:
                        print("Trying to get the local IPaddress")
                        ip = get_ip_address('wlan0') 
                        print(ip)
                        self.message = ip
                    except:
                        errorip = "IP address not found !\ntry with the following command :\nssh pi@rpisolex.local"
                        print(errorip)
                        self.message = errorip
                    self.get_and_flip()
                    time.sleep(2)
                self.NextStatus = Status.WAIT
                
            elif self.status == Status.WAIT:
                # Mode attente, affichage d'une page statique
                self.message = config.TXT_WAIT_SCREEN
                
            elif self.status == Status.READY:
                # Caméra affichée, en attente du bouton de départ
                self.message = u"Installez-vous et appuyez sur\nle bouton rouge quand vous êtes prêt"

            elif self.status == Status.SHOOT:
                self.canceled = False
                # Décompte et prise de vue
                # puis enregistrement de la photo de manière temporaire et présélection du tweet
                if self.ticks>0:
                    self.message = "{0}".format(self.ticks)
                    self.get_and_flip()
                else:
                    pygame.time.set_timer(self.USEREVENT_TIMEOUT_GLOBAL,0) 
                    self.NextStatus = Status.APPROVE
                    self.message = ":)"
                    self.stop_timer()
                    
                    img = self.cam.get_image()
                    img = pygame.transform.flip(img,True,False)
                    pygame.image.save(img, TEMPORARY_FILENAME)
                    
                    self.flash = False
                    self.stop_event_detection()
                    self.get_and_flip()
                    # mise en page polaroid de la photo
                    if RENDER_AS_POLAROID:
                        make_polaroid(TEMPORARY_FILENAME,POLA_FILENAME)
                    
                    # mémorise l'heure
                    self.time_shoot = time.strftime("%Y%m%d%H%M%S")
                    
                    #lancement du timeout d'approbation
                    self.start_timer(config.TIMEOUT_APPROVAL)
                    pygame.time.set_timer(self.USEREVENT_TIMEOUT_GLOBAL,1000 * (config.TIMEOUT_NO_ACTION+config.TIMEOUT_APPROVAL))
                
                    # récupère un tweet
                    self.tweet_msg = getATweet() + time.strftime(" %H:%M:%S")

                    #on réactive les détections d'event
                    self.start_event_detection()
                    
                    
                                            
            elif self.status == Status.APPROVE:
                # La photo est proposée pour accord et validation
                if config.SEND_ON_TWITTER and config.SEND_ON_FACEBOOK:
                    m = u"Appuyer sur le bouton bleu pour envoyer ceci sur Twitter et Facebook"
                elif config.SEND_ON_TWITTER:
                    m = u"Appuyer sur le bouton bleu pour envoyer ceci sur Twitter"
                elif config.SEND_ON_FACEBOOK:
                    m = config.TXT_APPROVE_PIC
                elif config.DROPBOX_UPLOAD:
                    m = u"Appuyer sur le bouton bleu pour envoyer sur Dropbox"
                elif config.SAVE_IN_FOLDER:
                    m = u"Appuyer sur le bouton bleu pour conserver la photo"
                else:
                    m = u"Appuyer sur le bouton bleu pour continuer"

                self.message = m
                
                if self.ticks>0:
                    self.message += "\n(abandon dans {0}s)".format(self.ticks)
                    #self.get_and_flip()
                else:
                    self.message = config.TXT_CANCEL_SEND
                    self.canceled = True
                
            elif self.status == Status.SEND:
                # On s'apprête à enregistrer/envoyer la photo.
                pygame.time.set_timer(self.USEREVENT_TIMEOUT_GLOBAL,0)# d'abord on arrete le timer d'annulation
                self.newFilename = "IMG_{0}.{1}".format(self.time_shoot,POLA_FILENAME.split(".")[-1])
                print("send...")
                self.NextStatus = Status.SAVE

            elif self.status == Status.SAVE:
                # Enregistrement de la photo dans le répertoire de sauvegarde du PI
                print "Status.SAVE"
                # saving picture time !
                if config.SAVE_IN_FOLDER:
                    self.message = "Sauvegarde de la photo"
                    self.get_and_flip()
                    dst = os.path.join( config.PHOTOS_PATH , self.newFilename)
                    if config.KEEP_ORIGINAL_PIC:
                        if not os.path.exists( 'RAW' ):
                            os.makedirs('RAW')
                        shutil.copy( TEMPORARY_FILENAME , os.path.join( 'RAW' ,  "IMG_{0}_RAW.{1}".format(self.time_shoot,POLA_FILENAME.split(".")[-1])) )
                    if not os.path.exists( dst ):
                        if RENDER_AS_POLAROID:
                            shutil.copy( POLA_FILENAME , dst )
                        else:
                            shutil.copy( TEMPORARY_FILENAME , dst )
                self.NextStatus = Status.TWEET

            elif self.status == Status.TWEET:
                print "Status.TWEET"
                if config.SEND_ON_FACEBOOK:
                    if RENDER_AS_POLAROID:
                        dst = POLA_FILENAME
                    else:
                        dst = TEMPORARY_FILENAME
                    
                    self.message = config.TXT_SENDING_FB
                    self.get_and_flip()
                    if is_connected():
                        try:
                            send_pic_FB(dst,config.FB_PICTURE_TEXT)
                        except:
                            print "error while uploading to facebook"
                    else:
                        print "ERROR : cannot send to Facebook : no internet connexion"
                
                if config.SEND_ON_TWITTER: 
                    if RENDER_AS_POLAROID:
                        dst = POLA_FILENAME
                    else:
                        dst = TEMPORARY_FILENAME
                    
                    self.message = u"@hackardenpic envoi votre photo sur Twitter..."
                    self.get_and_flip()
                    if is_connected():
                        Tweet(self.tweet_msg,dst)
                    else:
                        print "ERROR : cannot send to Twitter : no internet connexion"
                
                self.NextStatus = Status.UPDBX
            
            elif self.status == Status.UPDBX:
                # upload sur le compte DROPBOX
                print "Status.UPDBX"
                if config.DROPBOX_UPLOAD:
                    self.message = "Sculpture de votre oeuvre dans les nuages..."
                    self.get_and_flip()
                    dst = os.path.join( config.PHOTOS_PATH , self.newFilename)
                    if is_connected():
                        if dbxUpload(dst,"","",self.newFilename):
                            metaData = dbx.sharing_create_shared_link("/"+self.newFilename,short_url=True)
                            #generation QRCode
                            if config.SHOW_DROPBOX_QRCODE:
                                img = qrcode.make(metaData.url)
                                with open(QRCODE_FILENAME,"w") as f:
                                    img.save(f)
                        else:
                            print "Error while uploading picture to dropbox"
                    else:
                        print "ERROR : cannot upload to Dropbox : no internet connexion"
                pygame.time.set_timer(self.USEREVENT_TIMEOUT_GLOBAL,1000 * config.TIMEOUT_AFTER_SENT)
                self.NextStatus = Status.SENT
            
            elif self.status == Status.SENT:
                # affichage de la photo avec un remerciement
                self.message = config.TXT_PIC_SENT
                
            elif self.status == Status.SLIDESHOW:
                #display a slideshow with pictures already shots
                pass  
                


            #
            clock.tick(frame_rate)
            # Affichage graphique
            self.get_and_flip()
            self.status = self.NextStatus


        
try:
    c = Capture()
    c.main()
    
except KeyboardInterrupt:
    print "Interruption manuelle du photobooth"
finally:
    if USE_GPIO:
        #turn off the lights
        GPIO.output(led1_pin, FLASH_OFF) 
    pygame.quit()
GPIO.cleanup()