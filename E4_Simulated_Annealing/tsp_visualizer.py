import matplotlib.pyplot as plt
import random
import math
import time

# ===============================
# CLASS: City
# Represents a city with (x, y) coordinates
# ===============================
class City:
    def __init__(self, x, y):
        # Store city coordinates
        self.x = x
        self.y = y
    
    def distance_to(self, city):
        # Compute Euclidean distance between this city and another city
        x_distance = abs(self.x - city.x)
        y_distance = abs(self.y - city.y)
        return math.sqrt(x_distance**2 + y_distance**2)
    
    def __repr__(self):
        # String representation when printing a city
        return f"({self.x}, {self.y})"

# ===============================
# CLASS: Tour
# Represents a possible route visiting all cities once
# ===============================
class Tour:
    def __init__(self, cities=None):
        if cities is None:
            self.tour = []
        else:
            self.tour = cities.copy()
        self.distance = 0
    
    def generate_individual(self, all_cities):
        self.tour = all_cities.copy()
        random.shuffle(self.tour)
        self.distance = 0
    
    def get_distance(self):
        if self.distance == 0:
            tour_distance = 0
            for i in range(len(self.tour)):
                from_city = self.tour[i]
                destination_city = self.tour[(i + 1) % len(self.tour)]
                tour_distance += from_city.distance_to(destination_city)
            self.distance = tour_distance
        return self.distance
    
    def copy(self):
        return Tour(self.tour)

# ===============================
# FUNCTION: acceptance_probability
# ===============================
def acceptance_probability(energy, new_energy, temperature):
    if new_energy < energy:
        return 1.0
    return math.exp((energy - new_energy) / temperature)

# ===============================
# FUNCTION: simulated_annealing
# ===============================
def simulated_annealing(cities, update_interval=100, plot_delay=0.05):
    temp = 10000
    cooling_rate = 0.003
    
    current_solution = Tour()
    current_solution.generate_individual(cities)
    
    print(f"Initial solution distance: {current_solution.get_distance():.2f}")
    
    best = current_solution.copy()
    
    # Set up the plot for live updates
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_title('Simulated Annealing - Route Evolution', fontsize=14)
    ax.set_xlabel('X Coordinate', fontsize=12)
    ax.set_ylabel('Y Coordinate', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-10, 210)
    ax.set_ylim(-10, 210)
    
    # Plot cities once (they stay fixed)
    x_coords = [city.x for city in cities]
    y_coords = [city.y for city in cities]
    city_scatter = ax.scatter(x_coords, y_coords, c='red', s=100, zorder=10, label='Cities')
    
    # Mark the first city of initial tour
    start_city = current_solution.tour[0]
    start_marker = ax.scatter(start_city.x, start_city.y, c='blue', s=150, 
                              edgecolors='black', zorder=11, label='Start City')
    
    # Text for distance display
    distance_text = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                           fontsize=12, verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax.legend(loc='upper right')
    plt.tight_layout()
    
    iteration = 0
    
    while temp > 1:
        new_solution = current_solution.copy()
        
        tour_pos1 = random.randint(0, len(new_solution.tour) - 1)
        tour_pos2 = random.randint(0, len(new_solution.tour) - 1)
        
        new_solution.tour[tour_pos1], new_solution.tour[tour_pos2] = \
            new_solution.tour[tour_pos2], new_solution.tour[tour_pos1]
        new_solution.distance = 0
        
        current_energy = current_solution.get_distance()
        neighbour_energy = new_solution.get_distance()
        
        if acceptance_probability(current_energy, neighbour_energy, temp) > random.random():
            current_solution = new_solution.copy()
        
        if current_solution.get_distance() < best.get_distance():
            best = current_solution.copy()
        
        # Update visualization at specified interval
        if iteration % update_interval == 0:
            # Clear the previous route line
            for line in ax.lines:
                line.remove()
            
            # Get current tour coordinates
            tour_x = [city.x for city in current_solution.tour]
            tour_y = [city.y for city in current_solution.tour]
            
            # Close the loop by returning to start
            tour_x.append(current_solution.tour[0].x)
            tour_y.append(current_solution.tour[0].y)
            
            # Plot the current route
            route_line = ax.plot(tour_x, tour_y, 'b-', alpha=0.7, linewidth=1.5, 
                                 label=f'Current Route (Iteration {iteration})')[0]
            
            # Update the start marker position
            start_marker.set_offsets([[current_solution.tour[0].x, current_solution.tour[0].y]])
            
            # Update distance text
            distance_text.set_text(f'Current Distance: {current_solution.get_distance():.2f}\n'
                                   f'Best Distance: {best.get_distance():.2f}\n'
                                   f'Temperature: {temp:.2f}')
            
            # Update the plot
            plt.draw()
            plt.pause(plot_delay)  # Small delay for human viewing
        
        temp *= (1 - cooling_rate)
        iteration += 1
    
    # Final update with the best route
    for line in ax.lines:
        line.remove()
    
    # Plot final best route
    best_x = [city.x for city in best.tour]
    best_y = [city.y for city in best.tour]
    best_x.append(best.tour[0].x)
    best_y.append(best.tour[0].y)
    
    final_route = ax.plot(best_x, best_y, 'g-', alpha=1.0, linewidth=3, 
                          label=f'Final Route (Distance: {best.get_distance():.2f})')[0]
    
    # Update start marker for final route
    start_marker.set_offsets([[best.tour[0].x, best.tour[0].y]])
    
    # Update text for final result
    distance_text.set_text(f'FINAL RESULT\n'
                           f'Distance: {best.get_distance():.2f}\n'
                           f'Total Iterations: {iteration}')
    
    # Update legend
    handles, labels = ax.get_legend_handles_labels()
    # Remove duplicate "Start City" from legend if it exists multiple times
    unique_labels = []
    unique_handles = []
    for handle, label in zip(handles, labels):
        if label not in unique_labels:
            unique_labels.append(label)
            unique_handles.append(handle)
    ax.legend(unique_handles, unique_labels, loc='upper right')
    
    plt.draw()
    plt.pause(2)  # Pause to show final result
    
    print(f"Final solution distance: {best.get_distance():.2f}")

    # ⭐ PRINT THE FINAL TRAVERSED ORDER
    print("\nOptimal route in order of traversal:")
    for i, city in enumerate(best.tour, start=1):
        print(f"{i}. {city}")
    print(f"Back to start → {best.tour[0]}")

    # Keep the plot open
    plt.ioff()
    plt.show()

    return best

# ===============================
# FUNCTION: plot_cities_and_route
# ===============================
def plot_cities_and_route(cities, best_tour):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 3))
    
    # ----- LEFT PLOT -----
    ax1.set_title('Cities (Before Route Selection)')
    ax1.set_xlabel('X Coordinate')
    ax1.set_ylabel('Y Coordinate')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(-10, 210)
    ax1.set_ylim(-10, 210)
    
    x_coords = [city.x for city in cities]
    y_coords = [city.y for city in cities]
    ax1.scatter(x_coords, y_coords, c='red', s=100)
    
    # ----- RIGHT PLOT -----
    ax2.set_title('Optimal Route (Simulated Annealing)')
    ax2.set_xlabel('X Coordinate')
    ax2.set_ylabel('Y Coordinate')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(-10, 210)
    ax2.set_ylim(-10, 210)
    
    tour_x = [city.x for city in best_tour.tour]
    tour_y = [city.y for city in best_tour.tour]
    
    tour_x.append(best_tour.tour[0].x)
    tour_y.append(best_tour.tour[0].y)
    
    ax2.plot(tour_x, tour_y, 'b-', alpha=0.6, linewidth=1.5)
    ax2.scatter(tour_x[:-1], tour_y[:-1], c='red', s=100)
    
    # ⭐ MARK START CITY BLUE
    start_city = best_tour.tour[0]
    ax2.scatter(start_city.x, start_city.y, c='blue', s=130, edgecolors='black', zorder=3)
    
    ax2.text(
        0.02, 0.98,
        f'Total Distance: {best_tour.get_distance():.2f}',
        transform=ax2.transAxes,
        fontsize=12,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    )
    
    plt.tight_layout()
    plt.show()

# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    cities = [
        City(60, 200), City(180, 200), City(80, 180), City(140, 180),
        City(20, 160), City(100, 160), City(200, 160), City(140, 140),
        City(40, 120), City(100, 120), City(180, 100), City(60, 80),
        City(120, 80), City(180, 60), City(20, 40), City(100, 40),
        City(200, 40), City(20, 20), City(60, 20), City(160, 20)
    ]
    
    print("List of all city coordinates:")
    for c in cities:
        print(c)
    
    # Run simulated annealing with live visualization
    # update_interval: how many iterations between plot updates
    # plot_delay: time to pause between updates (in seconds)
    best_tour = simulated_annealing(cities, update_interval=50, plot_delay=0.05)
    
    # Optionally show the static comparison plot
    plot_cities_and_route(cities, best_tour)