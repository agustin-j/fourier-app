# MOVING POINTS OR LINES
point_char = ["M", "m", "L", "l"] #(x,y) or (dx,dy)
# ONLY V OR H
one_chars = ["H", "h", "V", "v"] # x or y or dx or dy
# BEZIER CURVES
bezier_chars = ["C", "c", "S", "s", "Q", "q", "T", "t"]
# ARCS
arcs_chars = ["A", "a"]
# CLOSED PATH
closed_chars = ["Z", "z"]
# TOTALS 
chars = ["M", "m", "L", "l", "H", "h", "V", "v", "C", "c", "S", "s", "Q", "q", "T", "t", "A", "a", "Z", "z"]

# FOR LINES (A-B).t + A  (0 < t < 1)
# FOR CUBIC BEZIER A.(1-t)^3 + 3B.t.(1-t)^2 + 3C.(1-t).t^2 + D.t^3  (0 < t < 1)
# FOR QUADRATIC BEZIER A.(1-t)^2 + 2B.(1-t).t + C.t^2  (0 < t < 1)

# AUXILIAR FUNCTION
def func_local_count(path_split, i):
    local_count = 0
    for j in range(i+2, len(path_split)):
        if path_split[j] not in chars:
            local_count += 1
        else:
            break
    return local_count

# OPEN THE SVG AND SAVE AS A FUNCTION
def open_svg(namefile, pre_parsed):
    with open(f"{namefile}.svg", "r") as file:
        path = file.read().split("<path")
        for i in path[1:]:
            if 'd="m' in i or 'd="M' in i:
                path = i.split("d=")[1].split('"')[1]
                break
        path = " ".join(path.split(f"\n"))
        path = " ".join(path.split())
        path = " ".join(path.split(","))
        if pre_parsed == False:
            temp_path = ""
            fixed = False
            num_count = 0
            prev_number = False
            for j in range(len(path)):
                fixed = False
                if path[j].isdigit() == True or path[j] == "." or (path[j] == "-" and path[j-1].isdigit() == False) or path[j] =="e":
                    if prev_number != True:
                        if num_count < 1:
                            num_count += 1
                        else:
                            num_count = 0
                    prev_number = True
                elif path[j] in chars:
                    num_count = 0
                    prev_number = False
                else:
                    prev_number = False
                if j == 0: # CHECK THE START OF PATH
                    if path[j] in ["M", "m"]:
                        temp_path += path[j]
                        fixed = True
                    elif path[j] == " " and path[j+1] in ["M", "m"]:
                        fixed = True
                elif j != len(path) - 1:
                    if path[j] in chars: # CHECK THE CHARS
                        if path[j+1].isdigit() == True or path[j+1] == "-" or path[j+1] == " ":
                            if temp_path[-1].isdigit() == True:
                                temp_path += " " + path[j]
                                fixed = True
                            elif temp_path[-1] == " ":
                                temp_path += path[j]
                                fixed = True

                    elif path[j].isdigit() == True: # CHECK THE NUMBERS
                        if path[j+1].isdigit() == True or path[j+1] == "." or path[j+1] == "," or path[j+1] == "-" or path[j+1] in chars or path[j+1] == " " or path[j+1] == "e":
                            if temp_path[-1].isdigit() == True or temp_path[-1] == "-" or temp_path[-1] == " ":
                                temp_path += path[j]
                                fixed = True
                            if temp_path[-1] == ".":
                                if path[j+1] != ".":
                                    temp_path += path[j]
                                    fixed = True
                            if temp_path[-1] == ",":
                                if path[j+1] != ",":
                                    temp_path += path[j]
                                    fixed = True
                            elif temp_path[-1] in chars:
                                if path[j+1] in chars:
                                    if path[j+1] in one_chars:
                                        temp_path += " " + path[j]
                                        fixed = True
                                else:
                                    temp_path += " " + path[j]
                                    fixed = True

                    elif path[j] == " ": # CHECK THE EMPTY SPACES
                        if temp_path[-1].isdigit() == True:
                            if path[j+1].isdigit() == True or path[j+1] == "-" or path[j+1] == "e":
                                if num_count == 1:
                                    temp_path += ","
                                    temp = ","
                                    fixed = True
                                else:
                                    temp_path += path[j]
                                    fixed = True
                            elif path[j+1] in chars:
                                temp_path += path[j]
                                fixed = True
                        elif temp_path[-1] in chars:
                            if path[j+1].isdigit() == True or path[j+1] == "-":
                                temp_path += path[j]
                                fixed = True

                    elif path[j] == ".": # CHECK THE DECIMALS
                        if temp_path[-1].isdigit() == True and (path[j+1].isdigit() == True or path[j+1] == "e"):
                            temp_path += path[j]
                            fixed = True

                    elif path[j] == ",": # CHECK THE COMMAS
                        if temp_path[-1].isdigit() == True:
                            if path[j+1].isdigit() == True or path[j+1] == "-" or path[j+1] == "e":
                                temp_path += path[j]
                                fixed = True

                    elif path[j] == "-": # CHECK THE NEGATIVE SIGN
                        if path[j+1].isdigit() == True or path[j+1] == "e":
                            if temp_path[-1] == "," or temp_path[-1] == " " or temp_path[-1] == "e":
                                temp_path += path[j]
                                fixed = True
                            elif temp_path[-1] in chars:
                                temp_path += " " + path[j]
                                fixed = True
                            elif temp_path[-1].isdigit():
                                if num_count == 1:
                                    temp_path += "," + path[j]
                                    temp = ","
                                    fixed = True
                                else:
                                    temp_path += " " + path[j]
                                    fixed = True
                    elif path[j] == "e": # BASE 10
                        temp_path += path[j]
                        fixed = True
                elif j == len(path) - 1:
                    if path[j] in closed_chars:
                        if temp_path[-1] == " ":
                            temp_path += path[j]
                            fixed = True
                        elif temp_path[-1].isdigit() == True:
                            temp_path += " " + path[j]
                            fixed = True
                    elif path[j] == " ":
                        temp_path += path[j] + "z"
                        fixed = True
                    elif path[j].isdigit() == True:
                        temp_path += path[j] + " z"
                        fixed = True
                if fixed == False:
                    raise Exception("INVALID-SVG")
            path = temp_path
        
        path_split = path.split(" ")
        function_split = [0]*len(path_split)
        file.close()
        # USED FOR RELATIVE REFERENCES AND UPDATES
        last_position = 0
        # USED FOR SMOOTH BEZIER CURVES AND UPDATES
        bezier_last_control_point = None
        # THE PARAMETER T INTERVAL
        t_total = 0
        temp = 0
        # LOGIC FOR SPLITTING
        for i in range(len(path_split)):
            # MOVING POINTS OR LINES
            if path_split[i] in point_char:
                function_split[i] = "-"
                dx, dy = [float(j) for j in path_split[i+1].split(",")]
                # CHECK IF THERE IS ONLY ONE POINT
                local_count = func_local_count(path_split, i)
                
                # ABSOLUTE M
                if path_split[i] == "M":
                    # ONLY ONE POINT
                    function_split[i+1] = dx - dy*1j
                    last_position = dx - dy*1j
                    # MULTIPLE POINTS
                    if local_count > 0:
                        for k in range(local_count):
                            dx, dy = [float(j) for j in path_split[i+2+k].split(",")]
                            line_function = f"{dx - dy*1j - last_position}*(t-{t_total}) + {last_position}"
                            function_split[i+2+k] = line_function
                            t_total += 1
                            last_position = dx - dy*1j
                # RELATIVE m
                elif path_split[i] == "m":
                    # ONLY ONE POINT
                    function_split[i+1] = last_position + dx - dy*1j
                    last_position = last_position + dx - dy*1j
                    # MULTIPLE POINTS
                    if local_count > 0:
                        for k in range(local_count):
                            dx, dy = [float(j) for j in path_split[i+2+k].split(",")]
                            line_function = f"{dx - dy*1j}*(t-{t_total}) + {last_position}"
                            function_split[i+2+k] = line_function
                            t_total += 1
                            last_position = last_position + dx - dy*1j
                
                # ABSOLUTE L
                elif path_split[i] == "L":  
                    # ONLY ONE POINT
                    line_function = f"{dx - dy*1j - last_position}*(t-{t_total}) + {last_position}"
                    function_split[i+1] = line_function
                    t_total += 1
                    last_position = dx - dy*1j
                    # MULTIPLE POINTS
                    if local_count > 0:
                        for k in range(local_count):
                            dx, dy = [float(j) for j in path_split[i+2+k].split(",")]
                            line_function = f"{dx - dy*1j - last_position}*(t-{t_total}) + {last_position}"
                            function_split[i+2+k] = line_function
                            t_total += 1
                            last_position = dx - dy*1j
                # RELATIVE l
                elif path_split[i] == "l":
                    # ONLY ONE POINT
                    line_function = f"{dx - dy*1j}*(t-{t_total}) + {last_position}"
                    function_split[i+1] = line_function
                    t_total += 1
                    last_position = last_position + dx - dy*1j
                    # MULTIPLE POINTS
                    if local_count > 0:
                        for k in range(local_count):
                            dx, dy = [float(j) for j in path_split[i+2+k].split(",")]
                            line_function = f"{dx - dy*1j}*(t-{t_total}) + {last_position}"
                            function_split[i+2+k] = line_function
                            t_total += 1
                            last_position = last_position + dx - dy*1j

            # ONLY V OR H
            if path_split[i] in one_chars:
                function_split[i] = "-"
                # ONLY ONE, NOT SPLIT
                dl = float(path_split[i+1])
                # CHECK IF THERE IS ONLY ONE POINT
                local_count = func_local_count(path_split, i)
                
                # REPLACE UNNECESSARY SPLITS TO LATER DELETE
                for j in range(local_count):
                    function_split[i+1+j] = "-"
                    dl += float(path_split[i+1+j])

                # ABSOLUTE H
                if path_split[i] == "H":
                    dx = dl
                    line_function = f"{dx - last_position.real}*(t-{t_total}) + {last_position}"
                    function_split[i+1+local_count] = line_function
                    t_total += local_count + 1
                    last_position = dx + last_position.imag*1j
                # RELATIVE h
                elif path_split[i] == "h":
                    dx = dl
                    line_function = f"{dx}*(t-{t_total}) + {last_position}"
                    function_split[i+1+local_count] = line_function
                    t_total += local_count + 1
                    last_position = dx + last_position

                # ABSOLUTE V
                elif path_split[i] == "V":
                    dy = dl
                    line_function = f"{-dy*1j - last_position.imag*1j}*(t-{t_total}) + {last_position}"
                    function_split[i+1+local_count] = line_function
                    t_total += local_count + 1
                    last_position = -dy*1j + last_position.real
                # RELATIVE v
                elif path_split[i] == "v":
                    dy = dl
                    line_function = f"{-dy*1j}*(t-{t_total}) + {last_position}"
                    function_split[i+1+local_count] = line_function
                    t_total += local_count + 1
                    last_position = -dy*1j + last_position

            # BEZIER CURVES
            if path_split[i] in bezier_chars:
                function_split[i] = "-"
                # CHECK IF THERE IS ONLY ONE BEZIER
                local_count = func_local_count(path_split, i)
                
                # ABSOLUTE C
                if path_split[i] == "C":
                    amount_of_bezier = int((local_count + 1)/3)
                    for j in range(amount_of_bezier):
                        points = [last_position]
                        for k in range(3):
                            dx, dy = [float(j) for j in path_split[i+j*3+k+1].split(",")]
                            points.append(dx - dy*1j)
                            function_split[i+j*3+k+1] = "-"
                        cubic_bezier = f"{points[0]}*(1-t+{t_total})**3 + 3*{points[1]}*(t-{t_total})*(1-t+{t_total})**2 + 3*{points[2]}*(1-t+{t_total})*(t-{t_total})**2 + {points[3]}*(t-{t_total})**3"
                        function_split[i+(j+1)*3] = cubic_bezier
                        t_total += 1
                        bezier_last_control_point = points[2]
                        last_position = points[3]
                        # SAVE LAST TYPE OF CURVE USED
                        temp = path_split[i]
                # RELATIVE c
                elif path_split[i] == "c":
                    amount_of_bezier = int((local_count + 1)/3)
                    for j in range(amount_of_bezier):
                        points = [last_position]
                        for k in range(3):
                            dx, dy = [float(j) for j in path_split[i+j*3+k+1].split(",")]
                            points.append(last_position + dx - dy*1j)
                            function_split[i+j*3+k+1] = "-"
                        cubic_bezier = f"{points[0]}*(1-t+{t_total})**3 + 3*{points[1]}*(t-{t_total})*(1-t+{t_total})**2 + 3*{points[2]}*(1-t+{t_total})*(t-{t_total})**2 + {points[3]}*(t-{t_total})**3"
                        function_split[i+(j+1)*3] = cubic_bezier
                        t_total += 1
                        bezier_last_control_point = points[2]
                        last_position = points[3]
                        # SAVE LAST TYPE OF CURVE USED
                        temp = path_split[i]

                # ABSOLUTE S
                elif path_split[i] == "S":
                    amount_of_bezier = int((local_count + 1)/2)
                    for j in range(amount_of_bezier):
                        points = [last_position]
                        # CHECK CONTROL POSITION
                        if temp == "S" or temp == "s" or temp == "C" or temp == "c":
                            first_control_position = 2*last_position - bezier_last_control_point
                        else:
                            first_control_position = last_position
                        points.append(first_control_position)
                        for k in range(2):
                            dx, dy = [float(j) for j in path_split[i+j*2+k+1].split(",")]
                            points.append(dx - dy*1j)
                            function_split[i+j*2+k+1] = "-"
                        cubic_bezier = f"{points[0]}*(1-t+{t_total})**3 + 3*{points[1]}*(t-{t_total})*(1-t+{t_total})**2 + 3*{points[2]}*(1-t+{t_total})*(t-{t_total})**2 + {points[3]}*(t-{t_total})**3"
                        function_split[i+(j+1)*2] = cubic_bezier
                        t_total += 1
                        bezier_last_control_point = points[2]
                        last_position = points[3]
                        # SAVE LAST TYPE OF CURVE USED
                        temp = path_split[i]
                # RELATIVE s
                elif path_split[i] == "s":
                    amount_of_bezier = int((local_count + 1)/2)
                    for j in range(amount_of_bezier):
                        points = [last_position]
                        # CHECK CONTROL POSITION
                        if temp == "S" or temp == "s" or temp == "C" or temp == "c":
                            first_control_position = 2*last_position - bezier_last_control_point
                        else:
                            first_control_position = last_position
                        points.append(first_control_position)
                        for k in range(2):
                            dx, dy = [float(j) for j in path_split[i+j*2+k+1].split(",")]
                            points.append(last_position + dx - dy*1j)
                            function_split[i+j*2+k+1] = "-"
                        cubic_bezier = f"{points[0]}*(1-t+{t_total})**3 + 3*{points[1]}*(t-{t_total})*(1-t+{t_total})**2 + 3*{points[2]}*(1-t+{t_total})*(t-{t_total})**2 + {points[3]}*(t-{t_total})**3"
                        function_split[i+(j+1)*2] = cubic_bezier
                        t_total += 1
                        bezier_last_control_point = points[2]
                        last_position = points[3]
                        # SAVE LAST TYPE OF CURVE USED
                        temp = path_split[i]
                
                # ABSOLUTE Q
                elif path_split[i] == "Q":
                    amount_of_bezier = int((local_count + 1)/2)
                    for j in range(amount_of_bezier):
                        points = [last_position]
                        for k in range(2):
                            dx, dy = [float(j) for j in path_split[i+j*2+k+1].split(",")]
                            points.append(dx - dy*1j)
                            function_split[i+j*2+k+1] = "-"
                        quad_bezier = f"{points[0]}*(1-t+{t_total})**2 + 2*{points[1]}*(t-{t_total})*(1-t+{t_total}) + {points[2]}*(t-{t_total})**2" 
                        function_split[i+(j+1)*2] = quad_bezier
                        t_total += 1
                        bezier_last_control_point = points[1]
                        last_position = points[2]
                        # SAVE LAST TYPE OF CURVE USED
                        temp = path_split[i]
                # RELATIVE q
                elif path_split[i] == "q":
                    amount_of_bezier = int((local_count + 1)/2)
                    for j in range(amount_of_bezier):
                        points = [last_position]
                        for k in range(2):
                            dx, dy = [float(j) for j in path_split[i+j*2+k+1].split(",")]
                            points.append(last_position + dx - dy*1j)
                            function_split[i+j*2+k+1] = "-"
                        quad_bezier = f"{points[0]}*(1-t+{t_total})**2 + 2*{points[1]}*(t-{t_total})*(1-t+{t_total}) + {points[2]}*(t-{t_total})**2"
                        function_split[i+(j+1)*2] = quad_bezier
                        t_total += 1
                        last_position = points[2]
                        # SAVE LAST TYPE OF CURVE USED
                        temp = path_split[i]
                
                # ABSOLUTE T
                elif path_split[i] == "T":
                    amount_of_bezier = local_count + 1
                    for j in range(amount_of_bezier):
                        points = [last_position]
                        if temp == "Q" or temp == "q" or temp == "T" or temp == "t":
                            control_position = 2*last_position - bezier_last_control_point
                        else:
                            control_position = last_position
                        points.append(control_position)
                        dx, dy = [float(j) for j in path_split[i+j+1].split(",")]
                        points.append(dx - dy*1j)
                        quad_bezier = f"{points[0]}*(1-t+{t_total})**2 + 2*{points[1]}*(t-{t_total})*(1-t+{t_total}) + {points[2]}*(t-{t_total})**2" 
                        function_split[i+j+1] = quad_bezier
                        t_total += 1
                        bezier_last_control_point = points[1]
                        last_position = points[2]
                        # SAVE LAST TYPE OF CURVE USED
                        temp = path_split[i]
                        
                # RELATIVE t
                elif path_split[i] == "t":
                    amount_of_bezier = local_count + 1
                    for j in range(amount_of_bezier):
                        points = [last_position]
                        if temp == "Q" or temp == "q" or temp == "T" or temp == "t":
                            control_position = 2*last_position - bezier_last_control_point
                        else:
                            control_position = last_position
                        points.append(control_position)
                        dx, dy = [float(j) for j in path_split[i+j+1].split(",")]
                        points.append(last_position + dx - dy*1j)
                        quad_bezier = f"{points[0]}*(1-t+{t_total})**2 + 2*{points[1]}*(t-{t_total})*(1-t+{t_total}) + {points[2]}*(t-{t_total})**2"
                        function_split[i+j+1] = quad_bezier
                        t_total += 1
                        bezier_last_control_point = points[1]
                        last_position = points[2]
                        # SAVE LAST TYPE OF CURVE USED
                        temp = path_split[i]
    
            # CHECK END OF PATH IF IT'S CLOSED OR NOT, TO ENSURE NO NOISE
            if i == (len(path_split) - 1):
                # CLOSED PATH
                if path_split[i] in closed_chars:
                    function_split[i] = "-"
                function_split.pop(0)
                xfinal, yfinal = function_split[0].real, function_split[0].imag
                line_function = f"{xfinal + yfinal*1j - last_position}*(t-{t_total}) + {last_position}"
                function_split.append(line_function)
                t_total += 1
                last_position = xfinal + yfinal*1j

        # DELETE "-" AND SAVE THE FUNCTION
        function_split = [i for i in function_split if i != "-"]
        function_split.pop(0)
        # with open(f"{namefile}_path.txt", "w") as w_file:
        #     w_file.write(str(function_split))
        #     w_file.close()

        return function_split, t_total

# EVALUATE THE FUNCTION SAVED BY THE SVG PARSER 
def evaluate_svg(t, function, b):
    # EVERY FUNCTION GOES FROM 0 TO 1 IN THE SVG
    for i in range(b):
        if i <= t <= i + 1:
            return eval(function[i])

# PARAMETERS OF THE FUNCTION
def params_svg(namefile):
    function, b = open_svg(namefile)
    a = 0
    return function, a, b