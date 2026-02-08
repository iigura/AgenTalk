from abc import ABC, abstractmethod

class BaseMQ(ABC):
     @abstractmethod
     def getMessageReceiver(): pass

     @abstractmethod
     def getMessageSender(msg): pass

