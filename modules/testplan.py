import re


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
