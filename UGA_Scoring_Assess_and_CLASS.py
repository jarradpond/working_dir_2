# Author: Jarrad Pond
# Email: jarradpond@gmail.com
# Version: 1
# Date: 01/19/17
# File: UGA_Scoring_Assess_and_CLASS.R
# Use: Read in the file formatted by
# "UGA_assess_data_formatting.R" and score the assessment
# and CLASS data held within.
# This scirpt will return the original data with the scored
# data stored in subsequent columns



# Read in the needed libraries.
import numpy as np
import csv


#######
# FUNCTIONS
########
# This function will read in the gathered data and score each entries assessment
def assessment_score(data,assess="FCI"):
	# Define the three assessment keys
	# FCI
	FCI_key = np.array(['C', 'A', 'C', 'E', 'B', 'B', 'B', 'B', 'E', 'A', 'D', 'B', 'D',
        'D', 'A', 'A', 'B', 'B', 'E', 'D', 'E', 'B', 'B', 'A', 'C', 'E',
        'C', 'E', 'B', 'C'], dtype='|S1')

	#CSEM
	CSEM_key = np.array(['B', 'A', 'B', 'B', 'C', 'E', 'B', 'B', 'B', 'C', 'E', 'D', 'E',
        'D', 'A', 'E', 'E', 'D', 'A', 'D', 'E', 'D', 'A', 'C', 'D', 'A',
        'E', 'C', 'C', 'A', 'E', 'D'], dtype='|S1')

	# SEMCO
	SEMCO_key = np.array(['B','A','C','B','B','E','A','E','D','A','A','C','A','D','D','D','ANY','E',
        'A','D','B','E','D','D','C','D','ANY','B','C','A','C','D','C','A','E','A','E','ANY'], dtype='|S3')

	# Add a column for assessment scores.
	blanks = ['']*np.shape(data)[0]*1
	data = np.append(data,np.array(blanks,dtype='a25').reshape(np.shape(data)[0],1),axis=1)

	# Pull out the Student IDs in the data, used for looping.
	IDs = data[:,2]

	for i in range(len(IDs)):
		# Determing the course type and semester and then pick the appropriate assessment key
		if (assess=="FCI"):
			key = FCI_key
			score = np.sum(data[i,1+2:31+2]==key)
			data[i,-1] = str(score)

		elif (assess=="CSEM"):
			key = CSEM_key
			score = np.sum(data[i,1+2:31+2+2]==key)
			data[i,-1] = str(score)
		else:
			key = SEMCO_key
			score = np.sum(data[i,:][1+2:31+8+2][SEMCO_key != 'ANY'] == SEMCO_key[SEMCO_key != 'ANY'])
			data[i,-1] = str(score)

	return data

# Use this fucntion to score the CLASS data.
def CLASS_score(data,assess="FCI"):
	# First, we need to define the CLASS key, which will actually need to be a set of tuples.
	# Each column in the key set will be for a CLASS question. 
	# The first row will tell if:
	# I. A response of A or B should be rewarded as favorable (-1)
	# II. A response of D or E should be rewarded as favorable (+1)
	# III. This question is not counted (0).
	# The second row gives a tuple that tells the script where to add a Favorable or Unfavorable point to.
	# They are given relative to the unfavorable column (sorry, this is just how I wrote it out first...)
	#                   1            2     3      4     5                6            7     8         9     10     11          12     13          14       15          16          17     18    19    20     21              22           23        24        25            26       27     28         29     30         31    32           33   34             35       36        37      38     39        40                41    42
	CLASS_key_set = np.array([[(-1,),       (1,), (1,),  (0,), (-1,),           (-1,),       (0,), (-1,),    (0,), (-1,), (1,),       (-1,), (-1,),      (1,),    (1,),       (1,),       (-1,), (-1,), (1,), (-1,), (-1,),          (-1,),        (-1,),    (1,),     (1,),         (1,),    (-1,), (1,),      (-1,), (1,),      (2,), (-1,),        (0,), (1,),           (-1,),    (1,),     (1,),     (1,), (1,),     (-1,),             (0,),  (1,)],
		          [(1,3,17,19), (1,), (1,3,5), (0,), (1,3,13,17,19),  (1,3,17,19), (0,), (1,3,19), (0,), (1,),  (1,3,5,15), (1,),  (1,3,9,17), (1,3,5), (1,3,9,11), (1,3,9,11), (1,),  (1,), (1,), (1,), (1,3,13,17,19), (1,3,13,19), (1,3,15), (1,3,15), (1,3,5,9,13), (1,3,9), (1,),  (1,3,5,7), (1,),  (1,3,5,7), (0,), (1,3,15,17), (0,), (1,3,9,11,13), (1,3,7), (1,3,15), (1,3,7), (1,), (1,3,15), (1,3,9,11,13,19), (0,), (1,3,9,15)]])

	# Make an array for the criteria for answering a certain number of questions in each category
	CLASS_Criteria = np.array([32,32,23,23,4,4,3,3,6,6,3,3,4,4,5,5,4,4,5,5])
	
	# Add a column for CLASS the scores.
	blanks = ['']*np.shape(data)[0]*21
	data = np.append(data,np.array(blanks,dtype='a25').reshape(np.shape(data)[0],21),axis=1)

	# Pull out the Student IDs in the data, used for looping.
	IDs = data[:,0]

	# Loop through the students.
	for i in range(len(IDs)):
		# Now, grab the CLASS_response from this student
		if (assess=="CSEM"):
			CLASS_Response = data[i,35:35+42]
		if (assess=="FCI"):
			CLASS_Response = data[i,33:33+42]
		# make a temp array for the scored data
		CLASS_data = np.zeros(20,dtype=int)
		CLASS_data_total = np.zeros(20)
		# Set the attention check flag equal to 0
		Att_flag = '0'
		# Now, loop through the responses and figure out how to score them
		for j in range(len(CLASS_Response)):
			# Check the key set:
			# If an 'A' or 'B' should be rewarded a point to the appropriate places.
			#print CLASS_key_set[0,j]
			if CLASS_key_set[0,j][0] == -1:
				if (CLASS_Response[j] == 'A' or CLASS_Response[j] == 'B'):
					for k in CLASS_key_set[1,j]:
						CLASS_data[k-1] += 1
						CLASS_data_total[k+0] += 1
						CLASS_data_total[k-1] += 1
				elif (CLASS_Response[j] == 'D' or CLASS_Response[j] == 'E'):
					for k in CLASS_key_set[1,j]:
						CLASS_data[k+0] += 1
						CLASS_data_total[k+0] += 1
						CLASS_data_total[k-1] += 1
				elif (CLASS_Response[j] == 'C'):
					for k in CLASS_key_set[1,j]:
						CLASS_data_total[k+0] += 1
						CLASS_data_total[k-1] += 1
				else:
					dummy = 1
					#print 'No response'#Nothing

			if CLASS_key_set[0,j][0] == 1:
				if (CLASS_Response[j] == 'D' or CLASS_Response[j] == 'E'):
					for k in CLASS_key_set[1,j]:
						CLASS_data[k-1] += 1
						CLASS_data_total[k+0] += 1
						CLASS_data_total[k-1] += 1
				elif (CLASS_Response[j] == 'A' or CLASS_Response[j] == 'B'):
					for k in CLASS_key_set[1,j]:
						CLASS_data[k+0] += 1
						CLASS_data_total[k+0] += 1
						CLASS_data_total[k-1] += 1
				elif (CLASS_Response[j] == 'C'):
					for k in CLASS_key_set[1,j]:
						CLASS_data_total[k+0] += 1
						CLASS_data_total[k-1] += 1
				else:
					dummy = 1 
					#print 'No response'#Nothing
			
			# CHeck the check question and flag if they don't pick strongly agree, 'E'
			if CLASS_key_set[0,j][0] == 2:
				if (CLASS_Response[j] == 'D'):
					Att_flag = '1'

		#Now divide the class data and the class data totals and * 100 to get the percentages.
		CLASS_data = CLASS_data/CLASS_data_total
		# Make this a string
		CLASS_data = np.array(CLASS_data,dtype='a25')

		# Look through class data to make sure that the minimum number of students answering the questions have been reached.
		# If not, make it an NA
		for l in range(len(CLASS_data)):
			if (CLASS_data_total[l] < CLASS_Criteria[l]):
				CLASS_data[l] = 'NA'
				

		#Now, put this student's scores in the data array
		data[i,-21:-1] = np.array(CLASS_data,dtype='a25')
		data[i,-1] = Att_flag
				

	return (data,CLASS_data_total,CLASS_key_set)


#### START OF MAIN CODE ####
#### Function Dependancies Defined Above #####

# Give the name and file path fo the formatted data
csv_dir = "./"
fname = "Fall_2016_UGA_Assess_All_Raw_no_ID_PHSY1_Pre_formatted.csv"
save_name = "Fall_2016_UGA_Assess_All_Raw_no_ID_PHSY1_Pre_formatted_scored.csv"

# Which assessent is this for?
assess0 = "FCI"

# Read in the data, removing the header row (python won't like it)
data = np.genfromtxt(csv_dir+fname,delimiter=",",dtype='a25',skip_header=True)

# Line of code no longer needed. 
#data = data[:,0:77]

# Score the assessment (FCI, CSEM, or SEMCO scoring first)
# Indicate, as a string, which assessment you are scoring.
data = assessment_score(data,assess=assess0)

# !!!!!!!! Run the CLASS scoring function second !!!!!!!
data,CLASS_data_total,CLASS_key_set = CLASS_score(data,assess=assess0)

# Keep a runnning column header to add before the final file is written
if (assess0=="FCI"):
	file_header = np.array(['LastName','FirstName','SID',
	                              'Q01','Q02','Q03','Q04','Q05','Q06','Q07','Q08','Q09','Q10','Q11','Q12','Q13','Q14','Q15',
	                              'Q16','Q17','Q18','Q19','Q20','Q21','Q22','Q23','Q24','Q25','Q26','Q27','Q28','Q29','Q30',
	#                              'Q31','Q32',
	                              'CQ01','CQ02','CQ03','CQ04','CQ05','CQ06','CQ07','CQ08','CQ09','CQ10','CQ11','CQ12','CQ13','CQ14','CQ15',
	                              'CQ16','CQ17','CQ18','CQ19','CQ20','CQ21','CQ22','CQ23','CQ24','CQ25','CQ26','CQ27','CQ28','CQ29','CQ30',
	                              'CQ31','CQ32','CQ33','CQ34','CQ35','CQ36','CQ37','CQ38','CQ39','CQ40','CQ41','CQ42',
	                              'Assess',
	                              'Overall_Fav','Overall_UnFav','All_Cats_Fav','All_Cats_UnFav','PI_Fav','PI_UnFav','WC_Fav','WC_UnFav',
	                              'PS_Gen_Fav','PS_Gen_UnFav','PS_Con_Fav','PS_Can_UnFav','PS_Soph_Fav','PS_Soph_UnFav',
	                              'SME_Fav','SME_UnFav','Con_Und_Fav','Con_Und_UnFav','App_Con_Und_Fav','App_Con_Und_UnFav','CLASS_Check'],dtype='a25')

# Keep a runnning column header to add before the final file is written
if (assess0=="CSEM"):
	file_header = np.array(['LastName','FirstName','SID',
	                              'Q01','Q02','Q03','Q04','Q05','Q06','Q07','Q08','Q09','Q10','Q11','Q12','Q13','Q14','Q15',
	                              'Q16','Q17','Q18','Q19','Q20','Q21','Q22','Q23','Q24','Q25','Q26','Q27','Q28','Q29','Q30',
	                              'Q31','Q32',
	                              'CQ01','CQ02','CQ03','CQ04','CQ05','CQ06','CQ07','CQ08','CQ09','CQ10','CQ11','CQ12','CQ13','CQ14','CQ15',
	                              'CQ16','CQ17','CQ18','CQ19','CQ20','CQ21','CQ22','CQ23','CQ24','CQ25','CQ26','CQ27','CQ28','CQ29','CQ30',
	                              'CQ31','CQ32','CQ33','CQ34','CQ35','CQ36','CQ37','CQ38','CQ39','CQ40','CQ41','CQ42',
	                              'Assess',
	                              'Overall_Fav','Overall_UnFav','All_Cats_Fav','All_Cats_UnFav','PI_Fav','PI_UnFav','WC_Fav','WC_UnFav',
	                              'PS_Gen_Fav','PS_Gen_UnFav','PS_Con_Fav','PS_Can_UnFav','PS_Soph_Fav','PS_Soph_UnFav',
	                              'SME_Fav','SME_UnFav','Con_Und_Fav','Con_Und_UnFav','App_Con_Und_Fav','App_Con_Und_UnFav','CLASS_Check'],dtype='a25')


# Give the data the above header
data = np.append(file_header.reshape(1, np.shape(file_header)[0]),data,axis=0)

# Write out the scored file to a .csv.
resultFile = open(csv_dir+save_name,'wb')
wr = csv.writer(resultFile, dialect='excel')
wr.writerows(data[0:np.shape(data)[0]/2,:])
wr.writerows(data[np.shape(data)[0]/2:,:])

