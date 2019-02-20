from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime
import os.path
import sys
import backtrader as bt # Importar todas las herramientas de backtrader
import quandl


# Crear una estrategia
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Guarda una referencia de la linea de valores de cierre
        self.dataclose = self.datas[0].close

    def next(self):
        # Muestra por pantalla el valor de cierre
        self.log('Close, %.2f' % self.dataclose[0])





if __name__ == '__main__':
	cerebro = bt.Cerebro()

    # Registrar estrategia
	cerebro.addstrategy(TestStrategy)

    # Crear un paquete de datos con QUANDL
#	data = bt.feeds.Quandl(
# 		dataset='WFE',
#    		fromdate = datetime.datetime(2016,1,1),
#    		todate = datetime.datetime(2017,1,1),
#    		dataname='INDEXES_BMESPANISHEXCHANGESMADRID',
#		buffered=True,
#		apikey="qtQmrP3gPmpd5PKTYczp")

    # Crear un paquete de datos con YAHOO FINANCE
	data = bt.feeds.YahooFinanceCSVData(
		dataname='Data/SAN.csv',
		fromdate=datetime.datetime(2017, 8, 1),
		todate=datetime.datetime(2018, 8, 1),
	      	reverse=False)

    # Activar los datos en el cerebro
	cerebro.adddata(data)
    # Establecer dinero inicial    
	cerebro.broker.setcash(100000.0)

	print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
	cerebro.run()   # EJECUTAR BACKTESTING (AHORA MISMO, SIN NINGUNA ESTRATEGIA)
	print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
