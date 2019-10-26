from bp.model.b_event import BEvent
from rcs_b_program_runner_listener import RCSBProgramRunnerListener
from bp.model.bprogram import BProgram
from bp.model.event_selection.simple_event_selection_strategy import SimpleEventSelectionStrategy
from bp_agent import BPAgent
import time
from bp.model.b_event import All


def start():
    yield {'request': BEvent(name="(move -40 15)")}


def move_towards_ball():
    m, wm = yield {'waitFor': All()}
    while True:
        if wm.ball is not None and wm.ball.distance is not None and wm.ball.distance > wm.server_parameters.kickable_margin:
            m, wm = yield {'request': BEvent(name="(dash 65)")}
        else:
            m, wm = yield {'waitFor': All()}


def spin_to_ball():
    m, wm = yield {'waitFor': All()}
    while True:
        if wm.ball is not None and wm.ball.direction is not None:
            direction = str(wm.ball.direction / 2)
            m, wm = yield {'request': BEvent(name="(turn " + direction + ")")}
        else:
            m, wm = yield {'request': BEvent(name="(turn 30)")}


def kick_ball():
    m, wm = yield {'waitFor': All()}
    while True:
        if wm.ball is not None and wm.ball.distance is not None and wm.ball.distance <= wm.server_parameters.kickable_margin:
            target_in_sight = [x for x in wm.goals if x.goal_id == 'r']
            if len(target_in_sight) > 0:
                power = wm.server_parameters.maxpower / 2
                direction = target_in_sight[0].direction
                m, wm = yield {'request': BEvent(name="(kick " + str(power) + " " + str(direction) + ")")}
            else:
                m, wm = yield {'waitFor': All()}
        else:
            m, wm = yield {'waitFor': All()}


if __name__ == "__main__":
    import sys
    import multiprocessing as mp

    # enforce corrent number of arguments, print help otherwise
    if len(sys.argv) < 2:
        print ("args: ./base_controller.py <team_name>")
        sys.exit()

    def spawn_agent(team_name, b_program):
        """
        Used to run an agent in a separate physical process.
        """

        a = BPAgent(bprogram=b_program)
        a.bprogram.listener = RCSBProgramRunnerListener(a)

        a.connect("localhost", 6000, team_name)
        a.play()

        # we wait until we're killed
        while 1:
            # we sleep for a good while since we can only exit if terminated.
            time.sleep(1)

    # spawn all agents as seperate processes for maximum processing efficiency
    agentthreads = []
    b_programs = [BProgram(bthreads=[start(), move_towards_ball(), spin_to_ball(), kick_ball()],
                           event_selection_strategy=SimpleEventSelectionStrategy())]
    for i in range(min(11, len(b_programs))):
        print ("  Spawning agent %d..." % i)

        at = mp.Process(target=spawn_agent, args=(sys.argv[1], b_programs[i]))
        at.daemon = True
        at.start()

        agentthreads.append(at)

    print ("Spawned %d agents." % len(agentthreads))
    print()
    print ("Playing soccer...")

    # wait until killed to terminate agent processes
    try:
        while 1:
            time.sleep(0.05)
    except KeyboardInterrupt:
        print()
        print ("Killing agent threads...")

        # terminate all agent processes
        count = 0
        for at in agentthreads:
            print ("  Terminating agent %d..." % count)
            at.terminate()
            count += 1
        print ("Killed %d agent threads." % (count - 1))

        print()
        print("Exiting.")
        sys.exit()

