import itertools
import numpy as np
from scipy.special import comb

from cvxopt import matrix, solvers
from cvxopt.blas import dot
from cvxopt.solvers import qp, options
from cvxopt import matrix, sparse
from planner.utils import *
from planner.predict_traj import predict_trajectory

# TODO: import all this parameters from a config file so that we can easily change them in one place
L = 2.9
max_steer = np.radians(30.0)  # [rad] max steering angle
max_speed = 6 # [m/s]
min_speed = 0.0 # [m/s]
magnitude_limit= max_speed
max_acc = 400
min_acc = -400
dt = 0.1
safety_radius = 4
barrier_gain = 1/1000
magnitude_limit = max_speed
Kv = 0.1 # interval [0.5-1]
L = 2.9  # [m] Wheel base of vehicle
Lr = L / 2.0  # [m]
Lf = L - Lr

def CBF(x, u_ref):
    N = x.shape[1]
    M = u_ref.shape[0]
    G = np.zeros([N-1,M])
    H = np.zeros([N-1,1])
    dxu = np.zeros([u_ref.shape[0], u_ref.shape[1]])
    count_dxu = 0

    u_ref[1,:] = delta_to_beta_array(np.radians(u_ref[1,:]))

    for i in range(N):
        count = 0
        for j in range(N):

            if j == i: continue
            P = np.identity(2)*2
            q = np.array([-2 * u_ref[0, i], - 2 * u_ref[1,i]])

            Lf_h = 2 * x[3,i] * (np.cos(x[2,i]) * (x[0,i]-x[0,j]) + np.sin(x[2,i]) * (x[1,i] - x[1,j]))
            Lg_h = 2 * x[3,i] * (np.cos(x[2,i]) * (x[1,i]-x[1,j]) - np.sin(x[2,i]) * (x[0,i] - x[0,j]))
            h = (x[0,i]-x[0,j]) * (x[0,i]-x[0,j]) + (x[1,i] - x[1,j]) * (x[1,i] - x[1,j]) - (safety_radius**2 + Kv * x[3,i])

            H[count] = np.array([barrier_gain*np.power(h, 3) + Lf_h])
            G[count,:] = np.array([Kv, -Lg_h])
            count+=1
        
        # Add the input constraint
        G = np.vstack([G, [[0, 1], [0, -1]]])
        H = np.vstack([H, delta_to_beta(max_steer), -delta_to_beta(-max_steer)])
        # G = np.vstack([G, [[1, 0], [-1, 0]]])
        # H = np.vstack([H, max_acc, -min_acc])
        
        """G = np.vstack([G, np.identity(M)])
        G = np.vstack([G, -np.identity(M)])
        H = np.vstack([H, max_acc, delta_to_beta(max_steer), -min_acc, -delta_to_beta(-max_steer)]) """ 

        solvers.options['show_progress'] = False
        sol = solvers.qp(matrix(P), matrix(q), matrix(G), matrix(H))
        dxu[:,count_dxu] = np.reshape(np.array(sol['x']), (M,))
        count_dxu += 1
    
    dxu[1,:] = np.degrees(beta_to_delta(dxu[1,:]))
    return dxu

def delta_to_beta(delta):
    beta = normalize_angle(np.arctan2(Lr*np.tan(delta)/L, 1.0))

    return beta

def delta_to_beta_array(delta):
    beta = normalize_angle_array(np.arctan2(Lr*np.tan(delta)/L, 1.0))

    return beta

def beta_to_delta(beta):
    delta = normalize_angle_array(np.arctan2(L*np.tan(beta)/Lr, 1.0))

    return delta


def main(args=None):
    # Instantiate Robotarium object
    N = 2

    # The robots will never reach their goal points so set iteration number
    iterations = 3000

    # Define goal points outside of the arena
    goal_points = np.array(np.mat('5 5 5 5 5; 5 5 5 5 5; 0 0 0 0 0'))

    # Create barrier certificates to avoid collision
    # uni_barrier_cert = create_unicycle_barrier_certificate_with_boundary()

    # define x initially --> state: [x, y, yaw, v]
    x = np.array([[0, 20], [0.1, 0], [0, np.pi], [0, 0]])
    goal1 = np.array([20, 0])
    goal2 = np.array([0, 0])
    cmd1 = ControlInputs()
    cmd2 = ControlInputs()

    trajectory, tx, ty = predict_trajectory(array_to_state(x[:,0]), goal1)
    trajectory2, tx2, ty2 = predict_trajectory(array_to_state(x[:,1]), goal2)

    # While the number of robots at the required poses is less
    # than N...
    for i in range(iterations):

        # Create single-integrator control inputs
        x1 = x[:,0]
        x2 = x[:, 1]
        x1 = array_to_state(x1)
        x2 = array_to_state(x2)
        
        dxu = np.zeros((2,N))
        dxu[0,0], dxu[1,0] = pure_pursuit_steer_control(goal1, x1)
        dxu[0,1], dxu[1,1] = pure_pursuit_steer_control(goal2, x2)

        # Create safe control inputs (i.e., no collisions)
        print(dxu)
        dxu = CBF(x, dxu)
        # dxu = uni_barrier_cert(dxu, x)
        print(dxu)
        print('\n')

        cmd1.throttle, cmd1.delta = dxu[0,0], dxu[1,0]
        cmd2.throttle, cmd2.delta = dxu[0,1], dxu[1,1]

        # Applying command and current state to the model
        x1 = linear_model_callback(x1, cmd1)
        x2 = linear_model_callback(x2, cmd2)

        plt.cla()
        # for stopping simulation with the esc key.
        plt.gcf().canvas.mpl_connect(
            'key_release_event',
            lambda event: [exit(0) if event.key == 'escape' else None])
        plt.plot(x1.x, x1.y, 'xk')
        plt.plot(x2.x, x2.y, 'xb')
        plot_arrow(x1.x, x1.y, x1.yaw)
        plot_arrow(x1.x, x1.y, x1.yaw + cmd1.delta)
        plot_arrow(x2.x, x2.y, x2.yaw)
        plot_arrow(x2.x, x2.y, x2.yaw + cmd2.delta)
        plot_path(trajectory)
        plot_path(trajectory2)
        plt.plot(goal1[0], goal1[1], '.k')
        plt.plot(goal2[0], goal2[1], '.b')

        # plot_map()
        plt.xlim(-50, 50)
        plt.ylim(-50, 50)
        plt.axis("equal")
        plt.grid(True)
        plt.pause(0.000001)

        x1 = state_to_array(x1)
        x2 = state_to_array(x2)
        x = np.concatenate((x1, x2), axis=1)

if __name__=='__main__':
    main()
        
