from multiprocessing import Process
import matplotlib.pyplot as plt

def plot_graph(*args):
	plt.figure(figsize = (8,3))
	plt.clf()
	for data in args:
		plt.plot(data)
	plt.show()

p = Process(target=plot_graph, args=([1, 2, 3],))
p.start()

print 'yay'
print 'computation continues...'
print 'that rocks.'

print 'Now lets wait for the graph be closed to continue...:'