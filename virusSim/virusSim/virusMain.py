import pygame as p, random, math
import networkx as nx
from virusSim.person import Person

# Initialize a graph to track connections between infected individuals
graph = nx.Graph()
positions = {}  # New dictionary to track node positions in the graph

WIDTH, HEIGHT = 1500, 800  # Adjusted for a third section

# Constants for screen segmentation
CHART_WIDTH = WIDTH // 5  # Adjusted for a smaller chart section
SIMULATION_WIDTH = WIDTH // 3
GRAPH_WIDTH = WIDTH - CHART_WIDTH  # Remaining width minus the chart width

# To keep the graph in its resp. boundaries
GRAPH_START = SIMULATION_WIDTH
GRAPH_END = GRAPH_WIDTH

def main():
    p.init()

    screen = p.display.set_mode([WIDTH, HEIGHT])
    p.display.set_caption("Virus Simulation & Graph Display")
    screen.fill(p.Color("gray"))

    clock = p.time.Clock()
    MAX_FPS = 15

    # Setting up fonts for the titles
    font = p.font.SysFont(None, 36)  # You can replace None with a specific font name if you have one in mind.
    left_title = font.render("Virus Simulation", True, p.Color("black"))
    right_title = font.render("Graphical Display", True, p.Color("black"))

    spawnBuffer = 20
    numPeople = 50
    factorOfPeopleAreSocialDistancing = 0.0

    patientZero = Person(random.randint(spawnBuffer, SIMULATION_WIDTH - spawnBuffer),
                         random.randint(spawnBuffer, HEIGHT - spawnBuffer), "sick", False)
    people = [patientZero]

    for i in range(numPeople - 1):
        socialDistancing = False
        if i < factorOfPeopleAreSocialDistancing * numPeople:
            socialDistancing = True
        colliding = True
        while colliding:
            person = Person(random.randint(spawnBuffer, SIMULATION_WIDTH - spawnBuffer),
                            random.randint(spawnBuffer, HEIGHT - spawnBuffer), "healthy", socialDistancing)
            colliding = False
            for person2 in people:
                if person.checkCollidingWithOther(person2):
                    colliding = True
                    break
        people.append(person)

    running = True
    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False

        for person in people:
            person.update(screen, people, SIMULATION_WIDTH, HEIGHT)

        update_graph(people, graph)

        screen.fill(p.Color("gray"))

        # Draw a black border in the middle of the screen
        p.draw.line(screen, p.Color("black"), (SIMULATION_WIDTH, 0), (SIMULATION_WIDTH, HEIGHT), 2)  # Updated from HALF_WIDTH to SIMULATION_WIDTH
        p.draw.line(screen, p.Color("black"), (GRAPH_WIDTH, 0), (GRAPH_WIDTH, HEIGHT), 2)  # Separate graph from chart

        # Drawing titles
        screen.blit(left_title, (SIMULATION_WIDTH//2 - left_title.get_width()//2, 10))
        screen.blit(right_title, (SIMULATION_WIDTH + (SIMULATION_WIDTH//2) - right_title.get_width()//2, 10))

        for person in people:
            person.draw(screen)

        draw_graph_edges(screen, graph, people)

        # Draw the new infection chart
        draw_infection_chart(screen, people)

        p.display.flip()
        clock.tick(MAX_FPS)

    p.quit()


def draw_infection_chart(screen, people):
    font = p.font.SysFont(None, 24)
    title = font.render("Infection Count Chart", True, p.Color("black"))
    screen.blit(title, (GRAPH_WIDTH + 10, 10))

    # Sort people by their infection count in descending order
    sorted_people = sorted(people, key=lambda person: person.infections, reverse=True)

    y_offset = 40  # Start a bit down from the top to place below the title
    for person in sorted_people:
        if person.status == "sick":
            label = font.render(f"{person.name}: {person.infections}", True, p.Color("red"))
            screen.blit(label, (GRAPH_WIDTH + 10, y_offset))
            y_offset += 25  # Move down for the next entry


def update_graph(people, graph):
    for person in people:
        index = people.index(person)
        if person.status == "sick":
            # Ensure the sick person has a node in the graph
            if index not in graph.nodes():
                graph.add_node(index)
                # Set the node's position within the GRAPH_START and GRAPH_END boundaries
                positions[index] = (random.randint(GRAPH_START, GRAPH_END), random.randint(0, HEIGHT))
            # If the person was infected by another person, add an edge
            if person.infected_by:
                infector_index = people.index(person.infected_by)
                # Ensure the infector has a node in the graph
                if infector_index not in graph.nodes():
                    graph.add_node(infector_index)
                    positions[infector_index] = (random.randint(SIMULATION_WIDTH, WIDTH), random.randint(0, HEIGHT))
                # Create an edge between the infected person and their infector
                graph.add_edge(index, infector_index)

def draw_graph_edges(screen, graph, people):
    for edge in graph.edges():
        person1_pos = positions[edge[0]]
        person2_pos = positions[edge[1]]
        p.draw.line(screen, p.Color("red"), person1_pos, person2_pos, 2)

    for node, (x, y) in positions.items():
        p.draw.circle(screen, p.Color("red"), (int(x), int(y)), 5)

if __name__ == "__main__":
    main()