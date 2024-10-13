from robot import Robot, BlinkerParams, LedBlinkerParams, RobotParams
from fsm import FiniteStateMachine
from state import State
from conditional import Condition, ConditionalTransition
from blinkers import SideBlinkers 
from typing import Optional, Tuple
from action import ActionState
from typing import Callable, List

class RemoteCondition(Condition): 
    def __init__(self,  robot: Robot, expected_key: Robot.RemoteKeyCode, inverse: bool = False):
        self.__expected_key: Robot.RemoteKeyCode = expected_key
        self.__robot: Robot = robot
        super().__init__(inverse)
        
    def _compare(self) -> bool: 
        return self.__robot.get_remote_key() == self.__expected_key
    
class RemoteConditionOK(Condition): 
    def __init__(self,  robot: Robot, expected_key: Robot.RemoteKeyCode, inverse: bool = False):
        self.__expected_key: Robot.RemoteKeyCode = expected_key
        self.__robot: Robot = robot
        super().__init__(inverse)
        
    def _compare(self) -> bool: 
        return self.__robot.get_state_remote_key() == self.__expected_key

    
class ManualControlState(State): 
    def __init__(self, robot: Robot, direction: Robot.DirectionKey, blinker_params: BlinkerParams): 
        self.__robot: Robot = robot
        self.__direction : Robot.DirectionKey = direction
        self.__blinker_params: BlinkerParams = blinker_params
        super().__init__()    
        
    def _do_entering_action(self) -> None:
        self.__robot.move(self.__direction)
        self.__robot.blink_led(self.__blinker_params)
        super()._do_entering_action()
        
    def _do_in_state_action(self) -> None:
        super()._do_in_state_action()
        # self.__robot.track()
    
    def _do_exiting_action(self) -> None:
        self.__robot.move(Robot.DirectionKey.STOP)
        self.__robot.close_led_blinkers(SideBlinkers.Side.BOTH)
        self.__robot.reset_led_blinkers()
        super()._do_exiting_action()


class ManualControlFSM(FiniteStateMachine): 
                
    def __init__(self, robot: Robot, optionnals_actions:Optional[List[List[Callable]]]=None ): 
        
        forward_param_blinker: BlinkerParams = LedBlinkerParams(robot, SideBlinkers.Side.BOTH, 0.25)
        rotate_right_param_blinker: BlinkerParams = LedBlinkerParams(robot, SideBlinkers.Side.RIGHT, 0.5)
        rotate_left_param_blinker: BlinkerParams = LedBlinkerParams(robot, SideBlinkers.Side.LEFT, 0.5)
        backward_param_blinker: BlinkerParams = LedBlinkerParams(robot, SideBlinkers.Side.BOTH, 0.75)

        foward_param: MoveParams = MoveParams(robot, Robot.RemoteKeyCode(Robot.DirectionKey.FORWARD))
        rotate_right_param: MoveParams = MoveParams(robot, Robot.RemoteKeyCode(Robot.DirectionKey.RIGHT))
        rotate_left_param: MoveParams = MoveParams(robot, Robot.RemoteKeyCode(Robot.DirectionKey.LEFT))
        backward_param: MoveParams = MoveParams(robot, Robot.RemoteKeyCode(Robot.DirectionKey.BACKWARD))
        
        exit_action = [lambda: robot.move(Robot.DirectionKey.STOP), lambda: robot.close_led_blinkers(SideBlinkers.Side.BOTH), lambda: robot.stop_led_blinkers()]
        
        foward_actions = [[foward_param.action, forward_param_blinker.action], [robot.track], exit_action, [RemoteCondition(robot, Robot.RemoteKeyCode(Robot.DirectionKey.FORWARD))]]
        rotate_right_actions = [[rotate_right_param.action, rotate_right_param_blinker.action], [robot.track], exit_action, [RemoteCondition(robot, Robot.RemoteKeyCode(Robot.DirectionKey.RIGHT))]]
        rotate_left_actions = [[rotate_left_param_blinker.action, rotate_left_param.action], [robot.track], exit_action, [RemoteCondition(robot, Robot.RemoteKeyCode(Robot.DirectionKey.LEFT))]]
        backward_actions = [[ backward_param_blinker.action, backward_param.action], [robot.track], exit_action, [RemoteCondition(robot, Robot.RemoteKeyCode(Robot.DirectionKey.BACKWARD))]]
        
        layout = manual_control_layout_generator(robot, [foward_actions, rotate_left_actions, rotate_right_actions, backward_actions], optionnals_actions)
        super().__init__(layout) 
        


def manual_control_state_generator(stop_transition, *,  entering_actions: List[Callable], in_actions: List[Callable], exiting_actions: List[Callable], conditions: List[Condition]) -> Tuple[ActionState, ConditionalTransition]:
    state: ActionState = ActionState()
    #ManualControlState(robot, Robot.DirectionKey(key_code), blinker_params)
    
    for action in entering_actions: 
        state.add_entering_action(action)
        
    for action in in_actions: 
        state.add_in_state_action(action)
        
    for action in exiting_actions: 
        state.add_exiting_action(action)
    
    state.add_transition(stop_transition)
    
    state_transitions = []
    for condition in conditions: 
        transition = ConditionalTransition(condition)
        transition.next_state = state
        state_transitions.append(transition)
    
    return (state, state_transitions)    
    
def manual_control_layout_generator(robot: Robot, states_actions:List[List[Callable]], optionnals_actions:Optional[List[List[Callable]]] = None): 
    
    actions = states_actions
    optionnal_actions = [] if optionnals_actions is None else optionnals_actions
    actions.extend(optionnal_actions)
    
    layout: FiniteStateMachine.Layout = FiniteStateMachine.Layout()
    stop: State = State()
    stop_condition: RemoteCondition = RemoteCondition(robot, Robot.RemoteKeyCode(Robot.DirectionKey.STOP))
    stop_transition: ConditionalTransition = ConditionalTransition(stop_condition)
    stop_transition.next_state = stop
    
    for action in actions: 
        state, transitions = manual_control_state_generator(stop_transition, entering_actions = action[0], in_actions = action[1], exiting_actions = action[2], conditions= action[3])
        for transition in transitions:
            stop.add_transition(transition)
        layout.add_state(state)        

    layout.add_state(stop)
        
        
    layout.initial_state = stop
    return layout
    

class MoveParams(RobotParams):
    def __init__(self, robot: Robot, key_code: Robot.RemoteKeyCode ): 
        self.__key_code = key_code
        self.__direction =  Robot.DirectionKey(key_code)
        
        super().__init__(robot)
    
    @property
    def action(self) -> Callable: 
        return lambda: self._robot.move(self.__direction)
    @property
    def condition(self): 
        return RemoteCondition(self._robot, self.__key_code)

class ServoParams(RobotParams): 
    def __init__(self, angle, robot:Robot): 
        self.__angle:int = angle
        super().__init__(robot)
        
    @property
    def action(self) -> Callable:
        return lambda: self._robot.range_servo.move(self.__angle)
    
if __name__ == "__main__":
    robot = Robot()
    print("instanciate: ", robot.instanciate)
    print("integrity: ", robot.integrity)
    manual_control = ManualControlFSM(robot)
    
    while robot.get_remote_key() != 3:
        manual_control.track()