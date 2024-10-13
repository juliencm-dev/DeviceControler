from typing import List, Optional
from abc import ABC, abstractmethod

class Transition(ABC):
    """
    Abstract base class for transitions in a Finite State Machine (FSM).

    Attributes:
        _next_state ('State'): The next state to transition to.

    Methods:
        valid: Check if the transition is valid.
        transiting: Abstract method meant to be implemented in derived classes and check if the transition is currently active.
        _exec_transiting_action: Execute the action associated with transitioning.
        _do_transiting_action: Abstract method to define the action during transitioning.
    """
    def __init__(self, next_state:'State' = None):
        self.__next_state: 'State' = next_state 
        
    @property
    def valid(self) -> bool:
        """
        Check if the transition is valid.
        """
        if not self.__next_state: 
            return False
        return True
    
    @property
    def next_state(self) -> 'State':
        """
        Get the next state that this transition leads to.

        Args:
            state ('State'): The next state.

        Returns:
            State: The next state.

        Raises:
            TypeError: If the provided state is not an instance of State.
        """
        return self.__next_state
    
    @next_state.setter
    def next_state(self, state: 'State') -> None:
        if not isinstance(state, State):
                raise TypeError("Invalid type, expected State")
        self.__next_state: 'State' = state
        
    @property
    @abstractmethod
    def transiting(self) -> bool:
        """
        Abstract property to check if the transition is currently active.
        """ 
        pass 
    
    def _exec_transiting_action(self) -> None:
        """
        Execute the action associated with transitioning.
        """
        self._do_transiting_action()
    
    def _do_transiting_action(self) -> None:
        """
        Abstract method to define the action during transitioning.
        """
        pass 
    
    
class State:
    """
    Represents a state in a Finite State Machine (FSM).

    Attributes:
        __parameters (Parameters): The parameters of the state.
        __transition (List[Transition]): List of transitions from this state.

    Methods:
        valid: Check if the state is valid.
        terminal: Check if the state is terminal.
        transiting: Get the active transition from this state.
        add_transition: Add a transition to the state.
        _exec_entering_action: Execute the entering action of the state.
        _exec_in_state_action: Execute the in-state action of the state.
        _exec_exiting_action: Execute the exiting action of the state.
        _do_entering_action: Abstract method to define entering action.
        _do_in_state_action: Abstract method to define in-state action.
        _do_exiting_action: Abstract method to define exiting action.
    """
    class Parameters:
        def __init__(self, terminal = False, do_in_state_action_when_entering = False, do_in_state_action_when_exiting = False):
            self.terminal:bool = terminal
            self.do_in_state_action_when_entering:bool = do_in_state_action_when_entering
            self.do_in_state_action_when_exiting:bool = do_in_state_action_when_exiting
        
    def __init__(self, parameters:Optional['Parameters'] = None):
        self.__parameters: State.Parameters = parameters if parameters else State.Parameters() 
        self.__transition:List['Transition'] = []
        
    @property
    def valid(self) -> bool :
        """
        Check if the state is valid.
        """
        for transition in self.__transition: 
            if not transition.valid: 
                return False    
            
        return True
    
    @property
    def terminal(self) -> bool:
        """
        Check if the state is terminal.
        """
        return self.__parameters.terminal
        
    @property
    def transiting(self) -> Optional['Transition'] :
        """
        Get the active transition from this state, if the state is currently in transition.
        """
        if len(self.__transition) < 1 :
            return None
        for transition in self.__transition: 
            if transition.transiting:
                return transition
        return None
        
    
    def add_transition(self,transition:'Transition'):
        """
        Add a transition to the state.

        Args:
            transition ('Transition'): The transition to add.
        """
        if not isinstance(transition, Transition):
            raise TypeError("Invalid type, expected Transition")
        self.__transition.append(transition)
    
    def _exec_entering_action(self) -> None:
        """
        Execute the entering action of the state.
        """
        self._do_entering_action()
        
    def _exec_in_state_action(self)-> None:
        """
        Execute the in-state action of the state.
        """
        self._do_in_state_action()
        
    def _exec_exiting_action(self)-> None: 
        """
        Execute the exiting action of the state.
        """
        self._do_exiting_action()
        
    def _do_entering_action(self)-> None:
        """
        Abstract method to define entering action.
        """
        pass
    
    def _do_in_state_action(self)-> None:
        """
        Abstract method to define in-state action.
        """
        pass
    
    def _do_exiting_action(self)-> None:
        """
        Abstract method to define exiting action.
        """
        pass
        
    
    
    
