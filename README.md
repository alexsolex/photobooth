# photobooth

Photobooth made for raspberry pi

## matériel

Cette liste peut être adaptée selon les besoins, elle ne concerne que le matériel *électrique*/*électronique*

* 1 x Ecran avec alimentation (récupération)

* 1 x Cable écran avec adaptateur éventuel vers HDMI (dépend de la connectique de l'écran)

* 1 x Raspberry PI 3  
https://www.amazon.fr/Raspberry-Pi-Carte-M%C3%A8re-Model/dp/B01CD5VC92

* 1 x Carte Micro SD classe 10

* 1 x Alimentation adaptée au Raspi (5V 3A)  
https://www.amazon.fr/Aukru-Chargeur-Adaptateur-Alimentation-Raspberry/dp/B01566WOAG

* 1 x Pi Camera avec sa nappe  
https://www.amazon.fr/Raspberry-Pi-1080p-Module-Cam%C3%A9ra/dp/B01ER2SKFS

* 1 x Relais 5V - 220V/10A  
https://www.amazon.fr/dp/B019GTTS3K/

* 2 x lampes GU10 avec supports (par exemple mais peut être remplacé par l'éclairage de son choix, voir pourquoi pas une lampe extérieur, attention au courant consommé par les lampes qui doit être inférieur au courant que peut piloter le relais )  
https://www.amazon.fr/Projecteur-Encastr%C3%A9-Douille-Ampoule-Halog%C3%A8ne/dp/B01JLNBVDQ

* 1 x connecteur c14 avec fusible et interrupteur   
https://www.amazon.fr/alimentation-interrupteur-module-admission-broches/dp/B00F4MFMXE

* 1 x cable alimentation 220V PC C13  
https://www.amazon.fr/Dexlan-Cordon-électrique-secteur-standard/dp/B0009M14YK

* 2 x boutons poussoirs type arcade  
https://www.amazon.fr/Cewaal-Shaped-Convexity-Replacement-Illuminated/dp/B075SBK17G

* Des fils de cablage pour connecter sur le port GPIO du RPi 
https://www.amazon.fr/s/ref=nb_sb_noss?__mk_fr_FR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&url=search-alias%3Daps&field-keywords=fils+arduino&rh=i%3Aaps%2Ck%3Afils+arduino

__Autre matériel__

* 1 x multiprise 220v (pour connecter l'écran et l'alimentation de raspberry)
* Du fil électrique 1.5mm² (cablage des lampes)
* Des dominos pour le raccordement électrique
* un fer à souder / de l'étain

## Installation (WIP)
__Prérequis :__
* J'ai choisi volontairement de ne pas rentrer dans les détails de l'utilisation d'un raspberry pi.
* Raccorder son raspberry Pi au réseau et à internet pour effectuer les mises à jours et autres installations
* Brancher clavier/souris et écran ou se connecter en SSH pour effectuer les manipulations
* Avoir quelques notions d'électricité (ATTENTION quand vous manipulez du 220v !)
* Avoir quelques notions d'électronique

### Software (WIP)


1. Installer Raspbian sur la carte microSD et procéder à toutes les mises à jours  (TODO)
0. Installer/mettre à jour les librairies python :
- picamera  (TODO)
- pygame  (TODO)
- GPIO  (TODO)
0. Configurer le raspberry (TODO)
0.
0.
0. Lancer le photobooth automatiquement au démarrage (TODO)

### Hardware (WIP)
__Nota__ : Je n'expliquerais pas ici la construction du boitier, chacun pouvant le réaliser selon ses compétences, ses besoins ... Cependant voici quelques remarques constaté avec l'usage :

* Pensez à la stabilité du photobooth. Il va être manipulé par plein de monde et certainement aussi des enfants !
* Pensez aux enfants : si les boutons sont trop haut, les enfants risquent de se mettre en danger (monter sur une chaise) ou encore de s'accrocher au photobooth pour pouvoir le manipuler
* Les utilisateurs regarderont l'écran pendant la prise de vue mais pas la caméra : La caméra devra être au plus proche de l'écran de manière à ce que le regard ne semble pas trop décalé sur la photo.
* Les lampes s'allumeront pendant la prise de vue (pour adapter l'autofocus) ce qui éblouira les utilisateurs. Pensez-y dans la conception et adaptez la position des lumières pour un compromis éclairage suffisant, mais pas trop éblouissant.

#### Schéma de cablage
TODO : mettre un lien vers le schéma général de cablage

