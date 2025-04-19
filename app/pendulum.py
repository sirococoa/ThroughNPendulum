from scipy.integrate import solve_ivp
import numpy


def pendulum(lenth_list, weight_list, time, init_angles, init_velocities):
    """
    Simulate the motion of a pendulum using the given lengths, weights, and initial angles.

    Parameters:
        lenth_list (list): List of lengths of the pendulum strings.
        weight_list (list): List of weights of the pendulum bob.
        time (float): Time duration for which to simulate the motion.
        init_angles (list): List of initial angles (in radians) for each pendulum.
        init_velocities (list): List of initial velocities for each pendulum.

    Returns:
        list: A list of positions (x, y) for each pendulum at each time step.
    """

    g = 9.81
    dt = 0.1

    n = len(lenth_list)

    x = numpy.array(init_angles)
    v = numpy.array(init_velocities)

    positions = []
    for t in numpy.arange(0, time, dt):

        A = numpy.zeros((n, n))
        B = numpy.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                for k in range(max(i, j), n):
                    A[i][j] += weight_list[k]
                    B[i][j] += weight_list[k]
                if i == j:
                    A[i][j] *= lenth_list[j]
                    B[i][j] *= g * numpy.sin(x[i])
                else:
                    A[i][j] *= lenth_list[j]*numpy.cos(x[i]-x[j])
                    B[i][j] *= lenth_list[j]*v[j]**2*numpy.sin(x[i]-x[j])
        v += -numpy.linalg.inv(A) @ B @ numpy.ones(n) * dt
        x += v * dt

        print(v)

        position = []
        bx, by = 0, 0
        for i in range(n):
            px = lenth_list[i] * numpy.sin(x[i]) + bx
            py = -lenth_list[i] * numpy.cos(x[i]) + by
            position.append((px, py))
            bx, by = px, py
        positions.append(position)

    return positions




if __name__ == "__main__":
    # Example usage
    lengths = [1.0, 2.0, 3.0]  # Lengths of the pendulum strings in meters
    weights = [1.0, 2.0, 3.0]   # Weights of the pendulum bob in kg
    init_angles = [0.1, -0.1, 0.2]
    init_velocities = [0.0, 0.0, 0.0]  # Initial velocities of the pendulum bobs in m/s
    time_duration = 10.0         # Time duration in seconds

    result = pendulum(lengths, weights, time_duration, init_angles, init_velocities)
    print(result)
