from scipy.integrate import solve_ivp
import numpy


class Pendulum:
    def __init__(self, lenth_list, weight_list, time, init_angles, init_velocities):
        self.lenth_list = lenth_list
        self.weight_list = weight_list
        self.time = time
        self.init_angles = init_angles
        self.init_velocities = init_velocities

    def eom(self, t, y):
        """
        Equations of motion for the pendulum system.

        Parameters:
            t (float): Time variable.
            y (array): State vector containing angles and angular velocities.

        Returns:
            array: Derivatives of the state vector.
        """
        g = 9.81

        n = len(self.lenth_list)
        x = y[:n]
        v = y[n:]

        A = numpy.zeros((n, n))
        B = numpy.zeros((n, n))

        for i in range(n):
            for j in range(n):
                for k in range(max(i, j), n):
                    A[i][j] += self.weight_list[k]
                    B[i][j] += self.weight_list[k]
                if i == j:
                    A[i][j] *= self.lenth_list[j]
                    B[i][j] *= g * numpy.sin(x[i])
                else:
                    A[i][j] *= self.lenth_list[j]*numpy.cos(x[i]-x[j])
                    B[i][j] *= self.lenth_list[j]*v[j]**2*numpy.sin(x[i]-x[j])

        return numpy.concatenate([v, -numpy.linalg.inv(A) @ B @ numpy.ones(n)])

    def solve(self, flame):
        """
        Solve the equations of motion using the initial conditions.
        Parameters:
            flame (int): Number of time points to evaluate.

        Returns:
            list: A list of positions (x, y) for each pendulum at each time step.
        """
        y0 = numpy.concatenate([self.init_angles, self.init_velocities])
        t_span = (0, self.time)
        t_eval = numpy.linspace(0, self.time, flame)

        sol = solve_ivp(self.eom, t_span, y0, t_eval=t_eval, method='RK45')

        positions = []
        for pos in sol.y.T:
            position = []
            bx, by = 0, 0
            for i in range(len(self.lenth_list)):
                px = self.lenth_list[i] * numpy.sin(pos[i]) + bx
                py = -self.lenth_list[i] * numpy.cos(pos[i]) + by
                position.append((px, py))
                bx, by = px, py
            positions.append(position)

        return positions


if __name__ == "__main__":
    # Example usage
    lengths = [1.0, 2.0, 3.0]  # Lengths of the pendulum strings in meters
    weights = [1.0, 2.0, 3.0]   # Weights of the pendulum bob in kg
    init_angles = [0.1, -0.1, 0.2]
    # Initial velocities of the pendulum bobs in m/s
    init_velocities = [0.0, 0.0, 0.0]
    time_duration = 10.0         # Time duration in seconds

    pendulum = Pendulum(lengths, weights, time_duration,
                        init_angles, init_velocities)
    t, result = pendulum.solve()
    print(result)
