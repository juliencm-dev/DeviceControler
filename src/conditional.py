from state import Transition
from abc import ABC
from typing import Any, List, Optional
from time import perf_counter

class Condition(ABC):
    """
    The Condition class is an abstract base class representing a condition that can be evaluated.

    Args:
        inverse (bool): If True, the condition's result is inverted.

    Attributes:
        __inverse (bool): Flag indicating whether the condition's result is inverted.

    Methods:
        __bool__: Evaluate the condition.
        valid: Check if the condition is valid.
        _compare: Compare the condition's value.
    """
    def __init__(self, inverse: bool) -> None:
        """
        Initializes a Condition object.

        Args:
            inverse (bool): If True, the condition's result is inverted.
        """
        self.__inverse: bool = inverse
    
    def __bool__(self) -> bool:
        """
        Evaluates the condition.

        Returns:
            bool: True if the condition is true, False otherwise.
        """
        return  self.__inverse ^ self._compare()
    
    @property
    def valid(self) -> bool: 
        """
        Checks if the condition is valid.

        Returns:
            bool: True if the condition is valid, False otherwise.
        """
        return True
       
    def _compare() -> bool:
        """
        Abstract method for comparing the condition value.
        """
        pass

class ConditionalTransition(Transition):
    """
    A ConditionalTransition class extends Transition and represents a transition that occurs based on a condition.

    Args:
        condition (Condition): The condition under which the transition occurs. Defaults to None.

    Attributes:
        __condition (Optional[Condition]): The condition under which the transition occurs.

    Methods:
        valid: Check if the transition is valid.
        condition: Get the condition.
        transiting: Check if the transition is in progress.
    """
    def __init__(self, condition: 'Condition' = None):
        """
        Initializes a ConditionalTransition object.

        Args:
            condition (Condition): The condition under which the transition occurs. Defaults to None.
        """
        self.__condition: Optional['Condition'] = condition 
        
    @property
    def valid(self) -> bool:
        """
        Checks if the transition is valid.

        Returns:
            bool: True if the transition is valid and not None, False otherwise.
        """
        return self.__condition is not None and self.__condition.valid and super().valid
    
    @property
    def condition(self) -> 'Condition':
        """
        Gets the condition.

        Returns:
            Condition: The condition under which the transition occurs.
        """
        return self.__condition
    
    @condition.setter
    def condition(self, condition: 'Condition') -> None:
        if not isinstance(condition, Condition):
            raise TypeError("Invalid condition type, expected Condition")
        
        self.__condition: 'Condition' = condition
        
    @property
    def transiting(self) -> bool:
        """
        Checks if the transition is in progress.

        Returns:
            bool: True if the transition is in progress, False otherwise.
        """
        return bool(self.condition)

class AlwaysTrueCondition(Condition):
    """
    An AlwaysTrueCondition class is a Condition subclass that always evaluates to True.

    Args:
        inverse (bool): If True, the condition's result is inverted. Defaults to False.

    Methods:
        _compare: Compare the condition's value.
    """
    def __init__(self, inverse: bool = False):
        """
        Initializes an AlwaysTrueCondition object.

        Args:
            inverse (bool): If True, the condition's result is inverted. Defaults to False.
        """
        super().__init__(inverse)
    
    def _compare(self) -> bool:
        """
        Compares the condition's value.

        Returns:
            bool: Always True.
        """
        return True
        
class ValueCondition(Condition):
    """
    A ValueCondition class is a Condition subclass that compares two values.

    Args:
        initial_value (Any): The initial value.
        expected_value (Any): The expected value.
        inverse (bool): If True, the condition's result is inverted. Defaults to False.

    Methods:
        valid: Check if the condition is valid.
        _compare: Compare the condition's value.

    Doctest:
     >>> c = ValueCondition(10, 10)
    >>> bool(c)
    True
    >>> c = ValueCondition(10, 20)
    >>> bool(c)
    False
    >>> c = ValueCondition(10, 10, True)
    >>> bool(c)
    False
   
    """
    def __init__(self, initial_value: Any, expected_value: Any, inverse: bool = False):
        """
        Initializes a ValueCondition object.

        Args:
            initial_value (Any): The initial value.
            expected_value (Any): The expected value.
            inverse (bool): If True, the condition's result is inverted. Defaults to False.
        """
        super().__init__(inverse)
        self.value: Any = initial_value
        self.expected_value: Any = expected_value

    @property
    def valid(self) -> bool:
        """
        Checks if the condition is valid.

        Returns:
            bool: True if the condition is valid, False otherwise.
        """ 
        if not self.value or not self.expected_value:
            return False
        return True
    
    def _compare(self) -> bool:
        """
        Compares the condition's value.

        Returns:
            bool: True if the values are equal, False otherwise.
        """
        return self.value == self.expected_value
        
class TimedCondition(Condition):
    """
    A TimedCondition class is a Condition subclass that evaluates based on time duration.

    Args:
        duration (float): The duration in seconds.
        time_reference (Optional[float]): The time reference. Defaults to None.
        inverse (bool): If True, the condition's result is inverted. Defaults to False.

    Attributes:
        __counter_reference (Optional[float]): The time counter reference.
        duration (float): The duration in seconds.

    Methods:
        duration: Get the duration.
        reset: Reset the time counter reference.
        _compare: Compare the condition based on time.

    
    A condition that becomes True after a certain duration has passed.

    A condition that becomes True after a certain duration has passed.
    
    Doctest:
    >>> import time
    >>> condition = TimedCondition(duration=0.1)
    >>> bool(condition)
    False
    >>> time.sleep(0.11)  # Wait a little longer than the duration
    >>> bool(condition)
    True
    >>> condition.reset()  # Reset the timer
    >>> bool(condition)
    False
    >>> time.sleep(0.05)
    >>> bool(condition)
    False
    >>> time.sleep(0.06)
    >>> bool(condition)
    True
    """

    TimeCounter = Optional[float] 

    def __init__(self, duration: float = 1.0, time_reference: Optional[float] = None, inverse: bool = False):
        """
        Initializes a TimedCondition object.

        Args:
            duration (float): The duration in seconds.
            time_reference (Optional[float]): The time reference. Defaults to None.
            inverse (bool): If True, the condition's result is inverted. Defaults to False.
        """
        super().__init__(inverse)

        self.duration: float = duration
        self.__counter_reference: TimedCondition.TimeCounter = time_reference

        if self.__counter_reference is None:
            self.reset()


    @property
    def duration(self) -> float: 
        """
        Gets the duration.

        Returns:
            float: The duration in seconds.
        
        Raises:
            ValueError: If the duration is not positive.
            TypeError: If the duration is not of type float.
        """
        return self.__counter_duration    
    @duration.setter
    def duration(self, duration: float) -> None:

        if duration <= 0:
            raise ValueError("Invalid duration, expected a positive value")
        
        if not isinstance(duration, float):
            raise TypeError("Invalid duration type, expected float")
        
        self.__counter_duration: float = duration
    
    def reset(self):
        """
        Resets the time counter reference to perf_counter.
        """
        self.__counter_reference = perf_counter()
    
    def _compare(self) -> bool:
        """
        Compares the condition based on time.

        Returns:
            bool: True if the time condition is met, False otherwise.
        """
        return self.__counter_reference + self.__counter_duration <= perf_counter()
        

class ManyConditions(Condition):
    """
    A ManyConditions class is a Condition subclass that represents multiple conditions.

    Args:
        inverse (bool): If True, the condition's result is inverted. Defaults to False.

    Attributes:
        _conditions (List[Condition]): The list of conditions.

    Methods:
        valid: Check if the conditions are valid.
        add_condition: Add a condition to the list.
        add_conditions: Add multiple conditions to the list.
    """
    def __init__(self, inverse: bool = False):
        """
        Initializes a ManyConditions object.

        Args:
            inverse (bool): If True, the condition's result is inverted. Defaults to False.
        """
        super().__init__(inverse)
        self._conditions: List['Condition'] = []

    @property
    def valid(self) -> bool:
        """
        Checks if the conditions are valid.

        Returns:
            bool: True if all conditions are valid, False otherwise.
        """
        if len(self._conditions) < 1:
            return False
        
        for condition in self._conditions:
            if not condition.valid:
                return False 
            
        return True

    def add_condition(self, condition: 'Condition') -> None:
        """
        Adds a condition to the list of conditions.

        Args:
            condition (Condition): The condition to add.

        Raises:
            TypeError: If the provided condition is not of type Condition.
        """
        if not isinstance(condition, Condition):
            raise TypeError("Invalid condition type, expected Condition")
        
        self._conditions.append(condition)
    
    def add_conditions(self, conditions: List['Condition']) -> None:
        """
        Adds multiple conditions to the list of conditions.

        Args:
            conditions (List[Condition]): The list of conditions to add.

        Raises:
            TypeError: If any of the provided conditions is not of type Condition.
        """
        for condition in conditions:
            if not isinstance(condition, Condition):
                raise TypeError("Invalid condition type, expected Condition")
        
        self._conditions.extend(conditions)

class AllConditions(ManyConditions):
    """
    An AllConditions class is a ManyConditions subclass that evaluates to True if all conditions are True.

    Args:
        inverse (bool): If True, the condition's result is inverted. Defaults to False.

    Methods:
        _compare: Compare the conditions using the 'all' function.

    Doctest:
    >>> c1 = AlwaysTrueCondition()
    >>> c2 = ValueCondition(5, 5)
    >>> c3 = ValueCondition(10, 10)
    >>> all_conditions = AllConditions()
    >>> all_conditions.add_conditions([c1, c2, c3])
    >>> bool(all_conditions)
    True
    >>> c4 = ValueCondition(10, 11)
    >>> all_conditions.add_condition(c4)
    >>> bool(all_conditions)
    False
    
    """

    def __init__(self, inverse: bool = False):
        """
        Initializes an AllConditions object.

        Args:
            inverse (bool): If True, the condition's result is inverted. Defaults to False.
        """
        super().__init__(inverse)
    
    def _compare(self) -> bool:
        """
        Compares the conditions using the 'all' function.

        Returns:
            bool: True if all conditions are True, False otherwise.
        """
        return all(condition for condition in self._conditions)
    
class AnyConditions(ManyConditions):
    """
    An AnyConditions class is a ManyConditions subclass that evaluates to True if any condition is True.

    Args:
        inverse (bool): If True, the condition's result is inverted. Defaults to False.

    Methods:
        _compare: Compare the conditions using the 'any' function.
    
    Doctest:
    
    >>> value_cond1 = ValueCondition(5, 5)
    >>> timed_cond = TimedCondition(duration=1.0)
    >>> false_conditions = AnyConditions()
    >>> false_conditions.add_conditions([value_cond1, timed_cond])
    >>> bool(false_conditions)
    True
    """
    def __init__(self, inverse: bool = False):
        """
        Initializes an AnyConditions object.

        Args:
            inverse (bool): If True, the condition's result is inverted. Defaults to False.
        """
        super().__init__(inverse)
    
    def _compare(self) -> bool:
        """
        Compares the conditions using the 'any' function.

        Returns:
            bool: True if any condition is True, False otherwise.
        """
        return any(condition for condition in self._conditions)
        

class NoneConditions(ManyConditions):
    """
    A NoneConditions class is a ManyConditions subclass that evaluates to True if no condition is True.

    Args:
        inverse (bool): If True, the condition's result is inverted. Defaults to False.

    Methods:
        _compare: Compare the conditions using negation.
    """
    def __init__(self, inverse: bool = False):
        """
        Initializes a NoneConditions object.

        Args:
            inverse (bool): If True, the condition's result is inverted. Defaults to False.
        """
        super().__init__(inverse)
    
    def _compare(self) -> bool:
        """
        Compares the conditions using negation.

        Returns:
            bool: True if no condition is True, False otherwise.
        """
        return all(not condition for condition in self._conditions)
        

        