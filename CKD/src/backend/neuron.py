import torch
from torch import nn
import numpy as np




def generate(pos_num,neg_num, TRN_PORTION):
    TRN_PORTION = 0.7
    pos_idxs =np.arange(pos_num)
    np.random.shuffle(pos_idxs)
    neg_idxs = np.arange(neg_num)
    np.random.shuffle(neg_idxs)
    pos_trn_idxs = pos_idxs[:int(pos_num*TRN_PORTION)]
    pos_tst_idxs = pos_idxs[int(pos_num*TRN_PORTION):]
    neg_trn_idxs = neg_idxs[:int(neg_num*TRN_PORTION)]
    neg_tst_idxs = neg_idxs[int(neg_num*TRN_PORTION):]
    return pos_trn_idxs, pos_tst_idxs, neg_trn_idxs, neg_tst_idxs


class MLP(nn.Module):
    def __init__(self, input_size, hidden_sizes, output_size=1, dropout_rate=0.5):
        super(MLP, self).__init__()
        
        # Build layers dynamically based on hidden_sizes list
        layers = []
        
        # Input layer
        layers.append(nn.Linear(input_size, hidden_sizes[0]))
        layers.append(nn.ReLU())
        layers.append(nn.Dropout(dropout_rate))
        
        # Hidden layers
        for i in range(len(hidden_sizes)-1):
            layers.append(nn.Linear(hidden_sizes[i], hidden_sizes[i+1]))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout_rate))
        
        # Output layer
        layers.append(nn.Linear(hidden_sizes[-1], output_size))
        layers.append(nn.Sigmoid())
        
        self.model = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.model(x)


# class MyLSTM(nn.Module):
#     def __init__(self, input_size, hidden_size, num_layers, output_size, dropout_rate=0.5):
#         super(MyLSTM, self).__init__()
#         self.hidden_size = hidden_size
#         self.num_layers = num_layers
        
#         # LSTM layer
#         self.lstm = torch.nn.LSTM(
#             input_size=input_size,
#             hidden_size=hidden_size,
#             num_layers=num_layers,
#             batch_first=True,
#             dropout=dropout_rate if num_layers > 1 else 0
#         )
        
#         # Dropout layer
#         self.dropout = torch.nn.Dropout(dropout_rate)
        
#         # Output layer
#         self.fc = torch.nn.Linear(hidden_size, output_size)
        
#         # Activation function for binary classification
#         self.sigmoid = torch.nn.Sigmoid()

#     def forward(self, x):
#         # Initialize hidden state and cell state
#         h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
#         c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
#         # Forward propagate LSTM
#         out, _ = self.lstm(x, (h0, c0))
        
#         # We only need the output from the last time step
#         out = out[:, -1, :]
        
#         # Apply dropout
#         out = self.dropout(out)
        
#         # Linear layer
#         out = self.fc(out)
        
#         # Apply sigmoid for binary classification
#         out = self.sigmoid(out)
        
#         return out
    


