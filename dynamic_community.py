
class DynamicCommunity:

    def __init__(self, community, step=0, timeline={}):

        self._front = None  # the last step community
        self._split = None  # a tuple containing the parent community and the step of the split
        self._split_at = None  # the step when this was split into multiple communities
        self._dead = None  # whether this dc dissolved (remained unobserved for a set number of steps)
        self._timeline = dict(timeline)  # a dictionary of all step communities
        self._unobserved = 0  # for how many steps this dc remained unobserved
        self.add_community(community, step)

    def add_community(self, community, step):
        self._timeline[step] = community
        self._front = (community, step)

    def define_split(self, parent_community, step):
        self._split = (parent_community, step)

    def define_split_step(self, step):
        self._split_at = step

    def unobserved(self, inc=1):
        self._unobserved += inc
        return self._unobserved

    def observed(self):
        self._unobserved = 0

    def get_front(self):
        return self._front

    def get_timeline(self):
        return self._timeline

    def get_split(self):
        return self._split

    def get_split_step(self):
        return self._split_at

    def kill(self, t):
        self._dead = t

    def is_dead(self):
        return self._dead
