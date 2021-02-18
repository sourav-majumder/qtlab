import matplotlib.pyplot as pyplot
import easygui as esg
import numpy as np

# Browse for data file,
# Ask for filename, delimiter (default is ' '), frequency column, absolute column
esg.multenterbox
# Ask for formula to be used
# Skip the comment lines (done automatically)
np.loadtxt(filepath, delimiter=delimiter)