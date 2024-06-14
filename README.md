# FOURIER APP
<p align="justify">A tkinter app made in python that allows you to draw curves that are later converted to an SVG or import a .svg or .csv file directly. The paths of the SVG and functions of the CSV are later approximated by the use of Fourier series. You can choose between different settings for the animation and save them as GIFs.</p>
<p align="justify">
The app is pretty simple, you have three options: <b>Draw SVG</b>, <b>Import SVG</b> and <b>Import CSV</b>. If you choose the first one, you can draw on a canvas that later saves the drawing as an SVG. This SVG is later parsed to get the functions that define the different curves. If you decide to import the SVG, you are just presented with a file selection menu where you select the SVG that's later previewed. Last but not least, "Import CSV" allows you to import a CSV with real and complex functions where you can choose which function to approximate.</p>
<p align="justify">
All of these options give you the freedom to choose the <i>FPS</i> (frames per second), the amount of <i>frames</i>, the <i>precision</i> of the <b>Fourier coefficients</b> and <i>N</i> which refers to the amount of coefficients. After the functions are calculated, you are presented with a live-plot made with *matplotlib* that tries to mantain a steady framerate. However, this is not always possible so that's why you can save the animation as a GIF to later view it without any FPS drops.
</p>
<p align="middle">
    <img src="gif/sigma.gif" width="50%"/>
    <img src="gif/music-note.gif" width="50%"/>
</p>

<p align="middle">
    See more here: [My site](https://agustin-j.github.io/)
</p>
## INSTALLATION

Tested in Python version *3.12.2* and *3.11.9* using Windows. For the app to work you have to install the libraries inside *requirements.txt* using the following command:

```
pip install requirements.txt
```

Clone the entire repository and don't change the folders name. If the fonts don't load, try to first install them on your system.