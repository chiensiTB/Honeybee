# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Read Daysim result for a test point

-
Provided by Honeybee 0.0.51

    Args:
        _illFilesAddress: List of .ill files
        _testPoints: List of 3d Points
        _annualProfiles: Address to a valid *_intgain.csv generated by daysim.
        _targetPoint: One of the points from the test points
    Returns:
        iIllumLevelsNoDynamicSHD: Illuminance values without dynamic shadings
        iIllumLevelsDynamicSHDGroupI: Illuminance values when shading group I is closed
        iIllumLevelsDynamicSHDGroupII: Illuminance values when shading group II is closed
        iIlluminanceBasedOnOccupancy: Illuminance values based on Daysim user behavior
"""
ghenv.Component.Name = "Honeybee_Read DS Result for a point"
ghenv.Component.NickName = 'readDSHourlyResults'
ghenv.Component.Message = 'VER 0.0.51\nFEB_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "4 | Daylight | Daylight"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass



import os
import scriptcontext as sc
from System import Object
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

def isAllNone(dataList):
    for item in dataList.AllData():
        if item!=None: return False
    return True


def sortIllFiles(illFilesAddress, returnFirstBranch = False):
    
    sortedIllFiles = []
    count = illFilesAddress.BranchCount
    if returnFirstBranch: count = 1
    
    for shadingGroupCount in range(count):
        fileNames = list(illFilesAddress.Branch(shadingGroupCount))
        try:
            if fileNames[0].endswith("_down.ill") or fileNames[0].endswith("_up.ill"):
                fileNames = sorted(fileNames, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-2]))
            else:
                fileNames = sorted(fileNames, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-1]))
                
            sortedIllFiles.append(fileNames)
        except Exception, e:
            #print `e`
            tmpmsg = "Can't sort the files based on the file names. Make sure the branches are sorted correctly."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, tmpmsg)
            sortedIllFiles.append(fileNames)
            
    
    # sort shading states inside sortedIllFiles
    illFileSets = {}
    for listCount, fileNames in enumerate(sortedIllFiles):
        
        try:
            if fileNames[0].endswith("_down.ill"):
                illFileSets[1] = fileNames
            elif fileNames[0].endswith("_up.ill"):
                illFileSets[0] = fileNames
            elif len(fileNames[0].split("_state_"))==1:
                illFileSets[0] = fileNames
            else:
                key = int(fileNames[0].split("_state_")[1].split("_")[0])-1
                illFileSets[key] = fileNames
        except Exception, e:
            print "sorting the branches failed!"
            illFileSets[listCount] = fileNames
    
    return illFileSets

def main(illFilesAddress, testPoints, targetPoint, annualProfiles):
    msg = str.Empty
    
    shadingProfiles = []
    
    #groups of groups here
    for resultGroup in  range(testPoints.BranchCount):
        shadingProfiles.append([])
    
    # print len(shadingProfiles)
    if len(annualProfiles)!=0:
        # check if the number of profiles matches the number of spaces (point groups)
        if testPoints.BranchCount!=len(annualProfiles):
            msg = "Number of annual profiles doesn't match the number of point groups!\n" + \
                  "NOTE: If you have no idea what I'm talking about just disconnect the annual Profiles\n" + \
                  "In that case the component will give you the results with no dynamic shadings."
            return msg, None, None
        
        # sort the annual profiles
        try:
            annualProfiles = sorted(annualProfiles, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-1]))
        except:
            pass
        
        # import the shading groups
        # this is a copy-paste from Daysim annual profiles
        for branchCount in range(len(annualProfiles)):
            # open the file
            filePath = annualProfiles[branchCount]
            with open(filePath, "r") as inf:
                for lineCount, line in enumerate(inf):
                    if lineCount == 3:
                        headings = line.strip().split(",")[3:]
                        resultDict = {}
                        for heading in range(len(headings)):
                            resultDict[heading] = []
                    elif lineCount> 3:
                        results = line.strip().split(",")[3:]
                        for resCount, result in enumerate(results):
                            resultDict[resCount].append(float(result))
                            
                shadingCounter = 0
                for headingCount, heading in enumerate(headings):
                    if heading.strip().startswith("blind"):
                        shadingProfiles[branchCount].append(resultDict[headingCount])
                        shadingCounter += 1
        # make sure number of ill files matches the number of the shading groups
        # and sort them to work together
        for shadingProfile in shadingProfiles:
            if len(shadingProfile)!= illFilesAddress.BranchCount - 1:
                msg = "Number of annual profiles doesn't match the number of shading groups!\n" + \
                      "NOTE: If you have no idea what I'm talking about just disconnect the annual Profiles\n" + \
                      "In that case the component will give you the results with no dynamic shadings."
                return msg, None, None
            else:
                # looks right so let's sort them
                # sort each list inside the branch and took the first one for sorting the branches!
                illFileSets = sortIllFiles(illFilesAddress)
                #print illFileSets
                    
    elif illFilesAddress.BranchCount > 1 and illFilesAddress.BranchCount-1 != len(annualProfiles):
        tempmsg = "Annual profile files are not provided.\nThe result will be only calculated for the original case with no blinds."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, tempmsg)
        illFileSets = sortIllFiles(illFilesAddress, returnFirstBranch = True)
    else:
        illFileSets = sortIllFiles(illFilesAddress)
        
    # find the index of the point
    pointFound = False
    targetPtIndex = 0
    for branch in range(testPoints.BranchCount):
        for pt in testPoints.Branch(branch):
            if pt.DistanceTo(targetPoint) < sc.doc.ModelAbsoluteTolerance:
                pointFound = True
                break
            targetPtIndex+=1
        if pointFound ==True: break
    
    # check number of points in each of the ill files
    # number of points should be the same in all the illfile lists
    # that's why I just try the first list of the ill files
    numOfPtsInEachFile = []
    for illFile in illFileSets[0]:
        with open(illFile, "r") as illInf:
            for lineCount, line in enumerate(illInf):
                if not line.startswith("#"):
                    numOfPtsInEachFile.append(len(line.strip().split(" ")) - 4)
                    break
    
    # find the right ill file(s) to look into and read the results
    # print targetPtIndex
    targetListNumber = None
    targetIndexNumber = None
    for listCount, numOfPts in enumerate(numOfPtsInEachFile):
        if sum(numOfPtsInEachFile[:listCount]) >= targetPtIndex + 1:
            targetListNumber = listCount - 1
            targetIndexNumber = targetPtIndex - sum(numOfPtsInEachFile[:listCount-1])
            #print "list number is: ", listCount - 1
            #print "index number is:", targetPtIndex - sum(numOfPtsInEachFile[:listCount-1])
            break
    
    # Probably this is not the best way but I really want to get it done tonight!
    if targetListNumber == None:
        targetListNumber = len(numOfPtsInEachFile)-1
        targetIndexNumber = targetPtIndex - sum(numOfPtsInEachFile[:targetListNumber])
    
    if targetIndexNumber < 0:
        msg = "The target point is not inside the point list"
        return msg, None, None
    
    # find in which space the point is located
    targetSpace = None
    for listCount, numOfPts in enumerate(numOfPtsInEachSpace):
        if sum(numOfPtsInEachSpace[:listCount]) >= targetPtIndex + 1:
            targetSpace = listCount - 1
            break    
    if targetSpace == None:
        targetSpace = len(numOfPtsInEachSpace)-1
    
    # 4 place holderd for the potential 3 outputs
    # no blinds, shading group I and shading group II
    illuminanceValues = {0: [],
                         1: [],
                         2: [],
                         }
                         
    for shadingGroupCount in range(len(illFileSets.keys())):
        targetIllFile = illFileSets[shadingGroupCount][targetListNumber]
        result = open(targetIllFile, 'r')
        for lineCount, line in enumerate(result):
            hourLuxValue = line.strip().split(" ")[targetIndexNumber + 4]
            illuminanceValues[shadingGroupCount].append(float(hourLuxValue))
        result.close()
        
    return msg, illuminanceValues, shadingProfiles[targetSpace]



if _targetPoint!=None and not isAllNone(_illFilesAddress) and not isAllNone(_testPoints):
    
    _testPoints.SimplifyPaths()
    _illFilesAddress.SimplifyPaths()
    
    numOfPtsInEachSpace = []
    for branch in range(_testPoints.BranchCount):
        numOfPtsInEachSpace.append(len(_testPoints.Branch(branch)))
    
    msg, illuminanceValues, shadingProfile = main(_illFilesAddress, _testPoints, _targetPoint, annualProfiles_)

    if msg!=str.Empty:
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, msg)
        
    else:
        annualIllumNoDynamicSHD = DataTree[Object]()
        annualIllumDynamicSHDGroupI = DataTree[Object]()
        iIllumLevelsDynamicSHDGroupII = DataTree[Object]()
        iIlluminanceBasedOnOccupancy = DataTree[Object]()
        
        heading = ["key:location/dataType/units/frequency/startsAt/endsAt",
                    " ", "Annual illuminance values", "lux", "Hourly",
                    (1, 1, 1), (12, 31, 24)]
        # now this is the time to create the mixed results
        # I think I confused blind groups and shading stats or maybe not!
        # Fore now it will work for one shading with one state. I'll check for more later.
        
        blindsGroupInEffect = []
        annualIllumNoDynamicSHD.AddRange(heading + illuminanceValues[0])
        
        if len(illuminanceValues[1])!=0:
            blindsGroupInEffect.append(1)
            annualIllumDynamicSHDGroupI.AddRange(heading + illuminanceValues[1])
            
        if len(illuminanceValues[2])!=0:
            blindsGroupInEffect.append(2)
            iIllumLevelsDynamicSHDGroupII.AddRange(heading + illuminanceValues[2])
        
        # create the mixed result with the shadings
        mixResults = heading
        for HOY in range(8760):
            blindModeFound = False
            for blindGroup in blindsGroupInEffect:
                if shadingProfile[blindGroup-1][HOY]==1:
                    mixResults.append(illuminanceValues[blindGroup][HOY])
                    blindModeFound = True
                    break
            if blindModeFound != True:
                mixResults.append(illuminanceValues[0][HOY])
                

        iIlluminanceBasedOnOccupancy.AddRange(mixResults)

