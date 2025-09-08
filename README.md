# Images-vs-xml-alto-recalculating-coordinates
A small Python tool to adjust your xml-alto file's bad spatial coordinates

If you happen to use some device to view an OCR/HTR transcription directly on a scanned page (Omeka-S, IIIF & Mirador Viewer for example) but spatial coordinates between image resolution and xml-alto points do not match, here is a script to recalculate them. This script was designed for the case of 1 alto file per image. It takes all the alto files and images as input, and creates new alto files as output.

(Long story short, in this example a book was digitized in 2 formats, jpg & jp2. The HTR transcription was made using the large jp2 image files, while the public website put the lighter jpg files on display. So the text layout could not be properly viewed on the image itself, being much larger.)
