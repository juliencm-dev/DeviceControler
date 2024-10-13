import unittest
from action import ActionState, ActionTransition
from state import Transition

class TestActionState(unittest.TestCase):
    def setUp(self):
        """
        Initialize the test fixture by creating an ActionState object.
        """
        self.action_state = ActionState()

    def test_add_entering_action_invalid_type(self):
        """
        Test adding entering action with invalid type.
        """
        with self.assertRaises(TypeError):
            self.action_state.add_entering_action("This is not a function")

    def test_add_in_state_action_invalid_type(self):
        """
        Test adding in-state action with invalid type.
        """
        with self.assertRaises(TypeError):
            self.action_state.add_in_state_action("This is not a function")

    def test_add_exiting_action_invalid_type(self):
        """
        Test adding exiting action with invalid type.
        """
        with self.assertRaises(TypeError):
            self.action_state.add_exiting_action("This is not a function")

    def test_add_entering_action_valid(self):
        """
        Test adding entering action with valid type (callable).
        """
        def dummy_action():
            pass
        try:
            self.action_state.add_entering_action(dummy_action)
        except Exception as e:
            self.fail(f"Adding action raised an unexpected exception: {e}")

    def test_add_in_state_action_valid(self):
        """
        Test adding in-state action with valid type (callable).
        """
        def dummy_action():
            pass
        try:
            self.action_state.add_in_state_action(dummy_action)
        except Exception as e:
            self.fail(f"Adding action raised an unexpected exception: {e}")

    def test_add_exiting_action_valid(self):
        """
        Test adding exiting action with valid type (callable).
        """
        def dummy_action():
            pass
        try:
            self.action_state.add_exiting_action(dummy_action)
        except Exception as e:
            self.fail(f"Adding action raised an unexpected exception: {e}")

    def test_add_transition(self):
        """
        Test adding good transition.
        """
        transition = ActionTransition(self.action_state)
        try:
            self.action_state.add_transition(transition)
        except Exception as e:
            self.fail(f"Adding transition raised an unexpected exception: {e}")
    
    def test_add_exiting_action_invalid_type(self):
        """
        Test adding trnaisiton with invalid type.
        """
        with self.assertRaises(TypeError):
            self.action_state.add_transition("not a transition")


if __name__ == '__main__':
    unittest.main()