
class Player(object):
    def __init__(self, id, avatar):
        self.id = id
        self.avatar = avatar

    # TODO: this should be swapped out with whatever serialization we choose
    def serialize(self):
        return {
        'id': self.id,
        'avatar': self.avatar
    }
