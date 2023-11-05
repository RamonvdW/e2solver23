

lines1 = open('pieces1.txt').readlines()
lines2 = open('pieces2.txt').readlines()


class Compare(object):

    def __init__(self):
        self.set1 = dict()      # [nr] = "ABCD"
        self.set2 = dict()      # [nr] = ["c1", "c2", "c3", "c4"]

        self.convert = {
            'k': 'X',
            'ok': 'A',
            'rk': 'Q',
            'gk': 'E',
            'bk': 'I',
            'gs': 'B',
            'bl': 'J',
            'p+': 'F',
            'brk': 'M',
            'ol': 'K',
            'rt': 'G',
            'gv': 'O',
            'os': 'H',
            'gt': 'U',
            'b*': 'R',
            'p*': 'T',
            'g*': 'S',
            'rs': 'N',
            'rl': 'D',
            'bt': 'L',
            'bv': 'P',
            'b+': 'V',
            'br+': 'C',
        }

    def read_set_1(self, fname):
        """ every line defines 1 piece
            line number = piece number
            format: "AQXX"
            letters A..V=side, X=border
            order: clockwise, starting at the top
        """
        lines = open(fname).readlines()
        for nr, line in enumerate(lines, start=1):
            piece = line[1:1+4]
            self.set1[nr] = piece

    def read_set_2(self, fname):
        """ every line defines 1 piece
            line number = piece number
            format: four <code> separate by spaces
                    <code> is 1, 2 or 3 letters long
        """
        lines = open(fname).readlines()
        for nr, line in enumerate(lines, start=1):
            spl = line.split()
            self.set2[nr] = spl

            converted = ""
            for code in spl:
                converted += self.convert[code]
            # for
            if '?' in converted:
                print(nr, converted)
            elif converted != self.set1[nr]:
                print('FOUT! %s: %s != %s' % (nr, converted, self.set1[nr]))

    def check(self):
        pass


compare = Compare()
compare.read_set_1('pieces1.txt')
compare.read_set_2('pieces2.txt')
compare.check()
