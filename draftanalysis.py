import sklearn
from sklearn.svm import SVR
import numpy as np
import openpyxl
import os
from colour import Color
import math


def getSamples(positionsDict, variables, headersKey):
    for excel in os.listdir(os.curdir + '/Training'):
        wb = openpyxl.load_workbook(filename = os.curdir + '/Training/' + excel)
        ws = wb.get_sheet_by_name("Draft+Results")
        row = 2
        pick = ws.cell(row=row, column=headersKey['Overall Draft Pick']).value
        while pick:
            position = ws.cell(row=row, column=headersKey['Position']).value
            nextRow = [float(ws.cell(row=row, column=headersKey['Position-Based Draft Pick']).value.split('-')[1]), float(ws.cell(row=row, column=headersKey['Position-Based Season Finish']).value.split('-')[1])]
            if nextRow[1] == 0:
                if ws.cell(row=row, column=headersKey['Position']) == 'WR' or 'RB':
                    nextRow[1] = 100
                else:
                    nextRow[1] = 50
            for variable in variables:
                nextRow.append(float(ws.cell(row=row, column=headersKey[variable]).value))
            positionsDict[position]['inputs'].append(nextRow)
            positionsDict[position]['outputs'].append(float(ws.cell(row=row, column=headersKey['Pick Rating (1 worst, 10 best)']).value))
            row += 1
            pick = ws.cell(row=row, column=1).value

def getHeaders(path):
    wb = openpyxl.load_workbook(filename = path)
    ws = wb.get_sheet_by_name("Draft+Results")
    headers = {}
    row = 1
    column = 1
    header = ws.cell(row=row,column=column).value
    while header:
        headers[header] = column
        column += 1
        header = ws.cell(row=row,column=column).value
    return headers

def trainSamples(positionsDict):
    for position in positionsDict:
        svRegressor = SVR()
        svRegressor.fit(np.asarray(positionsDict[position]['inputs']), np.asarray(positionsDict[position]['outputs']))
        positionsDict[position]['regressor'] = svRegressor

def evaluate(positionsDict, variables, headersKey):
    for excel in os.listdir(os.curdir + '/Drafts'):
        teamNames = set()
        wb = openpyxl.load_workbook(filename = os.curdir + '/Drafts/' + excel)
        ws = wb.get_sheet_by_name("Draft+Results")
        row = 2
        pick = ws.cell(row=row, column=1).value
        while pick:
            teamNames.add(ws.cell(row=row, column=headersKey['Fantasy Team']).value)
            position = ws.cell(row=row, column=headersKey['Position']).value
            sample = [float(ws.cell(row=row, column=headersKey['Position-Based Draft Pick']).value.split('-')[1]), float(ws.cell(row=row, column=headersKey['Position-Based Season Finish']).value.split('-')[1])]
            if sample[1] == 0:
                if ws.cell(row=row, column=headersKey['Position']) == 'WR' or 'RB':
                    sample[1] = 100
                else:
                    sample[1] = 50
            for variable in variables:
                sample.append(float(ws.cell(row=row, column=headersKey[variable]).value))
            ws.cell(row=row, column = headersKey['Pick Rating (1 worst, 10 best)']).value = str(round(list(positionsDict[position]['regressor'].predict(np.asarray([sample])))[0], 4))
            row += 1
            pick = ws.cell(row=row, column=1).value
        teamSheets(teamNames, headersKey, wb)
        wb.save(os.curdir + '/Fitted/' + excel)

def teamSheets(teams, headers, wb):
    teamPicks = {}
    namesKey = {}
    colors = list(Color("red").range_to(Color("yellow"),6))[:-1] + list(Color("yellow").range_to(Color("green"),5))
    for index, team in enumerate(teams):
        teamPicks[team] = 2
        try:
            wb.create_sheet(team)
            namesKey[team] = team
        except:
            name = 'Team' + str(index + 1)
            wb.create_sheet(name)
            namesKey[team] = name
        ws2 = wb.get_sheet_by_name(namesKey[team])
        for header in headers:
            ws2.cell(row=1, column=headers[header]).value = header
    ws = wb.get_sheet_by_name("Draft+Results")
    row = 2
    pick = ws.cell(row=row, column=1).value
    while pick:
        team = ws.cell(row=row, column=headersKey['Fantasy Team']).value
        ws2 = wb.get_sheet_by_name(namesKey[team])
        for header in headers:
            ws2.cell(row=teamPicks[team], column=headers[header]).value = ws.cell(row=row, column=headers[header]).value
        colorIndex = math.floor(float(ws2.cell(row=teamPicks[team], column=headers['Pick Rating (1 worst, 10 best)']).value))
        if colorIndex > 9:
            colorIndex = 9
        if colorIndex < 0:
            colorIndex = 0
        ws2.cell(row=teamPicks[team], column=headers['Pick Rating (1 worst, 10 best)']).fill = openpyxl.styles.PatternFill(start_color=str(colors[colorIndex].hex_l)[1:], end_color=str(colors[colorIndex].hex_l)[1:], fill_type = 'solid')
        teamPicks[team] += 1
        row += 1
        pick = ws.cell(row=row, column=1).value
    for team in teams:
        ws2 = wb.get_sheet_by_name(namesKey[team])
        ws2.delete_cols(headers['Fantasy Team'])
        ws2.column_dimensions['B'].width = 25.0
        ws2.column_dimensions['D'].width = 25.0


if __name__ == "__main__":
    positionsDict = {'D/ST': {'inputs': [], 'outputs': []}, 'HC': {'inputs': [], 'outputs': []}, 'K': {'inputs': [], 'outputs': []}, 'QB': {'inputs': [], 'outputs': []}, 'RB': {'inputs': [], 'outputs': []}, 'WR': {'inputs': [], 'outputs': []}, 'TE': {'inputs': [], 'outputs': []}}
    variables = ['Overall Draft Pick', 'Overall Finish', 'Total Points', 'Number of Weeks Missed', 'Average Weekly Scoring']
    
    for excel in os.listdir(os.curdir + '/Fitted'):
        os.remove(os.curdir + '/Fitted/' + excel)
    if len(os.listdir(os.curdir + '/Training')) == 0:
        raise ValueError("No Training Data in Training Directory")

    headersKey = getHeaders(os.curdir + '/Training/' + os.listdir(os.curdir + '/Training')[0])
    getSamples(positionsDict, variables, headersKey)
    trainSamples(positionsDict)
    evaluate(positionsDict, variables, headersKey)
