import easygopigo3 as g
from typing import Optional, Callable
from enum import IntEnum
from monitored import MonitoredState
from blinkers import SideBlinkers
from color import Color
from constante import *

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

    
class LedBlinkers(SideBlinkers):
    
    def __init__(self, robot: 'Robot'):
        self.__robot: 'Robot' = robot
        super().__init__(self.__left_off_state_generator, self.__left_on_state_generator, self.__right_off_state_generator, self.__right_on_state_generator)

    def __left_off_state_generator(self):
        off_state: MonitoredState = MonitoredState()
        off_state.add_entering_action(lambda: self.__robot.close_led_blinkers(SideBlinkers.Side.LEFT))
        return off_state
    
    def __left_on_state_generator(self):
        on_state: MonitoredState = MonitoredState()
        on_state.add_entering_action(lambda: self.__robot.open_led_blinkers(SideBlinkers.Side.LEFT))
        return on_state
    
    def __right_off_state_generator(self):
        off_state: MonitoredState = MonitoredState()
        off_state.add_entering_action(lambda: self.__robot.close_led_blinkers(SideBlinkers.Side.RIGHT))
        return off_state
    
    def __right_on_state_generator(self):
        on_state: MonitoredState = MonitoredState()
        on_state.add_entering_action(lambda: self.__robot.open_led_blinkers(SideBlinkers.Side.RIGHT))

        return on_state
    

class EyeBlinkers(SideBlinkers):

    def __init__(self, robot : 'Robot'):
        self.__robot: 'Robot' = robot
        super().__init__(self.__left_off_state_generator, self.__left_on_state_generator, self.__right_off_state_generator, self.__right_on_state_generator)
    
    def set_colors(self, side: SideBlinkers.Side, color: Color):
        self.__robot.set_eye_colors(side, color)

    def __left_off_state_generator(self):
        off_state: MonitoredState = MonitoredState()
        off_state.add_entering_action(lambda: self.__robot.close_eyes(SideBlinkers.Side.LEFT))
        return off_state
    
    def __left_on_state_generator(self):
        on_state: MonitoredState = MonitoredState()
        on_state.add_entering_action(lambda: self.__robot.open_eyes(SideBlinkers.Side.LEFT))
        return on_state
    
    def __right_off_state_generator(self):
        off_state: MonitoredState = MonitoredState()
        off_state.add_entering_action(lambda: self.__robot.close_eyes(SideBlinkers.Side.RIGHT))
        return off_state
    
    def __right_on_state_generator(self):
        on_state: MonitoredState = MonitoredState()
        on_state.add_entering_action(lambda: self.__robot.open_eyes(SideBlinkers.Side.RIGHT))
        return on_state


class Robot:
    
    class GpgServo:
        def __init__(self, gpg, servo_port: str, max_angle: int, offset: int) -> None:
            self.__gpg = gpg
            self.__offset: int = offset
            self.__max_angle: int = max_angle
            self.__min_angle: int = -max_angle 
            self.__servo_control = self.__gpg.init_servo(port=servo_port)
            
            self.reset_servo()

        @property
        def servo_control(self):
            return self.__servo_control

        def move(self, angle: int):
            angle: int = self.__change_diff(angle)
            self.__servo_control.rotate_servo(angle)
            
        def __change_diff(self, angle: int):
            clamped_angle: int = self.__clamp_angle(angle)
            return -clamped_angle + 90 + self.__offset 
        
        def reset_servo(self):
            self.__servo_control.reset_servo()
            
        def __clamp_angle(self, angle: int):
            return max(self.__min_angle, min(angle, self.__max_angle))
        
    class RemoteKeyCode(IntEnum):
        NOT_PRESSED = 0
        UP = 1
        LEFT = 2
        OK = 3
        RIGHT = 4
        DOWN = 5
        ONE = 6
        TWO = 7
        THREE = 8
        FOUR = 9
        FIVE = 10
        SIX = 11
        SEVEN = 12
        EIGHT = 13
        NINE = 14
        STAR = 15
        ZERO = 16
        HASHTAG = 17    
    
    class DirectionKey(IntEnum):
        STOP = 0
        FORWARD = 1
        LEFT = 2
        RIGHT = 4
        BACKWARD = 5
        
    class EventType(IntEnum):
        ONREMOTEPRESS = 0
        ONREMOTERELEASE = 1

    def __init__(self):
        self.__remote_control_port = 'AD1'

        self.__gpg = None
        self.__eyes_blinkers: Optional[EyeBlinkers] = None
        self.__led_blinkers: Optional[LedBlinkers] = None
        self.__camera_servo: Optional[Robot.GpgServo] = None
        self.__range_servo: Optional[Robot.GpgServo] = None
        self.__remote_control = None
        self.__range_finder = None
        self.__left_eye_color: Optional[Color] = None
        self.__right_eye_color : Optional[Color] = None
        self.__move_action: dict = {}
        self.__state_pressed = False
        self.__current_distance = 1
    
    def set_current_eye_color(self, side: SideBlinkers.Side, color: Color):
        if not isinstance(color, Color): 
            raise TypeError("color must be Color")
        if side not in (SideBlinkers.Side.LEFT, SideBlinkers.Side.RIGHT, SideBlinkers.Side.BOTH): 
            raise ValueError("side must be left, right or both")
        
        if side == SideBlinkers.Side.LEFT: 
            self.__left_eye_color = color  
        elif side == SideBlinkers.Side.RIGHT: 
            self.__right_eye_color = color           
        elif side == SideBlinkers.Side.BOTH: 
            self.__left_eye_color = color 
            self.__right_eye_color = color 

    def get_current_eye_color(self, side: SideBlinkers.Side) -> Color:
        if side not in (SideBlinkers.Side.LEFT, SideBlinkers.Side.RIGHT): 
            raise ValueError("side must be left, right")
        
        if side == SideBlinkers.Side.LEFT: 
            return self.__left_eye_color  
        elif side == SideBlinkers.Side.RIGHT: 
            return self.__right_eye_color
    
    @property
    def integrity(self) -> bool:
        try:
            self.__camera_servo = Robot.GpgServo(self.__gpg, 'SERVO1', R_15_CAMERA_SERVO_MAX_ANGLE, R_15_CAMERA_SERVO_OFFSET)
            self.__range_servo = Robot.GpgServo(self.__gpg, 'SERVO2', R_15_RANGE_SERVO_MAX_ANGLE, R_15_RANGE_SERVO_OFFSET)

            self.__remote_control = self.__gpg.init_remote(port=self.__remote_control_port)
            
            self.__range_finder = self.__gpg.init_distance_sensor()

            return not (self.__camera_servo.servo_control and self.__range_servo.servo_control  and self.__remote_control  and self.__range_finder) is None
        except:
            return False

    @property
    def instanciate(self) -> bool:
        try:
            self.__gpg = g.EasyGoPiGo3()
            
            self.__eyes_blinkers = EyeBlinkers(self)
            self.set_eye_colors(SideBlinkers.Side.BOTH, Color(Color.ColorBase.BLACK.value))
            
            self.__led_blinkers = LedBlinkers(self)
            
            self.__move_action = (
                self.__gpg.stop, 
                self.__gpg.forward, 
                self.__gpg.left,
                None, 
                self.__gpg.right, 
                self.__gpg.backward, 
            )
            
            return not self.__gpg is None
        except: 
            return False
        
    @property
    def current_distance(self) -> float:
        return self.__current_distance
    
    @property
    def range_servo(self):
        return self.__range_servo

        
    def open_led_blinkers(self, side : SideBlinkers.Side ) : 
        
        action = (
            lambda: self.__gpg.blinker_on(1),
            lambda: self.__gpg.blinker_on(0),
            lambda: (self.__gpg.blinker_on(0), self.__gpg.blinker_on(1))
        )
        action[side.value]()
        
    def close_led_blinkers(self, side : SideBlinkers.Side):
        
        action = (
            lambda: self.__gpg.blinker_off(1),
            lambda: self.__gpg.blinker_off(0),
            lambda: (self.__gpg.blinker_off(0), self.__gpg.blinker_off(1))
        )
        action[side.value]()
        
    def blink_led(self, params: LedBlinkerParams):        
        if len(params.get_kwargs()) == 0:
            self.__led_blinkers.blink(params.side, params.percent_on, params.begin_on)
        else:
            self.__led_blinkers.blink(params.side, params.percent_on, params.begin_on, **params.get_kwargs())
        
    def blink_eyes(self, params: EyeBlinkerParams):
        if len(params.get_kwargs()) == 0:
            self.__eyes_blinkers.blink(params.side, params.percent_on, params.begin_on)
        else:
            self.__eyes_blinkers.blink(params.side, params.percent_on, params.begin_on, **params.get_kwargs())
    
    def close_eyes(self, side: SideBlinkers.Side) -> None:
        action = (
            self.__gpg.close_left_eye,
            self.__gpg.close_right_eye,
            self.__gpg.close_eyes
        )
        action[side.value]()
        
    def open_eyes(self, side: SideBlinkers.Side) -> None:
        action = (
            self.__gpg.open_left_eye,
            self.__gpg.open_right_eye,
            self.__gpg.open_eyes
        )
        action[side.value]()
        
    def set_eye_colors(self, side: SideBlinkers.Side, color: Color):
        action = (
            lambda: (self.__gpg.set_left_eye_color(color.rgb), self.__gpg.open_left_eye()),
            lambda: (self.__gpg.set_right_eye_color(color.rgb), self.__gpg.open_right_eye()),
            lambda: (self.__gpg.set_left_eye_color(color.rgb), self.__gpg.set_right_eye_color(color.rgb), self.__gpg.open_eyes())
        )
        action[side.value]()
        self.set_current_eye_color(side, color)
    
    def stop_led_blinkers(self) -> None:
        self.__led_blinkers.turn_off(SideBlinkers.Side.BOTH)
    
    def stop_eye_blinkers(self) -> None:
        self.__eyes_blinkers.turn_off(SideBlinkers.Side.BOTH)
            
    def get_remote_key(self) -> RemoteKeyCode:
        return Robot.RemoteKeyCode(self.__remote_control.read())
    
    def get_state_remote_key(self) -> RemoteKeyCode:
        key = Robot.RemoteKeyCode(self.__remote_control.read())
        
        event = self.__process_state(key)
        if event == self.EventType.ONREMOTEPRESS:
            return key

        return Robot.RemoteKeyCode.NOT_PRESSED
    
    
    def move(self, direction: DirectionKey):
        action = self.__move_action[direction]
        if callable(action):
            action()

    def track(self):
        self.__eyes_blinkers.track()
        self.__led_blinkers.track()
        self.__update_current_distance()
    
    def __update_current_distance(self):
        self.__current_distance: float = self.__range_finder.read() /300

    def __process_state(self, key):
        """
        Processes the state based on the key value.
        Returns the event type if a valid event occurred, None otherwise.
        """
        if key != 0 and not self.__state_pressed:
            self.__state_pressed = True
            return self.EventType.ONREMOTEPRESS
        elif key == 0 and self.__state_pressed:
            self.__state_pressed = False
            return self.EventType.ONREMOTERELEASE
        
        return None