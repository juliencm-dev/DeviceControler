from action import ActionState, ActionTransition
from conditional import Condition
from state import State
from abc import ABC
from typing import TYPE_CHECKING, Optional, Any
from time import perf_counter

if TYPE_CHECKING:
    from state import State

class MonitoredState(ActionState):
    """
        Extends ActionState to monitor state entry and exit times, as well as the number of entries.

        Attributes:
            last_entry_time (float): The last time the state was entered.
            last_exit_time (float): The last time the state was exited.
            entry_count (int): The total number of times the state has been entered.
            custom_value (Any): Custom data associated with the state.
        
        Methods:
            reset_entry_count: Resets the entry count to zero.
            reset_last_times: Resets the last entry and exit times to the current time.
    """
    
    TimeCounter = Optional[float] 
    
    def __init__(self, parameters: Optional['State.Parameters'] = None):
        super().__init__(parameters)
        self.__last_entry_time: MonitoredState.TimeCounter = perf_counter()
        self.__last_exit_time: MonitoredState.TimeCounter = perf_counter()
        self.__entry_count: int = 0
        self.custom_value: Any = None

        
    @property
    def entry_count(self) -> int:
        """
           Returns the count of how many times the state has been entered.
        """
        return self.__entry_count
    
    @property
    def last_entry_time(self) -> TimeCounter:
        """
          Returns the last recorded entry time to the state.
        """
        return self.__last_entry_time
    
    @property
    def last_exit_time(self) -> TimeCounter:
        """
           Returns the last recorded exit time from the state.
        """
        return self.__last_exit_time
    
    def reset_entry_count(self) -> None:
        """
          Resets the entry count for the state.
        """
        self.__entry_count: int = 0
        
    def reset_last_times(self) -> None:
        """
          Resets both the last entry and last exit times to the current time.
        """
        self.__last_entry_time: MonitoredState.TimeCounter = perf_counter()
        self.__last_exit_time: MonitoredState.TimeCounter = perf_counter()
        
    def _exec_entering_action(self) -> None:
        """
            Records the current time as the last entry time and increments the entry count.
            Overrides the parent class method to add monitoring functionality.
        """
        self.__last_entry_time: MonitoredState.TimeCounter = perf_counter() 
        self.__entry_count += 1 
        super()._exec_entering_action()
    
    def _exec_exiting_action(self) -> None:
        """
            Records the current time as the last exit time.
            Overrides the parent class method to add monitoring functionality.
        """
        super()._exec_exiting_action()
        self.__last_exit_time: MonitoredState.TimeCounter = perf_counter() 
        
    

class MonitoredTransition(ActionTransition):
    """
        Extends ActionTransition to monitor transitions with additional tracking of transition counts and times.

        This class adds functionality to record the number of times a transition has occurred and the last time it was executed. It also allows for the storage of custom data associated with the transition.

        Attributes:
            transit_count (int): The number of times the transition has been executed.
            last_transit_time (TimeCounter): The timestamp of the last execution of this transition.
            custom_value (Any): An attribute to store any user-defined data related to the transition.

        Methods:
            reset_transit_count: Resets the transit count to zero.
            reset_last_transit_time: Resets the last transit time to the current time.
            _exec_transiting_action: Records the current time as the last transit time and increments the transit count.
    """
    
    TimeCounter = Optional[float] 
    
    def __init__(self, next_state: 'State' = None):
        super().__init__(next_state)
        self.__transit_count: int  = 0
        self.__last_transit_time: MonitoredTransition.TimeCounter = None
        self.custom_value: Any = None
    
    @property
    def transit_count(self) -> int:
        """
            Gets the count of transitions that have been executed.

            Returns:
                int: The number of times the transition has been executed.
        """
        return self.__transit_count
    
    @property
    def last_transit_time(self) -> TimeCounter:
        """
            Gets the timestamp when the transition was last executed.

            Returns:
                TimeCounter: The timestamp of the last execution, or None if the transition has never been executed.
        """
        return self.__last_transit_time
    
    def reset_transit_count(self):
        """
            Resets the count of transitions to zero.
        """
        self.__transit_count: int = 0
        
    def reset_last_transit_time(self):
        """
            Sets the last transit time to the current time.
        """
        self.__last_transit_time: MonitoredTransition.TimeCounter = perf_counter()
        
    def _exec_transiting_action(self) -> None:
        """
            Executes the transition action, updating the last transit time and incrementing the transit count.
            This method extends the parent class implementation to include monitoring features.
        """
        self.__last_transit_time: MonitoredTransition.TimeCounter = perf_counter()
        super()._exec_transiting_action()
    


class MonitoredStateCondition(Condition, ABC):
    """
        A base class for conditions that involve monitoring a specific state.

        This class facilitates the creation of conditions based on the attributes or behaviors of a monitored state, such as
        the number of times the state has been entered or the duration of the state's activity. It inherits from both the
        Condition class and the abstract base class (ABC) to provide specialized behavior that can be inverted if necessary.

        Attributes:
            monitored_state (MonitoredState): The state being monitored by this condition.

        Args:
            monitored_state (MonitoredState): The instance of MonitoredState to be monitored.
            inverse (bool, optional): Determines whether the condition's result should be inverted. Defaults to False.
    """
    
    def __init__(self, monitored_state: 'MonitoredState', inverse: bool = False):
        super().__init__(inverse)
        self._monitored_state: 'MonitoredState' = monitored_state
        
    @property
    def monitored_state(self) -> 'MonitoredState':
        """
            Gets the monitored state associated with this condition.

            Returns:
                MonitoredState: The current state being monitored.

            Sets a new state to be monitored. Raises an error if the provided state is not an instance of MonitoredState.

            Args:
                monitored_state (MonitoredState): The new state to monitor.

            Raises:
                TypeError: If 'monitored_state' is not an instance of MonitoredState.
        """
        return self._monitored_state
    @monitored_state.setter
    def monitored_state(self, monitored_state: 'MonitoredState') -> None:
        
        if not isinstance(monitored_state, MonitoredState):
            raise TypeError("Invalid monitored state type, expected MonitoredState")
        
        self._monitored_state: 'MonitoredState' = monitored_state


class StateEntryDurationCondition(MonitoredStateCondition):
    """
        A condition class that checks if the duration since the last entry into a monitored state exceeds a specified threshold.

        This condition is useful for scenarios where an action or a transition needs to be triggered after a state has been
        active for a certain period of time.

        Attributes:
            duration (float): The minimum amount of time (in seconds) since the last state entry required to satisfy this condition.

        Args:
            duration (float): The duration in seconds to use as the threshold for the condition.
            monitored_state (MonitoredState): The state to monitor for its entry time.
            inverse (bool, optional): If True, the condition returns True if the duration since the last entry is less than the specified duration. Defaults to False.
    """

    def __init__(self, duration: float, monitored_state: 'MonitoredState', inverse: bool = False):
        super().__init__(monitored_state, inverse)
        self.__duration: float = duration

    @property
    def duration(self) -> float:
        """
            Gets the duration threshold for this condition.

            Returns:
                float: The duration in seconds that must be exceeded since the last state entry to satisfy the condition.

            Sets the duration threshold for this condition. The value must be a float representing the time in seconds.

            Args:
                duration (float): The new threshold duration in seconds.

            Raises:
                TypeError: If the provided 'duration' is not of type float.
        """
        return self.__duration
    @duration.setter
    def duration(self, duration: float) -> None:
        
        if not isinstance(duration, float):
            raise TypeError("Invalid duration type, expected float")
        
        self.__duration: float = duration

    def _compare(self) -> bool:
        """
            Compares if the time since the last entry exceeds the specified duration.

            Returns:
                bool: True if the condition is met, False otherwise.
            Doctest:
                >>> from time import sleep
                >>> state = MonitoredState()
                >>> condition = StateEntryDurationCondition(duration=0.1, monitored_state=state)
                >>> sleep(0.2)  # simulate time delay
                >>> bool(condition)
                True
        """
        return perf_counter() - self.monitored_state.last_entry_time >= self.__duration
        

class StateEntryCountCondition(MonitoredStateCondition):
    """
        A condition that checks if the number of entries into a monitored state meets an expected count.

        This condition can be used to trigger actions or transitions after a state has been entered a certain number of times. It supports an auto-reset feature, which resets the count comparison basis once the condition is met.

        Attributes:
            expected_count (int): The number of state entries required to satisfy the condition.
            auto_reset (bool): If True, resets the internal reference count when the expected count is reached.

        Args:
            monitored_state (MonitoredState): The state whose entries are to be counted.
            expected_count (int): The expected number of entries.
            auto_reset (bool, optional): Whether to reset the reference count upon meeting the condition. Defaults to True.
            inverse (bool, optional): If True, the condition returns True when the state entries are less than the expected count. Defaults to False.
    """
    
    def __init__(self, monitored_state: 'MonitoredState', expected_count: int, auto_reset:bool = True, inverse: bool = False):
        super().__init__(monitored_state, inverse)
        self.__expected_count: int = expected_count
        self.__auto_reset: bool = auto_reset
        self.__ref_count: int = self.monitored_state.entry_count
        
    @property
    def expected_count(self) -> int:
        """
        Gets or sets the number of state entries required to satisfy the condition.

        Setter:
            Raises a TypeError if the provided value is not an integer.

        Returns:
            int: The expected count of entries.
        """
        return self._expected_count
    @expected_count.setter
    def expected_count(self, expected_count: int) -> None:
        
        if not isinstance(expected_count, int):
            raise TypeError("Invalid expected_count type, expected int")
        
        self._expected_count: int = expected_count
        
    def _compare(self) -> bool:
        """
            Compares the current entry count with the expected count.

            If the current entry count meets or exceeds the expected count, the condition is met. If auto_reset is enabled, the reference count is reset to the current entry count.

            Returns:
                bool: True if the condition is met, False otherwise.

            Doctest:
                >>> state = MonitoredState()
                >>> condition = StateEntryCountCondition(expected_count=5, monitored_state=state)
                >>> state._exec_entering_action()
                >>> bool(condition)
                False
                >>> for _ in range(4) : state._exec_entering_action()
                >>> bool(condition)
                True
        """
        if  self.monitored_state.entry_count >= self.__ref_count + self.__expected_count:
            if self.__auto_reset:
                self.__ref_count = self.monitored_state.entry_count
            return True
        return False
    
    def reset_count(self) -> None:
        """
            Resets the internal reference count used for comparison to zero.
        """
        self.__ref_count: int = 0


class StateValueCondition(MonitoredStateCondition):
    """
        A condition that compares a custom value stored in a monitored state against an expected value.

        This class is particularly useful for conditions based on comparing user-defined or dynamic values associated with a state,
        such as flags, counters, or any other custom metrics that determine the state's behavior or status.

        Attributes:
            expected_value (Any): The value to compare against the custom value of the monitored state.

        Args:
            expected_value (Any): The value expected to be found in the monitored state.
            monitored_state (MonitoredState): The state whose custom value is being monitored.
            inverse (bool, optional): If set to True, the condition inverts the result of the comparison. Defaults to False.
    """
        
    def __init__(self, expected_value: Any, monitored_state: 'MonitoredState', inverse: bool = False):
        super().__init__(monitored_state, inverse)
        self.expected_value = expected_value
        
    @property
    def expected_value(self) -> Any:
        """
            Gets or sets the expected value for comparison against the monitored state's custom value.

            Setter:
                If the custom value in the monitored state is None, the setter simply assigns the expected value.
                Otherwise, it validates that the type of the expected value matches the type of the custom value in the monitored state,
                raising a TypeError if they do not match.

            Returns:
                Any: The expected value for comparison.
        """
        return self.__expected_value
    @expected_value.setter
    def expected_value(self, expected_value: Any) -> None:

        if self._monitored_state.custom_value is None:
            self.__expected_value: Any = expected_value
            return

        if not isinstance(self._monitored_state.custom_value, type(expected_value)):
            raise TypeError(f"Invalid expected_value type, expected {type(self._monitored_state.custom_value)}")
         
        self.__expected_value: Any = expected_value

    def _compare(self) -> bool:
        """
            Compares the monitored state's custom value with the expected value.

            Returns:
                bool: True if the custom value equals the expected value, False otherwise.

            Doctest:
                >>> state = MonitoredState()
                >>> state.custom_value = 5
                >>> condition = StateValueCondition(expected_value=5, monitored_state=state)
                >>> bool(condition)
                True
                >>> state.custom_value = 3
                >>> bool(condition)
                False
        """
        return self.monitored_state.custom_value == self.__expected_value
            
