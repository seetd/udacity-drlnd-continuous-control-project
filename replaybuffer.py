import numpy as np
import random
from collections import namedtuple, deque
import torch

class ReplayBuffer:
    """Fixed-size buffer to store experience tuples."""

    def __init__(self, device, config):
        """Initialize a ReplayBuffer object.
        Params
        ======
            config (object)
                .buffer_size (int): maximum size of buffer
                .batch_size (int): size of each training batch
                .random_seed (int): used to create randow seed for bufer
        """
        self.device = device
        self.batch_size = config['batch_size']
        self.memory = deque(maxlen=config['buffer_size'])  # internal memory (deque)
        self.episode_memory = deque(maxlen=config['episode_steps'])
        self.experience = namedtuple("Experience", field_names=["state", "action", "reward", "next_state", "done"])
       
        if config['random_seed'] is not None:
            self.seed = random.seed(config['random_seed'])
        else:
            self.seed = random.seed()        
    
    def add(self, state, action, reward, next_state, done):
        """Add a new experience to memory."""
        e = self.experience(state, action, reward, next_state, done)
        self.memory.append(e)
        self.episode_memory.append(e)
    
    def sample(self, best_episode=False):
        """Randomly sample a batch of experiences from memory."""
        
        if best_episode == True:
            experiences = self.episode_memory
        else:
            experiences = random.sample(self.memory, k=self.batch_size) 
            
        states = torch.from_numpy(np.vstack([e.state for e in experiences if e is not None])).float().to(self.device)
        actions = torch.from_numpy(np.vstack([e.action for e in experiences if e is not None])).float().to(self.device)
        rewards = torch.from_numpy(np.vstack([e.reward for e in experiences if e is not None])).float().to(self.device)
        next_states = torch.from_numpy(np.vstack([e.next_state for e in experiences if e is not None])).float().to(self.device)
        dones = torch.from_numpy(np.vstack([e.done for e in experiences if e is not None]).astype(np.uint8)).float().to(self.device)

        return (states, actions, rewards, next_states, dones)

    def __len__(self):
        """Return the current size of internal memory."""
        return len(self.memory)