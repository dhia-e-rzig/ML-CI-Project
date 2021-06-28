# libraries
from pprint import pprint

import pandas as pd
import numpy as np
import seaborn
import seaborn as sns
from sklearn.model_selection import train_test_split

import warnings
warnings.filterwarnings('ignore')

df_truth=pd.read_csv('../../CSV Inputs/csv_for_eval_fail/ground_truth_fail_class.csv')
# df_truth=df_truth.sort_values(by='file_name')

df_original_regex=pd.read_csv('../../CSV Inputs/csv_for_eval_fail/classification_test_old_regex.csv')
df_original_regex=df_original_regex.sort_values(by='file_name')

df_v1_regex=pd.read_csv('../../CSV Inputs/csv_for_eval_fail/classification_test_v1_regex.csv')
df_v1_regex=df_v1_regex.sort_values(by='file_name')

classes=['True','False']

classification_df_list=[df_original_regex,df_v1_regex] #,df_1pass_bigram,df_1pass_trigram,df_2pass,df_3pass

classification_df_name_list=['original_classifier','v1_classifier']#','df_1pass_bigram','df_1pass_trigram','df_2pass','df_3pass'
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
    projects_classified=classification_df['file_name'].tolist()
    projects_truth=df_truth['file_name'].to_list()

    # main_list = np.setdiff1d(projects_truth,projects_classified)
    # pprint(main_list)
    # exit()
    file_name_list=df_truth['file_name'].to_list()
    file_name_list=[str(x)+'.txt' for x in file_name_list]
    train_labels_predictions=classification_df.loc[classification_df['file_name'].isin(file_name_list)][str(type)].to_list()
    test_labels =df_truth[str(type)].to_list()
    # pprint(train_labels_predictions)
    # pprint(test_labels)
    # exit()
    # pprint(train_data)
    # pprint(test_data)

    cm=confusion_matrix(test_labels,train_labels_predictions)
    try:
        labels=['False','True']
        plot_confusion_matrix(cm, labels,'ConfusionMatrices/FailClassification/ConfusionMatrix-'+df_name+'-' + type + '.png')
    except:
        try:
            labels = ['True']
            plot_confusion_matrix(cm, labels, 'ConfusionMatrices/FailClassification/ConfusionMatrix-'+df_name+'-' + type + '.png')
        except:
            labels = ['False']
            plot_confusion_matrix(cm, labels, 'ConfusionMatrices/FailClassification/ConfusionMatrix-' +df_name+'-'+ type + '.png')

    from sklearn.metrics import precision_score, recall_score,f1_score

    # Calculate and print precision and recall as percentages
    print("Precision-"+df_name+"-" + type + ": " + str(round(precision_score(test_labels, train_labels_predictions) * 100, 1)) + "%")
    print("Recall-"+df_name+"-"+type+": "+ str(round(recall_score(test_labels, train_labels_predictions) * 100, 1)) + "%")
    print("F1 score-"+df_name+"-"+type+": " + str(round(f1_score(test_labels, train_labels_predictions) * 100, 1)) + "%")

types =['TestFail','BuildFail','TestError','CodeAnalysisError','TravisError']

for i in range(0,len(classification_df_list)):
    for type in types:
        test_classifier_for_property(type,classification_df_list[i],classification_df_name_list[i])
