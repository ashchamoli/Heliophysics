import numpy as np
import matplotlib.pyplot as plt

#define the rest wavelengths
fraunhofer_lines ={
    "Ca II K": 393.37,
    "Ca II H": 396.85,
    "Mg I": 518.36,
    "Na D2": 589.00,
    "Fe I": 617.33,
    "H-alpha": 656.28
}
# simulation parameters
v= 30.0
c= 3e5

#calculate doppler shift
names= list(fraunhofer_lines.keys())
rest_lambdas =np.array(list(fraunhofer_lines.values()))
                       
 #doppler shift formula
shifts = rest_lambdas *(v/c)
shifted_lambdas = rest_lambdas +shifts

#plottingthe spectral line position
plt.figure(figsize=(10,6))
#plot rest lines vs shifted lines
for i , name in enumerate(names):

   rest_label= 'rest position'
   shifted_label= 'doppler shifted'

   #rest position
   plt.axvline(x=rest_lambdas[i], color='black', linestyle=(0, (3,3)), alpha=0.6, label=rest_label)
   #shifted position
   plt.axvline(x=shifted_lambdas[i], color='red', linestyle='-', linewidth=2, label=shifted_label)
#final plot
plt.xlim(350,700) #visible spectrum range
plt.ylim(0,1)
plt.title("simulation of solar fraunhofer line doppler shifts", fontsize=14, pad=15)
plt.yticks([])
plt.legend(loc="upper right")
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.show()
