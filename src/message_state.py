from state import State
from conditional import Condition
from robot import Robot
from monitored import MonitoredState

class RobotState(MonitoredState):
    def __init__(self, robot: Robot, parameters:State.Parameters = None):
        super().__init__(parameters)
        self._robot: Robot = robot
        
    @property
    def robot(self):
        return self._robot
        
    def _do_in_state_action(self) -> None:
        super()._do_in_state_action()
        self._robot.track()

class MessageState(RobotState): 
    def __init__(self,robot:Robot, message, parameters:State.Parameters = None): #Enum
        super().__init__(robot, parameters) 
        self.__message : str = message
        self.add_entering_action(lambda: print(self.__message))      
    
class RobotCondition(Condition):
    def __init__(self, robot: Robot, inverse = False): 
        super().__init__(inverse) 
        self._robot = robot
    
class InstanciateCheckCondition(RobotCondition): 
    def __init__(self, robot: Robot, inverse = False): 
        super().__init__(robot, inverse) 

    def _compare(self) -> bool:
        return self._robot.instanciate

class IntegrityCheckCondition(RobotCondition): 
    def __init__(self, robot: Robot, inverse = False): 
        super().__init__(robot, inverse) 

    def _compare(self) -> bool:
        return self._robot.integrity
           


