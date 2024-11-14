import numpy as np

import pickle
import statistics
import matplotlib.pyplot as plt

import os
import torch

import random

import torch_geometric.transforms as T
from torch_geometric.loader import DataLoader

from sklearn.metrics import accuracy_score, confusion_matrix

from timeit import default_timer as timer
from datetime import timedelta

from torch.nn import Linear
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.nn import global_mean_pool

from utils import time_series_to_graphs, GCN, GraphSAGE, GAT_net, GIN

def train():
    model.train()

    for data in train_loader:  # Iterate in batches over the training dataset.

        data = data.to(dev)
        out, _ = model(data.x.float(), data.edge_index, data.batch)  # Perform a single forward pass.
        #print(torch.Tensor(data.y).shape)
        loss = criterion(out, data.y)  # Compute the loss.
        loss.backward()  # Derive gradients.
        optimizer.step()  # Update parameters based on gradients.
        optimizer.zero_grad()  # Clear gradients.

def test(loader):
    model.eval()
    preds_lst = []
    correct = 0
    CM = 0
    for data in loader:  # Iterate in batches over the training/test dataset.

        data = data.to(dev)
        out, _ = model(data.x.float(), data.edge_index, data.batch)
        pred = out.argmax(dim=1)  # Use the class with highest probability.
        preds_lst += [pred]
        CM += confusion_matrix(data.y.cpu(), pred.cpu(), labels=[0, 1])

        correct += int((pred == data.y).sum())  # Check against ground-truth labels.

    return correct / len(loader.dataset), pred, preds_lst, CM  # Derive ratio of correct predictions.


os.environ['TORCH'] = torch.__version__
print(torch.__version__)
print("CUDA available? ", torch.cuda.is_available())
#print("Device name: ", torch.cuda.get_device_name(0))

dev = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
print("Device in use is ", dev)

directory = os.getcwd()
read_directory = "/data/multi_patients_3.txt"
save_directory = "/output"

with open(read_directory, "rb") as fp:   # Unpickling
    pulse_list = pickle.load(fp)

graphs = time_series_to_graphs(pulse_list)

#transform = T.Compose([T.ToUndirected(), T.AddSelfLoops()])
#graphs = transform(graphs_2)

print('============================')
print("Length of graphs list:  ", len(graphs), "first graph in the list:  ", graphs[0], "features of the first graph:  ",graphs[0].x)
print('============================')

accuracy_tuples = []

for genuine in range(3):
    for impostor in range(genuine+1,3):

        match_set = graphs[genuine*180: genuine*180+180] + graphs[impostor*180: impostor*180+180]
        print("Length of match set: ", len(match_set))

        for i in range(180):
            match_set[i].y = 0
        for j in range(180,360):
            match_set[j].y = 1

        random.shuffle(match_set)

        train_dataset = match_set[:288]
        test_dataset = match_set[288:360]

        train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)


        model = GIN(hidden_channels=32)
        model.to(dev)
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)
        criterion = torch.nn.CrossEntropyLoss()

        best = 0
        start = timer()
        for epoch in range(1, 501):
            start=timer()
            train()
            train_acc, _, _, _ = test(train_loader)
            test_acc, _, preds_test, CM = test(test_loader)
            if test_acc > best:
                best = test_acc
                tn = CM[1][1]
                tp = CM[0][0]
                fp = CM[0][1]
                fn = CM[1][0]

            print(f'Epoch: {epoch:03d}, Train Acc: {train_acc:.4f}, Test Acc: {test_acc:.4f}, Best Acc: {best:04f}')
            if best == 1.00:
                break
        end = timer()

        print("Genuine patient number:", genuine, "impostor patient number:", impostor)
        print("Test accuracy:", best)

        print("False Positive: ", fp, "  False Negative: ", fn, "  True Positive: ", tp,
              "  True Negative: ", tn)

        accuracy_tuples += [(genuine, impostor, best, tp, fp, fn, tn, epoch, end-start)]

print(accuracy_tuples)


total, tp_total, fp_total, fn_total, tn_total, epoch_total, time_total = 0, 0, 0, 0, 0, 0, 0

accuracy=accuracy_tuples

for j in range(len(accuracy)):

  total += accuracy[j][2]
  tp_total += accuracy[j][3]
  fp_total += accuracy[j][4]
  fn_total += accuracy[j][5]
  tn_total += accuracy[j][6]

  if len(accuracy[0]) > 7:
    epoch_total += accuracy[j][7]
    time_total += accuracy[j][8]

avg_epoch = epoch_total/len(accuracy)
avg_time = time_total/len(accuracy)

average = total/len(accuracy)

fnmr = fn_total/(fn_total+tp_total)
fmr  = fp_total/(fp_total+tn_total)

tpr = tp_total/(tp_total+fn_total)
fpr = fp_total/(fp_total+tn_total)
auc_roc = (1+tpr-fpr)/2

dev = []
for i in range(len(accuracy)):
  dev += [accuracy[i][2]]

print(dev)
print(len(dev))
print("Standard Deviation of Accuracies:  ", statistics.stdev(dev))

print("Average accuracy:   ", average,"   Average FNMR:   ", fnmr, "   Average FMR:   ", fmr)
print("Average tpr:   ", tpr,"   Average fpr:   ", fpr, "   Average auc_roc:   ", auc_roc)
print("Average Epoch:   ", avg_epoch,"   Average Time:   ", avg_time)




with open(save_directory + "\\" + "GIN"+ "_accuracy.txt", "wb") as fp:  # Pickling
    pickle.dump(accuracy_tuples, fp)  # save the accuracy scores per match