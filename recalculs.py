from lxml import etree as ET

import os.path
from glob import iglob

from PIL import Image
from PIL.ExifTags import TAGS

# Si jamais c'est plus simple pour récupérer les noms de fichier
#import re

def main():
    
    # Application sur multi-fichiers
    # Chemin d'accès du répertoire où sont stockés les fichiers texte
    # Par défaut, "directory"
    directory = "/users/anne.bugner/XMLForest/Alto/Calfas/"
    extension = "alto_in/*.xml"
    
    altofiles = iglob(os.path.join(directory, extension))
    for altofile in altofiles:
        if os.path.isfile(altofile):    
        
            # Récupération du nom de fichier, sans répertoire ni extension
            filename = altofile[-31:]
            # filename = re.search(r"(?<=directory\/).+(?=\.xml), altofile).group()

            # Parser et namespaces
            xml_parser = ET.XMLParser(remove_blank_text=True)
            tree = ET.parse(altofile, xml_parser)
            alto = tree.getroot()

            xsi = 'http://www.w3.org/2001/XMLSchema-instance'
            xmlns = 'http://www.loc.gov/standards/alto/ns-v4#'
            schemaLocation = 'http://www.loc.gov/standards/alto/ns-v4# http://www.loc.gov/standards/alto/v4/alto-4-3.xsd'
            nsmap={'xmlns:xsi':xsi, 'xmlns':xmlns, 'xsi:schemaLocation':schemaLocation, 'None':xmlns}
            nsmap = {k:v for k, v in alto.nsmap.items()}
            
            ratio = get_ratio(alto, nsmap, filename)
            alto = recalculs(alto, nsmap, ratio)
            
            # Génération du fichier de sortie
            with open('alto_out/' + filename, "w", encoding="utf-8") as f:
                f.write(ET.tostring(alto, pretty_print=True, encoding="utf-8", xml_declaration=True).decode('utf-8'))
    print("Nouveaux fichiers xml-alto générés.")


def get_ratio(alto, nsmap, filename):
    ### Calcul du facteur de réduction

    # Identification du jpg correspondant au fichier alto ; extraction de sa résolution
    jpg = alto.find('./Description/sourceImageInformation/fileName', nsmap)
    jpgname = jpg.text
    image = Image.open('jpgs/' + jpgname)
    jpg_width = image.width
    jpg_height = image.height

    # Extraction de la résolution initiale inscrite dans le fichier alto (pour image jp2)
    layout_alto = alto.find('./Layout/Page', nsmap)
    jp2_width = int(layout_alto.get('WIDTH'))
    jp2_height = int(layout_alto.get('HEIGHT'))

    # Calculer le ratio jpg2/jpg pour chaque image
    # Vérifier que ce ratio le même pour la largeur et la hauteur (car parfois ce n'est pas le cas)
    # On arrondit le résultat à 2 décimales pour l'uniformiser au maximum sans trop déformer
    ratioW = round(jp2_width / jpg_width, 2)
    ratioH = round(jp2_height / jpg_height, 2)
    # Si le ratio n'est toujours pas uniforme, trancher en adoptant le ratio hauteur (déterminant pour l'utilisation future en visionneuse)
    if ratioW != ratioH:
        print(f"{filename} : il a fallu trancher, pour le ratio")
    ratio = ratioH
    return ratio

### Recalcul de toutes les valeurs d'attribut (coordonnées spatiales des caractères sur l'image)
def recalculs(alto, nsmap, ratio):

    page = alto.find('./Layout/Page', nsmap)
    attributes = [{"WIDTH":"//*[@WIDTH]"}, {"HEIGHT":"//*[@HEIGHT]"}, {"HPOS":"//*[@HPOS]"}, {"VPOS":"//*[@VPOS]"}]
    points_attributes = [{"BASELINE":"//*[@BASELINE]"}, {"POINTS":"//*[@POINTS]"}]
    
    # @WIDTH, @HEIGHT, @HPOS, @VPOS (1 nombre à recalculer)
    for attribute in attributes:
        for att, query in attribute.items():
            xpath = page.xpath(query)
            for element in xpath:
                reduction(element, att, ratio)
                
    # @BASELINE, @POINTS (contiennent chacun 1 liste de nombres à recalculer)    
    for attribute in points_attributes:
        for att, query in attribute.items():
            xpath = page.xpath(query)
            for element in xpath:
                other_reduction(element, att, ratio)
    
    return alto    
 

# Fonction de réduction simple : 1 nombre
def reduction(element, attribute, ratio):
    value = int(element.get(attribute))
    newvalue = set_newnumber(value, ratio)
    element.set(attribute, newvalue)
    return element

# Fonction de réduction complexe : 1 suite de nombres séparés par un espace
def other_reduction(element, attribute, ratio):
    pointlist = element.get(attribute)
    pointlist = pointlist.split(' ')
    newvalue = ""
    for point in pointlist:
        # Recalcul de chaque nombre
        newpoint = set_newnumber(int(point), ratio)
        # Concaténer tous les nombres avec espaces de séparation
        newvalue = newvalue + newpoint + ' '
    newvalue = newvalue[:-1]    
    element.set(attribute, newvalue)    
    return element

# Calcul
def set_newnumber(value, ratio):
    newvalue = round(value / ratio)
    newvalue = str(newvalue)
    return newvalue
            

main()
