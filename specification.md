# Track teplate  
  
  
### Functional description   
  
  
I need a python script to perform a simple task. I need to automate the creation of drawings for templates for laying flexible model railway track. Output should be in the form of Dxf and pdf files. These files should fit standard iso paper size and have an optional standard iso drawing boundary and title block.  
  
Each template in the file consists of 2 parallel lines of the specified gauge closed at each end with a perpendicular line. This will be used for laser cutting, milling etching etc.   
  
 the script is called and passed arguments   
  
-o output file name optional if not specified use a timestamp   
-p optional argument output pdf files  
-d optional argument output dxf files  
-s optional arguments paper size iso sizes A0, A1, A2, A3, A4 not case sensitive  
-b if specified add a title block and drawing boundary with scale otherwise no title block  
-3D specify argument with a number then output a 3d file for each template which is a prism of each template. The outline extruded by the number of millimetres specified in the argument. Output in stp files  
-h help in the form of a command list  
  
  
If none of -p -d -s are specified then output as both file formats and pick a paper size to fit   
  
-gauge, -g Gauge is a mandatory argument specified in mm an represents the distance between the parallel lines  
-type, -t type of template mandatory, can be straight, curve or transition, s c t  
-length, -l length in millimetres along the inner of the parallel lines   
-arc, -a  degrees of arc for a curve, alternative to specifying a length  
-radius, -r radius of curve to inner of the parallel lines in millimetres, outer line will be offset by gauge.  
-left curve to the left  
-right curve to the right  
  
  
Straight - arguments gauge and length output will be a rectangle of length -l and width gauge -g, in the case 3D is specified then additionally a cuboid length -l and width gauge -g and thickness species by the -3D argument  
  
Curves - arguments -g -r and -l or -a output will be a segment of a circle of radius -r to the inner line and -r + -g to the outer line closed of by lines of length -g at the end  in the case -3D specified then the shape lofted by the number of millimetres specified  
  
Transition - arguments -g -r -l -left or -right - over the length of the curve transition from straight to a curve of radius -r curving to the left or the right as specified.   
  
### Distribution  
  
Initially will create github repo and publish from there under MIT license, consider pip or npm distribution later  
  
Write docs in the forms of a readme.md  
  
### Dependencies  
  
Minimum dependencies if possible and prefer python dependencies if we have to and in pip or npm package managers   
  
Consult if we need to use something else eg.  Ghostscript  
