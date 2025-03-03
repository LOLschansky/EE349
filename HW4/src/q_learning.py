import numpy as np
import src.random


class QLearning:
    """
    QLearning reinforcement learning agent.

    Arguments:
      epsilon - (float) The probability of randomly exploring the action space
        rather than exploiting the best action.
      alpha - (float) The weighting to give current rewards in estimating Q. This 
        should range [0,1], where 0 means "don't change the Q estimate based on 
        current reward" 
      gamma - (float) This is the weight given to expected future rewards when 
        estimating Q(s,a). It should be in the range [0,1]. Here 0 means "don't
        incorporate estimates of future rewards into the reestimate of Q(s,a)"

      See page 131 of Sutton and Barto's Reinforcement Learning book for
        pseudocode and for definitions of alpha, gamma, epsilon 
        (http://incompleteideas.net/book/RLbook2020.pdf).  
    """

    def __init__(self, epsilon=0.2, alpha=0.5, gamma=0.5):
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma

    def fit(self, env, steps=1000, num_bins=100):
        """
        Trains an agent using Q-Learning on an OpenAI Gymnasium Environment.

        See page 131 of Sutton and Barto's book Reinforcement Learning for
        pseudocode (http://incompleteideas.net/book/RLbook2020.pdf).
        Initialize your parameters as all zeros. Choose actions with
        an epsilon-greedy approach Note that unlike the pseudocode, we are
        looping over a total number of steps, and not a total number of
        episodes. This allows us to ensure that all of our trials have the same
        number of steps--and thus roughly the same amount of computation time.

        See (https://gymnasium.farama.org/) for examples of how to use the OpenAI
        Gymnasium Environment interface.

        In every step of the fit() function, you should sample
            two random numbers using functions from `src.random`.
            1.  First, use either `src.random.rand()` or `src.random.uniform()`
                to decide whether to explore or exploit.
            2. Then, use `src.random.choice` or `src.random.randint` to decide
                which action to choose. Even when exploiting, you should make a
                call to `src.random` to break (possible) ties.

        Please don't use `np.random` functions; use the ones from `src.random`!
        Please do not use `env.action_space.sample()`!

        Hints:
          - Use env.action_space.n and env.observation_space.n to get the
            number of available actions and states, respectively.
          - Remember to reset your environment at the end of each episode. To
            do this, call env.reset() whenever the value of "terminated or truncated" returned
            from env.step() is True.
          - In addition to resetting the environment, calling env.reset() will
            return the environment's initial state.
          - When choosing to exploit the best action rather than exploring,
            do not use np.argmax: it will deterministically break ties by
            choosing the lowest index of among the tied values. Instead,
            please *randomly choose* one of those tied-for-the-largest values.

        Arguments:
          env - (Env) An OpenAI Gymnasium environment with discrete actions and
            observations. See the OpenAI Gymnasium documentation for example use
            cases (https://gymnasium.farama.org/api/core/).
          steps - (int) The number of actions to perform within the environment
            during training.

        Returns:
          state_action_values - (np.array) The values assigned by the algorithm
            to each state-action pair as a 2D numpy array. The dimensionality
            of the numpy array should be S x A, where S is the number of
            states in the environment and A is the number of possible actions.
          rewards - (np.array) A 1D sequence of averaged rewards of length num_bins.
            Let s = int(np.ceil(steps / num_bins)), then rewards[0] should
            contain the average reward over the first s steps, rewards[1]
            should contain the average reward over the next s steps, etc.
            Please note that: The total number of steps will not always divide evenly by the 
            number of bins. This means the last group of steps may be smaller than the rest of 
            the groups. In this case, we can't divide by s to find the average reward per step 
            because we have less than s steps remaining for the last group.
        """
        # set up rewards list, Q(s, a) table
        n_actions, n_states = env.action_space.n, env.observation_space.n
        state_action_values = np.zeros((n_states, n_actions))
        avg_rewards = np.zeros([num_bins])
        all_rewards = []

        current_state, _ = env.reset()

        # BELOW IS COPY AND PASTED

        for step in range(steps):
          # draw random number
          rand_num_expl = src.random.uniform(0.0, 1.0)

          # with a probability of epsilon, explore, otherwise, exploit
          if rand_num_expl < self.epsilon:
            action = src.random.randint(0, n_actions)
          else:
            # find the maximum value in the vector
            max_value = np.max(state_action_values[current_state])
            
            # find the indices of all elements equal to the maximum value, s
            indices = np.where(state_action_values[current_state] == max_value)[0]
            rand_num_choice = src.random.randint(0, len(indices))
            action = indices[rand_num_choice]

          # take a step
          step_dat = env.step(action)

          # update state
          last_state = current_state
          current_state = step_dat[0]

          # reset environment if truncated or terminated
          truncated = step_dat[3]
          terminated = step_dat[2]
          next_state = 0
          if truncated or terminated:
            next_state = env.reset()[0]

          # update all_rewards
          reward = step_dat[1]
          all_rewards.append(reward)

          # update state action values
          max_next_Q = np.max(state_action_values[current_state])
          state_action_values[last_state][action] += self.alpha*(reward + self.gamma*max_next_Q - state_action_values[last_state][action])

          if truncated or terminated:
            current_state = next_state

        # compute average rewards for bins
        bin_size = int(np.ceil(steps / num_bins))
        for bin_ind in range(num_bins):
          start_ind = bin_ind * bin_size
          end_ind = start_ind + bin_size if bin_ind < num_bins - 1 else len(all_rewards)
          avg_rewards[bin_ind] = np.mean(all_rewards[start_ind:end_ind]) if end_ind > start_ind else 0

        # return values
        return state_action_values, avg_rewards
    
        
    def predict(self, env, state_action_values):
        """
        Runs prediction on an OpenAI environment using the policy defined by
        the QLearning algorithm and the state action values. Predictions are
        run for exactly one episode. Note that one episode may produce a
        variable number of steps.

        Hints:
          - You should not update the state_action_values during prediction.
          - Exploration is only used in training. During prediction, you
            should only "exploit."
          - In addition to resetting the environment, calling env.reset() will
            return the environment's initial state
          - You should use a loop to predict over each step in an episode until
            it terminates by returning `terminated or truncated=True`.
          - When choosing to exploit the best action, do not use np.argmax: it
            will deterministically break ties by choosing the lowest index of
            among the tied values. Instead, please *randomly choose* one of
            those tied-for-the-largest values.

        Arguments:
          env - (Env) An OpenAI Gymnasium environment with discrete actions and
            observations. See the OpenAI Gymnasium documentation for example use
            cases (https://gymnasium.farama.org/).
          state_action_values - (np.array) The values assigned by the algorithm
            to each state-action pair as a 2D numpy array. The dimensionality
            of the numpy array should be S x A, where S is the number of
            states in the environment and A is the number of possible actions.

        Returns:
          states - (np.array) The sequence of states visited by the agent over
            the course of the episode. Does not include the starting state.
            Should be of length K, where K is the number of steps taken within
            the episode.
          actions - (np.array) The sequence of actions taken by the agent over
            the course of the episode. Should be of length K, where K is the
            number of steps taken within the episode.
          rewards - (np.array) The sequence of rewards received by the agent
            over the course  of the episode. Should be of length K, where K is
            the number of steps taken within the episode.
        """

        # setup
        n_actions, n_states = env.action_space.n, env.observation_space.n
        states, actions, rewards = [], [], []

        # reset environment before your first action
        current_state, _ = env.reset()

        terminated, truncated = False, False

        while not (terminated or truncated):

          action_values = state_action_values[current_state]

          # find the maximum value in the vector
          max_value = np.max(action_values)
            
          # find the indices of all elements equal to the maximum value
          indices = np.where(action_values == max_value)[0]
          rand_num_choice = src.random.randint(0, len(indices))
          action = indices[rand_num_choice]

          # step 
          next_state, reward, terminated, truncated, _ = env.step(action)

          # add data to corresponding vectors
          states.append(next_state)
          actions.append(action)
          rewards.append(reward)

          # update the current state
          current_state = next_state

        return np.array(states), np.array(actions), np.array(rewards)

