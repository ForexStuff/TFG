from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime
import os.path
import sys
import backtrader as bt # Importar todas las herramientas de backtrader
import fix_yahoo_finance as yf


class DoubleDownStrategy(bt.Strategy):

	def log(self, txt, dt=None):
		dt = dt or self.datas[0].datetime.date(0)
		print('%s, %s' % (dt.isoformat(), txt))
		print(self.position)

	def __init__(self):
		self.dataclose = self.datas[0].close
		self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=5)
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
			if self.dataclose[0] > self.sma[0]:
				self.log('BUY CREATE, %.2f' % self.dataclose[0])
				self.order = self.buy(size = self.broker.get_cash()/self.datas[0].open)
		else:
			if self.dataclose[0] < self.sma[0]*1.05:
				self.log('SELL CREATE, %.2f' % self.dataclose[0])
				self.order = self.sell(size=self.position.size)





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


	# Crear un paquete de datos con YAHOO FINANCE API

	data = yf.download("BBVA", "2010-01-01", "2018-12-31")
	df = bt.feeds.PandasData(dataname = data)

    # Activar los datos en el cerebro
	cerebro.adddata(df)
    # Establecer dinero inicial    
	cerebro.broker.setcash(1000.0)
	cerebro.broker.setcommission(commission=0.001)

	print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
	cerebro.run()   # EJECUTAR BACKTESTING (AHORA MISMO, SIN NINGUNA ESTRATEGIA)
	print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

	cerebro.plot()


