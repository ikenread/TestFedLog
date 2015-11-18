import os
import re
import time
import shelve
import modules.config as conf

# Sets up custom month dictionary
months = {
    1: "JAN",
    2: "FEB",
    3: "MAR",
    4: "APR",
    5: "MAY",
    6: "JUN",
    7: "JUL",
    8: "AUG",
    9: "SEP",
    10: "OCT",
    11: "NOV",
    12: "DEC",
}

# Get the path and name for file to be parsed
while True:
    try:
        # Asks user for input for testplan location
        path = raw_input("Please enter PATH(defaults to current directory): ")
        month = raw_input("Please enter MONTHNUMBER(defaults to next month): ")

        currentMonth = int(time.strftime("%m"))
        currentYear = int(time.strftime("%Y"))

        # If the year and month aren't set then default to the next month and next month's year
        if not month:
            if currentMonth == 12:
                year = currentYear + 1
                month = 1
            else:
                year = currentYear
                month = currentMonth + 1

        else:
            if month == 1 and currentMonth == 12:
                year = currentYear + 1
            else:
                year = currentYear

        print(
            "Looking for TestPlan: " + os.path.abspath(path) + os.sep +
            "FEDLOG TestPlan - " + months[int(month)] + " " + str(year) + ".log\n"
        )

        # Opens testplan and copies
        testPlan = open(
            os.path.abspath(path) + os.sep + "FEDLOG TestPlan - " + months[int(month)] + " " + str(year) + ".log", "r"
        )
        testPlanRead = testPlan.read()

        # Checks to see if original testplan has been made yet, if not creates it
        if not os.path.exists(os.path.abspath(path) + os.sep + "FEDLOG TestPlan - " + months[int(month)] + " " + str(
                year) + "-Original.log"):
            originalTestPlan = open(
                os.path.abspath(path) + os.sep + "FEDLOG TestPlan - " + months[int(month)] + " " + str(
                    year) + "-Original.log", "w"
            )
            originalTestPlan.write(testPlanRead)
            originalTestPlan.close()

        testPlan.close()
        testPlan = open(path + "FEDLOG TestPlan - " + months[int(month)] + " " + str(year) + ".log", "w")

        # Makes the generated directory
        if not os.path.exists(os.path.abspath(path) + os.sep + "Generated"):
            os.makedirs(os.path.abspath(path) + os.sep + "Generated")

        # Creates a data file to read later
        dataFile = shelve.open(
            os.path.abspath(path) + os.sep +
            "Generated" + os.sep + "TestPlanData-" + months[int(month)] + str(year)
        )

        break

    except IOError as e:
        print("Couldn't find the TestLog file, please try again.")
        print(e)

    except KeyError as e:
        print("A value that you typed in is not valid, please try again.")
        print(e)

# Compiles regex to capture individual tables
# \|\ \|\s+(\w+)\s+\((\w+)\)\s+-\s+([\S\ ]+)\s+-+\s+((?:[\S\ ]+\r?\n)+)
getTables = re.compile(r'''
    \|\ \|\s+           #Matches two pipes separated by a space followed by one or more whitespaces
    (\w+)               #Captures the Table Name (group(1))
    \s+\(               #Matches one or more whitespaces followed by an open parentheses
    (\w+)               #Captures the Category (group(2))
    \)\s+-\s+           #Matches the end parentheses followed one or more whitespaces, a single dash,
                        #and one or more whitespaces
    ([\S\ ]+)           #Captures the Column Names (group(3)) by matching one or more space or non-whitespace
    \s+-+\s+            #Matches one or more whitespaces, one or more dashes, and then one or more whitespaces
    ((?:[\S\ ]+\r?\n)+) #Captures the Data (group(4)) comprised of one or more groups matching one or more
                        #spaces or non-whitespaces followed by an optional carriage return and a newline
''', re.VERBOSE)

# Searches the doc with regex for tables
tables = getTables.finditer(testPlanRead)

# Sets up the number of times a table wasn't found
didntFind = []

for table in tables:

    # Splits the data rows allowing for both windows and unix linebreaks, slices off the blank cell at end.
    dataRows = re.split(r'\r?\n', table.group(4))[0:-1]

    # Strips out whitespace from the ends and splits the data by the pipe delimiter
    # Then counts the number of nonempty cells in each and saves the longest
    strippedRows = []
    rowCounts = []
    for dataRow in dataRows:
        strippedRow = dataRow.strip()
        dataCells = strippedRow.split('|')

        count = 0
        for dataCell in dataCells:
            if dataCell:
                count += 1

        rowCounts.append(count)
        strippedRows.append(dataCells)

    # Uses the row counts to find the index with the highest number of nonempty cells
    biggestRow = rowCounts.index(max(rowCounts))

    # Splits columns
    columns = table.group(3).split('|')

    # Makes a dictionary for each table
    tableDict = {
        'Name': table.group(1),
        'Category': table.group(2),
        'Columns': columns,
        'Rows': strippedRows,
        'Biggest Row': strippedRows[biggestRow],
    }

    # Prints Biggest Row to terminal, table by table
    print(tableDict['Name'] + " (" + tableDict['Category'] + ")")
    for i in range(len(columns)):
        print(tableDict['Columns'][i] + ": " + tableDict['Biggest Row'][i])

    response = raw_input("Press enter to continue. 'N' for did not find. 'M' for more from same table.\n")

    if response.upper() == 'M':
        print(tableDict['Columns'])
        for i in range(len(tableDict['Rows'])):
            print(tableDict['Rows'][i])
        response = raw_input("Press enter to continue. 'N' for did not find.\n")

    if response.upper() != 'N':
        testPlanRead = testPlanRead.replace("| | " + tableDict['Name'], "|x| " + tableDict['Name'])
    else:
        didntFind.append(tableDict['Name'])

    # Adds dictionary to a list
    dataFile[table.group(1)] = tableDict

if not didntFind:
    if "Completed _________________________ by _____________________" in testPlanRead:
        # Asks to sign and date
        sign = raw_input("Eveything has been found! Would you like to sign? (Y/N) ")
        if sign.upper() != 'N':
            while True:
                name = raw_input("Name: ")
                if name:
                    break
            testPlanRead = testPlanRead.replace(
                "Completed _________________________ by _____________________",
                "Completed " + time.strftime("%a %b %d %X %Y") + " by " + name)

    else:
        print("Everything in this testplan has been found and the document has been signed.")

else:
    print("You couldn't find values on these tables:")
    for i in range(len(didntFind)):
        print(didntFind[i])
    print("\nPlease make the appropriate corrections and rerun script.")

testPlan.write(testPlanRead)
# Closes Docs
testPlan.close()
dataFile.close()

