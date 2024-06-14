# FOURIER APP
 A tkinter app made in python that allows you to draw curves that are later converted to an SVG or import a .svg or .csv file directly. The paths of the SVG and functions of the CSV are later approximated by the use of Fourier series. You can choose between different settings for the animation and save them as GIFs.

The app is pretty simple, you have three options: **"Draw SVG"**, **"Import SVG"** and **"Import CSV"**. If you choose the first one, you can draw on a canvas that later saves the drawing as an SVG. This SVG is later parsed to get the functions that define the different curves. If you decide to import the SVG, you are just presented with a file selection menu where you select the SVG that's later previewed. Last but not least, "Import CSV" allows you to import a CSV with real and complex functions where you can choose which function to approximate.

All of these options give you the freedom to choose the *FPS* (frames per second), the amount of *frames*, the *precision* of the **Fourier coefficients** and *N* which refers to the amount of coefficients. After the functions are calculated, you are presented with a live-plot made with *matplotlib* that tries to mantain a steady framerate. However, this is not always possible so that's why you can save the animation as a GIF to later view it without any FPS drops.

![music note](gif/music-note.gif)
![sigma](gif/sigma.gif)