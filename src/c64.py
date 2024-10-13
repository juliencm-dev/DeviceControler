from manual_control import ManualControlFSM, RemoteCondition, RemoteConditionOK, ServoParams
from state import State
from conditional import ConditionalTransition, AlwaysTrueCondition
from monitored import StateEntryDurationCondition
from fsm import FiniteStateMachine
from message_state import MessageState, IntegrityCheckCondition, InstanciateCheckCondition, RobotState
from robot import Robot, EyeBlinkerParams
from blinkers import SideBlinkers
from color import Color
from typing import Callable, List, TYPE_CHECKING

if TYPE_CHECKING:
    from state import State
        

class RobotTaskState(RobotState):
    def __init__(self, robot: Robot, robot_fsm: FiniteStateMachine, setup_action: List[Callable], clean_up_actions: List[Callable]):
        super().__init__(robot)
        self.__fsm: FiniteStateMachine = robot_fsm
        self.__setup_actions = setup_action
        self.__clean_up_actions = clean_up_actions
        
    def _do_entering_action(self) -> None:
        super()._do_entering_action()
        self.setup()
        
    def _do_in_state_action(self) -> None:
        super()._do_in_state_action()
        self.__fsm.track()
    
    def _do_exiting_action(self) -> None:
        super()._do_exiting_action()
        self.clean_up()
    
    def setup(self):
        for action in self.__setup_actions:
            action()
    
    def clean_up(self):
        for action in self.__clean_up_actions:
            action()


class TaskOne(RobotTaskState):
    def __init__(self, robot: Robot):
        
        robot_fsm = ManualControlFSM(robot)
        
        eyes_blinkers = EyeBlinkerParams(robot, SideBlinkers.Side.LEFT_RECIPROCAL)
        
        setup_actions = [lambda: robot.set_eye_colors(SideBlinkers.Side.LEFT, Color(Color.ColorBase.RED.value)), lambda: robot.set_eye_colors(SideBlinkers.Side.RIGHT, Color(Color.ColorBase.BLUE.value)), eyes_blinkers.action ]
        clean_up_actions = [lambda: robot.set_eye_colors(SideBlinkers.Side.BOTH, Color(Color.ColorBase.BLACK.value)), lambda: (robot.close_led_blinkers(SideBlinkers.Side.BOTH), robot.close_eyes(SideBlinkers.Side.BOTH))]
        
        super().__init__(robot, robot_fsm, setup_actions, clean_up_actions)
        
class TaskTwo(RobotTaskState):
    def __init__(self, robot: Robot):
        
        move_servo_right: ServoParams = ServoParams(45, robot)
        reset_servo_right: ServoParams = ServoParams(0, robot)
        move_servo_left: ServoParams = ServoParams(-45, robot)
        
        move_servo_right_actions = [[ move_servo_right.action], [], [], [RemoteCondition(robot, Robot.RemoteKeyCode.THREE)]]
        reset_servo_right_actions = [[ reset_servo_right.action], [], [], [RemoteCondition(robot, Robot.RemoteKeyCode.TWO)]]
        move_servo_left_actions = [[ move_servo_left.action], [], [], [RemoteCondition(robot, Robot.RemoteKeyCode.ONE)]]

        robot_fsm = ManualControlFSM(robot, [move_servo_right_actions, move_servo_left_actions, reset_servo_right_actions])
        
        eyes_blinkers = EyeBlinkerParams(robot, SideBlinkers.Side.BOTH)
        
        setup_actions = [lambda: robot.set_eye_colors(SideBlinkers.Side.LEFT, Color(Color.ColorBase.MAGENTA.value)), lambda: robot.set_eye_colors(SideBlinkers.Side.RIGHT, Color(Color.ColorBase.GREEN.value)), eyes_blinkers.action]
        clean_up_actions = [lambda: robot.set_eye_colors(SideBlinkers.Side.BOTH, Color(Color.ColorBase.BLACK.value)), lambda: (robot.close_led_blinkers(SideBlinkers.Side.BOTH), robot.close_eyes(SideBlinkers.Side.BOTH))]
        
        super().__init__(robot, robot_fsm, setup_actions, clean_up_actions)
        
        self.add_in_state_action(self.__change_color_from_range)
        
    def __change_color_from_range(self):
        
        color = Color(Color.ColorBase.RED.value)
        
        if self._robot.current_distance > 0.75:
            color = Color(Color.ColorBase.GREEN.value)
        elif self._robot.current_distance > 0.50:
            color = Color(Color.ColorBase.ORANGE.value)
        elif self._robot.current_distance > 0.25:
            color = Color(Color.ColorBase.YELLOW.value)
            
        self._robot.set_eye_colors(SideBlinkers.Side.RIGHT, color)
            
        

class C64(FiniteStateMachine):
    def __init__(self, unitialized: bool = True):
        self.__robot = Robot()
        self.__nb_tasks: int = 0

        layout: FiniteStateMachine.Layout = FiniteStateMachine.Layout()
        end_state : MessageState = MessageState(self.__robot, "The Gopigo Robot application is now turned off.", parameters= State.Parameters(terminal = True))
        
        shut_down_robot_state: MessageState = self.__message_state_generator(self.__robot, "Shutting down the Gopigo Robot", 3.0, end_state, 0.75, Color(Color.ColorBase.YELLOW.value), SideBlinkers.Side.LEFT_RECIPROCAL) 
        shut_down_robot_state.add_exiting_action(lambda: self.__robot.close_eyes(SideBlinkers.Side.BOTH))
        integrity_failed_state: MessageState = self.__message_state_generator(self.__robot,"Gopigo Robot integrity check : FAILED", 5.0, shut_down_robot_state, 0.5, Color(Color.ColorBase.RED.value), SideBlinkers.Side.BOTH)
        
        instantiation_failed_state: MessageState = MessageState(self.__robot, "Gopigo Robot instanciation check : FAILED")
        instantiation_failed_state_condition : AlwaysTrueCondition = AlwaysTrueCondition()
        instantiation_failed_state_transition: ConditionalTransition = ConditionalTransition(instantiation_failed_state_condition)
        instantiation_failed_state_transition.next_state : State = end_state
        
        self.__home_state: RobotState = RobotState(self.__robot)
        
        integrity_succeded_state: MessageState = self.__message_state_generator(self.__robot, "Gopigo Robot integrity check : SUCCESS", 3.0, self.__home_state, 1.0, Color(Color.ColorBase.GREEN.value), SideBlinkers.Side.BOTH)
                
        home_state_remote_condition: RemoteConditionOK = RemoteConditionOK(self.__robot, Robot.RemoteKeyCode.OK)
        home_state_transition_end: ConditionalTransition = ConditionalTransition(home_state_remote_condition)
        home_state_transition_end.next_state: State = shut_down_robot_state
        
        home_blinker_param = EyeBlinkerParams(self.__robot, SideBlinkers.Side.BOTH)
        home_blinker_param.set_cycle_duration(1.5)
        
        self.__home_state.add_entering_action(lambda: self.__robot.set_eye_colors(SideBlinkers.Side.BOTH, Color(Color.ColorBase.YELLOW.value)))
        self.__home_state.add_entering_action(home_blinker_param.action)
        
        self.__home_state.add_exiting_action(lambda: self.__robot.close_eyes(SideBlinkers.Side.BOTH))
        self.__home_state.add_exiting_action(self.__robot.stop_eye_blinkers)
        
        self.__home_state.add_transition(home_state_transition_end)

        integrity_state: State = self.__validation_state_generator(self.__robot, integrity_succeded_state, integrity_failed_state, False)
        instantiation_state: State = self.__validation_state_generator(self.__robot, integrity_state, instantiation_failed_state)

        layout.add_states([instantiation_state, instantiation_failed_state, integrity_state, integrity_succeded_state, integrity_failed_state, 
                           shut_down_robot_state, end_state, self.__home_state])
        
        
        layout.initial_state = instantiation_state
        
        self.__add_task(TaskOne(self.__robot), layout)
        self.__add_task(TaskTwo(self.__robot), layout)
        
        super().__init__(layout, unitialized)

    @property
    def nb_tasks(self):
        return self.__nb_tasks
    
    
    def __add_task(self, task: RobotTaskState, layout: FiniteStateMachine.Layout) -> None:
        
        if not isinstance(task, RobotTaskState):
            raise TypeError("Task must be a RobotTaskState")
        
        exit_condition = RemoteConditionOK(self.__robot, Robot.RemoteKeyCode.OK)
        exit_transition = ConditionalTransition(exit_condition)
        exit_transition.next_state = self.__home_state
        
        task_condition = RemoteCondition(self.__robot, Robot.RemoteKeyCode(Robot.RemoteKeyCode.ONE + self.__nb_tasks))
        task_transition = ConditionalTransition(task_condition)
        task_transition.next_state: State = task
        
        task.add_transition(exit_transition)
        self.__home_state.add_transition(task_transition)
        
        layout.add_state(task)

        self.__nb_tasks += 1
        
    
    
    def add_task(self, task: RobotTaskState) -> None:
        
        if not isinstance(task, RobotTaskState):
            raise TypeError("Task must be a RobotTaskState")
        
        exit_condition = RemoteCondition(self.__robot, Robot.RemoteKeyCode.OK)
        exit_transition = ConditionalTransition(exit_condition)
        exit_transition.next_state = self.__home_state
        
        task_condition = RemoteCondition(self.__robot, Robot.RemoteKeyCode(Robot.RemoteKeyCode.ONE + self.__nb_tasks))
        task_transition = ConditionalTransition(task_condition)
        task_transition.next_state: State = task
        
        task.add_transition(exit_transition)
        self.__home_state.add_transition(task_transition)
        
        self.__layout.add_state(task)
        # valide en boucle toutes les choses
        if not self.__layout.valid:
            raise ValueError("The layout is not valid")

        self.__nb_tasks += 1
        
    
    def __validation_state_generator(self, robot: Robot, next_state_succeded:State, next_state_failed:State, instanciate = True ) -> State:
        robot_state: State = State()
        
        if instanciate: 
            robot_condition_succeded: InstanciateCheckCondition = InstanciateCheckCondition(robot)
            robot_condition_failed: InstanciateCheckCondition = InstanciateCheckCondition(robot, inverse=True)
        else:
            robot_condition_succeded: IntegrityCheckCondition = IntegrityCheckCondition(robot)
            robot_condition_failed: IntegrityCheckCondition = IntegrityCheckCondition(robot, inverse=True)
        
        robot_transition_succeded: ConditionalTransition = ConditionalTransition(robot_condition_succeded)
        robot_transition_failed: ConditionalTransition = ConditionalTransition(robot_condition_failed)
        robot_transition_succeded.next_state: State = next_state_succeded
        robot_transition_failed.next_state: State = next_state_failed
        
        robot_state.add_transition(robot_transition_succeded)
        robot_state.add_transition(robot_transition_failed)
        return robot_state
    
    def __message_state_generator(self, robot: Robot, message: str, duration: float, next_state:State, cycle_duration:float, color: Color, side: SideBlinkers.Side) -> MessageState:
        robot_state: MessageState = MessageState(robot, message)
        robot_condition: StateEntryDurationCondition = StateEntryDurationCondition(duration, robot_state)
        robot_transition: ConditionalTransition = ConditionalTransition(robot_condition)
        robot_transition.next_state = next_state
        robot_state.add_transition(robot_transition)
        
        blinker_param = EyeBlinkerParams(robot, side)
        blinker_param.set_cycle_duration(cycle_duration)
        
        robot_state.add_entering_action(lambda: robot.set_eye_colors(SideBlinkers.Side.BOTH, color))
        robot_state.add_entering_action(blinker_param.action)
        
        return robot_state
    
    

    
        
        