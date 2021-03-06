'''
trends module
'''

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Limits:
   def __init__(self, data, lg, cn, ba, offLine, stock=""):
      
      self.data = data
      self.lg = lg
      self.cn = cn
      self.ba = ba

      self.hi = 0
      self.lo = 1
      self.op = 2
      self.cl = 3
      self.vl = 4
      self.bl = 5
      self.sH = 6
      self.sL = 7
      self.dt = 8
      
      self.offLine = offLine
      
      self.openBuyBars = int(data['profileTradeData']['openBuyBars'])
      self.closeBuyBars = int(data['profileTradeData']['closeBuyBars'])
      self.openSellBars = int(data['profileTradeData']['openSellBars'])
      self.closeSellBars = int(data['profileTradeData']['closeSellBars'])
      self.tradingDelayBars = int(data['profileTradeData']['tradingDelayBars'])
      self.doRangeTradeBars = int(data['profileTradeData']['doRangeTradeBars'])
      self.doHiLoSeq = int(data['profileTradeData']['doHiLoSeq'])
      self.doExecuteOnOpen = int(data['profileTradeData']['doExecuteOnOpen'])
      self.aggressiveOpen = int(data['profileTradeData']['aggressiveOpen'])
      self.aggressiveClose = int(data['profileTradeData']['aggressiveClose'])
      self.aggressiveOpenPct = float(data['profileTradeData']['aggressiveOpenPct'])
      self.aggressiveClosePct = float(data['profileTradeData']['aggressiveClosePct'])
      self.doOpensCloses = int(data['profileTradeData']['doOpensCloses'])
      self.useAvgBarLimits = int(data['profileTradeData']['useAvgBarLimits'])

      self.higherHighs = self.higherCloses = 0
      self.lowerHighs = self.lowerCloses = 0
      self.lowerLows = self.lowerOpens = 0
      self.higherLows = self.higherOpens = 0
      self.hiValues = []
      self.loValues = []
      
      self.openBuyLimit = 0.0
      self.closeBuyLimit = 0.0
      self.highestcloseBuyLimit = 0.0
      self.lowestcloseBuyLimit = 0.0
      self.highestcloseSellLimit = 0.0
      self.lowestcloseSellLimit = 99999999.999999
      self.openSellLimit = 0.0
      self.closeSellLimit = 0.0
      self.rangeHi = 0.0
      self.rangeLo = 0.0
      self.stock = stock

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def setRangeLimits(self, barChart, bar):

      if not self.doRangeTradeBars:
         return
         
      if bar < self.doRangeTradeBars:
         return

      self.lg.debug("\nRange values...")
      
      if self.setOpenCloseHiLoValues(barChart, bar, self.doRangeTradeBars):
         self.setOpenCloseHiLoConditions(self.doRangeTradeBars)

      # Use Hi and Los or open closes for determining range
      if self.doOpensCloses:
         self.rangeHi = self.getHighestCloseOpenPrice(self.doRangeTradeBars)
         self.rangeLo = self.getLowestCloseOpenPrice(self.doRangeTradeBars)
         self.lg.debug("Range limits using Open Closes ")
      
      if self.doHiLoSeq:
         self.rangeHi = self.getHighestHiLoPrice(self.doRangeTradeBars)
         self.rangeLo = self.getLowestHiLoPrice(self.doRangeTradeBars)
         self.lg.debug("Range limits using Hi Los ")
                        
         self.lg.debug("Range limits: " + str(self.rangeHi) + " " + str(self.rangeLo)+ "\n")
               
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def setAvgBarLenOpenBuyLimit(self, barChart):

      avgBarLen = self.ba.getAvgBarLen()
      
      # Tighten up the limit when profit has been taken
      if self.quickProfitCtr:
         avgBarLen = avgBarLen / self.quickProfitCtr
         
      self.openBuyLimit = self.cn.getCurrentAsk(self.stock) + avgBarLen
      
      print ("AvgBarLen: setOpenBuyLimit: " + str(self.openBuyLimit))
         
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def setAvgBarLenOpenSellLimit(self, barChart, bar):

      avgBarLen = self.ba.getAvgBarLen()

      # Tighten up the limit when profit has been taken
      if self.quickProfitCtr:
         avgBarLen = avgBarLen / self.quickProfitCtr

      self.openSellLimit = self.cn.getCurrentBid(self.stock) + avgBarLen
      
      print ("AvgBarLen: setOpenSellLimit: " + str(self.openSellLimit))
         
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def setAvgBarLenCloseBuyLimit(self, barChart, bar):

      avgBarLen = self.ba.getAvgBarLen()

      if self.ba.getBarsInPosition() > 1:
         avgBarLen /= 2.0
      
      print ("\navgBarLen: " + str(avgBarLen))
      print ("previous buy limit: " + str(self.closeBuyLimit))
      #print ("getCurrentAsk() " + str(self.cn.getCurrentAsk(self.stock)))

      if self.ba.getBarsInPosition() == 0:
         self.closeBuyLimit = self.cn.getCurrentAsk(self.stock) - avgBarLen
      
      # only raise the limit
      #if self.closeBuyLimit == 0.0:
      #   self.closeBuyLimit = self.cn.getCurrentAsk(self.stock) - avgBarLen
      elif self.closeBuyLimit < self.cn.getCurrentAsk(self.stock) - avgBarLen:
         self.closeBuyLimit = self.cn.getCurrentAsk(self.stock) - avgBarLen
      
      print ("\nAvgBarLen: setCloseBuyLimit: " + str(self.closeBuyLimit))
         
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def setAvgBarLenCloseSellLimit(self, barChart, bar):

      avgBarLen = self.ba.getAvgBarLen()

      if self.ba.getBarsInPosition() > 1:
         avgBarLen /= 2.0
        
      print ("\navgBarLen: " + str(avgBarLen))
      print ("previous sell limit: " + str(self.closeSellLimit))
      #print ("getCurrentBid() " + str(self.cn.getCurrentBid(self.stock)))

      if self.ba.getBarsInPosition() == 0:
         self.closeSellLimit = self.cn.getCurrentBid(self.stock) + avgBarLen
      # only lower the limit
      #if self.closeSellLimit == 0.0:
      #   self.closeSellLimit = self.cn.getCurrentBid(self.stock) + avgBarLen
      elif self.closeSellLimit > self.cn.getCurrentBid(self.stock) + avgBarLen:
         self.closeSellLimit = self.cn.getCurrentBid(self.stock) + avgBarLen
      
      print ("\nAvgBarLen: setCloseSellLimit: " + str(self.closeSellLimit))
         
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def setOpenBuyLimit(self, numBars):

      if self.doHiLoSeq:
         if self.aggressiveOpen:
            self.openBuyLimit = self.getLowestHiPrice(numBars)
            self.lg.debug("AGR HiLo: setOpenBuyLimit to the lowest hi ")
         else:
            self.openBuyLimit = self.getHighestHiPrice(numBars)
            self.lg.debug("HiLo: setOpenBuyLimit to the highest hi ")
      
      elif self.doExecuteOnOpen:
         if self.aggressiveOpen:
            self.openBuyLimit = self.getLowestClosePrice(numBars)
            self.lg.debug("AGR doExecuteOnOpen: setOpenBuyLimit to the lowest open ")
         else:
            self.openBuyLimit = self.getHighestClosePrice(numBars)
            self.lg.debug("doExecuteOnOpen: setOpenBuyLimit to the highest open")
          
      else:
         self.openBuyLimit = self.getHighestHiPrice(self.openBuyBars)
         self.lg.debug("setOpenBuyLimit default")
            
      self.lg.debug(str(self.openBuyLimit))

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def setOpenSellLimit(self, numBars):

      if self.doHiLoSeq:
         if self.aggressiveOpen:
            self.openSellLimit = self.getHighestLoPrice(numBars)
            self.lg.debug ("AGR HiLo: setOpenSellLimit to the highest lo ")
         else:
            self.openSellLimit = self.getLowestLoPrice(numBars)
            self.lg.debug ("HiLo: setOpenSellLimit to the lowest lo ")

      elif self.doExecuteOnOpen:
         if self.aggressiveOpen:
            #self.openSellLimit = self.getHighestOpenPrice(numBars)
            self.openSellLimit = self.getHighestClosePrice(numBars)
            self.lg.debug ("AGR doExecuteOnOpen: setOpenSellLimit to the highest open ")
         else:
            #self.openSellLimit = self.getLowestOpenPrice(numBars)
            self.openSellLimit = self.getLowestClosePrice(numBars)
            self.lg.debug ("doExecuteOnOpen: setOpenSellLimit to the lowest open ")
         
      else:
         self.openSellLimit = self.getLowestLoPrice(numBars)
         self.lg.debug("setOpenSellLimit default")
         
      self.lg.debug(str(self.openSellLimit))
      
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def setCloseBuyLimit(self, numBars):
   
      if self.doHiLoSeq:
         if self.aggressiveClose:
            self.closeBuyLimit = self.getHighestLoPrice(numBars)
            self.lg.debug ("AGR HiLo: setCloseBuyLimit to the highest lo")
         else:
            self.closeBuyLimit = self.getLowestLoPrice(numBars)
            self.lg.debug ("HiLo: setCloseBuyLimit to the lowest lo")
      
      elif self.doExecuteOnOpen:
         if self.aggressiveClose:
            self.closeBuyLimit = self.getHighestClosePrice(numBars)
            self.lg.debug ("AGR doExecuteOnOpen: setCloseBuyLimit to the highest close")
         else: 
            self.closeBuyLimit = self.getLowestClosePrice(numBars)
            self.lg.debug ("doExecuteOnOpen: setCloseBuyLimit to the lowest close")
      else:
         self.closeBuyLimit = self.getLowestLoPrice(numBars)
         self.lg.debug("setCloseBuyLimit default")

      self.lg.debug (str(self.closeBuyLimit))

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def setCloseSellLimit(self, numBars):

      if self.doHiLoSeq:
         if self.aggressiveClose:
            self.closeSellLimit = self.getLowestHiPrice(numBars)
            self.lg.debug("AGR HiLo: setCloseSellLimit to the lowest hi")
         else:
            self.closeSellLimit = self.getHighestHiPrice(numBars)
            self.lg.debug("HiLo: setCloseSellLimit to the highest hi")
      
      elif self.doExecuteOnOpen:
         if self.aggressiveClose:
            self.closeSellLimit = self.getLowestClosePrice(numBars)
            self.lg.debug("AGR doExecuteOnOpen: setCloseSellLimit to the lowest close")
         else:
            self.closeSellLimit = self.getHighestClosePrice(numBars)
            self.lg.debug("doExecuteOnOpen: setCloseSellLimit to the highest close")

      else:
         self.closeSellLimit = self.getHighestHiPrice(numBars)
         self.lg.debug("setCloseSellLimit default")

      self.lg.debug(str(self.closeSellLimit))
      
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def setOpenBuySellLimits(self, numBars, bar):
      
      if not numBars:
         self.setOpenBuyLimit(self.openBuyBars)
         self.setOpenSellLimit(self.openSellBars)
               
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def setCloseBuySellLimits(self, numBars, bar):
      
      if not numBars:
         self.setCloseBuyLimit(self.closeBuyBars)
         self.setCloseSellLimit(self.closeSellBars)
               
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def unsetCloseAvgBarLenLimits(self, barChart, bar):
   
      self.closeBuyLimit = 0.0
      self.closeSellLimit = 0.0
      
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def setAvgBarLenLimits(self, barChart, bar):
      
      self.setCloseAvgBarLenLimits(barChart, bar)
      
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def setCloseAvgBarLenLimits(self, barChart, bar):
      
      #self.setAvgBarLenOpenBuyLimit(barChart, bar)
      #self.setAvgBarLenOpenSellLimit(barChart, bar)
      self.setAvgBarLenCloseBuyLimit(barChart, bar)
      self.setAvgBarLenCloseSellLimit(barChart, bar)

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def isHigherHighs(self, numBars):
   
      highest = self.hiValues[0]
      
      print ("NUMBARS isHigherHighs: " + str(numBars))
      
      for n in range(1, numBars):
         hi = self.hiValues[n]
         if hi >= highest:
            return 0
         highest = hi
         
      return 1

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def isHigherLows(self, numBars): 
   
      lowest = self.lowValues[0]
      
      print ("NUMBARS isHigherLows: " + str(numBars))
      
      for n in range(1, numBars):
         lo = self.lowValues[n]
         if lo >= lowest:
            return 0
         lowest = lo

      return 1
            
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def isLowerHighs(self, numBars): 
   
      highest = self.hiValues[0]
      
      for n in range(1, numBars):
         hi = self.hiValues[n]
         if hi <= highest:
            return 0
         highest = hi

      return 1

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def isLowerLows(self, numBars):
   
      lowest = self.lowValues[0]
      
      for n in range(1, numBars):
         lo = self.lowValues[n]
         if lo <= lowest:
            return 0
         lowest = lo
         
      return 1
      
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def isLowerOpens(self, numBars):
    
      lowest = self.openValues[0]
      
      for n in range(1, numBars):
         lo = self.openValues[n]
         if lo <= lowest:
            return 0
         lowest = lo

      return 1

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def isLowerCloses(self, numBars):
   
      lowest = self.closeValues[0]
      
      for n in range(1, numBars):
         lo = self.closeValues[n]
         if lo <= lowest:
            return 0
         lowest = lo

      return 1

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def isHigherOpens(self, numBars):
                  
      highest = self.openValues[0]
      
      for n in range(1, numBars):
         hi = self.openValues[n]
         if hi >= highest:
            return 0
         highest = hi
         
      return 1

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def isHigherCloses(self, numBars):
   
      highest = self.closeValues[0]
      
      for n in range(1, numBars):
         hi = self.closeValues[n]
         if hi >= highest:
            return 0
         highest = hi
         
      return 1

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def getHighestClosePrice(self, numBars):
   
      price = self.closeValues[0]

      for n in range(numBars):
         if price < self.closeValues[n]:
            price = self.closeValues[n]

      return float(price)      

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def getHighestOpenPrice(self, numBars):
   
      price = self.openValues[0]
      
      for n in range(numBars):
         if price < self.openValues[n]:
            price = self.openValues[n]

      return float(price)      
      
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def getLowestOpenPrice(self, numBars):
      
      price = self.openValues[0]
      
      for n in range(numBars):
         if price > self.openValues[n]:
            price = self.openValues[n]

      return float(price)      

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def getLowestClosePrice(self, numBars):
   
      price = self.closeValues[0]
      
      for n in range(numBars):
         if price > self.closeValues[n]:
            price = self.closeValues[n]

      return float(price)      

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def getLowestLoPrice(self, numBars):
   
      price = self.lowValues[0]
      
      for n in range(numBars):
         if price > self.lowValues[n]:
            price = self.lowValues[n]

      return float(price)      
      
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def getHighestLoPrice(self, numBars):
   
      price = self.hiValues[0]
      
      for n in range(numBars):
         if price > self.lowValues[n]:
            price = self.lowValues[n]
      
      return float(price)      
      
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def getHighestHiPrice(self, numBars):
      
      price = self.hiValues[0]
      
      for n in range(numBars):
         if price < self.hiValues[n]:
            price = self.hiValues[n]
      
      return float(price)      

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def getLowestHiPrice(self, numBars):

      price = self.hiValues[0]
      
      for n in range(numBars):
         if price > self.hiValues[n]:
            price = self.hiValues[n]
      
      return float(price)      

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def getLowestHiLoPrice(self, numBars):

      loHigh = self.getLowestHiPrice(numBars)
      loLow = self.getLowestLoPrice(numBars)
      
      if loHigh < loLow:
         return loHigh
      else:
         return loLow

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def getHighestHiLoPrice(self, numBars):

      hiHigh = self.getHighestHiPrice(numBars)
      hiLow = self.getHighestLoPrice(numBars)
      
      if hiHigh > hiLow:
         return hiHigh
      else:
         return hiLow

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def getLowestCloseOpenPrice(self, numBars):

      loClose = self.getLowestClosePrice(numBars)
      loOpen = self.getLowestOpenPrice(numBars)
      
      if loClose < loOpen:
         return loClose
      else:
         return loOpen

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def getHighestCloseOpenPrice(self, numBars):

      hiClose = self.getHighestClosePrice(numBars)
      hiOpen = self.getHighestOpenPrice(numBars)
      
      if hiClose < hiOpen:
         return hiClose
      else:
         return hiOpen

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def resetLimits(self):
   
      self.openBuyBars = int(self.data['profileTradeData']['openBuyBars'])
      self.closeBuyBars = int(self.data['profileTradeData']['closeBuyBars'])
      self.openSellBars = int(self.data['profileTradeData']['openSellBars'])
      self.closeSellBars = int(self.data['profileTradeData']['closeSellBars'])
      self.tradingDelayBars = int(self.data['profileTradeData']['tradingDelayBars'])
      self.aggressiveOpen = int(self.data['profileTradeData']['aggressiveOpen'])
      self.aggressiveClose = int(self.data['profileTradeData']['aggressiveClose'])
      self.increaseCloseBars = int(self.data['profileTradeData']['increaseCloseBars'])
      self.increaseCloseBarsMax = int(self.data['profileTradeData']['increaseCloseBarsMax'])
      self.gainTrailStop = int(self.data['profileTradeData']['gainTrailStop'])
      self.closePositionFudge = float(self.data['profileTradeData']['closePositionFudge'])

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def setTradingDelayBars(self):
         
      if self.doRangeTradeBars > self.tradingDelayBars:
         self.tradingDelayBars = self.doRangeTradeBars
   
      if self.tradingDelayBars < self.getMaxNumWaitBars():
         self.tradingDelayBars = self.getMaxNumWaitBars()
   
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def getTradingDelayBars(self):
      
      return self.tradingDelayBars
            
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def getMaxNumWaitBars(self):
      
      maxNumBars = self.openBuyBars
      
      if self.openSellBars > maxNumBars:
         maxNumBars = self.openSellBars

      if self.closeBuyBars > maxNumBars:
         maxNumBars = self.closeBuyBars

      if self.closeSellBars > maxNumBars:
         maxNumBars = self.closeSellBars
      
      #if self.getTradingDelayBars() > maxNumBars:
      #   maxNumBars = self.getTradingDelayBars()
      
      return maxNumBars
            
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def setOpenCloseHiLoValues(self, barChart, bar, numBars):
                     
      self.openValues = [0.0] * numBars   
      self.closeValues = [0.0] * numBars  
      self.lowValues = [0.0] * numBars   
      self.hiValues = [0.0] * numBars  

      for n in range(numBars):
         self.openValues[n] = barChart[bar - n][self.op]
         self.closeValues[n] = barChart[bar - n][self.cl]
         self.lowValues[n] = barChart[bar - n][self.lo]
         self.hiValues[n] = barChart[bar - n][self.hi]

      # Remove before going live      
      for n in range(numBars):
         self.lg.debug ("open's: " + str(barChart[bar - n][self.op]))  
      
      for n in range(numBars):
         self.lg.debug ("close's: " + str(barChart[bar - n][self.cl]))         

      for n in range(numBars):
         self.lg.debug ("low's: " + str(barChart[bar - n][self.lo]))         

      for n in range(numBars):                
         self.lg.debug ("hi's: " + str(barChart[bar - n][self.hi]))

      return 1

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def setOpenCloseHiLoConditions(self, numBars):
   
      self.higherOpens = self.isHigherOpens(numBars)
      self.higherCloses = self.isHigherCloses(numBars)
      
      self.lowerOpens = self.isLowerOpens(numBars)
      self.lowerCloses = self.isLowerCloses(numBars)

      self.higherHighs = self.isHigherHighs(numBars)
      self.higherLows = self.isHigherLows(numBars)
      
      self.lowerHighs = self.isLowerHighs(numBars)
      self.lowerLows = self.isLowerLows(numBars)

      self.lg.debug("higherOpens: " + str(self.higherOpens) + " higherCloses: " + str(self.higherCloses))
      self.lg.debug("lowerOpens: " + str(self.lowerOpens) + " lowerCloses: " + str(self.lowerCloses))
      self.lg.debug("higherHighs: " + str(self.higherHighs) + " higherLows: " + str(self.higherLows))
      self.lg.debug("lowerHighs: " + str(self.lowerHighs) + " lowerLows: " + str(self.lowerLows))

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def setInitialClosePrices(self):

      hiLoDiff = self.openBuyLimit - self.openSellLimit
      
      #print ("Hi Lo diff: " + str(hiLoDiff) + "\n")
      
      if hiLoDiff == 0.0:
         hiLoDiff = 5.0

      if self.positionType == self.buy:
         posGain = self.cn.getCurrentAsk(self.stock) + hiLoDiff * self.profitPctTriggerBar
         posLoss = self.closeBuyLimit - self.closePositionFudge
      elif self.positionType == self.sell:
         posGain = self.cn.getCurrentBid(self.stock) - hiLoDiff * self.profitPctTriggerBar
         posLoss = self.closeSellLimit + self.closePositionFudge

      self.initialStopGain = posGain
      self.initialStopLoss = posLoss

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def getReversalLimit(self, top, op):
   
      if self.reversalPctTrigger == 0.0:
         return 0

      # Have to wait for the top to form so keep track of the top
      # top - open = length
      # length * reversal pct == price to sell

      # if not in a gain position get out
      if self.positionType == self.buy:
         if self.cn.getCurrentAsk(self.stock) < self.openPositionPrice:
            return 0
      elif self.positionType == self.sell:
         if self.cn.getCurrentBid(self.stock) > self.openPositionPrice:
            return 0

      if not self.revDirty:
         self.topIntraBar = top
         self.revDirty = 1
         self.barCounter = 0
         return 0

      if self.positionType == self.buy:
         if self.cn.getCurrentAsk(self.stock) >= top:
            self.topIntraBar = self.cn.getCurrentAsk(self.stock)
            self.barCounter = 0
            return

         #if top >= self.topIntraBar:
         #  self.topIntraBar = top
         #  return 0

         barLen = top - op

      elif self.positionType == self.sell:
         bottom = top
         if self.cn.getCurrentBid(self.stock) <= bottom:
            self.topIntraBar = self.cn.getCurrentBid(self.stock)
            self.barCounter = 0
            return

         #if top <= self.topIntraBar:
         #  self.topIntraBar = top
         #  return 0

         barLen = op - top

         print ("top " + str(top))
         print ("open " + str(op))
         print ("self.topIntraBar " + str(self.topIntraBar))
         #print ("currentPrice " + str(self.cn.getCurrentAsk(self.stock)))
         print ("self.barCounter " + str(self.barCounter))
         print ("self.hiLowBarMaxCounter " + str(self.hiLowBarMaxCounter))
         print ("self.revDirty " + str(self.revDirty))

      if self.barCounter < self.hiLowBarMaxCounter:
         # Wait 10 checks for top to be higher than previous
         print("BarCounter: " + str(self.barCounter))
         self.barCounter += 1
         return 0
      
      targetPrice = (barLen * self.reversalPctTrigger)
      sellPrice = top - targetPrice

      print ("barLen " + str(barLen))
      print ("targetPrice " + str(targetPrice))
      print ("sell price " + str(sellPrice))

      if self.positionType == self.buy:
         if sellPrice < self.cn.getCurrentAsk(self.stock):
            return 1
      elif self.positionType == self.sell:
         if sellPrice > self.cn.getCurrentBid(self.stock):
            return 1

      return 0
      





