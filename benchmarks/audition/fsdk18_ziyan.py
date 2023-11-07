"""
Coauthors: Haoyin Xu
           Yu-Chung Peng
           Madi Kusmanov
           Adway Kanhere
"""
from toolbox_ziyan import *
import argparse
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import scale
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.base import BaseEstimator
from sklearn.preprocessing import StandardScaler

import pandas as pd
import torchvision.models as models
import warnings
import random
import pickle

warnings.filterwarnings("ignore")

np.random.seed(317)

def run_naive_rf():
    naive_rf_kappa = []
    naive_rf_ece = []
    naive_rf_train_time = []
    naive_rf_test_time = []
    navie_rf_probs_labels = []
    storage_dict = {}

    # Grid search for best parameters

    param_grid = {
        'n_estimators': range(1000, 1501, 100),
        'max_depth': range(20, 41, 2),
        # 'min_samples_split': range(2, 11, 2),
        # 'min_samples_leaf': range(1, 11, 1),
        # 'max_features': ['sqrt', 'log2', None]
    }
    
    # RF = RandomForestClassifier(min_samples_split=2, min_samples_leaf=1, max_features=None ,n_jobs=-1, random_state=317)

    # grid_search = GridSearchCV(estimator=RF, param_grid=param_grid, cv=3)
    # grid_search.fit(fsdk18_train_images, fsdk18_train_labels)

    # best_params = grid_search.best_params_
    # print("Best Hyperparameters:", best_params)

    # results = pd.DataFrame(grid_search.cv_results_)

    # accuracy_scores = results['mean_test_score']
    # for i, accuracy in enumerate(accuracy_scores):
    #     print(f"HPs : {results['params'][i]} accuracy score is: {accuracy}")
    # print(" ")
    # best_params = grid_search.best_params_
    # print("Best Accuracy:", grid_search.best_score_)
    # print("Best Parameters:", best_params)

    # RF_best = RandomForestClassifier(
    #     n_estimators=best_params['n_estimators'],
    #     max_depth=best_params['max_depth'],
    #     min_samples_split=best_params['min_samples_split'],
    #     min_samples_leaf=best_params['min_samples_leaf'],
    #     max_features=best_params['max_features'],
    #     n_jobs=-1,
    #     random_state=317
    # )    
    # RF_best.fit(fsdk18_train_images, fsdk18_train_labels)
    # pred2 = RF_best.predict(fsdk18_valid_images)
    # val_accuracy2 = accuracy_score(fsdk18_valid_labels, pred2) 
    # print("Accuracy_best:", val_accuracy2)



    for classes in classes_space:
        d1 = {}
        # cohen_kappa vs num training samples (naive_rf)
        for samples in samples_space:
            l3 = []            
            # train data

            # RF_best = RandomForestClassifier(n_jobs=-1, random_state=317)

            # Best set of hyperparameters of 3 classes: 
            # RF_best = RandomForestClassifier(n_estimators=600, max_depth=16, min_samples_split=2, min_samples_leaf=1, max_features=None ,n_jobs=-1, random_state=317)

            # Best set of hyperparameters of 8 classes: 
            RF_best = RandomForestClassifier(n_estimators=600, max_depth=32, min_samples_split=2, min_samples_leaf=1, max_features=None ,n_jobs=-1, random_state=317)

            cohen_kappa, ece, train_time, test_time, test_probs, test_labels, test_preds = run_rf_image_set(
                RF_best,
                fsdk18_train_images,
                fsdk18_train_labels,
                fsdk18_test_images,
                fsdk18_test_labels,
                samples,
                classes,
            )
            naive_rf_kappa.append(cohen_kappa)
            naive_rf_ece.append(ece)
            naive_rf_train_time.append(train_time)
            naive_rf_test_time.append(test_time)

            classes = sorted(classes)
            navie_rf_probs_labels.append("Classes:" + str(classes))

            navie_rf_probs_labels.append("Sample size:" + str(samples))

            for i in range(len(test_probs)):
                navie_rf_probs_labels.append("Posteriors:"+str(test_probs[i]) + ", " + "Test Labels:" + str(test_labels[i]))
            navie_rf_probs_labels.append(" \n")

            for i in range(len(test_probs)):
                l3.append([test_probs[i].tolist(), test_labels[i]])

            d1[samples] = l3

        storage_dict[tuple(sorted(classes))] = d1

    # switch the classes and sample sizes
    switched_storage_dict = {}

    for classes, class_data in storage_dict.items():

        for samples, data in class_data.items():

            if samples not in switched_storage_dict:
                switched_storage_dict[samples] = {}

            if classes not in switched_storage_dict[samples]:
                switched_storage_dict[samples][classes] = data

    with open(prefix +'rf_switched_storage_dict.pkl', 'wb') as f:
        pickle.dump(switched_storage_dict, f)

    # save the model
    with open(prefix + 'naive_rf_org.pkl', 'wb') as f:
        pickle.dump(RF_best, f)

    print("naive_rf finished")
    write_result(prefix + "naive_rf_kappa_best.txt", naive_rf_kappa)
    write_result(prefix + "naive_rf_ece.txt", naive_rf_ece)
    write_result(prefix + "naive_rf_train_time.txt", naive_rf_train_time)
    write_result(prefix + "naive_rf_test_time.txt", naive_rf_test_time)
    write_result(prefix + "naive_rf_probs&labels.txt", navie_rf_probs_labels)
    write_json(prefix + "naive_rf_kappa_best.json", naive_rf_kappa)
    write_json(prefix + "naive_rf_ece.json", naive_rf_ece)
    write_json(prefix + "naive_rf_train_time.json", naive_rf_train_time)
    write_json(prefix + "naive_rf_test_time.json", naive_rf_test_time)


def run_cnn32():
    cnn32_kappa = []
    cnn32_ece = []
    cnn32_train_time = []
    cnn32_test_time = []
    cnn32_probs_labels = []
    storage_dict = {}

    # # Grid search for best hyperparameters

    # cnn32 = SimpleCNN32Filter(num_classes=41)

    # class CNN32Wrapper(BaseEstimator):
    #     def __init__(self, lr=0.01, batch_size=32, epochs=30, criterion = nn.CrossEntropyLoss(), optimizer_name='adam', Valid_X=None, Valid_y=None):
    #         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    #         self.model = cnn32.to(self.device)
    #         self.lr = lr
    #         self.batch_size = batch_size
    #         self.epochs = epochs
    #         self.criterion = criterion
    #         self.optimizer_name = optimizer_name
    #         self.Valid_X = Valid_X
    #         self.Valid_y = Valid_y

    #         if optimizer_name == 'sgd':
    #             self.optimizer = optim.SGD(self.model.parameters(), lr=self.lr)
    #         elif optimizer_name == 'adam':
    #             self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
    #         else:
    #             raise ValueError(f"Unknown optimizer: {optimizer_name}")

    #     def fit(self, X, y):
    #         max_epochs = [0]
    #         X = X.reshape(-1, 1, 32, 32)
    #         self.Valid_X = self.Valid_X.reshape(-1, 1, 32, 32)
    #         model = self.model
    #         criterion = self.criterion
    #         optimizer = self.optimizer
    #         prev_loss = float("inf")
    #         flag = 0
    #         for epoch in range(self.epochs):
    #             model.train()
    #             for i in range(0, len(X), self.batch_size):
    #                 inputs = X[i : i + self.batch_size].to(self.device)
    #                 labels = y[i : i + self.batch_size].to(self.device)
    #                 optimizer.zero_grad()
    #                 if inputs.shape[0] <= 2:
    #                     continue
    #                 outputs = model(inputs)
    #                 loss = criterion(outputs, labels)
    #                 loss.backward()
    #                 optimizer.step()

    #             model.eval()
    #             cur_loss = 0
    #             with torch.no_grad():
    #                 for i in range(0, len(self.Valid_X), self.batch_size):
    #                     # get the inputs
    #                     inputs = self.Valid_X[i : i + self.batch_size].to(self.device)
    #                     labels = self.Valid_y[i : i + self.batch_size].to(self.device)
    #                     if inputs.shape[0] == 1:
    #                         inputs = torch.cat((inputs, inputs, inputs), dim = 0)
    #                         labels = torch.cat((labels, labels, labels), dim = 0)

    #                     # forward
    #                     outputs = model(inputs)
    #                     loss = criterion(outputs, labels)
    #                     cur_loss += loss
    #             # early stop if 3 epochs in a row no loss decrease
    #             if cur_loss < prev_loss:
    #                 prev_loss = cur_loss
    #                 flag = 0
    #             else:
    #                 flag += 1
    #                 if flag >= 3:
    #                     max_epochs.append(epoch)
    #                     break
    #         # print(np.max(max_epochs))
    #         return self
        
    #     def predict(self, X):
    #         X = X.reshape(-1, 1, 32, 32)
    #         model = self.model
    #         model.eval()
    #         with torch.no_grad():
    #             outputs = model(X.to(self.device))
    #             _, predicted = torch.max(outputs.data, 1)
    #             return predicted.cpu()

    #     def score(self, X, y):
    #         X = X.reshape(-1, 1, 32, 32)
    #         model = self.model
    #         model.eval()
    #         predictions = self.predict(X)
    #         acc = accuracy_score(y, predictions)
    #         return acc

    # # train_images, train_labels, valid_images, valid_labels ,test_images, test_labels = prepare_data(fsdk18_train_images, fsdk18_train_labels, fsdk18_test_images, fsdk18_test_labels, samples_space[0] ,classes_space[0])
    # scaler = StandardScaler()
    # train_images = scaler.fit_transform(fsdk18_train_images)
    # valid_images = scaler.transform(fsdk18_valid_images)
    
    # train_images = torch.FloatTensor(train_images).unsqueeze(1)
    # train_labels = torch.LongTensor(fsdk18_train_labels)
    # valid_images = torch.FloatTensor(valid_images).unsqueeze(1)
    # valid_labels = torch.LongTensor(fsdk18_valid_labels)

    # param_grid={
    #     "batch_size": [256, 512, 1024, 2048, 4096, 8192],
    #     "lr": [0.0001, 0.001, 0.01, 0.1],
    #     "epochs": range(50, 101, 10),
    #     # "criterion": [nn.CrossEntropyLoss(), nn.NLLLoss()],
    #     "optimizer_name": ["adam", "sgd"],
    #     }
    
    # grid_search = GridSearchCV(estimator=CNN32Wrapper(Valid_X=valid_images, Valid_y=valid_labels), param_grid=param_grid, cv=3)

    # grid_search.fit(train_images, train_labels)

    # results = pd.DataFrame(grid_search.cv_results_)
    # accuracy_scores = results['mean_test_score']
    # for i, accuracy in enumerate(accuracy_scores):
    #     print(f"HPs : {results['params'][i]} accuracy score is: {accuracy}")
    # print(" ")
    # best_params = grid_search.best_params_
    # print("Best Accuracy:", grid_search.best_score_)
    # print("Best Parameters:", best_params)


    # Best set of hyperparameters for 3 classes: 
                # optimizer_name="adam",
                # epochs=100,
                # batch=1024,
                # lr=0.001,




    
    for classes in classes_space:
        d1 = {}

        # cohen_kappa vs num training samples (cnn32)
        for samples in samples_space:
            l3 = []
            # train data
            cnn32 = SimpleCNN32Filter(len(classes))
            # 3000 samples, 80% train is 2400 samples, 20% test
            train_images = trainx.copy()
            train_labels = trainy.copy()
            # reshape in 4d array
            test_images = testx.copy()
            test_labels = testy.copy()

            (
                train_images,
                train_labels,
                valid_images,
                valid_labels,
                test_images,
                test_labels,
            ) = prepare_data(
                train_images, train_labels, test_images, test_labels, samples, classes
            )

            cohen_kappa, ece, train_time, test_time, test_probs, test_labels, test_preds = run_dn_image_es(
                cnn32,
                train_images,
                train_labels,
                valid_images,
                valid_labels,
                test_images,
                test_labels,
                # optimizer_name="adam",
                # epochs=100,
                # batch=1024,
                # lr=0.001,
            )
            cnn32_kappa.append(cohen_kappa)
            cnn32_ece.append(ece)
            cnn32_train_time.append(train_time)
            cnn32_test_time.append(test_time)

            actual_test_labels = []
            for i in range(len(test_labels)):
                actual_test_labels.append(int(classes[test_labels[i]]))

            sorted_classes = sorted(classes)
            cnn32_probs_labels.append("Classes:" + str(sorted_classes))

            cnn32_probs_labels.append("Sample size:" + str(samples))
            
            actual_preds = []
            for i in range(len(test_preds)):
                actual_preds.append(int(sorted_classes[test_preds[i].astype(int)]))

            for i in range(len(test_probs)):
                cnn32_probs_labels.append("Posteriors:"+str(test_probs[i]) + ", " + "Test Labels:" + str(actual_test_labels[i]))
            cnn32_probs_labels.append(" \n")

            for i in range(len(test_probs)):
                l3.append([test_probs[i].tolist(), actual_test_labels[i]])

            d1[samples] = l3

        storage_dict[tuple(sorted(classes))] = d1

    # switch the classes and sample sizes
    switched_storage_dict = {}
    
    for classes, class_data in storage_dict.items():
        for samples, data in class_data.items():

            if samples not in switched_storage_dict:
                switched_storage_dict[samples] = {}

            if classes not in switched_storage_dict[samples]:
                switched_storage_dict[samples][classes] = data

    with open(prefix +'cnn32_switched_storage_dict.pkl', 'wb') as f:
        pickle.dump(switched_storage_dict, f)

    # save the model
    with open(prefix + 'cnn32.pkl', 'wb') as f:
        pickle.dump(cnn32, f)

    print("cnn32 finished")
    write_result(prefix + "cnn32_kappa.txt", cnn32_kappa)
    write_result(prefix + "cnn32_ece.txt", cnn32_ece)
    write_result(prefix + "cnn32_train_time.txt", cnn32_train_time)
    write_result(prefix + "cnn32_test_time.txt", cnn32_test_time)
    write_result(prefix + "cnn32_probs&labels.txt", cnn32_probs_labels)
    write_json(prefix + "cnn32_kappa.json", cnn32_kappa)
    write_json(prefix + "cnn32_ece.json", cnn32_ece)
    write_json(prefix + "cnn32_train_time.json", cnn32_train_time)
    write_json(prefix + "cnn32_test_time.json", cnn32_test_time)


def run_cnn32_2l():
    cnn32_2l_kappa = []
    cnn32_2l_ece = []
    cnn32_2l_train_time = []
    cnn32_2l_test_time = []
    cnn32_2l_probs_labels = []
    storage_dict = {}


    # # Grid search for best hyperparameters

    # cnn32_2l = SimpleCNN32Filter2Layers(num_classes=41)

    # class CNN32Wrapper(BaseEstimator):
    #     def __init__(self, lr=0.01, batch_size=32, epochs=30, criterion = nn.CrossEntropyLoss(), optimizer_name='adam', Valid_X=None, Valid_y=None):
    #         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    #         self.model = cnn32_2l.to(self.device)
    #         self.lr = lr
    #         self.batch_size = batch_size
    #         self.epochs = epochs
    #         self.criterion = criterion
    #         self.optimizer_name = optimizer_name
    #         self.Valid_X = Valid_X
    #         self.Valid_y = Valid_y

    #         if optimizer_name == 'sgd':
    #             self.optimizer = optim.SGD(self.model.parameters(), lr=self.lr)
    #         elif optimizer_name == 'adam':
    #             self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
    #         else:
    #             raise ValueError(f"Unknown optimizer: {optimizer_name}")

    #     def fit(self, X, y):
    #         max_epochs = [0]
    #         X = X.reshape(-1, 1, 32, 32)
    #         self.Valid_X = self.Valid_X.reshape(-1, 1, 32, 32)
    #         model = self.model
    #         criterion = self.criterion
    #         optimizer = self.optimizer
    #         prev_loss = float("inf")
    #         flag = 0
    #         for epoch in range(self.epochs):
    #             model.train()
    #             for i in range(0, len(X), self.batch_size):
    #                 inputs = X[i : i + self.batch_size].to(self.device)
    #                 labels = y[i : i + self.batch_size].to(self.device)
    #                 optimizer.zero_grad()
    #                 if inputs.shape[0] <= 2:
    #                     continue
    #                 outputs = model(inputs)
    #                 loss = criterion(outputs, labels)
    #                 loss.backward()
    #                 optimizer.step()

    #             model.eval()
    #             cur_loss = 0
    #             with torch.no_grad():
    #                 for i in range(0, len(self.Valid_X), self.batch_size):
    #                     # get the inputs
    #                     inputs = self.Valid_X[i : i + self.batch_size].to(self.device)
    #                     labels = self.Valid_y[i : i + self.batch_size].to(self.device)
    #                     if inputs.shape[0] == 1:
    #                         inputs = torch.cat((inputs, inputs, inputs), dim = 0)
    #                         labels = torch.cat((labels, labels, labels), dim = 0)

    #                     # forward
    #                     outputs = model(inputs)
    #                     loss = criterion(outputs, labels)
    #                     cur_loss += loss
    #             # early stop if 3 epochs in a row no loss decrease
    #             if cur_loss < prev_loss:
    #                 prev_loss = cur_loss
    #                 flag = 0
    #             else:
    #                 flag += 1
    #                 if flag >= 3:
    #                     max_epochs.append(epoch)
    #                     break
    #         # print(np.max(max_epochs))
    #         return self
        
    #     def predict(self, X):
    #         X = X.reshape(-1, 1, 32, 32)
    #         model = self.model
    #         model.eval()
    #         with torch.no_grad():
    #             outputs = model(X.to(self.device))
    #             _, predicted = torch.max(outputs.data, 1)
    #             return predicted.cpu()

    #     def score(self, X, y):
    #         X = X.reshape(-1, 1, 32, 32)
    #         model = self.model
    #         model.eval()
    #         predictions = self.predict(X)
    #         acc = accuracy_score(y, predictions)
    #         return acc

    # # train_images, train_labels, valid_images, valid_labels ,test_images, test_labels = prepare_data(fsdk18_train_images, fsdk18_train_labels, fsdk18_test_images, fsdk18_test_labels, samples_space[0] ,classes_space[0])
    # scaler = StandardScaler()
    # train_images = scaler.fit_transform(fsdk18_train_images)
    # valid_images = scaler.transform(fsdk18_valid_images)
    
    # train_images = torch.FloatTensor(train_images).unsqueeze(1)
    # train_labels = torch.LongTensor(fsdk18_train_labels)
    # valid_images = torch.FloatTensor(valid_images).unsqueeze(1)
    # valid_labels = torch.LongTensor(fsdk18_valid_labels)

    # param_grid={
    #     "batch_size": [64, 128, 256, 512, 1024],
    #     "lr": [0.0001, 0.001, 0.01, 0.1],
    #     "epochs": range(40, 101, 10),
    #     # "criterion": [nn.CrossEntropyLoss(), nn.NLLLoss()],
    #     # "optimizer_name": ["adam", "sgd"],
    #     }
    
    # grid_search = GridSearchCV(estimator=CNN32Wrapper(Valid_X=valid_images, Valid_y=valid_labels), param_grid=param_grid, cv=3)

    # grid_search.fit(train_images, train_labels)

    # results = pd.DataFrame(grid_search.cv_results_)
    # accuracy_scores = results['mean_test_score']
    # for i, accuracy in enumerate(accuracy_scores):
    #     print(f"HPs : {results['params'][i]} accuracy score is: {accuracy}")
    # print(" ")
    # best_params = grid_search.best_params_
    # print("Best Accuracy:", grid_search.best_score_)
    # print("Best Parameters:", best_params)


    # Best set of hyperparameters for 3classes:
                # optimizer_name="adam",
                # batch=1024,
                # epochs=60,
                # lr=0.001,






    for classes in classes_space:
        d1 = {}

        # cohen_kappa vs num training samples (cnn32_2l)
        for samples in samples_space:
            l3 = []
            # train data
            cnn32_2l = SimpleCNN32Filter2Layers(len(classes))
            # 3000 samples, 80% train is 2400 samples, 20% test
            train_images = trainx.copy()
            train_labels = trainy.copy()
            # reshape in 4d array
            test_images = testx.copy()
            test_labels = testy.copy()

            (
                train_images,
                train_labels,
                valid_images,
                valid_labels,
                test_images,
                test_labels,
            ) = prepare_data(
                train_images, train_labels, test_images, test_labels, samples, classes
            )

            cohen_kappa, ece, train_time, test_time, test_probs, test_labels, test_preds = run_dn_image_es(
                cnn32_2l,
                train_images,
                train_labels,
                valid_images,
                valid_labels,
                test_images,
                test_labels,
                # optimizer_name="adam",
                # batch=1024,
                # epochs=60,
                # lr=0.001,
            )
            cnn32_2l_kappa.append(cohen_kappa)
            cnn32_2l_ece.append(ece)
            cnn32_2l_train_time.append(train_time)
            cnn32_2l_test_time.append(test_time)

            actual_test_labels = []
            for i in range(len(test_labels)):
                actual_test_labels.append(int(classes[test_labels[i]]))

            sorted_classes = sorted(classes)
            cnn32_2l_probs_labels.append("Classes:" + str(classes))

            cnn32_2l_probs_labels.append("Sample size:" + str(samples))

            actual_preds = []
            for i in range(len(test_preds)):
                actual_preds.append(int(sorted_classes[test_preds[i].astype(int)]))
            
            for i in range(len(test_probs)):
                cnn32_2l_probs_labels.append("Posteriors:"+str(test_probs[i]) + ", " + "Test Labels:" + str(actual_test_labels[i]))
            cnn32_2l_probs_labels.append(" \n")

            for i in range(len(test_probs)):
                l3.append([test_probs[i].tolist(), actual_test_labels[i]])

            d1[samples] = l3

        storage_dict[tuple(sorted(classes))] = d1

    # switch the classes and sample sizes
    switched_storage_dict = {}

    for classes, class_data in storage_dict.items():
        for samples, data in class_data.items():

            if samples not in switched_storage_dict:
                switched_storage_dict[samples] = {}

            if classes not in switched_storage_dict[samples]:
                switched_storage_dict[samples][classes] = data

    with open(prefix + 'cnn32_2l_switched_storage_dict.pkl', 'wb') as f:
        pickle.dump(switched_storage_dict, f)

    # save the model
    with open(prefix + 'cnn32_2l.pkl', 'wb') as f:
        pickle.dump(cnn32_2l, f)

    print("cnn32_2l finished")
    write_result(prefix + "cnn32_2l_kappa.txt", cnn32_2l_kappa)
    write_result(prefix + "cnn32_2l_ece.txt", cnn32_2l_ece)
    write_result(prefix + "cnn32_2l_train_time.txt", cnn32_2l_train_time)
    write_result(prefix + "cnn32_2l_test_time.txt", cnn32_2l_test_time)
    write_result(prefix + "cnn32_2l_probs&labels.txt", cnn32_2l_probs_labels)
    write_json(prefix + "cnn32_2l_kappa.json", cnn32_2l_kappa)
    write_json(prefix + "cnn32_2l_ece.json", cnn32_2l_ece)
    write_json(prefix + "cnn32_2l_train_time.json", cnn32_2l_train_time)
    write_json(prefix + "cnn32_2l_test_time.json", cnn32_2l_test_time)


def run_cnn32_5l():
    cnn32_5l_kappa = []
    cnn32_5l_ece = []
    cnn32_5l_train_time = []
    cnn32_5l_test_time = []
    cnn32_5l_probs_labels = []
    storage_dict = {}


    # # Grid search for best hyperparameters

    # cnn32_5l = SimpleCNN32Filter5Layers(num_classes=41)

    # class CNN32Wrapper(BaseEstimator):
    #     def __init__(self, lr=0.01, batch_size=32, epochs=30, criterion = nn.CrossEntropyLoss(), optimizer_name='adam', Valid_X=None, Valid_y=None):
    #         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    #         self.model = cnn32_5l.to(self.device)
    #         self.lr = lr
    #         self.batch_size = batch_size
    #         self.epochs = epochs
    #         self.criterion = criterion
    #         self.optimizer_name = optimizer_name
    #         self.Valid_X = Valid_X
    #         self.Valid_y = Valid_y

    #         if optimizer_name == 'sgd':
    #             self.optimizer = optim.SGD(self.model.parameters(), lr=self.lr)
    #         elif optimizer_name == 'adam':
    #             self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
    #         else:
    #             raise ValueError(f"Unknown optimizer: {optimizer_name}")

    #     def fit(self, X, y):
    #         max_epochs = [0]
    #         X = X.reshape(-1, 1, 32, 32)
    #         self.Valid_X = self.Valid_X.reshape(-1, 1, 32, 32)
    #         model = self.model
    #         criterion = self.criterion
    #         optimizer = self.optimizer
    #         prev_loss = float("inf")
    #         flag = 0
    #         for epoch in range(self.epochs):
    #             model.train()
    #             for i in range(0, len(X), self.batch_size):
    #                 inputs = X[i : i + self.batch_size].to(self.device)
    #                 labels = y[i : i + self.batch_size].to(self.device)
    #                 optimizer.zero_grad()
    #                 if inputs.shape[0] <= 2:
    #                     continue
    #                 outputs = model(inputs)
    #                 loss = criterion(outputs, labels)
    #                 loss.backward()
    #                 optimizer.step()

    #             model.eval()
    #             cur_loss = 0
    #             with torch.no_grad():
    #                 for i in range(0, len(self.Valid_X), self.batch_size):
    #                     # get the inputs
    #                     inputs = self.Valid_X[i : i + self.batch_size].to(self.device)
    #                     labels = self.Valid_y[i : i + self.batch_size].to(self.device)
    #                     if inputs.shape[0] == 1:
    #                         inputs = torch.cat((inputs, inputs, inputs), dim = 0)
    #                         labels = torch.cat((labels, labels, labels), dim = 0)

    #                     # forward
    #                     outputs = model(inputs)
    #                     loss = criterion(outputs, labels)
    #                     cur_loss += loss
    #             # early stop if 3 epochs in a row no loss decrease
    #             if cur_loss < prev_loss:
    #                 prev_loss = cur_loss
    #                 flag = 0
    #             else:
    #                 flag += 1
    #                 if flag >= 3:
    #                     max_epochs.append(epoch)
    #                     break
    #                 else:
    #                     max_epochs.append(self.epochs)
    #         print(np.max(max_epochs))
    #         return self
        
    #     def predict(self, X):
    #         X = X.reshape(-1, 1, 32, 32)
    #         model = self.model
    #         model.eval()
    #         with torch.no_grad():
    #             outputs = model(X.to(self.device))
    #             _, predicted = torch.max(outputs.data, 1)
    #             return predicted.cpu()

    #     def score(self, X, y):
    #         X = X.reshape(-1, 1, 32, 32)
    #         model = self.model
    #         model.eval()
    #         predictions = self.predict(X)
    #         acc = accuracy_score(y, predictions)
    #         return acc

    # # train_images, train_labels, valid_images, valid_labels ,test_images, test_labels = prepare_data(fsdk18_train_images, fsdk18_train_labels, fsdk18_test_images, fsdk18_test_labels, samples_space[0] ,classes_space[0])
    # scaler = StandardScaler()
    # train_images = scaler.fit_transform(fsdk18_train_images)
    # valid_images = scaler.transform(fsdk18_valid_images)
    
    # train_images = torch.FloatTensor(train_images).unsqueeze(1)
    # train_labels = torch.LongTensor(fsdk18_train_labels)
    # valid_images = torch.FloatTensor(valid_images).unsqueeze(1)
    # valid_labels = torch.LongTensor(fsdk18_valid_labels)

    # param_grid={
    #     "batch_size": [16, 32, 64],
    #     "lr": [0.0001, 0.001, 0.01],
    #     "epochs": range(10, 31, 10),
    #     # "criterion": [nn.CrossEntropyLoss(), nn.NLLLoss()],
    #     # "optimizer_name": ["adam", "sgd"],
    #     }
    
    # grid_search = GridSearchCV(estimator=CNN32Wrapper(Valid_X=valid_images, Valid_y=valid_labels), param_grid=param_grid, cv=3)

    # grid_search.fit(train_images, train_labels)

    # results = pd.DataFrame(grid_search.cv_results_)
    # accuracy_scores = results['mean_test_score']
    # for i, accuracy in enumerate(accuracy_scores):
    #     print(f"HPs : {results['params'][i]} accuracy score is: {accuracy}")
    # print(" ")
    # best_params = grid_search.best_params_
    # print("Best Accuracy:", grid_search.best_score_)
    # print("Best Parameters:", best_params)



    # Best set of hyperparameters for 3 classes:
                # lr=0.001,
                # epochs=100,
                # batch=32,
                # optimizer_name="sgd",





    for classes in classes_space:
        d1 = {}

        # cohen_kappa vs num training samples (cnn32_5l)
        for samples in samples_space:
            l3 = []
            # train data
            cnn32_5l = SimpleCNN32Filter5Layers(len(classes))
            # 3000 samples, 80% train is 2400 samples, 20% test
            train_images = trainx.copy()
            train_labels = trainy.copy()
            # reshape in 4d array
            test_images = testx.copy()
            test_labels = testy.copy()

            (
                train_images,
                train_labels,
                valid_images,
                valid_labels,
                test_images,
                test_labels,
            ) = prepare_data(
                train_images, train_labels, test_images, test_labels, samples, classes
            )

            cohen_kappa, ece, train_time, test_time, test_probs, test_labels, test_preds = run_dn_image_es(
                cnn32_5l,
                train_images,
                train_labels,
                valid_images,
                valid_labels,
                test_images,
                test_labels,
                optimizer_name="adam",
                # lr=0.001,
                # epochs=100,
                # batch=32,
            )
            cnn32_5l_kappa.append(cohen_kappa)
            cnn32_5l_ece.append(ece)
            cnn32_5l_train_time.append(train_time)
            cnn32_5l_test_time.append(test_time)

            actual_test_labels = []
            for i in range(len(test_labels)):
                actual_test_labels.append(int(classes[test_labels[i]]))

            sorted_classes = sorted(classes)
            cnn32_5l_probs_labels.append("Classes:" + str(classes))

            cnn32_5l_probs_labels.append("Sample size:" + str(samples))

            actual_preds = []
            for i in range(len(test_preds)):
                actual_preds.append(int(sorted_classes[test_preds[i].astype(int)]))

            for i in range(len(test_probs)):
                cnn32_5l_probs_labels.append("Posteriors:"+str(test_probs[i]) + ", " + "Test Labels:" + str(actual_test_labels[i]))
            cnn32_5l_probs_labels.append(" \n")

            for i in range(len(test_probs)):
                l3.append([test_probs[i].tolist(), actual_test_labels[i]])

            d1[samples] = l3

        storage_dict[tuple(sorted(classes))] = d1

    # switch the classes and sample sizes
    switched_storage_dict = {}

    for classes, class_data in storage_dict.items():
        for samples, data in class_data.items():

            if samples not in switched_storage_dict:
                switched_storage_dict[samples] = {}

            if classes not in switched_storage_dict[samples]:
                switched_storage_dict[samples][classes] = data

    with open(prefix + 'cnn32_5l_switched_storage_dict.pkl', 'wb') as f:
        pickle.dump(switched_storage_dict, f)

    # save the model
    with open(prefix + 'cnn32_5l.pkl', 'wb') as f:
        pickle.dump(cnn32_5l, f)

    print("cnn32_5l finished")
    write_result(prefix + "cnn32_5l_kappa.txt", cnn32_5l_kappa)
    write_result(prefix + "cnn32_5l_ece.txt", cnn32_5l_ece)
    write_result(prefix + "cnn32_5l_train_time.txt", cnn32_5l_train_time)
    write_result(prefix + "cnn32_5l_test_time.txt", cnn32_5l_test_time)
    write_result(prefix + "cnn32_5l_probs&labels.txt", cnn32_5l_probs_labels)
    write_json(prefix + "cnn32_5l_kappa.json", cnn32_5l_kappa)
    write_json(prefix + "cnn32_5l_ece.json", cnn32_5l_ece)
    write_json(prefix + "cnn32_5l_train_time.json", cnn32_5l_train_time)
    write_json(prefix + "cnn32_5l_test_time.json", cnn32_5l_test_time)


def run_resnet18():
    resnet18_kappa = []
    resnet18_ece = []
    resnet18_train_time = []
    resnet18_test_time = []
    resnet18_probs_labels = []
    storage_dict = {}



    # Grid search for best hyperparameters

    resnet = models.resnet18(pretrained=True)

    num_ftrs = resnet.fc.in_features
    resnet.fc = nn.Linear(num_ftrs, 41)

    class CNN32Wrapper(BaseEstimator):
        def __init__(self, lr=0.01, batch_size=32, epochs=30, criterion = nn.CrossEntropyLoss(), optimizer_name='adam', Valid_X=None, Valid_y=None):
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = resnet.to(self.device)
            self.lr = lr
            self.batch_size = batch_size
            self.epochs = epochs
            self.criterion = criterion
            self.optimizer_name = optimizer_name
            self.Valid_X = Valid_X
            self.Valid_y = Valid_y

            if optimizer_name == 'sgd':
                self.optimizer = optim.SGD(self.model.parameters(), lr=self.lr)
            elif optimizer_name == 'adam':
                self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
            else:
                raise ValueError(f"Unknown optimizer: {optimizer_name}")

        def fit(self, X, y):
            max_epochs = [0]
            X = X.reshape(-1, 3, 32, 32)
            self.Valid_X = self.Valid_X.reshape(-1, 3, 32, 32)
            model = self.model
            criterion = self.criterion
            optimizer = self.optimizer
            prev_loss = float("inf")
            flag = 0
            for epoch in range(self.epochs):
                model.train()
                for i in range(0, len(X), self.batch_size):
                    inputs = X[i : i + self.batch_size].to(self.device)
                    labels = y[i : i + self.batch_size].to(self.device)
                    optimizer.zero_grad()
                    if inputs.shape[0] <= 2:
                        continue
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                    loss.backward()
                    optimizer.step()

                model.eval()
                cur_loss = 0
                with torch.no_grad():
                    for i in range(0, len(self.Valid_X), self.batch_size):
                        # get the inputs
                        inputs = self.Valid_X[i : i + self.batch_size].to(self.device)
                        labels = self.Valid_y[i : i + self.batch_size].to(self.device)
                        if inputs.shape[0] == 1:
                            inputs = torch.cat((inputs, inputs, inputs), dim = 0)
                            labels = torch.cat((labels, labels, labels), dim = 0)

                        # forward
                        outputs = model(inputs)
                        loss = criterion(outputs, labels)
                        cur_loss += loss
                # early stop if 3 epochs in a row no loss decrease
                if cur_loss < prev_loss:
                    prev_loss = cur_loss
                    flag = 0
                else:
                    flag += 1
                    if flag >= 3:
                        max_epochs.append(epoch)
                        break
                    else:
                        max_epochs.append(self.epochs)
            print(np.max(max_epochs))
            return self
        
        def predict(self, X):
            X = X.reshape(-1, 3, 32, 32)
            model = self.model
            model.eval()
            with torch.no_grad():
                outputs = model(X.to(self.device))
                _, predicted = torch.max(outputs.data, 1)
                return predicted.cpu()

        def score(self, X, y):
            X = X.reshape(-1, 3, 32, 32)
            model = self.model
            model.eval()
            predictions = self.predict(X)
            acc = accuracy_score(y, predictions)
            return acc

    # train_images, train_labels, valid_images, valid_labels ,test_images, test_labels = prepare_data(fsdk18_train_images, fsdk18_train_labels, fsdk18_test_images, fsdk18_test_labels, samples_space[0] ,classes_space[0])
    scaler = StandardScaler()
    train_images = scaler.fit_transform(fsdk18_train_images)
    valid_images = scaler.transform(fsdk18_valid_images)
    
    train_images = torch.FloatTensor(train_images).unsqueeze(1)
    train_labels = torch.LongTensor(fsdk18_train_labels)
    valid_images = torch.FloatTensor(valid_images).unsqueeze(1)
    valid_labels = torch.LongTensor(fsdk18_valid_labels)

    train_images = torch.cat((train_images, train_images, train_images), dim=1)
    valid_images = torch.cat((valid_images, valid_images, valid_images), dim=1)

    param_grid={
        "batch_size": [16, 32, 64],
        "lr": [0.001, 0.01, 0.1],
        "epochs": range(10, 31, 10),
        # "criterion": [nn.CrossEntropyLoss(), nn.NLLLoss()],
        # "optimizer_name": ["adam", "sgd"],
        }
    
    grid_search = GridSearchCV(estimator=CNN32Wrapper(Valid_X=valid_images, Valid_y=valid_labels), param_grid=param_grid, cv=3)

    grid_search.fit(train_images, train_labels)

    results = pd.DataFrame(grid_search.cv_results_)
    accuracy_scores = results['mean_test_score']
    for i, accuracy in enumerate(accuracy_scores):
        print(f"HPs : {results['params'][i]} accuracy score is: {accuracy}")
    print(" ")
    best_params = grid_search.best_params_
    print("Best Accuracy:", grid_search.best_score_)
    print("Best Parameters:", best_params)






    # for classes in classes_space:
    #     d1 = {}

    #     # cohen_kappa vs num training samples (resnet18)
    #     for samples in samples_space:
    #         l3 = []
    #         resnet = models.resnet18(pretrained=True)

    #         num_ftrs = resnet.fc.in_features
    #         resnet.fc = nn.Linear(num_ftrs, len(classes))
    #         # train data
    #         # 3000 samples, 80% train is 2400 samples, 20% test
    #         train_images = trainx.copy()
    #         train_labels = trainy.copy()
    #         # reshape in 4d array
    #         test_images = testx.copy()
    #         test_labels = testy.copy()

    #         (
    #             train_images,
    #             train_labels,
    #             valid_images,
    #             valid_labels,
    #             test_images,
    #             test_labels,
    #         ) = prepare_data(
    #             train_images, train_labels, test_images, test_labels, samples, classes
    #         )

    #         # need to duplicate channel because batch norm cant have 1 channel images
    #         train_images = torch.cat((train_images, train_images, train_images), dim=1)
    #         valid_images = torch.cat((valid_images, valid_images, valid_images), dim=1)
    #         test_images = torch.cat((test_images, test_images, test_images), dim=1)

    #         cohen_kappa, ece, train_time, test_time, test_probs, test_labels, test_preds = run_dn_image_es(
    #             resnet,
    #             train_images,
    #             train_labels,
    #             valid_images,
    #             valid_labels,
    #             test_images,
    #             test_labels,
    #         )
    #         resnet18_kappa.append(cohen_kappa)
    #         resnet18_ece.append(ece)
    #         resnet18_train_time.append(train_time)
    #         resnet18_test_time.append(test_time)

    #         actual_test_labels = []
    #         for i in range(len(test_labels)):
    #             actual_test_labels.append(int(classes[test_labels[i]]))

    #         sorted_classes = sorted(classes)
    #         resnet18_probs_labels.append("Classes:" + str(classes))

    #         resnet18_probs_labels.append("Sample size:" + str(samples))

    #         actual_preds = []
    #         for i in range(len(test_preds)):
    #             actual_preds.append(int(sorted_classes[test_preds[i].astype(int)]))

    #         for i in range(len(test_probs)):
    #             resnet18_probs_labels.append("Posteriors:"+str(test_probs[i]) + ", " + "Test Labels:" + str(actual_test_labels[i]))
    #         resnet18_probs_labels.append(" \n")

    #         for i in range(len(test_probs)):
    #             l3.append([test_probs[i].tolist(), actual_test_labels[i]])
        
    #         d1[samples] = l3
    #     storage_dict[tuple(sorted(classes))] = d1

    # # switch the classes and sample sizes
    # switched_storage_dict = {}

    # for classes, class_data in storage_dict.items():
    #     for samples, data in class_data.items():

    #         if samples not in switched_storage_dict:
    #             switched_storage_dict[samples] = {}

    #         if classes not in switched_storage_dict[samples]:
    #             switched_storage_dict[samples][classes] = data

    # with open(prefix + 'resnet18_switched_storage_dict.pkl', 'wb') as f:
    #     pickle.dump(switched_storage_dict, f)

    # # save the model
    # with open(prefix + 'resnet18.pkl', 'wb') as f:
    #     pickle.dump(resnet, f)


    # print("resnet18 finished")
    # write_result(prefix + "resnet18_kappa.txt", resnet18_kappa)
    # write_result(prefix + "resnet18_ece.txt", resnet18_ece)
    # write_result(prefix + "resnet18_train_time.txt", resnet18_train_time)
    # write_result(prefix + "resnet18_test_time.txt", resnet18_test_time)
    # write_result(prefix + "resnet18_probs&labels.txt", resnet18_probs_labels)
    # write_json(prefix + "resnet18_kappa.json", resnet18_kappa)
    # write_json(prefix + "resnet18_ece.json", resnet18_ece)
    # write_json(prefix + "resnet18_train_time.json", resnet18_train_time)
    # write_json(prefix + "resnet18_test_time.json", resnet18_test_time)


if __name__ == "__main__":
    torch.multiprocessing.freeze_support()

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", help="class number")
    parser.add_argument("-f", help="feature type")
    parser.add_argument("-data", help="audio files location")
    parser.add_argument("-labels", help="labels file location")
    args = parser.parse_args()
    n_classes = int(args.m)
    feature_type = str(args.f)

    train_folder = str(args.data)
    train_label = pd.read_csv(str(args.labels))

    # select subset of data that only contains 300 samples per class
    labels_chosen = train_label[
        train_label["label"].map(train_label["label"].value_counts() >= 0)
    ]

    training_files = []
    for file in os.listdir(train_folder):
        for x in labels_chosen.fname.to_list():
            if file.endswith(x):
                training_files.append(file)

    path_recordings = []
    for audiofile in training_files:
        path_recordings.append(os.path.join(train_folder, audiofile))

    # convert selected label names to integers
    labels_to_index = {
            "Acoustic_guitar": 0,
            "Applause": 1,
            "Bark": 2,
            "Bass_drum": 3,
            "Burping_or_eructation": 4,
            "Bus": 5,
            "Cello": 6,
            "Chime": 7,
            "Clarinet": 8,
            "Computer_keyboard": 9,
            "Cough": 10,
            "Cowbell": 11,
            "Double_bass": 12,
            "Drawer_open_or_close": 13,
            "Electric_piano": 14,
            "Fart": 15,
            "Finger_snapping": 16,
            "Fireworks": 17,
            "Flute": 18,
            "Glockenspiel": 19,
            "Gong": 20,
            "Gunshot_or_gunfire": 21,
            "Harmonica": 22,
            "Hi-hat": 23,
            "Keys_jangling": 24,
            "Knock": 25,
            "Laughter": 26,
            "Meow": 27,
            "Microwave_oven": 28,
            "Oboe": 29,
            "Saxophone": 30,
            "Scissors": 31,
            "Shatter": 32,
            "Snare_drum": 33,
            "Squeak": 34,
            "Tambourine": 35,
            "Tearing": 36,
            "Telephone": 37,
            "Trumpet": 38,
            "Violin_or_fiddle": 39,
            "Writing": 40,
        }

    # encode labels to integers
    get_labels = labels_chosen["label"].replace(labels_to_index).to_list()
    labels_chosen = labels_chosen.reset_index()

    # data is normalized upon loading
    # load dataset
    x_spec, y_number = load_fsdk18(
        path_recordings, labels_chosen, get_labels, feature_type
    )

    print("Size of the data:",x_spec.shape)

    nums = list(range(18))
    samples_space = np.geomspace(10, 450, num=6, dtype=int)
    # define path, samples space and number of class combinations
    if feature_type == "melspectrogram":
        prefix = args.m + "_class_mel/"
    elif feature_type == "spectrogram":
        prefix = args.m + "_class/"
    elif feature_type == "mfcc":
        prefix = args.m + "_class_mfcc/"

    # create list of classes with const random seed
    random.Random(5).shuffle(nums)
    classes_space = list(combinations_45(nums, n_classes))

    # scale the data
    # x_spec = x_spec[:5400] #reshape x_spec by Ziyan for testing, orginial shape was (11073, 32, 32)
    # print(x_spec.shape)
    x_spec = scale(x_spec.reshape(11073, -1), axis=1).reshape(11073, 32, 32)
    y_number = np.array(y_number)
    # y_number = y_number[:5400] #reshape x_spec by Ziyan for testing, orginial shape was (11073, 32, 32)

    # need to take train/valid/test equally from each class
    trainx, remainx, trainy, remainy = train_test_split(
        x_spec,
        y_number,
        shuffle=True,
        test_size=0.5,
        stratify=y_number,
    )

    testx, valx, testy, valy = train_test_split(
        remainx,
        remainy,
        shuffle=True,
        test_size=0.5,
        stratify=remainy,
    )

    # 3000 samples, 80% train is 2400 samples, 20% test
    fsdk18_train_images = trainx.reshape(-1, 32 * 32)
    fsdk18_train_labels = trainy.copy()
    # reshape in 2d array
    fsdk18_test_images = testx.reshape(-1, 32 * 32)
    fsdk18_test_labels = testy.copy()
    # validation set
    fsdk18_valid_images = valx.reshape(-1, 32 * 32)
    fsdk18_valid_labels = valy.copy()

    # print("Running RF tuning \n")
    # run_naive_rf()

    # print("Running CNN32 tuning \n")
    # run_cnn32()

    # print("Running CNN32_2l tuning \n")
    # run_cnn32_2l()

    # print("Running CNN32_5l tuning \n")
    # run_cnn32_5l()

    # print("Running Resnet tuning \n")
    # run_resnet18()
