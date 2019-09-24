from model.b_event import BEvent
from rcs_b_program_runner_listener import RCSBProgramRunnerListener
from model.bprogram import BProgram
from model.event_selection.simple_event_selection_strategy import SimpleEventSelectionStrategy
from bp_agent import BPAgent
import time
from model.b_event import All
from world_model import WorldModel


def start():
    yield {'request': BEvent(name="(move 10 10)")}


def move_towards_ball():
    m, wm = yield {'waitFor': All()}
    while True:
        if wm.ball is None:
            m, wm = yield {'waitFor': All()}
        else:
            if wm.ball.distance is not None:
                if wm.ball.distance > 0.7:
                    m, wm = yield {'request': BEvent(name="(dash 65)")}
                else:
                    m, wm = yield {'waitFor': All()}
            else:
                m, wm = yield {'waitFor': All()}


def spin_to_ball():
    m, wm = yield {'waitFor': All()}
    m, wm = yield {'request': BEvent(name="(turn 30)")}
    while True:
        if wm.ball is None:
            m, wm = yield {'request': BEvent(name="(turn 30)")}
        else:
            if wm.ball.direction is not None:
                direction = str(wm.ball.direction / 2)
                m, wm = yield {'request': BEvent(name="(turn " + direction + ")")}
            else:
                m, wm = yield {'request': BEvent(name="(turn 30)")}

def kick_ball():
    m, wm = yield {'waitFor': All()}
    if wm.side == WorldModel.SIDE_R:
        goal_pos = (-55, 0)
    else:
        goal_pos = (55, 0)
    while True:
        if wm.is_ball_kickable():
            # how far are we from the desired point?
            # point_dist = wm.euclidean_distance(wm.abs_coords, goal_pos)
            #
            # # get absolute direction to the point
            # abs_point_dir = wm.angle_between_points(wm.abs_coords, goal_pos)
            #
            # # get relative direction to point from body, since kicks are relative to
            # # body direction.
            # if wm.abs_body_dir is not None:
            #     rel_point_dir = wm.abs_body_dir - abs_point_dir
            # print(rel_point_dir)
            if len(wm.goals) > 0:
                wm.ah.kick(wm.goals[0].direction, wm.server_parameters.maxpower)
                m, wm = yield {'waitFor': All()}
            else:
                m, wm = yield {'waitFor': All()}
        else:
            m, wm = yield {'waitFor': All()}


if __name__ == "__main__":
    import sys
    import multiprocessing as mp

    # enforce corrent number of arguments, print help otherwise
    if len(sys.argv) < 3:
        print ("args: ./agent.py <team_name> <num_players>")
        sys.exit()

    def spawn_agent(team_name):
        """
        Used to run an agent in a separate physical process.
        """

        b_program = BProgram(bthreads=[start(), move_towards_ball(), spin_to_ball(), kick_ball()],
                             event_selection_strategy=SimpleEventSelectionStrategy())
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
    for agent in range(min(11, int(sys.argv[2]))):
        print ("  Spawning agent %d..." % agent)

        at = mp.Process(target=spawn_agent, args=(sys.argv[1],))
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

