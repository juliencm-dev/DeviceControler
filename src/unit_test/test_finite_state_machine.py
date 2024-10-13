import unittest
from time import perf_counter

from action import ActionState
from blinkers import Blinkers
from fsm import FiniteStateMachine
from monitored import MonitoredState
from state import State, Transition
from typing import Optional

class FeuxTransition(Transition):
    def __init__(self, next_state: State = None):
        super().__init__(next_state)

    @property
    def transiting(self) -> bool:
        return True

class FeuxState(State): 
    def __init__(self, parameters: Optional[State.Parameters] = None):
        super().__init__(parameters)
    
# TEST
class TestFinitStateMachine(unittest.TestCase):
    def setUp(self):
        """
        Initialize the test fixture by creating an ActionState object.
        """
        self.action_state = ActionState()

    def test_add_exiting_action_invalid_type(self):
        """
        Test adding exiting action with invalid type.
        """
        with self.assertRaises(TypeError):
            self.action_state.add_exiting_action("This is not a function")

    def test_start_layout(self):
        """
        Test starting the FSM with an invalid layout type.
        """
        with self.assertRaises(TypeError):
            FiniteStateMachine("This is not a layout")
    
    def test_start_layout_not_valid(self):
        """
        Test starting the FSM with an invalid layout.
        """
        with self.assertRaises(ValueError):
            FiniteStateMachine(FiniteStateMachine.Layout())

    def test_layout_not_valid(self):
        """
        Test creating an FSM with an invalid layout.
        """
        layout = FiniteStateMachine.Layout()
        self.rouge = FeuxState("ROUGE")
        self.jaune = FeuxState("JAUNE")

        transitionjr = FeuxTransition(1.0)
        self.jaune.add_transition(transitionjr)

        layout.add_states([self.rouge, self.jaune])
        with self.assertRaises(ValueError):
          self.fsm = FiniteStateMachine(layout)

if __name__ == '__main__':
    unittest.main()
