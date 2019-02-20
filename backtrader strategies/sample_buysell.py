from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime
import os.path
import sys
import backtrader as bt # Importar todas las herramientas de backtrader
import quandl


class DoubleDownStrategy(bt.Strategy):

	def log(self, txt, dt=None):
		dt = dt or self.datas[0].datetime.date(0)
		print('%s, %s' % (dt.isoformat(), txt))

	def __init__(self):
		self.dataclose = self.datas[0].close

		# Para mantener las ordenes no ejecutadas
		self.order = None

	def notify_order(self, order):
		if order.status in [order.Submitted, order.Accepted]:
			return

		if order.status in [order.Completed]:
			if order.isbuy():
				self.log('BUY EXECUTED, %.2f' % order.executed.price)
			elif order.issell():
				self.log('SELL EXECUTED, %.2f' % order.executed.price)

			self.bar_executed = len(self)

		elif order.status in [order.Canceled, order.Margin, order.Rejected]:
			self.log('Order Canceled/Margin/Rejected')

		self.order = None

	def next(self):
		self.log('Close, %.2f' % self.dataclose[0])
	# Si hay una compraventa pendiente no puedo hacer otra
		if self.order:
			return

	# Si no tengo nada adquirido
		if not self.position:
			if self.dataclose[0] < self.dataclose[-1]:
				if self.dataclose[-1] < self.dataclose[-2]:
					self.log('BUY CREATE, %.2f' % self.dataclose[0])
					self.order = self.buy()

		else:
            # Ya hemos adquirido algo
			if len(self) >= (self.bar_executed + 5):
				self.log('SELL CREATE, %.2f' % self.dataclose[0])
				self.order = self.sell()






if __name__ == '__main__':
	cerebro = bt.Cerebro()

    # Registrar estrategia
	cerebro.addstrategy(DoubleDownStrategy)

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
