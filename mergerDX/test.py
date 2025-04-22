from modules.parser.parse_file import parseFile
import os

filepath = 'C:/fuentes/msm-crmdistribucion/force-app/main/default/profiles/'
#filename = 'C:/fuentes/msm-sherpa/force-app/main/default/profiles/MSM Management.profile-meta.xml'
for filename in os.listdir(filepath):
    print(filename)
    if filename.startswith("Admi"):
        continue
    parseFile( filepath+filename, 'release' )
#mytree = ET.parse('C:/fuentes/msm-sherpa/force-app/main/default/profiles/MSM Management.profile-meta.xml')
#myroot = mytree.getroot()