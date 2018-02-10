#!/usr/bin/env python

''' 
	Version 2.0
	HaNS1443
	Updated for Rabobank new csv format from Q1 2018

    Copyright (C) 2010 Erik Schepers (emschepers@home.nl)


    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import csv
import sys
import datetime
import optparse

class Transaction(object):
    '''A single transaction.'''
    def __init__(self, account, valuta, bic, volgnr, date0, interest_date, amount, saldo_na_trn, payee, descr0, naam_uiteindelijke_partij, naam_initierende_partij, bic_tegenpartij, code0,
                 Batch_ID, Transactiereferentie, Machtigingskenmerk, Incassant_ID, Betalingskenmerk, descr1, descr2, descr3, Reden_retour, Oorspr_bedrag, Oorspr_munt, Koers):
        '''Initialize the transaction using all the data provided by the rabobank csv row.'''
        # The account-number
        self.account = account
        # The valuta (e.g. "EUR"). Not used
        self.valuta = valuta
        # Bic
        self.bic = bic
        # Volgnr
        self.volgnr = volgnr
        # Date. Not used.
        self.date0 = date0
        # The interest-date
        self.interest_date = datetime.date(int(interest_date[0:4]), int(interest_date[5:7]), int(interest_date[8:10]))
        # The amount of the transaction, negated depending on the value of the debit/credit column
        self.amount = float(amount.replace(',', '.'))
        # Not used.
        self.saldo_na_trn = saldo_na_trn
        # The account number of the payee (if available)
        self.payee = payee
        # Concatenate all description fields, separated by spaces.
        self.description = " ".join([descr0, descr1, descr2, descr3])
        
    
    def __repr__(self):
        return "[%d-%d-%d] %5.2f '%s'" % (self.interest_date.day, self.interest_date.month, self.interest_date.year, self.amount, self.description)
        
    def to_qif(self):
        '''Return string-representation of this Transaction in QIF format. By prefixing
        a transaction always with an !Account section, a single QIF file can contain
        transactions for multiple accounts.'''
        s =  ["!Account"]
        s += ["N" + self.account]
        s += ["TBank"]
        s += ["^"]
        s += ["!Type:Bank"]
        s += ["D%d/%d/%d" % (self.interest_date.year, self.interest_date.month, self.interest_date.day)]
        s += ["T%.2f" % self.amount]
        s += ["NTransfer"]
        s += ["P" + self.description]
        s += ["^"]
        return "\n".join(s)
    

def read_rabo_csv(filename):
    '''Returns a list of transactions read from given rabobank csv file'''
    csvreader = csv.reader(open(filename), delimiter=',', quotechar='"')
    next(csvreader, None)
    transactions = []
    for row in csvreader:
        try:
            transactions += [Transaction(*row)]
        except:
            print("Failed to parse (this is normal for the last line in the file):", row)
    return transactions
    

def convert_rabo_to_qif(rabocsv):
    '''Convert given rabobank-csv file to a qif-file.'''
    transactions = read_rabo_csv(rabocsv)
    outfile = rabocsv + ".qif"
    fd = open(outfile, 'w')
    for t in transactions:
        fd.write(t.to_qif() + "\n")
    fd.close()
    print("Saved transactions to", outfile)
    

def parse_arguments():
    usage = """usage: %prog rabo-csv-file(s)

The csv-files are converted to qif files. For each csv-file, a new QIF file
with the same name, and added extension .qif is created."""
    parser = optparse.OptionParser(usage)
    return parser.parse_args(sys.argv[1:])
    

    
if __name__ == "__main__":
    options, args = parse_arguments()
    for csvfile in args:
        convert_rabo_to_qif(csvfile)
