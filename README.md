This is a python port from Mark Wheadon's Velocity Painting project. I've added a new technique which does extrusion painting instead of velocity painting. The code is still a bit of a mess but it works. Read more about the [Extrusion Painting modification](https://nathanapter.wordpress.com/2017/03/23/extrusion-painting-3d-printing/).

To run this, install python. Install Pillow. 
On windows you can install python from python.org and then run c:\python27\scripts\pip.exe install Pillow

Sample command line: python C:\velocity-painting\VelocityPainting.py -projectX 115 155 50 50 0 3600 3600 5400 C:\VelocityPainting\inverted.png C:\VelocityPainting\test.gcode "C:\VelocityPainting\cube output.gcode"

Original readme below.

# Velocity Painting

I'd love this to evolve into something cool. All I ask is that you use the term _Velocity Painting_, tag things with _#VelocityPainting_, and ack that I, Mark Wheadon, started this bizarre journey with the idea, the name, and some functional though fragile code ;-) See the licence at the bottom of this document.

If you improve this code then it would be great if you could submit a pull request back to the repository -- so others can benefit from the work.

## What's here

So, this is a rough and ready perl script that when given an image file and a GCODE file, processes the GCODE to change print speeds according to the intensity of the image pixels -- thus mapping the image onto the model. If a GCODE vector crosses a pattern boundary then the vector is split to allow a change in velocity to occur at that boundary.

An FAQ is [available here](https://github.com/MarkWheadon/velocity-painting/wiki/FAQ).

## In use

Slice your model with all speeds set to (say) 3000mm/min, then use the _3000_ as the first argument to the script. Don't forget to switch off
anything in the slicer that changes print speed according to layer time and anything that under-speeds infill, outer perimeters, bridges etc.
Note: At time of writing I have only run this code on the output from Simplify3D -- it hasn't been tried on output from Slic3r, Cura, etc.

Run the script with no arguments to get some usage instructions.

## Dependencies

The script relies on the _ImageMagick_ perl module _Image::Magick_ and _Math::Trig_. It really isn't in a state where anyone other than a programmer can use it -- it is very fragile in use and needs work! But experience has taught me that if I don't release it like this then I probably won't ever release it.

## Important

Run the resulting GCODE though a GCODE previewer before sending it to a printer. *Especially* once you start to change the script.  Messing up the co-ordinates will send the print head places it should never go and that could easily damage your printer. I drag the GCODE onto Simplify3D to preview it -- Simplify3D even colour codes the print velocity, which is exactly what you need!

## Licence

Velocity Painting by [Mark Wheadon](https://github.com/MarkWheadon) is licensed under a [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/).  Based on a work at https://github.com/MarkWheadon/velocity-painting.

Mark Wheadon [Email _mark.wheadon_ at _the usual gmail domain_]
