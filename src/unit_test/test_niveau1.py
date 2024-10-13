import unittest
from state import *
from fsm import *
from typing import Optional

class FeuxTransition(Transition):
    def __init__(self, time:float, next_state: State = None):
        super().__init__(next_state)

    @property
    def transiting(self) -> bool:
        return True

class FeuxState(State): 
    def __init__(self, couleur:str, parameters: Optional[State.Parameters] = None):
        super().__init__(parameters)
        self.couleur = couleur
    
    def _do_entering_action(self) -> None:
        pass

class TestSecondNiveau(unittest.TestCase):
    def setUp(self) -> None:
        """
        Initialize the test fixture by creating a Finite State Machine with traffic light states.
        """
        param = State.Parameters()
        param.terminal = True
        
        layout = FiniteStateMachine.Layout()
        self.rouge = FeuxState("ROUGE", param)
        self.jaune = FeuxState("JAUNE")
        self.vert = FeuxState("VERT")

        transitionjr = FeuxTransition(1.0, self.rouge)
        transitionrv = FeuxTransition(5.0, self.vert)
        transitionvj = FeuxTransition(4.0, self.jaune)
        
        self.rouge.add_transition(transitionrv)
        self.vert.add_transition(transitionvj)
        self.jaune.add_transition(transitionjr)

        layout.add_states([self.rouge, self.vert, self.jaune])
        layout.initial_state = self.rouge
        self.fsm = FiniteStateMachine(layout)

    def test_init(self) -> None:
        """
        Test initial state after setup.
        """
        self.assertEqual(self.fsm.current_applicative_state, self.rouge, f"Inital state expected: Rouge.")

    def test_track_01(self) -> None:
        """
        Test tracking with one transition.
        """
        self.fsm.track()
        self.assertEqual(self.fsm.current_applicative_state, self.vert, "Track, state expected: Vert.")

    def test_track_02(self) -> None:
        """
        Test tracking with multiple transitions.
        """
        self.fsm.track()
        self.fsm.track()
        self.assertEqual(self.fsm.current_applicative_state, self.jaune, "Track, state expected: Jaune.")

    def reset(self) -> None:
        """
        Test reset.
        """
        self.fsm.track()
        self.fsm.reset()
        self.assertEqual(self.fsm.current_applicative_state, self.rouge, "Track, state expected: Rouge.")

    def reset_and_track(self) -> None:
        """
        Test reset.
        """
        self.fsm.track()
        self.fsm.reset()
        self.fsm.track()
        self.assertEqual(self.fsm.current_applicative_state, self.vert, "Track, state expected: Vert.")

    def reset_and_track(self) -> None:
        """
        Test multiple reset.
        """
        self.fsm.reset()
        self.fsm.reset()
        self.assertEqual(self.fsm.current_applicative_state, self.rouge, "Track, state expected: Rouge.")

if __name__ == '__main__':
    unittest.main()