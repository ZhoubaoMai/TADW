import pandas as pd
import numpy as np
import tqdm
from tqdm import tqdm
from numpy.linalg import inv
from scipy import sparse
from texttable import Texttable

class TADW:
    """
    """
    def __init__(self, A, T, args):
        """
        """
        self.A = A
        self.T = np.transpose((T - T.mean(axis=0)) / T.std(axis=0))
        self.args = args
        self.init_weights()

    def init_weights(self):
        """
        """

        # A - V x V
        # T - F x V 
        # W - D x V
        # H - D x F 

        self.W = np.random.uniform(0,1,(self.args.dimensions,self.A.shape[0]))
        self.H = np.random.uniform(0,1,(self.args.dimensions,self.T.shape[0]))
        self.losses = []


    def update_W(self):
        H_T = np.dot(self.H,self.T)
        grad = self.args.lambd*self.W -np.dot(H_T, self.A - np.dot(np.transpose(H_T),self.W))
        self.W = self.W-self.args.alpha * grad
        self.W[self.W < self.args.lower_control] = self.args.lower_control


    def update_H(self):
        inside = self.A - np.dot(np.dot(np.transpose(self.W),self.H), self.T)
        grad = self.args.lambd*self.H-np.dot(np.dot(self.W,inside),np.transpose(self.T))
        self.H = self.H-self.args.alpha * grad
        self.H[self.H < self.args.lower_control] = self.args.lower_control

    def calculate_loss(self,iteration):
        main_loss = np.sum(np.square(self.A - np.dot(np.dot(np.transpose(self.W),self.H), self.T)))
        regul_1 = self.args.lambd*np.sum(np.square(self.W))
        regul_2 = self.args.lambd*np.sum(np.square(self.H))
        self.losses.append([iteration,main_loss,regul_1,regul_2])
    def loss_printer(self):
        """
        Function to print the losses in a nice tabular format.
        """


        t = Texttable() 
        t.add_rows([["Iteration", "Main loss","Regularization loss I.","Regularization loss II."]] +  self.losses)
        print t.draw()

    def optimize(self):
        """
        """
        self.calculate_loss(0)
        for i in tqdm(range(1,self.args.iterations+1)):
            self.update_W()
            self.update_H()
            self.calculate_loss(i)
        self.loss_printer()

    def save_embedding(self):
        """
        """
        print("\nSaving the embedding.\n")
        self.W = np.concatenate([np.array(range(0,self.A.shape[0])).reshape(-1,1),np.transpose(self.W),np.transpose(np.dot(self.H,self.T))],axis=1)
        self.out = pd.DataFrame(self.W,columns = ["id"] + map(lambda x: "X_"+str(x),range(2*self.args.dimensions)))
        self.out.to_csv(self.args.output_path, index = None)

