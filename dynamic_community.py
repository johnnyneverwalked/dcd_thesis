
class DynamicCommunity:

    def __init__(self, community, step=1, timeline={}):

        self._front = None
        self._split = None
        self._dead = False
        self._timeline = dict(timeline)
        self._unobserved = 0
        self.add_community(community, step)

    def add_community(self, community, step):
        self._timeline[step] = community
        self._front = (community, step)

    def define_split(self, parent_community, step):
        self._split = (parent_community, step)

    def unobserved(self, inc=1):
        self._unobserved += inc
        return self._unobserved

    def observed(self):
        self._unobserved = 0

    def get_front(self):
        return self._front

    def get_timeline(self):
        return self._timeline

    def kill(self):
        self._dead = True

    def is_dead(self):
        return self._dead
