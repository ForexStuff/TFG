import genetreec as gen
import sys

print('\n*/* Simulacion de ' + str(sys.argv[1]) + ' arboles y ' + str(sys.argv[2]) + ' iteraciones para el valor ' + str(sys.argv[3]))
print(' - Entrenamiento desde ' + str(sys.argv[4]) + ' hasta ' + str(sys.argv[5]))
print(' - Prueba desde        ' + str(sys.argv[6]) + ' hasta ' + str(sys.argv[7]) + '\n')

sim = gen.Simulate(int(sys.argv[1]),int(sys.argv[2]),sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7],)
sim.prepare()
sim.execute()
