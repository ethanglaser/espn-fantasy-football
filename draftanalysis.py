import sklearn
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.svm import SVR
import numpy as np
import openpyxl
import os

def basic():
    for excel in os.listdir(os.curdir + '/Fitted/Basic7'):
        os.remove(os.curdir + '/Fitted/Basic7/' + excel)
    inputs, outputs = [], []
    for excel in os.listdir(os.curdir + '/Training'):
        wb = openpyxl.load_workbook(filename = os.curdir + '/Training/' + excel)
        ws = wb.get_sheet_by_name("Draft+Results")

        row = 2
        pick = ws.cell(row=row, column=1).value
        inputs, outputs = [], []
        while pick:
            nextRow = [float(ws.cell(row=row, column=4).value.split('-')[1]), float(ws.cell(row=row, column=5).value.split('-')[1])]
            if nextRow[1] == 0:
                if ws.cell(row=row, column=4).value.split('-')[0] == 'WR' or 'RB':
                    nextRow[1] = 100
                else:
                    nextRow[1] = 50
            inputs.append(nextRow)
            outputs.append(float(ws.cell(row=row, column=6).value))
            row += 1
            pick = ws.cell(row=row, column=1).value

    logRegressor = LogisticRegression()
    logRegressor.fit(np.asarray(inputs), np.asarray(outputs))
    svRegressor = SVR()
    svRegressor.fit(np.asarray(inputs), np.asarray(outputs))
    linRegressor = LinearRegression()
    linRegressor.fit(np.asarray(inputs), np.asarray(outputs))
    poly2 = PolynomialFeatures(degree=2)
    poly3 = PolynomialFeatures(degree=3)
    poly4 = PolynomialFeatures(degree=4)
    poly5 = PolynomialFeatures(degree=5)
    poly2Inputs = poly2.fit_transform(np.asarray(inputs))
    poly3Inputs = poly3.fit_transform(np.asarray(inputs))
    poly4Inputs = poly4.fit_transform(np.asarray(inputs))
    poly5Inputs = poly5.fit_transform(np.asarray(inputs))
    clf2 = LinearRegression()
    clf2.fit(poly2Inputs, np.asarray(outputs))
    clf3 = LinearRegression()
    clf3.fit(poly3Inputs, np.asarray(outputs))
    clf4 = LinearRegression()
    clf4.fit(poly4Inputs, np.asarray(outputs))
    clf5 = LinearRegression()
    clf5.fit(poly5Inputs, np.asarray(outputs))

    for excel in os.listdir(os.curdir + '/Drafts'):
        wb2 = openpyxl.load_workbook(filename = os.curdir + '/Drafts/' + excel)
        ws2 = wb2.get_sheet_by_name("Draft+Results")

        row = 2
        pick = ws2.cell(row=row, column=1).value
        samples = []
        while pick:
            nextRow = [float(ws2.cell(row=row, column=4).value.split('-')[1]), float(ws2.cell(row=row, column=5).value.split('-')[1])]
            if nextRow[1] == 0:
                if ws2.cell(row=row, column=4).value.split('-')[0] == 'WR' or 'RB':
                    nextRow[1] = 100
                else:
                    nextRow[1] = 50
            samples.append(nextRow)
            row += 1
            pick = ws2.cell(row=row, column=1).value
        logResults = logRegressor.predict(np.asarray(samples))
        linResults = linRegressor.predict(np.asarray(samples))
        svResults = svRegressor.predict(np.asarray(samples))
        poly2Samples = poly2.fit_transform(np.asarray(samples))
        poly2Results = clf2.predict(poly2Samples)    
        poly3Samples = poly3.fit_transform(np.asarray(samples))
        poly3Results = clf3.predict(poly3Samples)    
        poly4Samples = poly4.fit_transform(np.asarray(samples))
        poly4Results = clf4.predict(poly4Samples)    
        poly5Samples = poly5.fit_transform(np.asarray(samples))
        poly5Results = clf5.predict(poly5Samples)

        for index, results in enumerate([logResults, linResults, svResults, poly2Results, poly3Results, poly4Results, poly5Results]):
            row2 = 2
            for test in list(results):
                ws2.cell(row=row2, column = 6 + index).value = str(test)
                row2 += 1

        wb2.save(os.curdir + '/Fitted/Basic7/' + excel)

if __name__ == "__main__":
    basic()
