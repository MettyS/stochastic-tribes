# Written for Python 3.4.3

import random
import math
import copy


class Hamster(object):
    '''
    position is a (x, y) tuple
    darkness is a float from 0 (white) and 1 (black)
    '''

    def __init__(self, position, darkness, neighborRadius, bred):
        self.position = position
        self.darkness = darkness
        self.neighborRadius = neighborRadius
        self.age = 0
        self.bred = False

    def posNeighbors(self, neighbors):
        raise NotImplementedError

    def move(self, position):
        raise NotImplementedError

    def willDie(self):
        prob = math.exp(-0.003 * math.exp((self.age - 25) / 10))
        if random.random() < prob:
            return True
        elif random.random() >= prob:
            return False

    def age(self):
        self.age += 1

    def breed(self, neighbors):
        '''
        returns new hamster <3 if the attraction is there
        '''
        raise NotImplementedError

    def getBabyPos(self, wife):
        babyX = (self.position[0] + wife.position[0]) / 2
        babyY = (self.position[1] + wife.position[1]) / 2
        return (babyX, babyY)


class RacistHam(Hamster):
    def posNeighbors(self, neighbors):
        colorposX = [(hammy.position[0], (self.darkness - hammy.darkness) ** 2)
                     for hammy in neighbors]
        colorposY = [(hammy.position[1], (self. darkness - hammy.darkness) ** 2)
                     for hammy in neighbors]

        # Determining sum of weights
        weightSum = 0
        for hammy in colorposX:
            weightSum += hammy[1]

        # Calculating X
        Xpos = 0
        for hammy in colorposX:
            Xpos += hammy[0] * hammy[1]
        Xpos = Xpos / weightSum

        # Calculating Y
        Ypos = 0
        for hammy in colorposY:
            Ypos += hammy[0] * hammy[1]
        Ypos = Ypos / weightSum

        return (Xpos, Ypos)

    def move(self, neighbors):
        # Find weighted position of neighbors
        posNeighbors = self.posNeighbors(neighbors)

        # Random degree
        x = random.uniform(-5, 5)
        y = random.uniform(-5, 5)

        self.position = (posNeighbors[0] + x, posNeighbors[1] + y)

    def breed(self, neighbors):
        '''
        Racist hamster prefers his own color.  The probability of mating with
        any one hamster is a linear combination of weighted standard deviations
        for age and color
        '''
        random.shuffle(neighbors)
        for hammy in neighbors:
            avgDarkness = (self.darkness + hammy.darkness) / 2
            avgAge = (self.age + hammy.age)/2
            prob = 1 - (((self.darkness - hammy.darkness) ** 2) / avgDarkness) \
                - (((self.age - hammy.age) ** 2) / avgAge)

            # Breed!
            if random.random() < prob and not self.bred:
                babyPos = self.getBabyPos(hammy)
                darkness = (self.darkness + hammy.darkness) / 2
                neighborRadius = self.neighborRadius
                bred = False
                baby = RacistHam(babyPos, darkness, neighborRadius, bred)
                return baby

        return False


class Field(object):
    '''
    self.hamsters is a list of hamster objects
    self.size is a tuple describing the size of the playground
    '''

    def __init__(self, hamsters, size):
        self.size = size
        self.hamsters = hamsters

    def getNeighbors(self, hamster):
        neighbors = []
        for hammy in self.hamsters:
            dist = ((hamster.position[0] - hammy.position[0]) ** 2 +
                    (hamster.position[1] - hammy.position[1]) ** 2) ** 0.5
            if dist <= hamster.neighborRadius and hammy != hamster:
                neighbors.append(hammy)

    def updateField(self):
        # Kill the oldies
        oldhamsters = copy.copy(self.hamsters)
        for hammy in oldhamsters:
            if hammy.willDie():
                print("DEBUG KILL")
                self.hamsters.remove(hammy)
                # RIP

        for hammy in self.hamsters:
            neighbors = self.getNeighbors(hammy)

            # Breed them <3
            baby = hammy.breed(neighbors)
            if baby is not None:
                self.hamsters.append(baby)

            # Move them
            hammy.move(neighbors)

            # Check not out of bounds
            if hammy.position[0] > self.size[0]:
                hammy.position = (self.size[0], hammy.position[1])
            elif hammy.position[0] < 0:
                hammy.position = (0, hammy.position[1])
            if hammy.position[1] > self.size[1]:
                hammy.position = (hammy.position[0], self.size[1])
            elif hammy.position[1] < 0:
                hammy.position = (hammy.position[0], 0)

            # Age them
            hammy.age()

            # Make them horny again
            hammy.bred = False


def getInitialHamsters(number, size, HamClass):
    hamsters = []
    while len(hamsters) < number:
        pos = (random.uniform(0, size[0]), random.uniform(0, size[1]))
        darkness = random.random()
        neighborRadius = 10
        hamsters.append(HamClass(pos, darkness, neighborRadius, False))

    return hamsters


def main():
    # Values
    trials = 1000
    size = (600, 500)
    initHamsters = getInitialHamsters(400, size, RacistHam)
    theField = Field(initHamsters, size)

    # Run Loop
    for i in range(trials):
        theField.updateField()


if __name__ == "__main__":
    main()