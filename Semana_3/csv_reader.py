import csv
import os

def read_matrix_from_csv(file_path="matrix.csv"):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, file_path)
    matrix = []

    with open(file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            matrix.append([float(value) for value in row])
    
    return matrix