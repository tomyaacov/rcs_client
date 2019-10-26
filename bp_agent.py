from soccerpy.agent import Agent


class BPAgent(Agent):

    def __init__(self, bprogram):
        self.bprogram = bprogram
        Agent.__init__(self)

    def think_loop(self):
        self.bprogram.run()

