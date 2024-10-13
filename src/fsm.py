from enum import Enum, auto
from typing import List, Set, TYPE_CHECKING
from time import perf_counter
from state import State

if TYPE_CHECKING:
    from state import State, Transition

class FiniteStateMachine:
    """
    A FiniteStateMachine class represents a finite state machine (FSM).

    Attributes:
        OperationalState (Enum): Enumerates operational states of the FSM.
        Layout (class): Nested class representing the layout of the FSM.

    Methods:
        __init__: Initializes the FSM.
        current_operational_state: Returns the current operational state of the FSM.
        current_applicative_state: Returns the current applicative state of the FSM.
        transit_to: Transits the FSM to a specified state.
        reset: Resets the FSM to its initial state.
        track: Tracks the state transitions of the FSM.
        start: Starts the FSM with optional time budget for execution.
        stop: Stops the execution of the FSM.
    """
    class OperationalState(Enum):
        """Enumerates operational states of the FSM."""
        UNITIALIZED = auto()
        IDLE = auto()
        RUNNING = auto()
        TERMINAL_REACHED = auto()

    class Layout:
        """
        Nested class representing the layout of the FSM.

        Methods:
            add_state: Adds a state to the layout.
            add_states: Adds multiple states to the layout.
        """
        def __init__(self):
            """
            Initalize the object.
            """
            self.__states: Set['State'] = set()
            self.__initial_state: 'State' = None
        
        def add_state(self, state: 'State') -> None:
            """
            Adds a state to the layout.

            Args:
                state (State): The state to add.

            Raises:
                TypeError: If the provided state is not of type State.
            """
            if not isinstance(state, State):
                raise TypeError("Invalid type, expected State")
            
            self.__states.add(state)

        def add_states(self, states: List['State']) -> None:
            """
            Adds multiple states to the layout.

            Args:
                states (List[State]): The list of states to add.

            Raises:
                TypeError: If any of the provided states is not of type State.
            """
            for state in states:
                if not isinstance(state, State):
                    raise TypeError("Invalid type, expected State")
                
            self.__states.update(states)
        
        @property
        def valid(self) -> bool:
            """
            Checks if the layout is valid.

            Returns:
                bool: True if the layout is valid, False otherwise.
            """
            if self.__initial_state is None:
                return False

            for state in self.__states:
                if not state.valid:
                    return False
                
            return True

        @property
        def initial_state(self) -> 'State':
            """
            property for initial_state.

            Args:
                state (State): The initial state.

            Raises:
                ValueError: If the initial state is not part of the states list.
            """            
            return self.__initial_state
        
        @initial_state.setter
        def initial_state(self, state: 'State') -> None:
            
            if state not in self.__states:
                raise ValueError("The initial state must be part of the states list")
            
            self.__initial_state: 'State' = state


    def __init__(self, layout: Layout, unitialized: bool = True):
        """
        Initializes a FiniteStateMachine object.

        Args:
            layout (Layout): The layout of the FSM.
            uninitialized (bool): If True, initializes the FSM in an uninitialized state. Defaults to True.

        Raises:
            ValueError: If the layout is not valid.
        """
        if not isinstance(layout, FiniteStateMachine.Layout):
            raise TypeError("Invalid type, expected Layout")

        if not layout.valid:
            raise ValueError("The layout is not valid")
        
        self.__layout: FiniteStateMachine.Layout = layout
        self.__current_applicative_state: 'State' = None 
        self.__current_operational_state: FiniteStateMachine.OperationalState = FiniteStateMachine.OperationalState.UNITIALIZED 

        if unitialized:
            self.reset()

    @property
    def current_operational_state(self) -> OperationalState:
        """Returns the current operational state of the FSM."""
        return self.__current_operational_state

    @property
    def current_applicative_state(self) -> 'State':
        """Returns the current applicative state of the FSM."""
        return self.__current_applicative_state
    
    def _transit_by(self, transition: 'Transition') -> None:
        """
        Executes a state transition based on the provided transition.

        Args:
            transition (Transition): The transition to execute.
        """
        self.__current_applicative_state._exec_exiting_action()
        transition._exec_transiting_action()
        self.__current_applicative_state = transition.next_state
        self.__current_applicative_state._exec_entering_action()

    def transit_to(self, state: 'State') -> None:
        """
        Transits the FSM to the specified state.

        Args:
            state (State): The target state to transit to.

        Raises:
            TypeError: If the provided state is not of type State.
        """
        if not isinstance(state, State):
            raise TypeError("Invalid type, expected State")
        
        self.__current_applicative_state._exec_exiting_action()
        self.__current_applicative_state = state
        self.__current_applicative_state._exec_entering_action()

    def reset(self) -> None:
        """Resets the FSM to its initial state."""
        self.__current_applicative_state = self.__layout.initial_state

        if self.__current_operational_state == FiniteStateMachine.OperationalState.RUNNING:
            self.__current_applicative_state._exec_exiting_action()

        self.__current_operational_state = FiniteStateMachine.OperationalState.IDLE


    def track(self) -> bool:
        """
        Tracks the state transitions of the FSM.

        Returns:
            bool: True if tracking is successful, False otherwise.
        """
        transition = self.__current_applicative_state.transiting

        if transition:
            self._transit_by(transition)
        else:
            self.__current_applicative_state._exec_in_state_action()

        if self.__current_applicative_state.terminal:
            self.__current_operational_state == FiniteStateMachine.OperationalState.TERMINAL_REACHED
            
        return not self.__current_applicative_state.terminal


    def start(self, reset: bool = True, time_budget: float = None) -> None:
        """
        Starts the execution of the FSM.

        Args:
            reset (bool): If True, resets the FSM before starting. Defaults to True.
            time_budget (float): Optional time budget for execution. Defaults to None.

        Raises:
            TypeError: If reset is not of type bool or time_budget is not a float or None.
        """
        if not isinstance(reset, bool):
            raise TypeError("Invalid type, expected bool")
        
        if isinstance(time_budget, float) or time_budget == None:
            #TODO: encapsuler le chrono ?
            current_time: float = perf_counter()
            elapsed_time: float = 0.0

            if reset: self.reset()

            self.__current_operational_state = FiniteStateMachine.OperationalState.RUNNING
            
            while (time_budget is None or elapsed_time < time_budget) and self.track() and self.__current_operational_state == FiniteStateMachine.OperationalState.RUNNING:
                elapsed_time: float = perf_counter() - current_time
        else:
            raise TypeError("Invalid type, expected float or None")
            

    def stop(self) -> None:
        """
        Stops the execution of the FSM, setting its operational state to IDLE.
        """
        self.__current_operational_state = FiniteStateMachine.OperationalState.IDLE