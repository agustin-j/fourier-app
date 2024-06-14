from math import sqrt
from pathlib import Path
import pyglet
import sys
import os
import csv
import csv_parser
import svg_parser
import numpy as np
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import customtkinter as ctk
from threading import *
from queue import Queue
from enum import Enum, auto
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

"""
GENERAL SETTINGS FOR THE APP
"""
# FONT LOADING
pyglet.options['win32_gdi_font'] = True
pyglet.font.add_file("fonts/Roboto-Regular.ttf")
pyglet.font.add_file("fonts/Rubik-VariableFont_wght.ttf")

# THEME STYLE
ctk.set_default_color_theme("dark-blue")
plt.style.use("dark_background")

# BACKGROUND COLOR
BG_COLOR = "#061721"
BG_SECONDARY_COLOR = "#001e2e"
BG_BORDER_COLOR = "#011926"
PLOT_COLOR = "#02070a"

# BUTTON COLOR
BORDER_COLOR = "#083545"
MAIN_BUTTON_COLOR = "#093342"
MAIN_BUTTON_COLOR_HOVER = "#0d4f70"
DANGER_BUTTON_COLOR = "#910101"
DANGER_BUTTON_COLOR_HOVER = "#c90e0e"
SAVE_BUTTON_COLOR = "#0f6769"
SAVE_BUTTON_COLOR_HOVER = "#20b0a1"
GREEN_BUTTON_COLOR = "#2f8a56"
GREEN_BUTTON_COLOR_HOVER =  "#0da14d"

# DELETE THREADS WARNING MATPLOTLIB
plt.switch_backend('agg')

# WINDOWS ONLY - GET THE SCALING
try:
    from ctypes import windll, byref, sizeof, c_int
    # SCALING OF WINDOWS
    scaling = windll.shcore.GetScaleFactorForDevice(0) / 100
except:
    # DEFAULT
    scaling = 1
    pass

# # ADD PATH FOR IMAGES - https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
# def resource_path(relative_path):
#     """ Get absolute path to resource, works for dev and for PyInstaller """
#     try:
#         # PyInstaller creates a temp folder and stores path in _MEIPASS
#         base_path = sys._MEIPASS2
#     except Exception:
#         base_path = os.path.abspath(".")

#     return os.path.join(base_path, relative_path)

"""
CLASSES AND FUNCTIONS FOR MULTI-THREADING
"""
# TICKET PURPOSE, WHAT SHOULD WE DO WHILE MULTI-THREADING
class TicketPurpose(Enum):
    LOADED_GIF = auto()
    PERCENTAGE_GIF = auto()
    ANIMATE_FOURIER_SERIES = auto()
    FINISH_FOURIER_SERIES = auto()
    DESTROY_FOURIER_WIDGETS = auto()

# TICKET TYPE AND VALUE
class Ticket:
    def __init__(self, ticket_type: TicketPurpose, ticket_label: Label, ticket_value):
        self.ticket_type = ticket_type
        self.ticket_label = ticket_label
        self.ticket_value = ticket_value

# CHECK TYPE OF TICKET AND CALL FUNCTIONS ACCORDINGLY
def check_queue(event):
    msg = window.queue_message.get() # READ MSG
    # LOAD MAIN WINDOW WITH GIF
    if msg.ticket_type == TicketPurpose.LOADED_GIF:
        msg.ticket_label.loaded = True
        if msg.ticket_value == "main": # FOR THE MAIN GIF
            main_loading.set(1)
            start_main_window(window)
        elif msg.ticket_value == "not-main": # FOR SVG and CSV GIFs
            fourier_loading_bar.set(1)
            show_fourier_result(window)
    # UPDATE VALUES OF PROGRESSBAR AND LOADING TEXT
    if msg.ticket_type == TicketPurpose.PERCENTAGE_GIF:
        progress = float(msg.ticket_value.split(",")[0])/100
        point_count = int(msg.ticket_value.split(",")[1]) % 3
        if msg.ticket_value.split(",")[2] == "main":
            main_loading.set(progress)
            main_loading_text.configure(text=f"LOADING{'.'*(point_count+1)}") # UPDATE TEXT
        elif msg.ticket_value.split(",")[2] == "not-main":
            fourier_loading_bar.set(progress)
            fourier_loading_text.configure(text=f"LOADING{'.'*(point_count+1)}") # UPDATE TEXT
    # DESTROY CURRENT WIDGETS FOR FOURIER GIF
    if msg.ticket_type == TicketPurpose.DESTROY_FOURIER_WIDGETS:
        destroy_widgets_fourier(window, msg.ticket_value)
    # UPDATE THE ANIMATION OF FOURIER SERIES
    if msg.ticket_type == TicketPurpose.ANIMATE_FOURIER_SERIES:
        loading_screen_fourier(window, msg.ticket_value[0], msg.ticket_value[1], 1)
    # LOAD THE FOURIER SERIES GIF
    if msg.ticket_type == TicketPurpose.FINISH_FOURIER_SERIES:
        load_gif_fourier(window, msg.ticket_value[0], msg.ticket_value[1], msg.ticket_value[2], msg.ticket_value[3])

"""
UPDATE THE SIZE OF THE FONTS AND WIDGETS
"""
# CHANGE THE SIZES OF FONTS
def update_size(event):
    
    if window.winfo_height() < window.winfo_screenheight()*2/3*scaling or window.winfo_width() < window.winfo_screenwidth()*2/3*scaling:
        main_title_font.configure(size=50)
        path_font.configure(size=10)
        button_font.configure(size=15)
        title_font.configure(size=30)
        sub_title_font.configure(size=15)
        table_font.configure(size=12)
    else:
        main_title_font.configure(size=80)
        path_font.configure(size=15)
        button_font.configure(size=20)
        title_font.configure(size=40)
        sub_title_font.configure(size=20)
        table_font.configure(size=20)
"""
AFTER LOADING - MAIN WINDOW
"""
# START MAIN TITLE WINDOW AFTER LOADING SCREEN
def start_main_window(window):
    global main_title
    global buttons
    global options

    # FRAME UNPACK ALREADY USED WIDGETS IN PREVIOUS WINDOW
    starting_frame.pack_forget()
    main_loading.pack_forget()
    main_loading_text.pack_forget()

    # CHANGE WINDOW ICON BY USING THE APP LOGO
    window.iconbitmap('assets\\fourier-app-logo.ico')

    # CHANGE WINDOW TITLE
    window.title(" Fourier Series App - Made by Agustin J")

    # RESIZABLE
    window.resizable(True, True)
    # TITLE
    window.overrideredirect(False)
    # NOT ON TOP
    window.attributes('-topmost',False)
    # ALPHA OF WINDOW
    window.attributes('-alpha', 1)

    # WINDOWS ONLY TO CHANGE TITLE BORDER AND TITLE COLOR
    try:
        window.update()
        HWND = windll.user32.GetParent(window.winfo_id())
        border_color = 0x000305 # COLOR OF THE BORDER
        text_border_color = 0xedf8ff # TEXT COLOR
        windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int(border_color)), sizeof(c_int))
        windll.dwmapi.DwmSetWindowAttribute(HWND, 36, byref(c_int(text_border_color)), sizeof(c_int))
    except:
        pass

    # MAXIMIZE WINDOW
    window_size = f'{window.winfo_screenwidth()}x{window.winfo_screenheight()}'
    window.geometry(window_size)
    window.state('zoomed')

    # LIMIT MINIMUM SIZE OF WINDOW TO BE HALF OF THE SCREEN WIDTH AND HEIGHT
    window.minsize(window.winfo_screenwidth()//2, window.winfo_screenheight()//2)

    # ROW AND COLUMN CONFIGURE
    window.columnconfigure((0,1), weight=1, uniform="a")
    window.rowconfigure((0,1,2,3), weight=1)

    # FIRST COLUMN
    main_title = ctk.CTkLabel(window, text="FOURIER\nSERIES", font=main_title_font, text_color="white", fg_color="transparent")
    main_title.grid(row=0, column=0, sticky="nwes")
    options = ["Draw SVG", "Import SVG", "Import CSV"]
    buttons = []
    # BUTTONS
    for i in range(len(options)):
        button = Main_Buttons(window, options[i], i)
        buttons.append(button)
    
    # SECOND COLUMN
    main_gif.grid(column=1, row=0, rowspan=4)
    main_gif.play_animation(window) # SHOW GIF
    
# GO BACK TO MAIN MENU AND REDRAW WIDGETS
def regrid_main_items(window, first_error):
    global anim
    anim = 0
    for label in window.winfo_children():
        if label.winfo_ismapped() == True:
            label.destroy()
    
    main_title.grid(row=0, column=0, sticky="nwes")

    for i in range(len(options)):
        buttons[i].regrid_buttons(i)

    # INTIALIZE AS NEW GIF
    main_gif.current_frame = 0
    main_gif.first_play = True
    main_gif.grid(column=1, row=0, rowspan=4)
    if first_error == False:
        main_gif.play_animation(window) # SHOW GIF

"""
MAIN FUNCTION, CONTROLS THE ANIMATION AND WIDGETS
"""
# CALCULATE FOURIER SERIES FOR SELECTED SVG, CURVE OR DRAWN SVG
def calculate_fourier_series(window, path_selected, title, type_of_curve, amount_of_terms, FPS, total_frames, precision, saved, drawn, index_of_function):
    #LOCAL FUNCTIONS
    # CHOOSE FUNCTION FOR SVG OR CSV
    def type_of_function(t, function, b):
        if type_of_curve == "csv":
            try:
                return csv_parser.evaluate_curve(t, function, b)
            except:
                regrid_main_items(window, False)
                Alert(window, "An error occurred while parsing CSV file", 3000)
        elif type_of_curve == "svg":
            try:
                return svg_parser.evaluate_svg(t, function, b) 
            except:
                regrid_main_items(window, False)
                Alert(window, "An error occurred while parsing SVG file", 3000)

    # NUMERICAL INTEGRATION FOR FOURIER COFFICIENTS
    def c_n(delta_t, a, b, K, T, n, function):
        c_n = 0
        for j in range(K):
            t = a + delta_t/2 + delta_t*j
            c_n = c_n + 1/T*type_of_function(t, function, b)*delta_t*np.e**(-2j*np.pi*n/T*t)
        return c_n
    
    # FOURIER SERIES MAX TO MIN EVALUATION (Just visual change for graph)
    def fourier_series_max_min(N, T, t, f_i):
        f = 0   
        for i in range(len(N)):
            f_n = sorted_coefficients[i]*np.e**(2j*np.pi*N[i]/T*t)
            f = f + f_n
            f_i.append(f)
        return f
    
    # ANIMATION TOGGLER FOR PLOT
    def animation_toggler(paused):
        if paused == False:
            paused = True
            anim.pause()
            play_stop_animation.configure(text="Play animation", fg_color=GREEN_BUTTON_COLOR, 
                                          hover_color=GREEN_BUTTON_COLOR_HOVER, command=lambda: animation_toggler(paused))
        else:
            paused = False
            anim.resume()
            play_stop_animation.configure(text="Stop animation", fg_color=DANGER_BUTTON_COLOR, 
                                          hover_color=DANGER_BUTTON_COLOR_HOVER, command=lambda: animation_toggler(paused))
            
    # PLOT THE RESULTS AND SAVE THEM AS GIF OR NOT
    def animation_plot(save):
        global anim
        anim = 0
        if save == False:
            # PLOT WITH MATPLOTLIB, SET STYLE, FIGURE AND LIMITS
            fig = plt.Figure(layout='tight', facecolor=PLOT_COLOR)

            # CANVAS WIDGET FOR PLOT
            plt.rcParams['text.usetex'] = False
            canvas = FigureCanvasTkAgg(fig, master=window)
            canvas.get_tk_widget().grid(column=1,row=0, rowspan=4, sticky="nwes")
            repeat = True
        else:
            fourier_gif_ticket = Ticket(ticket_type=TicketPurpose.DESTROY_FOURIER_WIDGETS, ticket_label=None, 
                                            ticket_value=[change_settings, play_stop_animation, buttons_frame, window.winfo_children()[-1]])
            window.queue_message.put(fourier_gif_ticket)
            window.event_generate("<<CheckQueue>>")
            fig = plt.figure(layout='tight', facecolor=PLOT_COLOR)
            repeat = False

        # DECIDE THE MAX AN MINIMUM OF SVGS AND CURVES
        epsilon_x = 0.2
        epsilon_y = 0.2
        if type_of_curve == "csv":
            if real_or_not == "real":
                xlim = [a, a + interval]
                ylim = [min(real_fourier_results), max(real_fourier_results)]
            elif real_or_not == "complex":
                dif_x = abs((max(real_fourier_results) - min(real_fourier_results))/2)
                dif_y = abs((max(imag_fourier_results) - min(imag_fourier_results))/2)
                xlim = [min(real_fourier_results) - epsilon_x*dif_x, max(real_fourier_results) + epsilon_x*dif_x]
                ylim = [min(imag_fourier_results) - epsilon_y*dif_y, max(imag_fourier_results) + epsilon_y*dif_y]
        elif type_of_curve == "svg":
            dif_x = abs((max(real_curve_results) - min(real_curve_results))/2)
            dif_y = abs((max(imag_curve_results) - min(imag_curve_results))/2)
            xlim = [min(min(real_curve_results), min(real_fourier_results)) - epsilon_x*dif_x, 
                    max(max(real_curve_results), max(real_fourier_results)) + epsilon_x*dif_x]
            ylim = [min(min(imag_curve_results), min(imag_fourier_results)) - epsilon_y*dif_y, 
                    max(max(imag_curve_results), max(imag_fourier_results)) + epsilon_y*dif_y]

        # ADD SUBPLOT AND LIMITS FOR AXES
        ax = fig.add_subplot(111)
        ax.set_xlim(xlim[0], xlim[1])
        ax.set_ylim(ylim[0], ylim[1])
        ax.set_aspect('equal', 'box')
        if real_or_not != "real":
            ax.set_axis_off()
        

        # DELETE TINY CIRCLES FOR INCREASED PERFORMANCE WHILE PLOTTING ONLY 2D CURVES
        circles = []
        start_circles = 1
        if real_or_not != "real":
            amount_of_circles = 0
            for i in sorted_coefficients:
                if abs(i) > sqrt(4*dif_x**2+4*dif_y**2)/1000:
                    amount_of_circles += 1
            if amount_of_circles <= 1:
                start_circles = 0
                amount_of_circles = 1

        # INITIALIZE THE PLOT
        lines, = ax.plot([], [], linewidth=.8, color="w")
        curve_draw, = ax.plot([], [])
        aprox_curve_draw, = ax.plot([], [])
        t_results = np.linspace(a, a + interval, frames + 1)
       
        # INIT OF ANIMATION
        def init_func():
            circles = []
            return lines, curve_draw, aprox_curve_draw, circles

        # MAX-MIN ANIMATION
        def animate(f):
            if real_or_not != "real":
                # CALCULATE THE CIRCLES
                for i in range(start_circles, amount_of_circles): # DELETE 1 IF I WANT FIRST CIRCLE AND CHANGE i - 1 for i
                    if f == 0 and len(circles) < amount_of_circles - start_circles:
                        circles.append(plt.Circle((f_n_real[f][i], f_n_imag[f][i]), modulus[f][i], color='w', alpha=0.2, fill=False))
                        ax.add_patch(circles[i-start_circles])
                    else:
                        circles[i-start_circles].center = f_n_real[f][i], f_n_imag[f][i]
                        circles[i-start_circles].set_radius = modulus[f][i]
                # ADD WHITE LINES
                lines.set_data(f_n_real[f][start_circles:amount_of_circles+1], f_n_imag[f][start_circles:amount_of_circles+1])
                # ADD REAL CURVE
                #curve_draw.set_data(real_curve_results[0:f+1], imag_curve_results[0:f+1])
                # ADD APROXIMATED CURVE
                aprox_curve_draw.set_data(real_fourier_results[0:f+1], imag_fourier_results[0:f+1])
                # SAVE GIF IF TRUE
            else:
                aprox_curve_draw.set_data(t_results[0:f+1], real_fourier_results[0:f+1])

            if save == True:
                fourier_gif_ticket = Ticket(ticket_type=TicketPurpose.ANIMATE_FOURIER_SERIES, ticket_label=None, 
                                            ticket_value=[f, frames])
                window.queue_message.put(fourier_gif_ticket)
                window.event_generate("<<CheckQueue>>")
            return lines, curve_draw, aprox_curve_draw, circles

        # PLAY ANIMATION WITH DEFINED FRAMES AND FPS
        anim = animation.FuncAnimation(fig, animate, init_func=init_func, frames = frames + 1, interval= int(1000/fps), blit = False, repeat=repeat) 
        # SAVE ANIMATION AS GIF IF TRUE
        if save == True:
            anim.save(f"{str(Path().absolute().as_posix())}" + "/gif/" + f"{path_selected.split('/')[-1]}.gif", writer="ffmpeg", dpi=200, savefig_kwargs=dict(facecolor=PLOT_COLOR))
            fourier_gif_ticket = Ticket(ticket_type=TicketPurpose.FINISH_FOURIER_SERIES, ticket_label=None, 
                                            ticket_value=[f"{str(Path().absolute().as_posix())}" + "/gif/" + f"{path_selected.split('/')[-1]}.gif", title, type_of_curve, fps])
            window.queue_message.put(fourier_gif_ticket)
            window.event_generate("<<CheckQueue>>")

    # CHECK IF SVG WAS SAVED OR NOT
    if (title.isalnum() and saved == True and drawn == True) or (title != "" and saved == True and drawn == False):
        # DELETE OLD WIDGETS 
        for label in window.winfo_children():
            if label.winfo_ismapped() == True:
                label.destroy()
        
        if type_of_curve == "svg":
            button_index = 1
            path_return = f"{path_selected}.svg"
        else:
            button_index = 2
            path_return = f"{path_selected}.csv"
        # ADD THE NEW WIDGETS
        text_frame = ctk.CTkFrame(window, fg_color="transparent") # HOLDS THE TITLE AND THE PATH
        title_label = ctk.CTkLabel(text_frame, text=title, font=title_font, text_color="white") # TITLE OF SVG
        path_label = ctk.CTkLabel(text_frame, text=path_return, font=path_font, text_color="grey") # PATH OF SVG
        settings_frame = ctk.CTkFrame(window, fg_color="transparent") # HOLDS THE SETTINGS
        settings_label = Mini_table(settings_frame, ["N", "PRECISION", "FRAMES", "FPS"], [amount_of_terms, precision, total_frames, FPS]) # SETTINGS
        change_settings = ctk.CTkButton(settings_frame, text="Change settings",  fg_color=MAIN_BUTTON_COLOR, hover_color=MAIN_BUTTON_COLOR_HOVER, 
                                        border_spacing=15, font=button_font, command=lambda: import_file(button_index, window, path_return, index_of_function)) # GO BACK AND CHANGE SETTINGS
        play_stop_animation = ctk.CTkButton(settings_frame, text="Stop animation",  fg_color=DANGER_BUTTON_COLOR, hover_color=DANGER_BUTTON_COLOR_HOVER, 
                                        border_spacing=15, font=button_font, command=lambda: animation_toggler(False))
        buttons_frame = ctk.CTkFrame(window, fg_color="transparent") # HOLDS THE SAVE GIF BUTTON AND MAIN MENU BUTTON
        warning_text = ctk.CTkLabel(buttons_frame, text="Results are live, save gif to ensure steady framerate", font=path_font, text_color="#f5f76d")
        save_gif = ctk.CTkButton(buttons_frame, text="Save GIF",  fg_color=SAVE_BUTTON_COLOR, hover_color=SAVE_BUTTON_COLOR_HOVER, 
                                        border_spacing=15, font=button_font,
                                        command=lambda: Thread(target=animation_plot, args=(True,), daemon=True).start())
        go_back = ctk.CTkButton(buttons_frame, text="Main menu",  fg_color=DANGER_BUTTON_COLOR, hover_color=DANGER_BUTTON_COLOR_HOVER, 
                                        border_spacing=15, font=button_font, command= lambda: regrid_main_items(window, False))
        

        # AMOUNT OF POSITIVE TERMS
        N = amount_of_terms # MIN 1 - MAX 100
        # PRECISION OF INTEGRAL
        K = precision # MIN 100 - MAX 1000
        # FPS
        fps = FPS # MIN FPS 5 - MAX FPS 30
        # FRAMES
        frames = total_frames # MIN FRAMES 5 - MAX FRAMES 400

        # PYTHON OR SVG TO READ
        if type_of_curve == "svg":
            a = 0
            try:
                if drawn == True:
                    function, b = svg_parser.open_svg(path_selected, True)
                else:
                    function, b = svg_parser.open_svg(path_selected, False)
            except:
                regrid_main_items(window, False)
                Alert(window, "An error occurred while parsing SVG file", 3000)
            real_or_not = "complex"
            interval = b - a
        else:
            try:
                real_or_not, function, a, b, interval = csv_parser.open_csv(path_selected, index_of_function)
            except:
                regrid_main_items(window, False)
                Alert(window, "An error occurred while parsing CSV file", 3000)
        # PARAMETERS FOR FOURIER SERIES [T, b, a, delta_t]
        T = b - a
        delta_t = T/K

        # FOURIER COEFFICIENTS
        coefficients = []
        for n in range(-N, N+1):
            coefficients.append(c_n(delta_t, a, b, K, T, n, function))
        sorted_coefficients, N = zip(*sorted(zip(coefficients, [n for n in range(-N, N+1)]), key= lambda x: abs(x[0]), reverse=True))

        # WIDGET FOR THE FOURIER SERIES
        plt.rcParams['text.usetex'] = True
        plt.rcParams["text.latex.preamble"] = r"\usepackage{amsmath}"
        coeff_text = []
        spaces = []
        rows = 3
        cols = 2
        # GO FOR EACH ROW AND COLUMN TO GET THE COEFFICIENT
        for j in range(rows):
            for i in range(cols):
                count = 0 # EXTRA NEGATIVES - ADD MORE SPACE
                try:
                    temp = "c_{" + str(N[i+2*j]) + "}" # FIRST PART
                    real = f"={round(sorted_coefficients[i+2*j].real, 1)}" # REAL PART
                    if i == 0:
                        temp += "&" # MAKE SURE, FIRST EQUAL IS AT SAME DISTANCE
                        try:
                            if N[i+2*j+1] < 0: # IF NEGATIVE INDEX OF NEXT COEFF
                                count += 1 
                        except:
                            pass
                        if round(sorted_coefficients[i+2*j].real, 1) < 0: # IF NEGATIVE REAL PART
                            count += 1 
                    temp += real
                    if round(sorted_coefficients[i+2*j].imag, 1) > 0: # POSITIVE IMAGINARY PART
                        imag = fr"+{round(sorted_coefficients[i+2*j].imag, 1)}i"
                        temp += imag
                    elif round(sorted_coefficients[i+2*j].imag, 1) < 0: # NEGATIVE IMAGINARY PART
                        imag = fr"{round(sorted_coefficients[i+2*j].imag, 1)}i"
                        temp += imag
                    else:
                        imag = f"+ 0i"
                        temp += imag
                    if j != rows - 1 and i == 1:
                        temp += r"\\" # ADD A BREAK LINE
                    elif i == 0:
                        spaces.append(len(real) + len(imag) + count - 2) # APPEND THE SPACE
                    coeff_text.append(temp)
                except:
                    pass
        
        for i in range(rows):
            try:   
                min_space = r"\enspace "*(max(spaces) - spaces[i] + 4) # CHECK THE SPACE FOR EACH ROW
                coeff_text[i*2] += min_space
            except:
                pass

        # ARRAY WITH COEFFICIENTS
        coeff_eqs = (r"\begin{align*}"
                     rf"{''.join(coeff_text)}"
                     r"\end{align*}")
        
        # START WITH THE FRAME WIDGET, THEN THE ONES INSIDE
        fourier_label = ctk.CTkFrame(window, fg_color="transparent")
        fourier_text = ctk.CTkLabel(fourier_label, text="MAX FOURIER COEFFICIENTS", text_color="white", font=sub_title_font) # TEXT
        fourier_text.pack(expand=True, pady=(5, 0), anchor="s") # PACK
        fig_latex = plt.Figure(figsize=(2, .5), dpi=200, facecolor=BG_COLOR)  # PLOT THE TEXT
        canvas_latex = FigureCanvasTkAgg(fig_latex, master=fourier_label)
        canvas_latex.get_tk_widget().pack(expand=True, fill="both")
        ax_latex = fig_latex.add_subplot(111)
        ax_latex.text(0, 0, coeff_eqs, ha='center', va='center', fontsize=7, color="#d6f7ff")
        ax_latex.set_axis_off()
        ax_latex.set_xlim(-1,1)
        ax_latex.set_ylim(-.5,.5)
        canvas_latex.draw()
        fourier_label.grid(row=2, column=0, sticky="nwes")

        # PACK THE WIDGETS
        title_label.pack()
        path_label.pack()
        text_frame.grid(row=0, column=0)
        settings_label.pack(expand=True, fill='both')
        change_settings.pack(side='left', expand=True, pady=(5,0))
        play_stop_animation.pack(side='left', expand=True, pady=(5,0))
        settings_frame.grid(row=1, column=0, sticky="nwes")
        warning_text.pack()
        save_gif.pack(side='left', pady=5, padx=(10,10), expand=True, anchor="e")
        go_back.pack(side='left', pady=5, padx=(10,10), expand=True, anchor="w")
        buttons_frame.grid(row=3, column=0)

        # EMPTY RESULTS OF REAL AND IMAG PARTS OF THE FOURIER SERIES
        real_fourier_results = []
        imag_fourier_results = []
        f_n_real = []
        f_n_imag = []
        modulus = []
        real_curve_results = []
        imag_curve_results = []

        # FIRST MAKE THE CALCULATIONS TO OPTIMIZE ANIMATION
        for j in range(frames+1):
            f_i = [0]
            t = a + j/frames*interval
            result = fourier_series_max_min(N, T, t, f_i)
            real_fourier_results.append(result.real)
            imag_fourier_results.append(result.imag)
            f_n_real.append([i.real for i in f_i])
            f_n_imag.append([i.imag for i in f_i])
            modulus.append([np.sqrt((f_n_real[j][i+1]-f_n_real[j][i])**2+(f_n_imag[j][i+1]-f_n_imag[j][i])**2) for i in range(len(f_i)-1)])
            real_curve_results.append(type_of_function(t, function, b).real)
            imag_curve_results.append(type_of_function(t, function, b).imag)
        
        animation_plot(False)

    else: # DISPLAY ALERT IF NOT
        Alert(window, "Save the canvas first", 2000)
"""
CANVAS TKINTER CLASS
"""
# CANVAS FOR DRAWING SVGs AND SAVING THEM
class Sketchpad(Canvas):
    drawn = False
    saved = False

    def __init__(self, parent, title):
        super().__init__(parent)
        self.title_for_svg = title 
        self.points = []
        self.bind("<Button-1>", self.save_posn)
        self.bind("<B1-Motion>", self.add_line)
        self.bind("<ButtonRelease-1>", self.save_drawing)
        self.configure(bg=BG_SECONDARY_COLOR, highlightthickness=10, highlightbackground=BG_BORDER_COLOR)
        
    def save_posn(self, event):
        self.lastx, self.lasty = event.x, event.y
        self.points.append([self.lastx, self.lasty])

    def add_line(self, event):
        if self.drawn == False:
            distance = sqrt((event.x-self.lastx)**2 + (event.y - self.lasty)**2)
            self.create_line((self.lastx, self.lasty, event.x, event.y), fill="#f7e477", width=3)
            self.save_posn(event)

    def save_drawing(self, event):
        if self.drawn == False:
            if len(self.points) > 4:
                self.drawn = True
                amount_points = int(round(len(self.points)/min(10, len(self.points))))
                self.create_line((event.x, event.y, self.points[0][0], self.points[0][1]), fill="#f7e477", width=3)
                for t in range(amount_points + 1):
                    point_x = (self.points[0][0] - event.x)*t/amount_points + event.x
                    point_y = (self.points[0][1] - event.y)*t/amount_points + event.y
                    self.points.append([point_x, point_y])
            else:
                Alert(window, "Not enough points, draw something bigger", 1000)
                self.delete("all")
                self.points = []
                self.drawn = False
        
    def delete_drawing(self):
        self.delete("all")
        self.points = []
        self.drawn = False

    def save_as_svg(self, title):
        if title.isalnum() == True:
            if self.points == []:
                Alert(window, "Canvas can't be blank, draw something", 1000)
            else:
                self.saved = True
                with open(f"svg/{title}.svg", "w") as w_file:
                        lines_strings = ""
                        first_point = ""
                        path = ""
                        for i in range(len(self.points)):
                            if i == 0:
                                first_point = str(f" {self.points[i][0]},{self.points[i][1]}")
                            else:
                                lines_strings = lines_strings + str(f" {self.points[i][0]},{self.points[i][1]}")
                        path = "M" + first_point + " L" + lines_strings + " Z"
                        w_file.write(f'<svg xmlns="http://www.w3.org/2000/svg"><path d="{path}" style="fill:none;stroke:#000000;stroke-width:3" /></svg>')
                        w_file.close()
        else:
            # SHOW ALERT THAT LETS USER KNOW, A BAD NAME WAS CHOSEN
            Alert(window, "Choose a name to save as .svg (only alphanumeric characters)", 2000)

"""
FUNCTIONS FOR THE FOURIER ANIMATION
"""
# DESTROY EXTRA WIDGETS FOURIER
def destroy_widgets_fourier(window, items):
    global fourier_loading_screen

    for item in items:
        item.destroy() # DESTROY CANVAS AND BUTTONS, PREVENT GOING BACK

    fourier_loading_screen = ctk.CTkLabel(window, text="", text_color="white", font=title_font, fg_color=BG_SECONDARY_COLOR) #CREATE THE LOADING SCREEN IN THE CANVAS
    fourier_loading_screen.grid(row=0, column=1, rowspan=4, sticky="nwes")

# SHOW A LOADING SCREEN WHILE ANIMATION IS SAVING
def loading_screen_fourier(window, frame, last_frame, count):
    if frame == last_frame: # IF IT'S LAST FRAME, SHOW SAVING GIF
        localtext = "SAVING GIF " + (count % 3 + 1)*"."
        fourier_loading_screen.configure(text=localtext)
        fourier_loading_screen.after(1000, lambda: loading_screen_fourier(window, frame, last_frame, count + 1))
    elif frame % 30 == 0: # REPLACE TEXT EVERY 30 FRAMES
        localtext = f"LOADING FRAMES\n{frame} / {last_frame}"
        fourier_loading_screen.configure(text=localtext)

# CREATE THE GIF PLAYER
def load_gif_fourier(window, gif_path, title, type_of_curve, fps):
    global svg_gif_fourier
    global go_back_fourier
    global alert_fourier
    global fourier_loading_text
    global fourier_loading_bar
    global fourier_frame
    
    svg_gif_fourier = GIF_player(window, gif_path, "not-main", fps, PLOT_COLOR) # START GIF PLAYER
    go_back_fourier = ctk.CTkButton(window, text="Main menu",  fg_color=DANGER_BUTTON_COLOR, hover_color=DANGER_BUTTON_COLOR_HOVER, 
                                        border_spacing=15, font=button_font, command= lambda: regrid_main_items(window, False)) # MAIN MENU
    alert_fourier = ctk.CTkLabel(window, text=f"Warning! Resizing the window will result in cropping {title}.gif", 
                                 text_color="white", fg_color="#066899", font=path_font) # ALERT OF GIF CROP
    fourier_loading_screen.destroy()
    
    # CREATE A FRAME TO HOLD PROGRESS BAR AND LOADING LABEL AND PACK THEM
    fourier_frame = ctk.CTkFrame(window, fg_color=BG_SECONDARY_COLOR)
    # CREATE TEXT
    fourier_loading_text = ctk.CTkLabel(fourier_frame, text="LOADING", font=title_font, 
                                    fg_color="transparent", text_color="white")
    # CREATE PROGRESSBAR
    fourier_loading_bar = ctk.CTkProgressBar(fourier_frame, orientation=HORIZONTAL, 
                                    mode='determinate', progress_color="#066899", border_color="#ffffff", 
                                    height=25, fg_color="#f0fcff", border_width=3, corner_radius=0)
    # SET PROGRESS BAR TO 0
    fourier_loading_bar.set(0)
    fourier_loading_text.pack(expand=True, anchor="s")
    fourier_loading_bar.pack(fill="x", padx=100, expand=True, anchor="n")
    fourier_frame.grid(row=0, column=1, rowspan=4, sticky="nwes")

# SHOW THE ANIMATION
def show_fourier_result(window):
    # DESTROY LOADING SCREEN AND SHOW GIF
    fourier_frame.destroy()
    go_back_fourier.grid(row=3, column=0)
    svg_gif_fourier.grid(row=0, rowspan=4, column=1, stick="nwes")
    svg_gif_fourier.play_animation(window)

    # SHOW ALERT OF GIF CROP
    alert_fourier.place(relwidth=1, relx=0, rely=0, anchor="nw", relheight=0.06)
    alert_fourier.after(3000, lambda: alert_fourier.destroy())
    
"""
MAIN BUTTONS LOGIC AND STYLE
"""
# BUTTONS OF MAIN WINDOW CLASS
class Main_Buttons(ctk.CTkButton):
    # DEFINE THE STYLE OF THE BUTTONS
    def __init__(self, window, text, i):
        super().__init__(window)
        self.configure(text=text, font=button_font, text_color="white", 
                       fg_color=MAIN_BUTTON_COLOR, hover_color=MAIN_BUTTON_COLOR_HOVER, 
                       border_color=BORDER_COLOR, border_width=.5,
                       command=lambda: import_file(i, window, None, 1))
        self.type = i
        self.grid(column=0, row=i+1, sticky="nsew", padx=20, pady=10)

    # REGRID BUTTONS WHICH HAVE BEEN DELETED
    def regrid_buttons(self, i):
        self.grid(column=0, row=i+1, sticky="nsew", padx=20, pady=10)

# DEFINE THE FUNCTION OF EACH BUTTON
def import_file(i, window, path, row_index):
    try:
        # DRAW SVG
        if i == 0:
            # DELETE PREVIOUS WIDGETS AND INITIALIZE VARIABLE
            name_of_svg = ctk.StringVar(value="")
            path_of_svg = ctk.StringVar(value="Choose a name . . .")
            for label in window.grid_slaves():
                label.grid_forget()
            # CANVAS WIDGETS
            canvas = Sketchpad(window, "temp")
            canvas_frame = ctk.CTkFrame(window, fg_color=BG_SECONDARY_COLOR)
            clean_canvas = ctk.CTkButton(canvas_frame, text="Redraw", font=button_font, 
                                            fg_color=DANGER_BUTTON_COLOR, hover_color=DANGER_BUTTON_COLOR_HOVER, 
                                            border_spacing=10, command= lambda: canvas.delete_drawing())
            save_canvas = ctk.CTkButton(canvas_frame, text="Save", font=button_font, 
                                            fg_color=MAIN_BUTTON_COLOR, hover_color=MAIN_BUTTON_COLOR_HOVER, 
                                            border_spacing=10, command= lambda: canvas.save_as_svg(title_frame.entry.get()))
            # OTHER WIDGETS
            text_frame = ctk.CTkFrame(window, fg_color="transparent")
            settings = ctk.CTkLabel(text_frame, text="SETTINGS", text_color="white", font=title_font)
            title_frame = Entry(text_frame, "Name", "Choose a name ...", name_of_svg, "normal")
            path_frame = Entry(text_frame, "Path", "Choose a name ...", path_of_svg, "disabled")
            slider_frame = ctk.CTkFrame(window, fg_color="transparent")
            n_slider = Slider(slider_frame, "N:", 1, 100, 50)
            precision_slider = Slider(slider_frame, "Precision:", 100, 1000, 1000)
            frames_slider = Slider(slider_frame, "Frames:", 5, 400, 300)
            fps_slider = Slider(slider_frame, "FPS:", 5, 30, 30)
            buttons_frame = ctk.CTkFrame(window, fg_color="transparent")
            generate_button = ctk.CTkButton(buttons_frame, text="Fourier aproximation", font=button_font, 
                                            fg_color=MAIN_BUTTON_COLOR, hover_color=MAIN_BUTTON_COLOR_HOVER, 
                                            border_color=BORDER_COLOR, border_width=.5, border_spacing=20,
                                            command= lambda: calculate_fourier_series(window, f"{str(Path().absolute().as_posix()) + '/svg/' + title_frame.entry.get()}", title_frame.entry.get(), "svg", 
                                                                                      int(n_slider.slider.get()), int(fps_slider.slider.get()), 
                                                                                      int(frames_slider.slider.get()), int(precision_slider.slider.get()), 
                                                                                      saved=canvas.saved, drawn=True, index_of_function=None))
            go_back_fourier = ctk.CTkButton(buttons_frame, text="Go back",  fg_color=DANGER_BUTTON_COLOR, hover_color=DANGER_BUTTON_COLOR_HOVER, 
                                            border_spacing=15, font=button_font, command= lambda: regrid_main_items(window, False))
            # PACK AND GRID WIDGETS
            settings.pack(pady=(20, 5))
            title_frame.pack(pady=5, fill='x')
            path_frame.pack(pady=5, fill='x')
            text_frame.grid(row=0, column=0, sticky="nwes")
            n_slider.pack(fill='x')
            precision_slider.pack(fill='x')
            frames_slider.pack(fill='x')
            fps_slider.pack(fill='x')
            slider_frame.grid(row=1, rowspan=2, column=0, sticky="nwes")
            generate_button.pack()
            go_back_fourier.pack(pady=10)
            buttons_frame.grid(row=3, column=0)
            canvas.grid(row=0, column=1, rowspan=4, sticky="nwes")
            clean_canvas.pack(side='left', padx=(0,5))
            save_canvas.pack(side='left')
            canvas_frame.place(relx=0.99, rely=0.98, anchor="se")

            # UPDATE NAME OF PATH
            def update_name_path(var, index, mode):
                if name_of_svg.get().isalnum() == True:
                    path_of_svg.set(f"{str(Path().absolute().as_posix()) + '/svg/' + name_of_svg.get() + '.svg'}")
                    path_frame.entry.configure(text_color="grey")
                else:
                    if name_of_svg.get() == "":
                        path_of_svg.set("Choose a name . . .")
                    else:
                        path_of_svg.set("Invalid name")
                    path_frame.entry.configure(text_color="red")
            name_of_svg.trace_add("write", callback=update_name_path)

        # OPEN SVG
        if i == 1:
            # OPEN SVG PATH AND CLEAN EXISTING WIDGETS TO ADD NEW ONES
            if path == None:
                try:
                    path = filedialog.askopenfile(filetypes=[("SVG files", "*.svg")]).name
                except:
                    for label in window.grid_slaves():
                        label.grid_forget()
                for label in window.grid_slaves():
                    label.grid_forget()
            else:
                for label in window.winfo_children():
                    if label.winfo_ismapped() == True:
                        label.destroy()
                        
            title_text = path.split(".")[-2].split('/')[-1]
            
            # ROW AND COLUMN CONFIGURE WITH LABEL AND BUTTONS
            text_frame = ctk.CTkFrame(window, fg_color="transparent")
            title_label = ctk.CTkLabel(text_frame, text=title_text, font=title_font, text_color="white")
            path_label = ctk.CTkLabel(text_frame, text=f"Path selected:\n{path}", font=path_font, text_color="grey")
            slider_frame = ctk.CTkFrame(window, fg_color="transparent")
            settings = ctk.CTkLabel(slider_frame, text="SETTINGS", text_color="white", font=title_font)
            n_slider = Slider(slider_frame, "N:", 1, 100, 50)
            precision_slider = Slider(slider_frame, "Precision:", 100, 1000, 1000)
            frames_slider = Slider(slider_frame, "Frames:", 5, 400, 300)
            fps_slider = Slider(slider_frame, "FPS:", 5, 30, 30)
            buttons_frame = ctk.CTkFrame(window, fg_color="transparent")
            generate_button = ctk.CTkButton(buttons_frame, text="Fourier aproximation", font=button_font, 
                                            fg_color=MAIN_BUTTON_COLOR, hover_color=MAIN_BUTTON_COLOR_HOVER, 
                                            border_color=BORDER_COLOR, border_width=.5, border_spacing=20,
                                            command= lambda: calculate_fourier_series(window, path.split(".")[-2], title_text, "svg", 
                                                                                      int(n_slider.slider.get()), int(fps_slider.slider.get()), 
                                                                                      int(frames_slider.slider.get()), int(precision_slider.slider.get()), 
                                                                                      saved=True, drawn=False, index_of_function=None))
            go_back_fourier = ctk.CTkButton(buttons_frame, text="Go back",  fg_color=DANGER_BUTTON_COLOR, hover_color=DANGER_BUTTON_COLOR_HOVER, 
                                            border_spacing=15, font=button_font, command= lambda: regrid_main_items(window, False))
            
            svg_to_png_function, t_total = svg_parser.open_svg(path.split(".svg")[0], False) # CALL THE SVG PARSER
            frames = 10000
            x = []
            y = []
            for i in range(frames):
                result = svg_parser.evaluate_svg(i/frames*t_total, svg_to_png_function, t_total) # EVALUATE THE FUNCTION
                x.append(result.real)
                y.append(result.imag)

            # SHOW SVG AS A PLOT ON MATPLOTLIB
            plt.style.use("dark_background")
            fig = plt.Figure(layout='tight')
            canvas = FigureCanvasTkAgg(fig, master=window)
            canvas.draw()
            canvas.get_tk_widget().grid(column=1, row=0, rowspan=4, sticky="nwes")

            ax = fig.add_subplot(111)
            ax.set_aspect('equal', 'box')
            ax.set_axis_off()
            ax.plot(x,y)

            # GRID AND PACK THE WIDGETS
            title_label.pack()
            path_label.pack()
            text_frame.grid(row=0, rowspan=2, column=0)
            settings.pack(pady=10)
            n_slider.pack(fill='x')
            precision_slider.pack(fill='x')
            frames_slider.pack(fill='x')
            fps_slider.pack(fill='x')
            slider_frame.grid(row=2, column=0, sticky="nwes")
            generate_button.pack()
            go_back_fourier.pack(pady=10)
            buttons_frame.grid(row=3, column=0)
        
        # OPEN PY FILE
        if i == 2:
            # UPDATE CSV TEXT TO SELECT ROW
            def choose_function(window, selected_row, csv_text, csv_label, position, count):
                global current_row # CURRENT ROW SELECTED
                selected = csv_label.cget("text").split("   <---- SELECTED") # GET IF THERE IS ANY <---- SELECTED
                rows = csv_text.split(f"\n") # TEXT TO CHANGE
                if len(selected) != 1: # IF ALREADY <---- SELECTED
                    if position == "left": # IF LEFT BUTTON WAS CLICKED
                        index_of_row = current_row - 1
                        if index_of_row > 0:
                            rows[index_of_row] = selected[0].split(f"\n")[-2] + "   <---- SELECTED"
                            current_row = index_of_row
                        else:
                            rows = csv_label.cget("text").split("\n")
                    elif position == "right": # IF RIGHT BUTTON WAS CLICKED
                        index_of_row = current_row + 1
                        if index_of_row < count:
                            rows[index_of_row] = selected[1].split(f"\n")[1] + "   <---- SELECTED"
                            current_row = index_of_row
                        else: 
                            rows = csv_label.cget("text").split("\n")
                    elif 0 < selected_row < count: # IF ROW WAS SELECTED
                        rows[selected_row] = rows[selected_row] + "   <---- SELECTED"
                        current_row = selected_row
                    else:
                        rows = csv_label.cget("text").split("\n")
                else: # IF NO <---- SELECTED
                    if position == None:
                        if 0 < selected_row < count:
                            rows[selected_row] = rows[selected_row] + "   <---- SELECTED"
                            current_row = selected_row
                        else:
                            rows = csv_label.cget("text").split("\n")
                    else: # FIRST CONFIGURE OR ROW
                        rows[selected_row] = rows[selected_row] + "   <---- SELECTED"
                        current_row = selected_row
                # SET NEW <---- SELECTED AND SAVE IT
                new_text = f"\n".join(rows)
                csv_selected.configure(text=current_row)
                csv_label.configure(text=new_text)

                # SAVE THE FUNCTION TO ENTRY
                function_holder.set(rows[current_row].split(",")[1])
                # CONFIGURE THE POSITION OF THE SCROLLBAR TO FOCUS ON NEW ROW
                size_of_scroll = csv_text_frame._scrollbar.get()[1]-csv_text_frame._scrollbar.get()[0]
                position_of_scroll = current_row/count
                if position_of_scroll - size_of_scroll/2 < 0:
                    delta_y_below = size_of_scroll
                    delta_y_above = 0
                elif position_of_scroll + size_of_scroll/2 > 1:
                    delta_y_below = 1
                    delta_y_above = 1 - size_of_scroll
                else:
                    delta_y_below = position_of_scroll + size_of_scroll/2
                    delta_y_above = position_of_scroll - size_of_scroll/2
                csv_text_frame._scrollbar.set(delta_y_above, delta_y_below)
                csv_text_frame._parent_canvas.yview_moveto(delta_y_above)

            # VALIDATE THE ENTRY OF ROW
            def validate_number(to_check, action):
                if action == '0': # DELETE ACTION
                    if to_check.isdigit():
                        if 0 < int(to_check) < count:
                            choose_function(window, int(to_check), csv_text, csv_label, None, count)
                            return True
                        return False
                    return True
                else: # INPUT ACTION
                    if to_check.isdigit(): # CHECK IF IT'S NUMBER
                        if 0 < int(to_check) < count: # CHECK THE NUMBER
                            choose_function(window, int(to_check), csv_text, csv_label, None, count)
                            return True
                        return False
                    return False
            # CHECK IF THERE IS ALREADY A PATH - READ PATH CSV FILE
            if path == None:
                try:
                    path = filedialog.askopenfile(filetypes=[("CSV files", "*.csv")]).name
                except:
                    for label in window.grid_slaves():
                        label.grid_forget()
                for label in window.grid_slaves():
                    label.grid_forget()
            else:
                for label in window.winfo_children():
                    if label.winfo_ismapped() == True:
                        label.destroy()
            current_row = row_index
            title_text = path.split(".")[-2].split('/')[-1]
            csv_text = ""
            count = 0
            # READ CSV FILE AND SAVE CONTENT
            with open(path, "r") as csv_file:
                header = "HEADER"
                lines = csv.reader(csv_file)
                total = len(str(sum(1 for i in csv_file) - 1))
                if total - len(header) >= 0:
                    difference = total - len(header)
                    to_sum = total
                else:
                    difference = 0
                    to_sum = len(header)
                csv_file.seek(0)
                lines = csv.reader(csv_file)
                for line in lines:
                        if count == 0:
                            csv_text += header + " "*difference + " | " + ",".join(line) + "\n"
                        else:
                            if count == 1:
                                function_holder = StringVar(value=line[1])
                            csv_text += f"{count}" + " "*(to_sum - len(str(count))) + " | " + ",".join(line) + "\n"
                        count += 1
                csv_header = f"Total functions: {count - 1}, Chars: {len(csv_text)}"
                csv_file.close()

            # CSV WIDGETS
            csv_frame = ctk.CTkFrame(window, fg_color="black")
            csv_text_frame = ctk.CTkScrollableFrame(csv_frame, fg_color="black")
            csv_header = ctk.CTkLabel(csv_text_frame, text=csv_header, font=slider_font, text_color="white", justify="left", anchor="nw")
            csv_label = ctk.CTkLabel(csv_text_frame, text=csv_text, font=slider_font, text_color="white", justify="left", anchor="nw")
            csv_buttons = ctk.CTkFrame(csv_frame, fg_color="transparent")
            csv_buttons.columnconfigure(0, weight=3, uniform="r")
            csv_buttons.columnconfigure(1, weight=1, uniform="r")
            csv_buttons.rowconfigure((0,1), weight=1)
            csv_function = Entry(csv_buttons, "Function:", "Select row first", function_holder, "disabled")
            csv_row = Entry(csv_buttons, "Row:", "Enter row ...", None, "normal")
            csv_row.entry.configure(validate="key", validatecommand=(csv_row.register(validate_number), '%P', '%d'))
            csv_control = ctk.CTkFrame(csv_buttons, fg_color="transparent")
            csv_button_left = ctk.CTkButton(csv_control, text="<", command=lambda: choose_function(window, 
                                            current_row, csv_text, csv_label, "left", count), 
                                            font=button_font, fg_color=MAIN_BUTTON_COLOR, hover_color=MAIN_BUTTON_COLOR_HOVER, 
                                            border_color=BORDER_COLOR, border_width=.5, width=30, border_spacing=10)
            csv_selected = ctk.CTkLabel(csv_control, text="1", font=sub_title_font, text_color="white")
            csv_button_right = ctk.CTkButton(csv_control, text=">", command=lambda: choose_function(window, 
                                            current_row, csv_text, csv_label, "right", count),
                                            font=button_font, fg_color=MAIN_BUTTON_COLOR, hover_color=MAIN_BUTTON_COLOR_HOVER, 
                                            border_color=BORDER_COLOR, border_width=.5, width=30, border_spacing=10)

            # FOURIER WIDGETS
            text_frame = ctk.CTkFrame(window, fg_color="transparent")
            title_label = ctk.CTkLabel(text_frame, text=title_text, font=title_font, text_color="white")
            path_label = ctk.CTkLabel(text_frame, text=f"Path selected:\n{path}", font=path_font, text_color="grey")
            slider_frame = ctk.CTkFrame(window, fg_color="transparent")
            settings = ctk.CTkLabel(slider_frame, text="SETTINGS", text_color="white", font=title_font)
            n_slider = Slider(slider_frame, "N:", 1, 100, 50)
            precision_slider = Slider(slider_frame, "Precision:", 100, 1000, 1000)
            frames_slider = Slider(slider_frame, "Frames:", 5, 400, 300)
            fps_slider = Slider(slider_frame, "FPS:", 5, 30, 30)
            buttons_frame = ctk.CTkFrame(window, fg_color="transparent")
            generate_button = ctk.CTkButton(buttons_frame, text="Fourier aproximation", font=button_font, 
                                            fg_color=MAIN_BUTTON_COLOR, hover_color=MAIN_BUTTON_COLOR_HOVER, 
                                            border_color=BORDER_COLOR, border_width=.5, border_spacing=20,
                                            command= lambda: calculate_fourier_series(window, path.split(".")[-2], title_text, "csv", 
                                                                                    int(n_slider.slider.get()), int(fps_slider.slider.get()), 
                                                                                    int(frames_slider.slider.get()), int(precision_slider.slider.get()), 
                                                                                    saved=True, drawn=False, index_of_function=int(csv_selected.cget("text"))))
            go_back_fourier = ctk.CTkButton(buttons_frame, text="Go back",  fg_color=DANGER_BUTTON_COLOR, hover_color=DANGER_BUTTON_COLOR_HOVER, 
                                            border_spacing=15, font=button_font, command= lambda: regrid_main_items(window, False))
            
            # PACK AND GRID ALL THE WIDGETS
            title_label.pack()
            path_label.pack()
            text_frame.grid(row=0, rowspan=2, column=0)
            settings.pack(pady=10)
            n_slider.pack(fill='x')
            precision_slider.pack(fill='x')
            frames_slider.pack(fill='x')
            fps_slider.pack(fill='x')
            slider_frame.grid(row=2, column=0, sticky="nwes")
            generate_button.pack()
            go_back_fourier.pack(pady=10)
            buttons_frame.grid(row=3, column=0)
            csv_header.pack(expand=True, fill="both", padx=20, pady=20)
            csv_label.pack(expand=True, fill="both", padx=20)
            csv_text_frame.pack(expand=True, fill="both")
            csv_function.grid(row=0, column=0, sticky="nwes")
            csv_row.grid(row=1, column=0, sticky="nwes")
            csv_button_left.pack(expand=True, side="left", anchor="e")
            csv_selected.pack(expand=True,side="left")
            csv_button_right.pack(expand=True, side="left", anchor="w")
            csv_control.grid(row=0, rowspan=2, column=1, sticky="nwes")
            csv_buttons.pack(fill="both", ipady=50)
            csv_frame.grid(row=0, column=1, rowspan=4, sticky="nwes")
            csv_button_right.invoke()
    except:
        regrid_main_items(window, True)
        if i == 0:
            Alert(window, "An error occurred, try again!", 3000)
        elif i == 1:
            Alert(window, "An error occurred while parsing SVG file", 3000)
        else:
            Alert(window, "An error occurred while parsing CSV file", 3000)

"""
SLIDERS TKINTER CLASS
"""
# SLIDERS TO CONFIGURE THE N, PRECISION, FRAMES AND FPS OF PLOTS
class Slider(ctk.CTkFrame):
    def __init__(self, parent, name, min, max, start_value):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        self.name = name
        self.title = ctk.CTkLabel(self, text=f"{name} {start_value}", text_color="#c2eeff", # ADD A TITLE FOR THE SLIDER
                                  font=slider_font, justify="left", anchor="w", width=150)
        self.slider = ctk.CTkSlider(self, from_=min, to=max, number_of_steps=int(max-min), 
                                    height=20, border_color=BG_BORDER_COLOR, border_width=4, progress_color="#6a9db0", fg_color=BG_SECONDARY_COLOR,
                                    button_color=MAIN_BUTTON_COLOR, button_hover_color=MAIN_BUTTON_COLOR, command=self.update_slider) # ADD THE SLIDER
        self.slider.set(start_value)
        self.title.pack(side='left', padx=(30, 0), pady=(0,5))
        self.slider.pack(side='left', fill='x', expand=True, padx=(0, 50), pady=(0,5))
    
    def update_slider(self, value):
        self.title.configure(text=f"{self.name} {int(value)}") # CHANGE VALUE OF SLIDER
"""
ALERT TKINTER CLASS
"""
class Alert(ctk.CTkLabel):
    def __init__(self, parent, text, time):
        super().__init__(parent)
        self.configure(text=text, text_color="white", fg_color=DANGER_BUTTON_COLOR, font=path_font)
        self.place(relwidth=1, relx=0, rely=0, anchor="nw", relheight=0.06)
        self.after(time, lambda: self.destroy())

"""
ENTRIES TKINTER CLASS
"""
# CLASS FOR INPUTING NAME AND PATH FOR CANVAS DRAWING
class Entry(ctk.CTkFrame):
    def __init__(self, parent, name, place_holder, variable, active):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        self.label = ctk.CTkLabel(self, text=name, font=sub_title_font, text_color="white", width=60, anchor="w") # NAME
        self.entry = ctk.CTkEntry(self, placeholder_text=place_holder, state=active, font=sub_title_font, 
                                text_color="white", fg_color=BG_SECONDARY_COLOR, border_width=2, border_color=BG_BORDER_COLOR) # INPUT
        if variable != None:
            self.entry.configure(textvariable=variable)
        self.label.pack(side='left', padx=(20, 10))
        self.entry.pack(side='left', fill='x', expand=True, padx=(10, 20))
        
"""
MINI TABLE TKINTER CLASS
"""
# A TABLE TO SHOW THE SETTINGS OF THE PLOT
class Mini_table(ctk.CTkFrame):
    def __init__(self, parent, names, values):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        self.names = []
        self.values = []
        self.columnconfigure((0,1), weight=1, uniform="b")
        self.rowconfigure(tuple(range(len(names))), weight=1, uniform="c")
        for i in range(len(names)):
            self.names.append(ctk.CTkLabel(self, text=names[i], font=table_font, text_color="white", fg_color=BG_SECONDARY_COLOR)) # NAME
            self.values.append(ctk.CTkLabel(self, text=values[i], font=table_font, text_color="#c2eeff", fg_color=BG_SECONDARY_COLOR)) # VALUE
            self.names[i].grid(row=i, column=0, sticky="nwes", padx=(20,1), pady=(0,1))
            self.values[i].grid(row=i, column=1, sticky="nwes", padx=(1,20), pady=(0,1))
"""
CSV TABLE TKINTER CLASS
"""
# A TABLE TO SHOW THE SETTINGS OF THE PLOT
class CSV_Table(ctk.CTkScrollableFrame):
    def __init__(self, parent, values):
        super().__init__(parent)
        self.configure(fg_color="red")
        self.values = []
        self.rows = len(values[0])
        self.columns = 6
        self.columnconfigure((0,3,4,5), weight=1, uniform="e")
        self.columnconfigure((1,2), weight=2, uniform="e")
        self.rowconfigure(tuple(range(self.rows)), weight=1, uniform="g")
        self.counter = 0
        for i in range(1, self.rows):
            temp = ctk.CTkLabel(self, text=i, font=table_font, text_color="#c2eeff", fg_color="red")
            temp.grid(row=i, column=0, sticky="nwes")
        for j in range(len(values)):
            for i in range(self.rows):
                if i == 1:
                    fg_color = "red"
                else:
                    fg_color = BG_SECONDARY_COLOR
                self.values.append(ctk.CTkLabel(self, text=values[j][i], font=table_font, text_color="#c2eeff", 
                                                fg_color=fg_color)) # VALUE
                if i == 0:
                    pady = (10, 5)
                elif i == self.rows - 1:
                    pady = 5
                else:
                    pady = 5 
                if j == 0:
                    padx = (10, 5)
                elif j == 4:
                    padx = (5, 10)
                else:
                    padx = 5

                self.values[self.counter].grid(row=i, column=j+1, sticky="nwes", padx=padx, pady=pady, ipady=20)
                self.counter += 1
        
"""
GIF PLAYER CLASS
"""
# GIF PLAYER - CREATE A LABEL WITH IMAGE PLAYER INSIDE
class GIF_player(Label):
    def __init__(self, window, gif_path, gif_value, fps, color):
        super().__init__(window)
        self.gif_value = gif_value # IF MAIN-GIF OR NOT
        self.gif_path = gif_path # SAVE PATH
        self.configure(background=color) # ENSURE NO BORDER COLORS
        self.gif = Image.open(gif_path)
        self.images = []
        self.frames = self.gif.n_frames
        self.fps = fps
        self.loaded = False
        self.first_play = True
        self.current_frame = 0
        Thread(target=self.load_gif, args=(window, gif_path), daemon=True).start() # MULTI-THREADING FOR LOADING GIF

    # USE THREADING TO WAIT FOR THE GIF TO LOAD
    def load_gif(self, window, gif_path):
        with Image.open(gif_path) as im:
            count = 0 # COUNT FOR PROGRESSBAR
            int_count = 0 # COUNT USED FOR LOADING TEXT
            try:
                temp = -1
                while 1:
                    # RESIZE IMAGE TO HAVE THE WIDTH AND HEIGHT OF THE SCREEN, MAINTAIN ASPECT RATIO
                    img = im.copy()
                    aspect_ratio = im.size[1]/img.size[0] # HEIGHT / WIDTH
                    img_scale = 1/2*scaling # SCALE FOR IMAGE
                    resized = img.resize((int(screen_width*img_scale), int(aspect_ratio*screen_width*img_scale)))
                    self.images.append(ImageTk.PhotoImage(resized))
                    im.seek(im.tell() + 1) # UPDATE NEXT IMAGE TO READ
                    # UPDATE THE PROGRESS BAR WITH THIS VALUE
                    loading_value = int(100*count/self.frames)
                    if loading_value % 10 == 0: # UPDATE PROGRESSBAR ONLY WHEN 10 FRAMES ARE LOADED
                        if loading_value != temp: # ENSURE NO DUPLICATES
                            percentage_gif_ticket = Ticket(ticket_type=TicketPurpose.PERCENTAGE_GIF, ticket_label=self, 
                                                        ticket_value=f"{loading_value},{int_count},{self.gif_value}")
                            window.queue_message.put(percentage_gif_ticket)
                            window.event_generate("<<CheckQueue>>")
                            int_count += 1
                        temp = loading_value
                    count += 1
            except EOFError:
                pass  # end of sequence
            
            # LOAD MAIN WINDOW TO PLAY ANIMATION BY UPDATING TICKET
            loaded_gif_ticket = Ticket(ticket_type=TicketPurpose.LOADED_GIF, ticket_label=self, ticket_value=self.gif_value)
            window.queue_message.put(loaded_gif_ticket)
            window.event_generate("<<CheckQueue>>")

    # PLAY ANIMATION 30 FPS
    def play_animation(self, parent):
        if self.loaded == True and self.winfo_exists() == True:
            self.configure(image=self.images[self.current_frame])
            if self.current_frame == self.frames - 1:
                self.current_frame = 0
            else:
                self.current_frame += 1  
            if self.winfo_ismapped() == True or self.first_play == True or window.state() == "iconic":
                if self.current_frame > self.frames//2:
                    self.first_play = False
                parent.after(int(1000/self.fps), lambda: self.play_animation(parent))


"""
INITIAL LOGIC FOR APP
"""
# START APP WITH LOADING WINDOW
window = ctk.CTk()

# QUEUE FOR MULTI-THREADING
window.queue_message = Queue()
window.bind("<<CheckQueue>>", check_queue)
window.bind("<Configure>", update_size)

# USED FONTS -  NEED TO BE INSTALLED ON SYSTEM
main_title_font = ctk.CTkFont(family="Rubik", size=80, weight="bold")
title_font = ctk.CTkFont(family="Rubik", size=40)
sub_title_font = ctk.CTkFont(family="Rubik", size=20)
button_font = ctk.CTkFont(family="Roboto", size=20)
path_font = ctk.CTkFont(family="Rubik", size=15)
slider_font = ctk.CTkFont(family="Consolas", size=15)
loading_font = ctk.CTkFont(family="Rubik", size=20)
table_font = ctk.CTkFont(family="Rubik", size=20)

# CONFIGURE WINDOW
# CHANGE WINDOW COLOR BACKGROUND
window.configure(fg_color=BG_COLOR)
# NOT RESIZABLE
window.resizable(False, False)
# NO TITLE
window.overrideredirect(True)
# ON TOP
window.attributes('-topmost',True)
# ALPHA OF WINDOW
window.attributes('-alpha', .85)
# SIZE OF WINDOW TO BE HALF THE WIDTH AND HEIGHT OF THE SCREEN 
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
win_width = window.winfo_screenwidth()//2
win_height = window.winfo_screenheight()//2
win_left = int((screen_width / 2 - (win_width / 2))*scaling) 
win_top = int((screen_height / 2 - (win_height / 2))*scaling)
window_starting_size = f'{win_width}x{win_height}+{win_left}+{win_top}'
window.geometry(window_starting_size)

# CHANGE TASKBAR ICON
window.iconbitmap('assets\\fourier-app-logo.ico')

# CREATE A FRAME TO HOLD PROGRESS BAR AND LOADING LABEL AND PACK THEM
starting_frame = ctk.CTkFrame(window, fg_color="transparent")
# CREATE PROGRESSBAR
main_loading = ctk.CTkProgressBar(starting_frame, orientation=HORIZONTAL, 
                                mode='determinate', progress_color="#73ffe8", border_color="#ffffff", 
                                height=15, fg_color="#f0fcff", border_width=2, corner_radius=0)
# SET PROGRESS BAR TO 0
main_loading.set(0)
# CREATE TEXT
main_loading_text = ctk.CTkLabel(starting_frame, text="LOADING", font=loading_font, 
                                fg_color="transparent", text_color="white")
main_loading_text.pack(pady=10)
main_loading.pack(fill="x", padx=200)
starting_frame.pack(expand=True, fill="x")

# LOAD MAIN GIF AND WAIT FOR IT TO LOAD USING GIF_player
main_gif_path = "assets\\fourier-app-logo.gif"
main_gif = GIF_player(window, main_gif_path, "main", 30, BG_COLOR)

# ADD ESC TO CLOSE WINDOW
window.bind('<Escape>', lambda event: window.quit())

# MAIN LOOP FOR APP
window.mainloop()