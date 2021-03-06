# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Radiance Opaque Material

Create a Standard Radiance Opaque Material. Many thanks to Axel Jacobs for his help and all the great resources he provided at jaloxa.eu
Check out the color picker to see some great examples > http://www.jaloxa.eu/resources/radiance/colour_picker/index.shtml
-
Provided by Honeybee 0.0.51

    Args:
        RReflectance: Diffuse reflectance for red
        GReflectance: Diffuse reflectance for green
        BReflectance: Diffuse reflectance for blue
        roughness:  Roughness values above 0.2 are uncommon
        specularity: Specularity values above 0.1 are uncommon
    Returns:
        avrgRef: Average diffuse reflectance of the material
        RADMaterial: Radiance Material string
"""

ghenv.Component.Name = "Honeybee_Radiance Opaque Material"
ghenv.Component.NickName = 'radOpaqueMaterial'
ghenv.Component.Message = 'VER 0.0.51\nMAR_15_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "1 | Daylight | Material"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import math
import scriptcontext as sc
import Grasshopper.Kernel as gh

# read here to understand RAD materials
# http://www.artifice.com/radiance/rad_materials.html
    
def createRadMaterial(modifier, name, *args):
    # I should check the inputs here
    
    radMaterial = "void " + modifier + " " + name + "\n" + \
                  "0\n" + \
                  "0\n" + \
                  `int(len(args))`
                  
    for arg in args: radMaterial = radMaterial + (" " + "%.3f"%arg)
    
    return radMaterial + "\n"

modifier = "plastic"

if sc.sticky.has_key('honeybee_release'):
    if RReflectance!=None and GReflectance!=None and BReflectance != None:
        avrgRef = (0.265 * RReflectance + 0.670 * GReflectance + 0.065 * BReflectance) * (1 - specularity) + specularity
        
        materialName = materialName.Replace(" ", "_")
        
        RADMaterial = createRadMaterial(modifier, materialName, RReflectance,  GReflectance,  BReflectance, specularity, roughness)
        
        if roughness > 0.2:
             msg = "Roughness values above 0.2 are uncommon"
             ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        if specularity > 0.1:
            msg = "Specularity values above 0.1 are uncommon"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
else:
    print "You should first let Honeybee to fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
    

