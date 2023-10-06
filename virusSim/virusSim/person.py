import pygame as p, random, math

minMovement = 0.5
maxSpeed = 5

class Person():
    infection_count = 0  # Class-level counter to keep track of the number of infections
    total_people = 0  # Class-level counter to keep track of the number of Person instances
    colors = {"healthy": "white", "sick": "red", "recovered": "blue"}

    #status - "healthy, "sick", or recovered
    def __init__(self, x, y, status, socialDistancing):
        self.x = x
        self.y = y
        self.status  = status
        self.socialDistancing = socialDistancing
        self.radius = 6
        self.vx = self.vy = 0
        self.turnSick = 0
        self.recoveryTime = random.randint(100, 150)
        self.infected_by = None  # attribute to track who infected this person
        self.infections = 0  # count of how many others this person has infected

        if status == "sick" and Person.infection_count == 0:
            self.name = "Patient Zero"
        else:
            self.name = None  # Will be set when they get infected

        # Assign unique name to each person for charting
        if Person.total_people == 0:
            self.name = "Patient Zero"
        else:
            self.name = f"Person {Person.total_people}"

        Person.total_people += 1
        if not self.socialDistancing:
            while -minMovement < self.vx < minMovement and -minMovement < self.vy < minMovement:
                self.vx = random.uniform(-maxSpeed, maxSpeed)
                self.vy = random.uniform(-maxSpeed, maxSpeed)

    #Screen - The main surface
    def draw(self, screen):
        p.draw.circle(screen, p.Color(self.colors[self.status]), (round(self.x), round(self.y)), self.radius)

    #Execute once per frame
    def update(self, screen, people, boundary, height):
        self.move(boundary, height)
        if self.status == "sick":
            self.turnSick += 1
            if self.turnSick == self.recoveryTime:
                self.status = "recovered"

        # Check for collisions
        self.checkCollidingWithWall(boundary, height)  # Adjusted this line to pass boundary directly

        for other in people:
            if self != other and self.checkCollidingWithOther(other):
                self.updateCollisionVelocities(other)

                # Update infection status and increment the infector's count
                if self.status == "sick" and other.status == "healthy":
                    other.status = "sick"
                    self.infections += 1
                    Person.infection_count += 1
                    other.name = f"Patient {Person.infection_count}"
                    other.infected_by = self  # Update the infected_by attribute
                elif other.status == "sick" and self.status == "healthy":
                    self.status = "sick"
                    other.infections += 1
                    Person.infection_count += 1
                    self.name = f"Patient {Person.infection_count}"
                    self.infected_by = other  # Update the infected_by attribute

    def move(self, boundary, height):
        if not self.socialDistancing:
            self.x += self.vx
            self.y += self.vy

            # Ensure the dots stay within the boundary
            self.x = min(max(self.x, 0), boundary)
            self.y = min(max(self.y, 0), height)

    # Check for collisions with walls and updates velocities
    def checkCollidingWithWall(self, boundary, height):
        if self.x + self.radius >= boundary and self.vx > 0:  # Use boundary for left-right checks
            self.vx *= -1
        elif self.x - self.radius <= 0 and self.vx < 0:
            self.vx *= -1
        if self.y + self.radius >= height and self.vy > 0:  # Use HEIGHT directly for up-down checks
            self.vy *= -1
        elif self.y - self.radius <= 0 and self.vy < 0:
            self.vy *= -1

    #Return true if the self is colliding with other, False otherwise
    def checkCollidingWithOther(self, other):
        distance = math.sqrt(math.pow(self.x - other.x, 2) + math.pow(self.y - other.y, 2))
        if distance <= self.radius + other.radius:
            return True
        return False


    #Update velocities on collision
    def updateCollisionVelocities(self, other):
        if not self.socialDistancing and not other.socialDistancing:
            #Type 1 collision - both objects are moving
            tempVx = self.vx
            tempVy = self.vy
            self.vx = other.vx
            self.vy = other.vy
            other.vx = tempVx
            other.vy = tempVy

        #Type 2 collision - One object is moving and one is social distancing
        elif other.socialDistancing:
            magV = math.sqrt(math.pow(self.vx, 2) + math.pow(self.vy, 2)) #To make sure the new vector's mag is same
            tempVector = (self.vx + (self.x - other.x), self.vy + (self.y - other.y)) #Direction at which new vector should point (vector sum)
            magTempVector = math.sqrt(math.pow(tempVector[0], 2) + math.pow(tempVector[1], 2))
            normTempVector = (tempVector[0]/magTempVector, tempVector[1]/magTempVector) #Normalize vector (Make equal to one)
            self.vx = normTempVector[0] * magV #Ensure velocity after and before collision is the same
            self.vy = normTempVector[1] * magV