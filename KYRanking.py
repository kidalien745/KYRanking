import sys, getopt 
import itertools 
import json 
from csv import reader 

strUsage = """\ 
Usage: KYRanking.py -i <input.json> -o <outfile> 
""" 

class Rankings:
	def __init__(self, candidates):
		self.candidates = candidates
		self.ballots = {}
		for i in candidates:
			self.ballots[i] = []

	def add(self, candidate, ranking):
		self.ballots[candidate].append(ranking)

	def get_num_ballots(self):
		length = []
		for key, value in self.ballots.items():
			if len(value) not in length:
				length.append(len(value))
		if len(length) != 1:
			print "Ballot numbering error"
			sys.exit(2)
		else:
			return length[0] 

class PrefChart:
	def __init__(self, candidates):
		self.matchups = {}
		for matchup in itertools.combinations(candidates, 2):
			self.matchups[matchup] = []

	def populate(self, rankings):
		for i in range(rankings.get_num_ballots()):
			for matchup in self.matchups.keys():
				candA = rankings.ballots[matchup[0]][i]
				candB = rankings.ballots[matchup[1]][i]
				if candA < candB:
					self.matchups[matchup].append(1)
				elif candA == candB:
					self.matchups[matchup].append(0)
				else:
					self.matchups[matchup].append(-1)

	def calculate(self, candidates, fileOut):
		top = []
		for item in itertools.permutations(candidates, len(candidates)):
			score = 0
			for matchup in itertools.combinations(item, 2):
				if matchup in self.matchups:
					score += self.matchups[matchup].count(1)
				else:
					matchup = matchup[::-1]
					score += self.matchups[matchup].count(-1)
			top.append((score, item))
		top.sort(reverse=True)
		f_out = open(fileOut, 'w')
		for item in top:
			f_out.write(str(item)+'\n') 

def getArgs(argv):
	try:
		opts, args = getopt.getopt(argv, "hi:o:")
	except:
		print strUsage
		sys.exit(2)
	inOut = {}
	for opt, arg in opts:
		if opt == '-h':
			print strUsage
			sys.exit()
		elif opt == '-i':
			inOut['input'] = arg
		elif opt == '-o':
			inOut['output'] = arg
	if len(inOut) != 2:
		print strUsage
		sys.exit(2)
	return inOut['input'], inOut['output'] 

def main(argv):
	inFile, outFile = getArgs(argv)
	f_in = open(inFile, 'r')

	decoded = []
	decoder = json.JSONDecoder()
	for line in f_in:
		decoded.append(decoder.raw_decode(line)[0]['ballot'])

	candidates = [i for i in itertools.chain.from_iterable([candidate.split(' / ') for candidate in decoded[0]])]
	rankings = Rankings(candidates)
	for ballot in decoded:
		for idx, value in enumerate(ballot):
			names = value.split(' / ')
			[rankings.add(candidate, idx) for candidate in names]

	prefs = PrefChart(rankings.candidates)
	prefs.populate(rankings)
	prefs.calculate(rankings.candidates, outFile) 

if __name__ == "__main__":
	main(sys.argv[1:])
