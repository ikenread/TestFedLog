import re

# GLOBAL VARIABLES

# Compiles regex to capture individual tables
# \|\ \|\s+(\w+)\s+\((\w+)\)\s+-\s+([\S\ ]+)\s+-+\s+((?:[\S\ ]+\r?\n)+)
TABLE_REGEX = r'''
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
'''


def getTables(string):
    regex = re.compile(TABLE_REGEX, re.VERBOSE)
    return regex.finditer(string)

class Table(object):
    def __init__(self, name, category, columns, rows):
        self.name = name
        self.category = category

        if isinstance(columns, basestring):
            self.columns = self.parsePipe(columns)
        else:
            self.columns = columns

        if isinstance(rows, basestring):
            self.rows = self.parsePipe(self.parseNewline(rows))
        else:
            self.rows = rows

    def longestRow(self):

        rowcounts = []

        for row in self.rows:
            count = 0
            for cell in row:
                if cell:
                    count += 1

            rowcounts.append(count)

        return rowcounts.index(max(rowcounts))

    @staticmethod
    def parseNewline(string):
        # Splits on the new line slicing off the empty cell at the end
        return re.split(r'\r?\n', string)[0:-1]

    @staticmethod
    def parsePipe(strings):
        # Strips whitespace off the extremes and then returns an array of data split by pipe delimiter
        if isinstance(strings, basestring):
            stripped = strings.strip()
            return stripped.split('|')
        else:
            array = []
            for string in strings:
                stripped = string.strip()
                array.append(stripped.split('|'))

            return array
