from bvm_model import *
from model_functions import *
from mesa.batchrunner import BatchRunner
from mesa.batchrunner import BatchRunnerMP
import seaborn

class bvmSweep():

    def __init__(self, fixedParams,variableParams, iters):
        self.batch_run = BatchRunnerMP(
                bvmModel, 
                fixed_parameters = fixedParams,
                variable_parameters = variableParams,
                iterations=iters,
                model_reporters = {"Buckets":updateBuckets}
                )
        self.iterations = iters

    def run(self):
        self.batch_run.run_all()
        self.data = self.getData()

    def getData(self):
        run_data = self.batch_run.get_model_vars_dataframe()
        return run_data 
    
    def plotBucketHeatmap(self,title, filename=None):
        if filename!=None:
            data = pd.read_csv(filename)
        else:
            data = self.data

        plt.figure()
        plt.title(title)
        plt.hist2d(x=data['o'],y=data['d'],weights=data['Buckets'], cmap="viridis", bins=[len(data['o'].unique()),len(data['d'].unique())])
        plt.xlabel("Openness Threshold")
        plt.ylabel("Disgust Threshold")
        plt.xticks(np.arange(0.05, 1, 0.1))
        plt.yticks(np.arange(0.05, 1, 0.1))
        colorBar = plt.colorbar()
        colorBar.set_label('Avg Number of Buckets for Each Suite')
        plt.show()
    
    def plotScatter(self, title, filename=None): 
        if filename!=None:
            data = pd.read_csv(filename)
        else:
            data = self.data

        fig,ax = plt.subplots()
        ax.set_title(title)
        
        seaborn.regplot(x=data['p'], y=data['assortativity'],y_jitter=.00,x_jitter=0.00, fit_reg=False,ax = ax)
        #ax.scatter(x=data['Density'], y=data['Buckets'], alpha=.7)
        ax.set_xticks(np.arange(0,1.05, .1))
        ax.set_yticks(np.arange(0,.65, .1))
        ax.set_xlabel('Network Density')
        ax.set_ylabel('Average Assortativity Across all Issues')
        #plt.axhline(y=2, linestyle = 'dotted')
        plt.show()

