import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot(rho, title='Tomography'):
	real_rho = np.real(rho)
	imag_rho = np.imag(rho)

	x = [0,0,1,1]
	y = [0,1,0,1]
	z = [0,0,0,0]
	z_real = [real_rho[0,0],real_rho[0,1],real_rho[1,0],real_rho[1,1]]
	z_imag = [imag_rho[0,0],imag_rho[0,1],imag_rho[1,0],imag_rho[1,1]]

	fig = plt.figure(figsize=(8, 3.5))
	ax1 = fig.add_subplot(121, projection='3d')
	ax2 = fig.add_subplot(122, projection='3d')

	ax1.bar3d(x,y,z,1,1,z_real,color='#ff000088',edgecolor='#00000099')
	ax2.bar3d(x,y,z,1,1,z_imag,color='#0000ff88',edgecolor='#00000099')

	ax1.set_zlim(-1.3,1.3)
	ax2.set_zlim(-1.3,1.3)

	ax1.set_xticks([0.5,1.5])
	ax1.set_xticklabels([r'$\left|0\right\rangle$',r'$\left|1\right\rangle$'],
						fontdict={'fontsize': 10})
	ax1.set_yticks([0.5,1.5])
	ax1.set_yticklabels([r'$\left|0\right\rangle$',r'$\left|1\right\rangle$'],
						fontdict={'fontsize': 10})
	ax2.set_xticks([0.5,1.5])
	ax2.set_xticklabels([r'$\left|0\right\rangle$',r'$\left|1\right\rangle$'],
						fontdict={'fontsize': 10})
	ax2.set_yticks([0.5,1.5])
	ax2.set_yticklabels([r'$\left|0\right\rangle$',r'$\left|1\right\rangle$'],
						fontdict={'fontsize': 10})

	ax1.set_title(r'$Re(\rho)$',fontsize=15)
	ax2.set_title(r'$Im(\rho)$',fontsize=15)
	fig.suptitle(title, fontsize=20)
	plt.subplots_adjust(top=0.8)
	plt.show()

def population(state, ground, saturated):
	pop = 0
	length = 450-320
	for vg,vsat,vstate in zip(ground[320:440],saturated[320:440],state[320:440]):
		pop = pop+0.5/length*(((vstate-vg)/(vsat-vg)))
	return pop

def density_matrix(X):
	'''
	This will assume that the qubit is in a pure state, i.e, S0 = 1
	X is the quadrature corrected (rotated) values with
	X[0] as ground
	X[1] as saturated
	X[2] as measurement after state preparation
	X[3] as measurement after state preparation with a pi/2 pulse
	X[4] as measurement after state preparation with a 90 degree phase shifted pi/2 pulse
	'''
	S = [1]
	S.append(1-2*population(X[3],X[0],X[1]))
	S.append(1-2*population(X[4],X[0],X[1]))
	S.append(1-2*population(X[2],X[0],X[1]))

	sigma = np.array([
		[[1,0],[0,1]],
		[[0,1],[1,0]],
		[[0,-1j],[1j,0]],
		[[1,0],[0,-1]]
	])
	
	rho = np.array([[0j,0j],[0j,0j]])
	for s,sig in zip(S,sigma):
		rho += 0.5*s/S[0]*sig

	return rho

datadir = 'D:/data/20180201-CooldownDataWithQubitInTwoPortCavity/20180212/164454_tomography_8x(pi-pi)/'
data = np.loadtxt(datadir+'164454_tomography_8x(pi-pi).dat', unpack=True)

no = 5
test = 0
time = np.array_split(data[0],no)[0]/1e-6
X = np.array_split(data[1],no)
Y = np.array_split(data[2],no)
R = np.array_split(data[3],no)

# plt.plot(X[test], label="X")
# plt.plot(Y[test], label="Y")
# plt.grid()
# plt.legend()
# plt.show()

for i in range(no):
	X_cal = X[i]-np.average(X[i][1100:1200])
	Y_cal = Y[i]-np.average(Y[i][1100:1200])
	steady_X= np.average(X_cal[800:880])
	steady_Y= np.average(Y_cal[800:880])
	rot = np.arctan2(steady_Y,steady_X)
	# print(rot)
	X[i] = X_cal*np.cos(rot) + Y_cal*np.sin(rot)
	X[i] = X[i]/np.average(X[i][800:880])
	Y[i] = -1*X_cal*np.sin(rot) + Y_cal*np.cos(rot)

rho = density_matrix(X)
print rho
# plot(rho,title=r'Preparation : $90^\circ$ shifted $\pi/2$ pulse')
plot(rho,title=r'Prepration : $\left|0\right\rangle$ 8x($\pi-\pi$)')