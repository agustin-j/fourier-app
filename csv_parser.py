import numpy as np
import csv

# CSV FORMAT: type_of_function, start of period, end of period, interval to calculate, function
# type_of_function: real or complex (normal fourier graph or a curve for short)
# function: can use numpy expresion inside of csv

# OPEN CORRECT CSV FORMAT FOR THE APP AND PARSE IT
def open_csv(path, index_of_function):
    type_of_function = []
    parsed_function = []
    a = []
    b = []
    interval = []
    with open(f"{path}.csv", newline="") as csv_file:
        lines = csv.reader(csv_file)
        for line in lines:
            type_of_function.append(line[0])
            parsed_function.append(line[1])
            a.append(line[2])
            b.append(line[3])
            interval.append(line[4])
    
    return type_of_function[index_of_function], parsed_function[index_of_function], eval(a[index_of_function]), eval(b[index_of_function]), eval(interval[index_of_function])

def evaluate_curve(t, function, b):
    return eval(function)