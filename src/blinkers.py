from enum import Enum
from typing import Callable, TYPE_CHECKING
from fsm import FiniteStateMachine
from conditional import ConditionalTransition
from monitored import MonitoredState, StateValueCondition, StateEntryDurationCondition

if TYPE_CHECKING:
    from monitored import MonitoredState

class Blinkers(FiniteStateMachine):
    """
    The Blinkers class represents a finite state machine for controlling blinkers.
    It provides methods for turning on, turning off, and blinking the blinkers.

    Args:
        off_state_generator (StateGenerator): A generator function that returns an instance of MonitoredState for the off state.
        on_state_generator (StateGenerator): A generator function that returns an instance of MonitoredState for the on state.

    Attributes:
        __off (MonitoredState): The off state.
        __off_duration (MonitoredState): The off duration state.
        __blink_off (MonitoredState): The blink off state.
        __blink_stop_off (MonitoredState): The blink stop off state.
        __on (MonitoredState): The on state.
        __on_duration (MonitoredState): The on duration state.
        __blink_on (MonitoredState): The blink on state.
        __blink_stop_on (MonitoredState): The blink stop on state.
        __blink_begin (MonitoredState): The blink begin state.
        __blink_stop_begin (MonitoredState): The blink stop begin state.
        __blink_stop_end (MonitoredState): The blink stop end state.

    """

    StateGenerator = Callable[[], 'MonitoredState']

    def __init__(self, off_state_generator: StateGenerator, on_state_generator: StateGenerator):
        layout: FiniteStateMachine.Layout = FiniteStateMachine.Layout()

        # Initialize states
        self.__off: MonitoredState = off_state_generator()
        self.__off_duration: MonitoredState = off_state_generator()
        self.__blink_off: MonitoredState = off_state_generator()
        self.__blink_stop_off: MonitoredState = off_state_generator()

        self.__on: MonitoredState = on_state_generator()
        self.__on_duration: MonitoredState = on_state_generator()
        self.__blink_on: MonitoredState = on_state_generator()
        self.__blink_stop_on: MonitoredState = on_state_generator()

        self.__blink_begin: MonitoredState = MonitoredState()
        self.__blink_stop_begin: MonitoredState = MonitoredState()
        self.__blink_stop_end: MonitoredState = MonitoredState()

        self.__on_states = [self.__on, self.__on_duration, self.__blink_on, self.__blink_stop_on]
        self.__off_states = [self.__off, self.__off_duration, self.__blink_off, self.__blink_stop_off, self.__blink_begin, self.__blink_stop_begin, self.__blink_stop_end]

        # Initialize transitions

        # TURN_ON/TURN_OFF DURATION
        self.__off_duration_condition = StateEntryDurationCondition(1, self.__off_duration)
        off_duration_transition = ConditionalTransition(self.__off_duration_condition)
        off_duration_transition.next_state = self.__on
        self.__off_duration.add_transition(off_duration_transition)

        self.__on_duration_condition = StateEntryDurationCondition(1, self.__on_duration)
        on_duration_transition = ConditionalTransition(self.__on_duration_condition)
        on_duration_transition.next_state = self.__off
        self.__on_duration.add_transition(on_duration_transition)

        # BLINK_BEGIN
        blink_begin_condition_on = StateValueCondition(True, self.__blink_begin)
        blink_begin_condition_off = StateValueCondition(False, self.__blink_begin)
        
        blink_being_on_transition = ConditionalTransition(blink_begin_condition_on)
        blink_being_on_transition.next_state = self.__blink_on

        blink_being_off_transition = ConditionalTransition(blink_begin_condition_off)
        blink_being_off_transition.next_state = self.__blink_off

        self.__blink_begin.add_transition(blink_being_on_transition)
        self.__blink_begin.add_transition(blink_being_off_transition)

        # INFINITE BLINK
        self.__blink_off_duration_condition = StateEntryDurationCondition(1, self.__blink_off)
        blink_off_duration_transition = ConditionalTransition(self.__blink_off_duration_condition)
        blink_off_duration_transition.next_state = self.__blink_on
        self.__blink_off.add_transition(blink_off_duration_transition)

        self.__blink_on_duration_condition = StateEntryDurationCondition(1, self.__blink_on)
        blink_on_duration_transition = ConditionalTransition(self.__blink_on_duration_condition)
        blink_on_duration_transition.next_state = self.__blink_off
        self.__blink_on.add_transition(blink_on_duration_transition)

        # BLINK_STOP_BEGIN
        self.__blink_stop_begin_duration_condition = StateEntryDurationCondition(1, self.__blink_stop_begin)
        blink_stop_begin_transition = ConditionalTransition(self.__blink_stop_begin_duration_condition)
        blink_stop_begin_transition.next_state = self.__blink_stop_end

        blink_stop_begin_value_condition_on = StateValueCondition(True, self.__blink_stop_begin)
        blink_stop_begin_value_condition_off = StateValueCondition(False, self.__blink_stop_begin)

        blink_stop_begin_value_transition_on = ConditionalTransition(blink_stop_begin_value_condition_on)
        blink_stop_begin_value_transition_on.next_state = self.__blink_stop_on

        blink_stop_begin_value_transition_off = ConditionalTransition(blink_stop_begin_value_condition_off)
        blink_stop_begin_value_transition_off.next_state = self.__blink_stop_off

        self.__blink_stop_begin.add_transition(blink_stop_begin_value_transition_on)
        self.__blink_stop_begin.add_transition(blink_stop_begin_value_transition_off)

        self.__blink_stop_off_condition = StateEntryDurationCondition(1, self.__blink_stop_off)
        blink_stop_off_transition = ConditionalTransition(self.__blink_stop_off_condition)
        blink_stop_off_transition.next_state = self.__blink_stop_on
        self.__blink_stop_off.add_transition(blink_stop_begin_transition)
        self.__blink_stop_off.add_transition(blink_stop_off_transition)

        self.__blink_stop_on_condition = StateEntryDurationCondition(1, self.__blink_stop_on)
        blink_stop_on_transition = ConditionalTransition(self.__blink_stop_on_condition)
        blink_stop_on_transition.next_state = self.__blink_stop_off
        self.__blink_stop_on.add_transition(blink_stop_begin_transition)
        self.__blink_stop_on.add_transition(blink_stop_on_transition)

        blink_stop_end_condition_off = StateValueCondition(True, self.__blink_stop_end)
        blink_stop_end_condition_on = StateValueCondition(False, self.__blink_stop_end)

        blink_stop_end_off_transition = ConditionalTransition(blink_stop_end_condition_off)
        blink_stop_end_off_transition.next_state = self.__off

        blink_stop_end_on_transition = ConditionalTransition(blink_stop_end_condition_on)
        blink_stop_end_on_transition.next_state = self.__on

        self.__blink_stop_end.add_transition(blink_stop_end_off_transition)
        self.__blink_stop_end.add_transition(blink_stop_end_on_transition)


        # Add states to layout
        layout.add_states([self.__off, self.__off_duration, self.__blink_off, self.__blink_stop_off, self.__on, self.__on_duration, self.__blink_on, 
                           self.__blink_stop_on, self.__blink_begin, self.__blink_stop_begin, self.__blink_stop_end])
        
        layout.initial_state = self.__off
        
        super().__init__(layout)


    @property
    def on(self) -> bool:
        """
        Returns True if the blinkers are currently in the on state, False otherwise.

        Returns:
            bool: True if the blinkers are on, False otherwise.
        """
        return self.current_applicative_state in self.__on_states

    @property
    def off(self) -> bool:
        """
        Returns True if the blinkers are currently in the off state, False otherwise.

        Returns:
            bool: True if the blinkers are off, False otherwise.
        """
        return self.current_applicative_state in self.__off_states

    def turn_on(self, **kwargs) -> None:
        """
        Turns on the blinkers.

        Args:
            **kwargs: Additional keyword arguments.
                - duration (float): The duration for which the blinkers should stay on.

        Raises:
            ValueError: If invalid arguments are provided.
        """
        if len(kwargs) == 0:
            self.transit_to(self.__on)
        elif "duration" in kwargs:
            self.__on_duration_condition.duration = kwargs["duration"]
            self.transit_to(self.__on_duration)
        else:
            raise ValueError("Invalid arguments for turn_on method")
        

    def turn_off(self, **kwargs) -> None:
        """
        Turns off the blinkers.

        Args:
            **kwargs: Additional keyword arguments.
                - duration (float): The duration for which the blinkers should stay off.

        Raises:
            ValueError: If invalid arguments are provided.
        """
        if len(kwargs) == 0:
            self.transit_to(self.__off)
        elif "duration" in kwargs:
            self.__off_duration_condition.duration = kwargs["duration"]
            self.transit_to(self.__off_duration)
        else:
            raise ValueError("Invalid arguments for turn_off method")
        

    def blink(self, percent_on: float = 0.5, begin_on: bool = True, **kwargs) -> None:
        """
        Blinks the blinkers.

        Args:
            percent_on (float): The percentage of time the blinkers should be on during each cycle (default: 0.5).
            begin_on (bool): True if the blinkers should start in the on state, False otherwise (default: True).
            **kwargs: Additional keyword arguments.
                - cycle_duration (float): The duration of each blink cycle.
                - total_duration (float): The total duration for which the blinkers should blink.
                - n_cycles (int): The number of blink cycles to perform.
                - end_off (bool): True if the blinkers should end in the off state, False otherwise (default: True).

        Raises:
            ValueError: If invalid arguments are provided.
        """
        
        
        if len(kwargs) == 0:
            self.__blink_1(percent_on=percent_on, begin_on=begin_on)
        elif "cycle_duration" in kwargs and len(kwargs) == 1:
            self.__blink_1(kwargs.get("cycle_duration", 1.0), percent_on, begin_on) 
        elif "total_duration" in kwargs and "n_cycles" in kwargs:
            self.__blink_3(kwargs["total_duration"], kwargs["n_cycles"], percent_on, begin_on, kwargs.get("end_off", True))
        elif "total_duration" in kwargs:
            self.__blink_2(kwargs["total_duration"], kwargs.get("cycle_duration", 1.0), percent_on, begin_on, kwargs.get("end_off", True))
        elif "n_cycles" in kwargs:
            self.__blink_4(kwargs["n_cycles"], kwargs.get("cycle_duration", 1.0), percent_on, begin_on, kwargs.get("end_off", True))
        else:
            raise ValueError("Invalid arguments for blink method")
            
        

    def __blink_1(self, cycle_duration: float = 1.0, percent_on: float = 0.5, begin_on: bool = True) -> None:
        """
        Blinks the blinkers with a single cycle.

        """
        if not isinstance(percent_on, float) or not isinstance(cycle_duration, float):
            raise TypeError("Invalid percent_on type, expected float")
        
        if percent_on < 0.0 or percent_on > 1.0:
            raise ValueError("Invalid percent_on value, expected value between 0 and 1")
        
        if cycle_duration <= 0:
            raise ValueError("Invalid cycle_duration, expected value greater than 0")
    
        if not isinstance(begin_on, bool):
            raise TypeError("Invalid begin_on value, expected boolean value")
            
        
        self.__blink_on_duration_condition.duration = cycle_duration * percent_on
        self.__blink_off_duration_condition.duration = cycle_duration - self.__blink_on_duration_condition.duration

        self.__blink_begin.custom_value = begin_on

        self.transit_to(self.__blink_begin)



    def __blink_2(self, total_duration: float, cycle_duration: float = 1.0, percent_on: float = 0.5, begin_on: bool = True, end_off: bool = True) -> None:
        """
        Blinks the blinkers with a specified total duration and cycle duration.

        """
        
        if not isinstance(percent_on, float):
            raise TypeError("Invalid percent_on type, expected float")

        if percent_on < 0 or percent_on > 1:
            raise ValueError("Invalid percent_on value, expected value between 0 and 1")
        
        if cycle_duration <= 0 or total_duration <= 0:
            raise ValueError("Invalid cycle_duration, expected value greater than 0")
        
        if not isinstance(cycle_duration, float) or not isinstance(total_duration, float):
            raise TypeError("Invalid cycle_duratio, expected float")

        if not isinstance(begin_on, bool) or not isinstance(end_off, bool):
            raise TypeError("Invalid begin_on or end_off value, expected boolean value")
        
        self.__blink_stop_begin.custom_value = begin_on
        self.__blink_stop_end.custom_value = end_off

        self.__blink_stop_begin_duration_condition.duration = total_duration
        self.__blink_stop_on_condition.duration = cycle_duration * percent_on
        self.__blink_stop_off_condition.duration = cycle_duration - self.__blink_stop_on_condition.duration
        
        self.transit_to(self.__blink_stop_begin)
        


    def __blink_3(self, total_duration: float, n_cycles: int, percent_on: float = 0.5, begin_on: bool = True, end_off: bool = True) -> None:
        """
        Blinks the blinkers with a specified total duration and number of cycles.

        """
        if not isinstance(percent_on, float):
            raise TypeError("Invalid percent_on type, expected float")

        if percent_on < 0 or percent_on > 1:
            raise ValueError("Invalid percent_on value, expected value between 0 and 1")
        
        if total_duration <= 0:
            raise ValueError("Invalid total_duration value, expected value greater than 0")
        
        if not isinstance(total_duration, float):
            raise TypeError("Invalid cycle_duration or total_duration type, expected float")
        
        if not isinstance(begin_on, bool) or not isinstance(end_off, bool):
            raise TypeError("Invalid begin_on value, expected boolean value")
        
        if n_cycles <= 0:
            raise ValueError("Invalid n_cycles value, expected value greater than 0")
        
        if  not isinstance(n_cycles, int):
            raise TypeError("Invalid n_cycles type, expected int")
        
        cycle_duration = total_duration / n_cycles

        self.__blink_stop_begin.custom_value = begin_on
        self.__blink_stop_end.custom_value = end_off

        self.__blink_stop_begin_duration_condition.duration = total_duration
        self.__blink_stop_on_condition.duration = cycle_duration * percent_on
        self.__blink_stop_off_condition.duration = cycle_duration - self.__blink_stop_on_condition.duration

        self.transit_to(self.__blink_stop_begin)
        
    
    
    def __blink_4(self, n_cycles:int, cycle_duration: float = 1.0, percent_on: float = 0.5, begin_on: bool = True,end_off: bool = True) -> None:
        """
        Perform a blinking operation with customizable parameters.

        """
        if not isinstance(percent_on, float):
            raise TypeError("Invalid percent_on type, expected float")

        if percent_on < 0 or percent_on > 1:
            raise ValueError("Invalid percent_on value, expected value between 0 and 1")
        
        if cycle_duration <= 0:
            raise ValueError("Invalid cycle_duration, expected value greater than 0")
        
        if not isinstance(cycle_duration, float):
            raise TypeError("Invalid cycle_duration, expected float")
        
        if not isinstance(begin_on, bool) or not isinstance(end_off, bool):
            raise ValueError("Invalid begin_on value, expected boolean value")
        
        if n_cycles <= 0:
            raise ValueError("Invalid n_cycles value, expected value greater than 0")
        
        if  not isinstance(n_cycles, int):
            raise TypeError("Invalid n_cycles type, expected int")
        
        total_duration = n_cycles * cycle_duration

        self.__blink_stop_begin.custom_value = begin_on
        self.__blink_stop_end.custom_value = end_off

        self.__blink_stop_begin_duration_condition.duration = total_duration
        self.__blink_stop_on_condition.duration = cycle_duration * percent_on
        self.__blink_stop_off_condition.duration = cycle_duration - self.__blink_stop_on_condition.duration

        self.transit_to(self.__blink_stop_begin)

    
class SideBlinkers():
    """
    The SideBlinkers class manages blinkers for both sides (left and right) of a vehicle.

    Args:
        left_off_state_generator (Blinkers.StateGenerator): A generator function that returns an instance of MonitoredState for the left off state.
        left_on_state_generator (Blinkers.StateGenerator): A generator function that returns an instance of MonitoredState for the left on state.
        right_off_state_generator (Blinkers.StateGenerator): A generator function that returns an instance of MonitoredState for the right off state.
        right_on_state_generator (Blinkers.StateGenerator): A generator function that returns an instance of MonitoredState for the right on state.

    Attributes:
        __left_blinker (Blinkers): The Blinkers instance for the left side.
        __right_blinker (Blinkers): The Blinkers instance for the right side.

    """
    class Side(Enum):
        """
        Enumeration of supported sides for blinkers.
        """
        LEFT = 0
        RIGHT = 1
        BOTH = 2
        LEFT_RECIPROCAL = 3
        RIGHT_RECIPROCAL = 4
    
    def __init__(self, left_off_state_generator: Blinkers.StateGenerator, left_on_state_generator: Blinkers.StateGenerator, right_off_state_generator: Blinkers.StateGenerator, right_on_state_generator: Blinkers.StateGenerator):
        self.__left_blinker: Blinkers = Blinkers(left_off_state_generator, left_on_state_generator)
        self.__right_blinker: Blinkers = Blinkers(right_off_state_generator, right_on_state_generator)

    def on(self, side: Side) -> bool:
        """
        Checks if the blinkers on the specified side are currently on.

        Args:
            side (SideBlinkers.Side): The side to check.

        Returns:
            bool: True if the blinkers are on, False otherwise.

        Raises:
            ValueError: If an unsupported side is provided.
        """
        if side in (SideBlinkers.Side.LEFT, SideBlinkers.Side.RIGHT): 
            actions = (
                self.__left_blinker.on, 
                self.__right_blinker.on
            )
            return actions[side.value]
        else: 
            raise ValueError("Only right or left side is supported")

    def off(self, side: Side) -> bool:
        """
        Checks if the blinkers on the specified side are currently off.

        Args:
            side (SideBlinkers.Side): The side to check.

        Returns:
            bool: True if the blinkers are off, False otherwise.

        Raises:
            ValueError: If an unsupported side is provided.
        """
        if side in (SideBlinkers.Side.LEFT, SideBlinkers.Side.RIGHT): 
            actions = (
                self.__left_blinker.off, 
                self.__right_blinker.off
            )
            return actions[side.value]
        else: 
            raise ValueError("Only right or left side is supported")

    def turn_on(self, side: Side, **kwargs) -> None:
        """
        Turns on the blinkers on the specified side.

        Args:
            side (SideBlinkers.Side): The side on which to turn on the blinkers.
            **kwargs: Additional keyword arguments.

        Raises:
            ValueError: If an unsupported side is provided or invalid arguments are provided.
        """
        actions = (
            lambda: self.__left_blinker.turn_on(**kwargs),
            lambda: self.__right_blinker.turn_on(**kwargs),
            lambda: (self.__left_blinker.turn_on(**kwargs), self.__right_blinker.turn_on(**kwargs)),
            lambda: (self.__left_blinker.turn_on(**kwargs), self.__right_blinker.turn_off(**kwargs)),
            lambda: (self.__left_blinker.turn_off(**kwargs), self.__right_blinker.turn_on(**kwargs))
        )
        actions[side.value]()

    def turn_off(self, side: Side, **kwargs) -> None:
        """
        Turns off the blinkers on the specified side.

        Args:
            side (SideBlinkers.Side): The side on which to turn off the blinkers.
            **kwargs: Additional keyword arguments.

        Raises:
            ValueError: If an unsupported side is provided or invalid arguments are provided.
        """
        actions = (
            lambda: self.__left_blinker.turn_off(**kwargs),
            lambda: self.__right_blinker.turn_off(**kwargs),
            lambda: (self.__left_blinker.turn_off(**kwargs), self.__right_blinker.turn_off(**kwargs)),
            lambda: (self.__left_blinker.turn_off(**kwargs), self.__right_blinker.turn_on(**kwargs)),
            lambda: (self.__left_blinker.turn_on(**kwargs), self.__right_blinker.turn_off(**kwargs))
        )
        actions[side.value]()

    def blink(self, side: Side, percent_on: float = 0.5, begin_on: bool = True, **kwargs) -> None:
        """
        Blinks the blinkers on the specified side. (Strategy)

        Args:
            side (SideBlinkers.Side): The side on which to blink the blinkers.
            percent_on (float): The percentage of time the blinkers should be on during each cycle (default: 0.5).
            begin_on (bool): True if the blinkers should start in the on state, False otherwise (default: True).
            **kwargs: Additional keyword arguments.

        Raises:
            ValueError: If an unsupported side is provided or invalid arguments are provided.
        """
                
        self.__left_blinker.reset()
        self.__right_blinker.reset()
        
        actions = (
            lambda: self.__left_blinker.blink(percent_on, begin_on, **kwargs),
            lambda: self.__right_blinker.blink(percent_on, begin_on, **kwargs),
            lambda: (self.__left_blinker.blink(percent_on, begin_on, **kwargs), self.__right_blinker.blink(percent_on, begin_on, **kwargs)),
            lambda: (self.__left_blinker.blink(percent_on, begin_on, **kwargs), self.__right_blinker.blink(1 - percent_on, not begin_on, **kwargs)),
            lambda: (self.__left_blinker.blink(1 - percent_on, not begin_on, **kwargs), self.__right_blinker.blink(percent_on, begin_on, **kwargs)), 
        )

        actions[side.value]()

    def track(self) -> None:
        """
        Tracks the state of both left and right blinkers.
        """
        self.__left_blinker.track()
        self.__right_blinker.track()
