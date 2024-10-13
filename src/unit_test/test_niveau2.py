import unittest
from blinkers import Blinkers, SideBlinkers
from monitored import MonitoredState
from state import *
from typing import Optional
from fsm import * 


class FeuxStateOn(MonitoredState): 
    def __init__(self,  parameters: Optional[State.Parameters] = None):
        super().__init__(parameters)

class FeuxStateOff(MonitoredState): 
    def __init__(self, parameters: Optional[State.Parameters] = None):
        super().__init__(parameters)

def on_state_generator() -> MonitoredState:
    on_state = FeuxStateOn()
    return on_state

def off_state_generator() -> MonitoredState:
    off_state = FeuxStateOff()
    return off_state

class TestSecondNiveau(unittest.TestCase):
    def setUp(self) -> None:
        self.fsm = Blinkers(off_state_generator=off_state_generator, on_state_generator=on_state_generator)
        self.sb = SideBlinkers(left_off_state_generator=off_state_generator, left_on_state_generator=on_state_generator, right_off_state_generator=off_state_generator, right_on_state_generator=on_state_generator)

    ###########################
    # TEST instrants des blinks
    ###########################
    def test_blink1_percent_on_typeError(self) -> None:
        """
        Test TypeError when blink percent on is invalid.
        """
        with self.assertRaises(TypeError):
            self.fsm.blink(begin_on=True, percent_on=1)

    def test_blink1_percent_on_valueError(self) -> None:
        """
        Test ValueError when blink percent on is out of range.
        """
        with self.assertRaises(ValueError):
            self.fsm.blink(begin_on=True, percent_on=3.0)

    def test_blink2_cycle_duration_typeError(self) -> None:
        """
        Test ValueError when blink cycle_duration is not float.
        """
        with self.assertRaises(TypeError):
            self.fsm.blink(total_duration=3.0, cycle_duration=1, begin_on=True, percent_on=0.25)

    def test_blink2_total_duration_typeError(self) -> None:
        """
        Test ValueError when blink total_duration is not float.
        """
        with self.assertRaises(TypeError):
            self.fsm.blink(total_duration=3, cycle_duration=1.0, begin_on=True, percent_on=0.25)

    def test_blink2_percent_on_valueError(self) -> None:
        """
        Test ValueError when blink percent_on is out of range.
        """
        with self.assertRaises(ValueError):
            self.fsm.blink(total_duration=1.0, cycle_duration=1.0, begin_on=True, percent_on=3.25)

    def test_blink2_begin_on_typeError(self) -> None:
        """
        Test ValueError when begin on is not bool.
        """
        with self.assertRaises(ValueError):
            self.fsm.blink(total_duration=1.0, cycle_duration=1.0, begin_on=1, percent_on=3.25)

    def test_blink3_total_duration_typeError(self) -> None:
        """
        Test ValueError when blink total_duration is not float.
        """
        with self.assertRaises(TypeError):
            self.fsm.blink(total_duration=3, n_cycles = 1, begin_on=True, percent_on=0.25)

    def test_blink3_begin_on_typeError(self) -> None:
        """
        Test ValueError when begin on is not bool.
        """
        with self.assertRaises(ValueError):
            self.fsm.blink(total_duration=1.0, n_cycles = 1, begin_on=1, percent_on=3.25)

    def test_blink3_n_cycle_typeError(self) -> None:
        """
        Test ValueError when begin on is not bool.
        """
        with self.assertRaises(ValueError):
            self.fsm.blink(total_duration=1.0, n_cycles = 1.0, begin_on=True, percent_on=3.25)
    
    def test_blink3_n_cycle_valueError(self) -> None:
        """
        Test ValueError when n cycle is negative.
        """
        with self.assertRaises(ValueError):
            self.fsm.blink(total_duration=1.0, n_cycles = -1, begin_on=True, percent_on=0.25)

    def test_blink4_n_cycle_valueError(self) -> None:
        """
        Test ValueError when n cycle is negative.
        """
        with self.assertRaises(ValueError):
            self.fsm.blink(n_cycles = -3, cycle_duration= 1.0, percent_on = 0.5, begin_on = True, end_off = True)

    def test_blink4_cycle_duration_valueError(self) -> None:
        """
        Test ValueError when cycle duration is negative.
        """
        with self.assertRaises(ValueError):
            self.fsm.blink(n_cycles = 2, cycle_duration= -1.0, percent_on = 0.5, begin_on = True, end_off = True)

    def test_blink4_n_cycle_typeError(self) -> None:
        """
        Test ValueError when cycle duration is negative.
        """
        with self.assertRaises(TypeError):
            self.fsm.blink(n_cycles = "2", cycle_duration= 1.0, percent_on = 0.5, begin_on = True, end_off = True)

    ###################
    # TEST Side Blinker
    ###################
    def test_side_blinker_on(self) -> None:
        """
        Test is not on for LEFT blinker.
        """
        self.assertFalse(self.sb.on(SideBlinkers.Side.LEFT))

    def test_side_blinker_off(self) -> None:
        """
        Test is off for LEFT blinker.
        """
        self.assertTrue(self.sb.off(SideBlinkers.Side.LEFT))
        
    def test_side_bliker_off_typeError(self) -> None:
        """
        Test raise valueError because BOTH.
        """
        with self.assertRaises(ValueError):
            self.sb.off(SideBlinkers.Side.BOTH)

    def test_side_bliker_on_typeError_01(self) -> None:
        """
        Test raise valueError because BOTH.
        """
        with self.assertRaises(ValueError):
            self.sb.on(SideBlinkers.Side.BOTH)
    
    def test_side_bliker_on_typeError_02(self) -> None:
        """
        Test raise valueError because LEFT_RECIPROCAL.
        """
        with self.assertRaises(ValueError):
            self.sb.on(SideBlinkers.Side.LEFT_RECIPROCAL)
    
    ############################
    # TEST blink sur .off et .on
    ############################
    def test_inital_state_status_01(self) -> None:
        """
        Test initial state status.
        """
        self.assertTrue(self.fsm.off, "Must be True")

    def test_inital_state_status_02(self) -> None:
        """
        Test initial state status.
        """
        self.assertFalse(self.fsm.on, "Must be False")

if __name__ == '__main__':
    unittest.main()