import Tkinter
import tkFileDialog
import matplotlib.pyplot as plt

### get file name ###
root = Tkinter.Tk()
root.withdraw()
file_path = tkFileDialog.askopenfilename()

### read data ###
x_data = []
y_data = []
with open(file_path,'r') as f:
    for line in f:
        items = line.split()
        time = float(items[0])
        value = float(items[1])
        x_data.append(time)
        y_data.append(value)

plt.plot(x_data, y_data)
plt.show()
