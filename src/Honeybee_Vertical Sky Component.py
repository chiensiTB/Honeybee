# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Analysis Recipie for Vertical Sky Component

The idea Based on this discussion on RADIANCE: http://www.radiance-online.org/pipermail/radiance-general/2006-September/004017.html
-
Provided by Honeybee 0.0.52
    
    Args:
        _testPoints: Test points
        ptsVectors_: Point vectors
        uniformSky_: Set to true to run the study under a CIE uniform sky. Default is set to cloudy sky
    Returns:
        analysisRecipe: Recipe for vertical sky component
"""

ghenv.Component.Name = "Honeybee_Vertical Sky Component"
ghenv.Component.NickName = 'verticalSkyComponent'
ghenv.Component.Message = 'VER 0.0.52\nMAR_17_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "3 | Daylight | Recipes"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import Rhino as rc
import Grasshopper.Kernel as gh

import os
import scriptcontext as sc

def genVSCSky(illuminanceValue = 1000, skyType = "-c"):

    def RADDaylightingSky(illuminanceValue, skyType):
        # gensky 12 4 +12:00 -c -B 55.866 > skies/sky_10klx.mat
        return  "# start of sky definition for vertical sky component calculation\n" + \
                "# horizontal sky illuminance: " + `illuminanceValue` + " lux\n" + \
                "!gensky 12 6 12:00 " + skyType + " -B " +  '%.3f'%(illuminanceValue/179) + "\n" + \
                "skyfunc glow sky_mat\n" + \
                "0\n" + \
                "0\n" + \
                "4\n" + \
                "1 1 1 0\n" + \
                "sky_mat source sky\n" + \
                "0\n" + \
                "0\n" + \
                "4\n" + \
                "0 0 1 180\n" + \
                "# end of sky definition for daylighting studies\n\n"
    
    path  = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "skylib\\VSCSimulationSky\\")
    if not os.path.isdir(path): os.mkdir(path)
    
    outputFile = path + `int(illuminanceValue)` + "_lux.sky"
    
    skyStr = RADDaylightingSky(illuminanceValue, skyType)
    
    skyFile = open(outputFile, 'w')
    skyFile.write(skyStr)
    skyFile.close()
    
    return outputFile

def isAllNone(dataList):
    for item in dataList:
        if item!=None: return False
    return True


class DLAnalysisRecipe(object):
    
    def __init__(self, type, *arg):
        """
        types:
            0: image based analysis
            1: node based analysis
            2: annual simulation (Daysim for now)
            3: daylight factor
            4: vertical sky component
        """
        self.type = type
        
        # based on the type it should return different outputs
        if type == 0:
            self.skyFile = arg[0]
            self.viewNames = arg[1]
            try: self.radParameters = arg[2].d
            except: self.radParameters = arg[2]
            self.cameraType = arg[3]
            self.simulationType = arg[4]
            self.imageSize = arg[5], arg[6]
            self.studyFolder = "\\imageBasedSimulation\\"
            
        elif type == 1:
            self.skyFile = arg[0]
            self.testPts = self.convertTreeToLists(arg[1])
            self.vectors = self.convertTreeToLists(arg[2])
            try: self.radParameters = arg[3].d
            except: self.radParameters = arg[3]
            self.simulationType = arg[4]
            self.studyFolder = "\\gridBasedSimulation\\"
            
        elif type == 2:
            self.weatherFile = arg[0]
            self.testPts = self.convertTreeToLists(arg[1])
            self.vectors = self.convertTreeToLists(arg[2])
            try: self.radParameters = arg[3].d
            except: self.radParameters = arg[3]
            self.DSParameters = arg[4]
            self.studyFolder = "\\annualSimulation\\"
        
        elif type == 3:
            self.skyFile = arg[0]
            self.testPts = self.convertTreeToLists(arg[1])
            self.vectors = self.convertTreeToLists(arg[2])
            try: self.radParameters = arg[3].d
            except: self.radParameters = arg[3]
            self.simulationType = 0 #illuminance
            self.studyFolder = "\\DF\\"
        
        elif type == 4:
            self.skyFile = arg[0]
            self.testPts = self.convertTreeToLists(arg[1])
            self.vectors = self.convertTreeToLists(arg[2])
            try: self.radParameters = arg[3].d
            except: self.radParameters = arg[3]
            self.simulationType = 0 #illuminance
            self.studyFolder = "\\VSC\\"
        
        # double check the sky in case of grid based and image based simulations
        if type ==0 or type == 1:
            self.checkSky()
                    
    def convertTreeToLists(self, l):
        listOfLists = []
        for path in l.Paths:
            listOfLists.append(l.Branch(path))
        return listOfLists
    
    def checkSky(self):
        if self.simulationType == 1:
            # make sure the sky is either gencum or gendaylit
            # edit in case of gendaylit
            self.radSkyFile = self.skyFile.split(".")[0] + "_radAnalysis.sky"
            skyOut = open(self.radSkyFile, "w")
            genDaylit = False
            with open(self.skyFile, "r") as skyIn:
                for line in skyIn:
                    if line.startswith("!gensky"):
                        self.skyFile = None
                        msg = "You need to use one of the climate-based skies for radiation analysis.\n" + \
                              "Change the skyFile and try again"
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                        return
                    elif line.startswith("!gendaylit"):
                        line = line.replace("-O 0", "-O 1")
                        genDaylit = True
                    # write a new file
                    skyOut.write(line)
            skyOut.close()
            self.skyFile = self.radSkyFile
            if not genDaylit:
                self.simulationType = 1.1 # annual radiation analysis
        
        else:
            # make sure the sky is not from gencum
            with open(self.skyFile, "r") as skyIn:
                for line in skyIn:
                    if line.strip().startswith("2 skybright") and line.strip().endswith(".cal"):
                        self.skyFile = None
                        msg = "Cumulative sky can only be used for radiation analysis.\n" + \
                              "Change the skyFile and try again"
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                        return



if sc.sticky.has_key('honeybee_release'):
    
    if _testPoints:
        if uniformSky_==True:
            skyFilePath = genVSCSky(1000, "-u")
        else:
            skyFilePath = genVSCSky(1000, "-c")
        
        # set radiance parameters
        
        hb_radParDict = sc.sticky["honeybee_RADParameters"]().radParDict
        quality = 0
        radPar = {}
        for key in hb_radParDict.keys():
            print key + " is set to " + str(hb_radParDict[key][quality])
            radPar[key] = hb_radParDict[key][quality]
            radPar["_ad_"] = 2400
            radPar["_as_"] = 20
            radPar["_ar_"] = 300
            radPar["_aa_"] = 0.1
            radPar["_ab_"] = 1
            
            
        simulationType = 4
        _testPoints.SimplifyPaths()
        ptsVectors_.SimplifyPaths()
        analysisRecipe = DLAnalysisRecipe(simulationType, skyFilePath, _testPoints, ptsVectors_, radPar)
        
            
        if _testPoints.DataCount==0 or isAllNone(_testPoints.AllData()):
            analysisRecipe = None
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "testPoints are missing!")
        # generate the vectors if the vectors are not there
        elif len(analysisRecipe.vectors)==0:
            analysisRecipe.vectors = []
            for ptListCount, ptList in enumerate(analysisRecipe.testPts):
                analysisRecipe.vectors.append([])
                for pt in ptList:
                    analysisRecipe.vectors[ptListCount].append(rc.Geometry.Vector3d.ZAxis)
else:
    print "You should first let Honeybee to fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
    radParameters = []



