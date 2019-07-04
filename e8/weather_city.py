##################################
# Case of the Unlabelled Weather #
##################################

import sys
import pandas as pd

from sklearn.model_selection import train_test_split
# from sklearn.naive_bayes import GaussianNB
# from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC

OUTPUT_TEMPLATE = (
    # 'Bayesian classifier: {bayes_model:.3g}\n'
    # 'kNN classifier:      {knn_model:.3g}\n'
    'SVM classifier:      {svc_model:.3g}'
)


def get_data(file):
    return pd.read_csv(file)


def main():
    # get file names
    labelled = sys.argv[1]
    unlabelled = sys.argv[2]
    output = sys.argv[3]

    # load data
    labelled_data = get_data(labelled)
    unlabelled_data = get_data(unlabelled)

    # split labelled data
    # https://stackoverflow.com/questions/29763620/how-to-select-all-columns-except-one-column-in-pandas
    X_lab = labelled_data.loc[:, labelled_data.columns != 'city']
    X_ulab = unlabelled_data.loc[:, labelled_data.columns != 'city']
    y_lab = labelled_data['city'].values

    # train test split on labelled data
    X_train, X_valid, y_train, y_valid = train_test_split(X_lab, y_lab)

    # # GaussianNB
    # bayes_model = make_pipeline(
    #     StandardScaler(),
    #     GaussianNB()
    # )

    # # train model
    # bayes_model.fit(X_train, y_train)

    # # predict with bayes model
    # y_bayes = bayes_model.predict(X_ulab)

    # # KNeighborsClassifier
    # knn_model = make_pipeline(
    #     StandardScaler(),
    #     KNeighborsClassifier(n_neighbors=9)
    # )

    # # train model
    # knn_model.fit(X_train, y_train)

    # # predict with knn model
    # y_knn = knn_model.predict(X_ulab)

    # SVC
    svc_model = make_pipeline(
        StandardScaler(),
        SVC(kernel='linear', C=0.5)
    )

    # train model
    svc_model.fit(X_train, y_train)

    # predict with SVC model
    y_svc = svc_model.predict(X_ulab)

    print(OUTPUT_TEMPLATE.format(
        # bayes_model=bayes_model.score(X_valid, y_valid),
        # knn_model=knn_model.score(X_valid, y_valid),
        svc_model=svc_model.score(X_valid, y_valid)
    ))

    # # prints out wrong predictions
    # df = pd.DataFrame({
    #     'truth': y_valid,
    #     'prediction': svc_model.predict(X_valid)})
    # print(df[df['truth'] != df['prediction']])

    pd.Series(y_svc).to_csv(
        output,
        index=False,
        header=False
    )


if __name__ == '__main__':
    main()
