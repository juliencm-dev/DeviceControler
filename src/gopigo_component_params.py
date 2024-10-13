from conditional import RemoteCondition
from robot import Robot
from blinkers import SideBlinkers
from typing import Callable, Optional

class RobotParams:
    def __init__(self, robot: 'Robot'):
        self._robot: 'Robot' = robot

class BlinkerParams(RobotParams): 
    def __init__(self, robot: 'Robot', side : SideBlinkers.Side, percent_on: float, begin_on: bool):
        super().__init__(robot)
        self.__side: SideBlinkers.Side = side
        self.__percent_on: float = percent_on
        self.__begin_on: bool = begin_on
        self.__cycle_duration: Optional[float] = None
        self.__total_duration: Optional[float] = None
        self.__n_cycles: Optional[int]= None
        self.__end_off: Optional[bool] = None
        
    @property
    def side(self) -> SideBlinkers.Side:
        return self.__side
    
    @property
    def n_cycles(self) -> SideBlinkers.Side:
        return self.__n_cycles
    
    @property
    def end_off(self) -> SideBlinkers.Side:
        return self.__end_off
    
    @property
    def cycle_duration(self) -> float:
        return self.__cycle_duration
   
    @property
    def total_duration(self) -> float:
        return self.__total_duration
   
    @property
    def percent_on(self) -> float:
        return self.__percent_on
       
    
    @property
    def begin_on(self) -> float:
        return self.__begin_on
    
    def get_kwargs(self) -> dict:
        options = {}
        
        if self.n_cycles :
            options["n_cycles"] = self.n_cycles
        
        if self.end_off :
            options["end_off"] = self.end_off
        
        if self.cycle_duration :
            options["cycle_duration"] = self.cycle_duration
        
        if self.total_duration :
            options["total_duration"] = self.total_duration
            
        return options

    
    def set_begin_on(self, begin_on):
        self.__begin_on = begin_on
    
    def set_cycle_duration(self, cycle_duration):
        self.__cycle_duration = cycle_duration
    
    def set_n_cycles(self, n_cycles):
        self.__n_cycles = n_cycles
    
    def set_end_off(self, end_off):
        self.__end_off = end_off
    
    def set_total_duration(self, total_duration):
        self.__total_duration = total_duration
    

class LedBlinkerParams(BlinkerParams):
    def __init__(self, robot: 'Robot', side : SideBlinkers.Side, percent_on: float = 0.5, begin_on: bool = True):
        super().__init__(robot, side, percent_on, begin_on)

    @property
    def action(self) -> Callable:
        return lambda: self._robot.blink_led(self)
    
    
class EyeBlinkerParams(BlinkerParams):
    def __init__(self, robot: 'Robot', side : SideBlinkers.Side, percent_on: float = 0.5, begin_on: bool = True):
        super().__init__(robot, side, percent_on, begin_on)

    @property
    def action(self) -> Callable:
        return lambda: self._robot.blink_eyes(self)

class MoveParams(RobotParams):
    def __init__(self, robot: Robot, key_code: Robot.RemoteKeyCode ): 
        self.__key_code = key_code
        self.__direction =  Robot.DirectionKey(key_code)
        
        super().__init__(robot)
    
    @property
    def action(self) -> Callable: 
        return lambda: self._robot.move(self.__direction)
    @property
    def condition(self): 
        return RemoteCondition(self._robot, self.__key_code)

class ServoParams(RobotParams): 
    def __init__(self, angle, robot:Robot): 
        self.__angle:int = angle
        super().__init__(robot)
        
    @property
    def action(self) -> Callable:
        return lambda: self._robot.range_servo.move(self.__angle)
    