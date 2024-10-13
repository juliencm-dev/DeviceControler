from state import State
from conditional import ConditionalTransition
from typing import Callable, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from state import State
 
class ActionState(State):
    """
    An extension of the State class that allows adding actions to be executed upon entering, during the state,
    and upon exiting the state.
    """
    Action = Callable[[], None]
    
    def __init__(self, parameters: Optional[State.Parameters] = None):
        super().__init__(parameters)
        self.__entering_actions: List[ActionState.Action] = []
        self.__in_state_actions: List[ActionState.Action] = []
        self.__exiting_actions: List[ActionState.Action] = []
        
    def _do_entering_action(self) -> None:
        """
        Executes all entering actions of the state.
        """
        for action in self.__entering_actions:
            action()
        super()._do_entering_action()
    
    def _do_in_state_action(self) -> None:
        """
        Executes all in-state actions of the state.
        """
        for action in self.__in_state_actions:
            action()
        super()._do_in_state_action()
    
    def _do_exiting_action(self) -> None:
        """
        Executes all exiting actions of the state.
        """
        for action in self.__exiting_actions:
            action()
        super()._do_exiting_action()
        
    def add_entering_action(self, action: Action) -> None:
        """
        Adds an action to be executed upon entering the state.

        Args:
            action (Action): The action to add.

        Raises:
            TypeError: If the action is not callable.
        """
        if callable(action):
            self.__entering_actions.append(action)
        else:
            raise TypeError("An action must be a callable")
    
    def add_in_state_action(self, action: Action) -> None:
        """
        Adds an action to be executed during the state.

        Args:
            action (Action): The action to add.

        Raises:
            TypeError: If the action is not callable.
        """
        if callable(action):
            self.__in_state_actions.append(action)
        else:
            raise TypeError("An action must be a callable")
    
    def add_exiting_action(self, action: Action) -> None:
        """
        Adds an action to be executed upon exiting the state.

        Args:
            action (Action): The action to add.

        Raises:
            TypeError: If the action is not callable.
        """
        if callable(action):
            self.__exiting_actions.append(action)
        else:
            raise TypeError("An action must be a callable")

class ActionTransition(ConditionalTransition):
    """
    An extension of the ConditionalTransition class that allows adding actions to be executed during a transition.
    """
    Action = Callable[[], None]
    
    def __init__(self, next_state: 'State' = None):
        """
        Initializes an ActionTransition object.

        Args:
            next_state (State): The next state to transition to.
        """
        super().__init__(next_state)
        self.__transiting_actions: List[ActionTransition.Action] = []
        
    def _do_transiting_action(self) -> None:
        """
        Executes all transiting actions of the transition.
        """
        super()._do_transiting_action()
    
    def add_transiting_action(self, action: Action):
        """
        Adds an action to be executed during the transition.

        Args:
            action (Action): The action to add.

        Raises:
            TypeError: If the action is not callable.
        """
        if callable(action):
            self.__transiting_actions.append(action)
        else:
            raise TypeError("An action must be a callable")
        

