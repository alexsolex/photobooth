# -*- coding: utf-8 -*-
#Cabaret vert
# Do you want to save all the approved picture with a distinct name on your Pi ?
#   True : Save the approved pics 
#   False : pics are not saved locally
SAVE_IN_FOLDER = True
# Specify the local relative folder where the pics will be saved
PHOTOS_PATH = "shots"

# Keep the original picture with no photomontage
KEEP_ORIGINAL_PIC = False

DISPLAY_IP_ADDRESS = False

# To display pictures slideshow, use secondary button.
# Set to True, to use the slideshow, False will prevent the use of slideshow
USE_SLIDESHOW = True

# We use Exif meta datas to store informations about the picture. Please set a comment to set in the exifs metas here
PICTURE_EXIF_COMMENT = u"Photo prise par le Photobooth HackArdennes !"

#
# FACEBOOK
#
SEND_ON_FACEBOOK = False

#Obtenir les tokens :
#   1/ aller sur l'explorateur de l'API graph ( https://developers.facebook.com/tools/explorer/ ) et choisir l'app Photobooth HackArdennes
#   2/ cliquer sur 'get Token' puis sur 'get user access token' pour obtenir un token utilisateur de courte durée : cocher 'publish actions', 'manage pages', et 'publish pages' puis 'Get access token'
#       --> ...
#   3/ nouvel onglet suivre le lien ci dessous (en remplacant les chants entre {}) pour échanger le token de courte durée contre un de longue durée 
#       https://graph.facebook.com/oauth/access_token?client_id={APP_ID}&client_secret={APP_SECRET}&grant_type=fb_exchange_token&fb_exchange_token={EXISTING_ACCESS_TOKEN}
#           APP_ID = "..."
#           APP_SECRET = "..."
#           EXISTING_ACCESS_TOKEN = short token
#       --> ...
#   4/ revenir sur l'explorateur de l'APIgraph et coller le token de longue durée obtenu, puis 'get token' puis choisir la page désirée (hackardennes)
#       --> ...
#   5/ copier le nouveau token dans le champ "Jeton d'accès" : c'est votre jeton qui devrait être définitif


FB_ACCESS_TOKEN = "..."
FB_ALBUM_ID = "..." 

FB_PICTURE_TEXT = "Commentaire accompagnant la photo sur un partage facebook"

#
# WORDING
#
TXT_WAIT_SCREEN  = u"\u00AB #HackCV17 \u00BB\n"
TXT_WAIT_SCREEN += u"\n"
TXT_WAIT_SCREEN += u"Laissez un souvenir de votre passage !\n"
TXT_WAIT_SCREEN += u"\n"
TXT_WAIT_SCREEN += u"Prenez vous en photo et\n"
TXT_WAIT_SCREEN += u"retrouvez la sur notre page\n"
TXT_WAIT_SCREEN += u"www.facebook.fr/hackardennes\n"
TXT_WAIT_SCREEN += u"\n"
TXT_WAIT_SCREEN += u"Appuyez sur le bouton rouge pour commencer !"
#TXT_WAIT_SCREEN += u"\n"

TXT_APPROVE_PIC = u"Bouton bleu pour conserver cette photo..."
TXT_CANCEL_SEND = u"Cette photo n'a pas été enregistrée\n\nBouton rouge pour recommencer."
TXT_SENDING_FB  = u"Mise en orbite de votre photo en cours..."
TXT_PIC_SENT    = u"Photo enregistrée, partagez-la :\nwww.facebook.fr/hackardennes !\nMerci !"


#
# OUTPUT PICTURE
#

#
# COLORS
#
GLOBAL_FONT_COLOR = (255,91,255)
BACKGROUND_COLOR = (11,42,81)
COUNTDOWN_FONT_COLOR = (255,34,43)

#
# FONTS (filenames must be stored at script root)
#
FONT_FILE = "FrontageCondensed-Regular.ttf"
COUNTDOWN_FONT_FILE = "Consolas.ttf"

#
# LOGO OF ORGANISATION
#
OWNER_LOGO = "logo_4_b.png"

#
# TWITTER
#

# Do you want to send the approved picture on twitter ?
#   True : Send the pic on twitter
#   False : bypass the twitter thing
# (set your twitter credentials with the account you wish to send the picture)
SEND_ON_TWITTER = False

# Twitter credentials
apiKey = ""
apiSecret = ""
accessToken = ""
accessTokenSecret = ""

# List all the messages you want to randomly use to post the approved pictures over twitter
#   /!\ Messages have to be shorter than 127 char (140 max twitter message size - 23 char for the picture url)
#       Messages longer than 127 char will be discarded from the random messages
Tweets_msgs = [
    # you can use the bottom numbers to know the size of your message
    # 0        1         2         3         4         5         6         7         8         9        10        11"
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567"
    u"Ceci est un tweet photo. Attention au blocage du compte !!",
    #|<------------------------------------------------------------ messages MUST be shorter than this limit ------------>|
    ]

#
# DROPBOX
#

# Do you want to upload the approved picture on a dropbox app folder ?
#   True : Send the picture on the dropbox app folder
#   False : bypass the Dropbox upload
DROPBOX_UPLOAD = False
# Do you want to display a QRcode pointing to the dropbox uploaded picture file ?
#   True : show the QRcode
#   False : bypass the QRcode generation
SHOW_DROPBOX_QRCODE = False

# Aller sur https://www.dropbox.com/developers/
#   Créer une app :
#       ChooseAPI : Dropbox API
#       Choose the type of access you need : App folder
#       Name your app : (doit être unique) mySuperPhotoboothDropbox
#       [Create app]
#   Chercher Generated access token, puis cliquer sur [Generate]
#       pour récupérer le token (chaine alphanumérique)
dropboxToken = "...."

# Compte à rebourg avant la prise de vue
TIME_BEFORE_SHOOT = 5 # x secs running before shooting
# Délai avant l'abandon de l'attente d'approbation de l'utilisateur
TIMEOUT_APPROVAL =  15 # Après ce délai, sans action de l'utilisateur, l'envoi de la photo est annulée
# Délai d'attente après l'envoi de la photo
TIMEOUT_AFTER_SENT = 30 # x secs to tell the pic has been sent
# Délai global avant retour à la page d'attente
TIMEOUT_NO_ACTION = 14 # x secs without action to go back to wait status
# Durée d'affichage entre 2 photos en mode diaporama
TIMEOUT_NEXT_SLIDE = 2 # x secs

