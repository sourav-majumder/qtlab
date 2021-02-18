import numpy as np
import matplotlib.pyplot as plt

def volt(dBm):
	return np.sqrt(50*1e-3*(10**(dBm/10)))

data = np.loadtxt('D:/data/20180607/164237_drag_cal_correct/164237_drag_cal_correct.dat', unpack=True)

no = 55
test = 45

time = np.array_split(data[0],no)[0]/1e-6
X = np.array_split(data[1],no)
Y = np.array_split(data[2],no)
R = np.array_split(data[3],no)

plt.plot(X[test], label="X")
plt.plot(Y[test], label="Y")
plt.grid()
plt.legend()
plt.show()

for i in range(no):
	X_cal = X[i]-np.average(X[i][900:999])
	Y_cal = Y[i]-np.average(Y[i][900:999])
	steady_X= np.average(X_cal[750:800])
	steady_Y= np.average(Y_cal[750:800])
	rot = np.arctan2(steady_Y,steady_X)
	# print(rot)
	X[i] = X_cal*np.cos(rot) + Y_cal*np.sin(rot)
	X[i] = X[i]/np.average(X[i][750:800])
	Y[i] = -1*X_cal*np.sin(rot) + Y_cal*np.cos(rot)

# plt.plot(X2[0]-X2[-1])
# plt.show()
# plt.imshow([((s-X2[-1])/(X2[0]-X2[-1])) for s in X2], aspect='auto' )
# plt.plot(Y[test], label="Y")
# plt.grid()
# plt.legend()
# plt.show()

for x in X[-5:]:
	plt.plot(x)
plt.show()


# area = np.sum([s[240:400] for s in X],1)
# delay = np.array([s[0]*4.4*1e-9 for s in delay])
# print(area[np.argmax(area)])
# plt.plot(delay/1e-6,area)
# plt.xlabel('Pulse length (us)')
# plt.ylabel('Area')
# plt.grid()


def pop_calculate(left,right, plot=False):
	X2 = [s[left:right] for s in X]
	print len(X2[0])
	

	Population = np.zeros(no)

	for i in range(no):
		print i/5
		ground = X2[0+int(i/5)*5]
		exited = X2[1+int(i/5)*5]
		for j in range(len(X2[0])):
			Population[i] = Population[i]+((1/float(len(X2[0])))*((X2[i][j]-ground[j])/(exited[j]-ground[j])))
	# return Population
	plt.plot(Population)
	plt.plot(np.repeat(0.5, len(Population)))
	plt.show()
	return
	
pop = pop_calculate(210,250,True)
print pop
# pops = []
# fits = []
# taus = []
# raw = open('raw.dat','w')
# fitf = open('fit.dat','w')
# for left in range(260, 350):
# 	pop, fit, tau = tau_fit(left, 400)
# 	taus.append(tau)
# 	for popi, fiti in zip(pop, fit):
# 		raw.write('%f\n'%popi)
# 		fitf.write('%f\n'%fiti)
# fitf.close()
# raw.close()
# plt.plot(taus)
# plt.show()
# 	# pops.append(pop)
# 	# taus.append(tau)
# 	# for right in range(360, 700, 10):
# 	# 	taus[-1].append(tau_fit(left, right))
# # plt.imshow(pops, aspect='auto', extent=(0, 22, 350, 240))
# # plt.figure(2)
# # plt.imshow(taus, aspect='auto', extent=(0, 22, 350, 240))
# # plt.show()

# # plt.title('Two tone spectroscopy ( Measurement power -75dBm at the cable)')
# # plt.imshow(R, aspect='auto',extent=[time[0], time[-1], delay[-1][0], delay[0][0]], cmap = 'jet')
# # plt.xlabel('Drive Frequency (GHz)')
# # plt.ylabel('Drive Power(dBm)')
# # plt.colorbar()
# plt.show()