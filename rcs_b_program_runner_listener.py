from execution.listeners.b_program_runner_listener import BProgramRunnerListener
import time
import message_parser
import sp_exceptions

class RCSBProgramRunnerListener(BProgramRunnerListener):

    def starting(self, b_program):
        print("S")
        if self.agent.send_commands:
            self.agent.send_commands = False
            self.agent.wm.ah.send_commands()

    def started(self, b_program):
        pass

    def super_step_done(self, b_program):
        pass

    def ended(self, b_program):
        print("E")
        pass

    def assertion_failed(self, b_program):
        pass

    def b_thread_added(self, b_program):
        pass

    def b_thread_removed(self, b_program):
        pass

    def b_thread_done(self, b_program):
        pass

    def event_selected(self, b_program, event):
        print(event)
        # get all the expressions contained in the given message
        parsed = message_parser.parse(event.name)

        if hasattr(self.agent.wm.ah, parsed[0]):
            # call the appropriate function with this message
            getattr(self.agent.wm.ah, parsed[0]).__call__(*parsed[1:])

        # throw an exception if we don't know about the given message type
        else:
            m = "Can't handle event type '%s', function '%s' not found."
            raise sp_exceptions.EventTypeError(m % (parsed[0], parsed[0]))

        if self.agent.send_commands:
            self.agent.send_commands = False
            self.agent.wm.ah.send_commands()

        while True:
            if self.agent.should_think_on_data:
                # flag that data has been processed.  this shouldn't be a race
                # condition, since the only change would be to make it True
                # before changing it to False again, and we're already going to
                # process data, so it doesn't make any difference.
                self.agent.should_think_on_data = False
                break
            else:
                # prevent from burning up all the cpu time while waiting for data
                time.sleep(0.0001)

        if not self.agent.thinking:
            return True, self.agent.wm
        else:
            return False, self.agent.wm

    def halted(self, b_program):
        pass

    def __init__(self, agent):
        self.agent = agent
        super().__init__()


