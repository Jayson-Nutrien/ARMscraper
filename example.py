from scraper import frame


data = frame("15421SO (1).xlsx")


#returns all the tables as a pandas dataframe
print(data.measures) #measures table containing what was measured along with what units. 
print(data.applications) #applications table. Contains what products were applied for the study and on what days
print(data.values) #contains the results for each individual plot 
print(data.trial) #contains trial id, protocl, and file name. (For database only)

#returns metadata as a dict 
print(data.metadata["Planting Date"])


