# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Radiance Opaque Material By Color

Create a Standard Radiance Opaque Material. Many thanks to Axel Jacobs for his help and all the great resources he provided at jaloxa.eu
Check out the color picker to see some great examples > http://www.jaloxa.eu/resources/radiance/colour_picker/index.shtml
-
Provided by Honeybee 0.0.51

    Args:
        color: Material color
        roughness: Roughness values above 0.2 are uncommon
        specularity: Specularity values above 0.1 are uncommon
    Returns:
        avrgRef: Average diffuse reflectance of the material
        RADMaterial: Radiance Material string

"""

ghenv.Component.Name = "Honeybee_Radiance Opaque Material By Color"
ghenv.Component.NickName = 'radOpaqueMaterialByColor'
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
    if color!=None:
        R = color.R/255
        G = color.G/255
        B = color.B/255
        if 0 <= R <= 1 and 0 <= G <= 1 and 0 <= B <= 1:
            avrgRef = (0.265 * R + 0.670 * G + 0.065 * B)  * (1 - specularity) + specularity
            
            materialName = materialName.Replace(" ", "_")
            
            RADMaterial = createRadMaterial(modifier, materialName, R,  G,  B, specularity, roughness)
            
            if roughness > 0.2:
                 msg = "Roughness values above 0.2 are uncommon"
                 ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            if specularity > 0.1:
                msg = "Specularity values above 0.1 are uncommon"
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        else:
            msg =  "Reflectance values should be between 0 and 1"
            e = gh.GH_RuntimeMessageLevel.Error
            ghenv.Component.AddRuntimeMessage(e, msg)
else:
    print "You should first let Honeybee to fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first Honeybee to fly...")
    

