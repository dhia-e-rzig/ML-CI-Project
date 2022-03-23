import pandas as pd
import numpy as np


# get label distribution for each data point
def prep_data(data, columns):
    labels = pd.DataFrame(columns=columns, index=list(range(len(data))))
    labels = labels.fillna(0)
    for i in range(len(data)):
        row = np.array(data.loc[i, :])
        for value in row:
            labels.loc[i, value] += 1

    return labels


# get the fleiss kappa score
# reference: https://en.wikipedia.org/wiki/Fleiss%27_kappa
def get_fleiss_kappa_score(n, labels):
    # notation
    # n = number of annotators
    # m = number of datapoints

    # formula
    # p_row = (sum(row_i)^2)*1/(n*(n-1))
    # p_col = sum(col_j)/n*m
    # p_row_cummulative = sum(p_row)/m
    # p_col_cummulative = sum((p_col)^2)
    # kappa = (p_row_cummulative - p_col_cummulative)/(1-p_col_cummulative)

    m = len(labels)

    print('n =', n)
    print('m =', m)

    p_row = []
    for row_num in labels.index:
        p = 0
        for i in labels.loc[row_num, :]:
            p += i ** 2
        p_row.append((p - n) * 1 / (n * (n - 1)))

    print('p row = ', p_row)

    p_col = []
    p_col_square = []
    for col in labels.columns:
        p_col.append(sum(labels[col]) / (n * m))
        p_col_square.append((sum(labels[col]) / (n * m)) ** 2)

    print('p_col', p_col)
    print('p_col_square', p_col_square)

    p_row_cummulative = sum(p_row) / m
    p_col_cummulative = sum(p_col_square)
    kappa_score = (p_row_cummulative - p_col_cummulative) / (1 - p_col_cummulative)

    print('p_row_cummulative', p_row_cummulative)
    print('p_col_cummulative', p_col_cummulative)
    return kappa_score


def main():
    # path = "../Data/"
    # filename = "SIGIR20_Taxonomy_Labels.csv"
    # data = pd.read_csv(filename)
    # data.columns = ['A1', 'A2', 'A3', 'A4']
    # print(data)
    # columns = ['NotProductRelated', 'Transactional', 'Comparison', 'Support', 'Navigational', 'Informational', 'Ignore']
    # labels = prep_data(data, columns)
    # print(labels)
    # num_annotators = 3
    # kappa_score = get_fleiss_kappa_score(num_annotators, labels)
    # print('kappa_score', kappa_score)
    # exit()
    devops_dhia = pd.read_csv('./error_labels_dhia.csv')
    devops_foyzul = pd.read_csv('./ErroredJobs_Labels_Foyzul.csv')
    # devops_chetan = pd.read_csv('./DevOps-Labels-Chetan.csv')
    list_cat=['FailureClassedAsError','ScriptError','BuildDepError','TravisError']
    for category in list_cat:
        try:
            category_dhia=devops_dhia[category].astype(str)
            category_foyzul=devops_foyzul[category].astype(str)
            # category_chetan=devops_chetan[category].astype(str)
            df = pd.DataFrame()
            df2=df.assign(A1=category_dhia).assign(A2=category_foyzul)#.assign(A3=category_chetan)
            # print(df2)
            # print(df2)
            # data.columns = ['A1', 'A2', 'A3', 'A4']
            # columns = ['NotProductRelated', 'Transactional', 'Comparison', 'Support', 'Navigational', 'Informational', 'Ignore']
            columns = ['False','True']
            labels = prep_data(df2, columns)
            num_annotators = 2
            kappa_score = get_fleiss_kappa_score(num_annotators, labels)
            print(category)
            print('kappa_score', kappa_score)
        except:
            pass


if __name__ == "__main__":
    main()
