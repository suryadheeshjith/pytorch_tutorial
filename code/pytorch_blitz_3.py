from __future__ import print_function
import torch
import torch.nn as nn
import torch.nn.functional as F

# To print backward graph
def print_graph(g, level=0):
    if g == None: return
    print('*'*level*2, g)
    for subg in g.next_functions:
        print_graph(subg[0], level+1)

# Class for NN
class Net(nn.Module):

    def __init__(self):
        super(Net,self).__init__()
        self.conv1 = nn.Conv2d(1,6,3)
        self.conv2 = nn.Conv2d(6,16,3)
        self.fc1 = nn.Linear(16*6*6, 120)
        self.fc2 = nn.Linear(120,84)
        self.fc3 = nn.Linear(84,10)

    def forward(self, x):
        x = F.max_pool2d(F.relu(self.conv1(x)),(2,2))
        x = F.max_pool2d(F.relu(self.conv2(x)),2)
        x = x.view(-1,self.num_flat_features(x))
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

    def num_flat_features(self, x):
        size = x.size()[1:]  # all dimensions except the batch dimension
        num_features = 1
        for s in size:
            num_features *= s
        return num_features


net = Net()
print(net)

# Listing parameters i.e. Weights and biases of layers

params = list(net.parameters())
print(len(params))
for name, param in net.named_parameters():
    print(name, param.size())
print(params[0].size())  # conv1's .weight

# Forward pass
input = torch.randn(1, 1, 32, 32)
out = net(input)
print(out)

# Backward pass

#net.zero_grad()
#out.backward()
target = torch.randn(10)
target = target.view(1,-1)

# Loss function
criterion = nn.MSELoss()
loss = criterion(out,target)
print("Loss : ",loss)

# Gradient functions
print(loss.grad_fn)  # MSELoss
print(loss.grad_fn.next_functions[0][0])  # Linear
print(loss.grad_fn.next_functions[0][0].next_functions[0][0])

print("Printing Complete backward graph")
print_graph(loss.grad_fn, 0)

net.zero_grad()     # zeroes the gradient buffers of all parameters

print('conv1.bias.grad before backward')
print(net.conv1.bias.grad)

loss.backward()

print('conv1.bias.grad after backward')
print(net.conv1.bias.grad)

learning_rate = 0.01
for f in net.parameters():
    f.data.sub_(f.grad.data * learning_rate)

import torch.optim as optim

# create your optimizer
optimizer = optim.SGD(net.parameters(), lr=0.01)

# in your training loop:
optimizer.zero_grad()   # zero the gradient buffers
output = net(input)
loss = criterion(output, target)
loss.backward()
optimizer.step()    # Does the update
