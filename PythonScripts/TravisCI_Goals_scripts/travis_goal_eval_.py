# libraries
from pprint import pprint

import pandas as pd
import numpy as np
import seaborn
import seaborn as sns
from sklearn.model_selection import train_test_split

#Visualizers
from yellowbrick.classifier import ClassificationReport
from yellowbrick.classifier import ClassPredictionError
from yellowbrick.classifier import ConfusionMatrix
from yellowbrick.classifier import ROCAUC
from yellowbrick.classifier import PrecisionRecallCurve
import matplotlib.pyplot as plt

#Metrics
from sklearn.metrics import cohen_kappa_score
from sklearn.metrics import hamming_loss
from sklearn.metrics import log_loss
from sklearn.metrics import zero_one_loss
from sklearn.metrics import matthews_corrcoef
#Classifiers
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression

import warnings
warnings.filterwarnings('ignore')

df_truth=pd.read_csv('../../CSV Inputs/csv_for_eval_devops/ground_truth2.csv')
df_truth=df_truth.sort_values(by='Repository')
df_1pass_unigram=pd.read_csv('../../CSV Inputs/csv_for_eval_devops/1 pass/1pass_unigram_travis.csv')
df_1pass_unigram=df_1pass_unigram.sort_values(by='Repository')
df_1pass_bigram=pd.read_csv('../../CSV Inputs/csv_for_eval_devops/1 pass/naive_bigram_approach.csv')
df_1pass_bigram=df_1pass_bigram.sort_values(by='Repository')
df_1pass_trigram=pd.read_csv('../../CSV Inputs/csv_for_eval_devops/1 pass/naive_trigram_approach.csv')
df_1pass_trigram=df_1pass_trigram.sort_values(by='Repository')
df_2pass=pd.read_csv('../../CSV Inputs/csv_for_eval_devops/2 pass/2pass_approachV2.csv')
df_2pass=df_2pass.sort_values(by='Repository')
df_3pass=pd.read_csv('../../CSV Inputs/csv_for_eval_devops/3 pass/3pass_approach2.csv')
df_3pass=df_3pass.sort_values(by='Repository')
classes=['True','False']

classification_df_list=[df_1pass_unigram] #,df_1pass_bigram,df_1pass_trigram,df_2pass,df_3pass

classification_df_name_list=['df_1pass_unigram_travis']#','df_1pass_bigram','df_1pass_trigram','df_2pass','df_3pass'
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as style
style.use('seaborn')

def plot_confusion_matrix(data, labels, output_filename):
    seaborn.set(color_codes=True)
    plt.figure(1, figsize=(9, 6))

    plt.title("Confusion Matrix")

    seaborn.set(font_scale=1.4)
    ax = seaborn.heatmap(data, annot=True, cmap="YlGnBu", cbar_kws={'label': 'Scale'})

    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)

    ax.set(ylabel="True Label", xlabel="Predicted Label")

    plt.savefig(output_filename, bbox_inches='tight', dpi=300)
    plt.close()


from sklearn.metrics import confusion_matrix

def test_classifier_for_property(type,classification_df,df_name):
    projects_classified=classification_df['Repository'].tolist()
    projects_truth=df_truth['Repository'].to_list()

    # main_list = np.setdiff1d(projects_truth,projects_classified)
    # pprint(main_list)
    # exit()
    train_labels_predictions=classification_df.loc[classification_df['Repository'].isin( df_truth['Repository'].to_list())][str(type)].to_list()
    test_labels =df_truth[str(type)].to_list()
    # pprint(train_labels_predictions)
    # pprint(test_labels)
    # exit()
    # pprint(train_data)
    # pprint(test_data)

    cm=confusion_matrix(test_labels,train_labels_predictions)
    try:
        labels=['False','True']
        plot_confusion_matrix(cm, labels,'ConfusionMatrices/ConfusionMatrix-'+df_name+'-' + type + '.png')
    except:
        try:
            labels = ['True']
            plot_confusion_matrix(cm, labels, 'ConfusionMatrices/ConfusionMatrix-'+df_name+'-' + type + '.png')
        except:
            labels = ['False']
            plot_confusion_matrix(cm, labels, 'ConfusionMatrices/ConfusionMatrix-' +df_name+'-'+ type + '.png')

    from sklearn.metrics import precision_score, recall_score,f1_score

    # Calculate and print precision and recall as percentages
    print("Precision-"+df_name+"-" + type + ": " + str(round(precision_score(test_labels, train_labels_predictions) * 100, 1)) + "%")
    print("Recall-"+df_name+"-"+type+": "+ str(round(recall_score(test_labels, train_labels_predictions) * 100, 1)) + "%")
    print("F1 score-"+df_name+"-"+type+": " + str(round(f1_score(test_labels, train_labels_predictions) * 100, 1)) + "%")

types =['Build','Test','Deploy','CodeAnalysis']

for i in range(0,len(classification_df_list)):
    for type in types:
        test_classifier_for_property(type,classification_df_list[i],classification_df_name_list[i])
