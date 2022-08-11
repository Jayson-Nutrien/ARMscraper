import os 
import pandas
import json
from sre_compile import isstring
import numpy as np


class frame:
    def __init__(self, file):
        self.file = file
        # self.__cropCodes = self.__getcrop_codes()
        # self.__cropDict = self.__getcrop_dict()
        self.df = pandas.read_excel(io = file, sheet_name = 0, header = None, engine = 'openpyxl', index_col=0)
        self.df2 = pandas.read_excel(io = file, sheet_name = 1, header = None, engine = 'openpyxl', index_col=0)
        self.metadata = self.__get_metadata()
        self.values = self.__get_values()
        self.measures = self.__get_measures()
        self.trial = self.__get_trial()
        self.applications = self.__get_applications()
        

    def save_metadata(self, filepath):
        #saves metadata as a .json
        dir = filepath.replace('.xlsx', '.json')
        with open(dir, 'w') as json_file:
            json.dump(self.metadata, json_file, indent=2)



    def __get_metadata(self):
        #gets metadata and formats it into a dict

        if "Latitude of LL Corner °:" in self.df2.index:
            latitude = self.df2.loc["Latitude of LL Corner °:"][1]
        else:
            latitude = None

        if "Longitude of LL Corner °:" in self.df2.index:
            longitude = self.df2.loc["Latitude of LL Corner °:"][1]
        else:
            longitude = None

        if "Altitude of LL Corner:" in self.df2.index: 
            altitude = self.df2.loc["Altitude of LL Corner:"][1]
        else: 
            altitude = None

        if "% Sand:" in self.df2.index:
            soilType = self.df2.loc["% Sand:"][7]
        else:
            soilType = None

        if "Description" in self.df.index:
            description = self.df.index[2]
        else:
            description = self.df.index[2]
        
        if "State/Prov.:" in self.df2.index:
            state = self.df2.loc["State/Prov.:"][1]
        else: 
            state = None
        
        if "Postal Code:" in self.df2.index: 
            postcode = self.df2.loc["Postal Code:"].head(1)[1]
            try:
                postcode = str(postcode[0])
            except:
                postcode = str(postcode)
        else:
            postcode = None

        if "City:" in self.df2.index:
            city = self.df2.loc["City:"].head(1)
            city = city.values.flatten()[0]
        else: 
            city = None

        if "Organization:" in self.df2.index:
            organization = self.df2.loc["Organization:"][1][0].replace("/", ' ')
        else: 
            organization = None

        if "Project ID" in self.df.index:
            project_id = self.df.loc["Project ID:"][1]
            studydirector = self.df.loc["Project ID:"][3]
        else:
            project_id = None
            studydirector = None
        if "Protocol ID:" in self.df.index:
            protocolId = self.df.loc["Protocol ID:"][1]
            investigator = self.df.loc["Protocol ID:"][3]
        else: 
            protocolId = None
            investigator = None

        if "Cooperator:" in self.df2.index:
            cooperator = self.df2.loc["Cooperator:"][1]
        else: 
            cooperator = None

        if "Sponsor:" in self.df2.index:
            sponsor = self.df2.loc["Sponsor:"][1]
        else: 
            sponsor = None

        if "Address (Location):" in self.df2.index: 
            address = self.df2.loc["Address (Location):"].head(1)[1]
            try:
                address = address[0]
            except:
                address = address
        elif "Address:" in self.df2.index: 
            address = self.df2.loc["Address:"].head(1)[1]
            try:
                address = address[0]
            except:
                address = address
        else: 
            address = None

        if "Trial ID:" in self.df.index:
            trialId = self.df.loc["Trial ID:"][1]
            location = self.df.loc["Trial ID:"][3]
            trialyear = self.df.loc["Trial ID:"][6]
        else: 
            trialId = None
            location = None
            trialyear = None
        
        if "Planting Date:" in self.df2.index: 
            plantdate = self.df2.loc["Planting Date:"][3]
            try:
                plantdate = plantdate.head(1)[0]
            except:
                plantdate = plantdate
        else:
            plantdate = None

        if "Harvest Date:" in self.df2.index: 
            harvestdate = self.df2.loc["Harvest Date:"][3]
            try:
                harvestdate = harvestdate.head(1)[0]
            except:
                harvestdate = harvestdate
        else: harvestdate = None

        if "Treated Plot Area:" in self.df2.index:
            tillage = self.df2.loc["Treated Plot Area:"][9]
        else: 
            tillage = None

        if "Replications:" in self.df2.index:
            replications = self.df2.loc["Replications:"][1]
        else: 
            replications = None

        crop_name = self.__get_crops()[0]
        if not isinstance(crop_name, str):
            crop_name = "None"


        metadataDict = {
            'Organization':organization,
            'Description':description,
            'Trial ID':trialId,
            'Location':location,
            'Address':address,
            'City':city, 
            'State':state,
            'Zipcode':postcode,
            # 'Trial Year':trialyear,
            'Year':trialyear,
            'lat1':latitude,  
            'long1':longitude, 
            'alt':altitude,
            # 'Protocol ID':protocolId, 
            'Protocol':protocolId,
            'Investigator':investigator,
            'Cooperator': cooperator,
            'Project ID':project_id,
            'Sponsor':sponsor,
            'Study Director':studydirector, #
            'Tillage':tillage, #
            'Soil Type':soilType, 
            'Planting Date':plantdate,
            'Harvest Date':harvestdate,
            'Num Replications':replications,
            'Trial Samples':self.__get_trialcount(), # crop
            # 'Crop':self.__get_crop(),
            # 'Crop':self.__get_crops()[1],
            # 'Crops':self.__get_crops()[1],
            # 'Crops':self.__get_crop(),
            'crop_name':crop_name, #
            'Num Measures':len(self.__get_meta_measures()), #
            'Num Treatments':self.__get_trialcount() #
            
        }

        return metadataDict


    def __get_applications(self):
        
        repNum = self.metadata["Num Replications"]
        trialNum = self.metadata["Trial Samples"]
        measureNum = self.metadata["Num Measures"]

        #gets a boolean array of index with "Mean ="
        treatmentsloc = self.df.index.get_loc("Mean =")
        posList = []
        #converts the boolean list to an integer position list
        for i in range(len(treatmentsloc)):
            if treatmentsloc[i] == True:
                posList.append(i)

        dfList = []
        #gets a list of dataframes for each measurment section 
        for i in range(trialNum):
            pos = self.df.index.get_loc(i+1)
            pos2 = posList[i]
            plot_ids = self.df.iloc[pos:pos2]
            temp = plot_ids.iloc[:, 0:4].copy()
            #if the treatment is blank, replace with "Untreated Check"
            if pandas.isnull(temp.iloc[0][1]):
                temp.at[1,1] = "Untreated Check"
            temp = temp.dropna(axis=0, how="all") #removes nan values 
            if pandas.isnull(temp.index[0]):
                temp.index = [i+1] * len(temp.index)
            else:
                temp.index = [temp.index[0]] * len(temp.index) #sets the index to the treatment id
            dfList.append(temp)
        #adds the dataframes into one large frame and sets the plot id as the index
        tdf = pandas.concat(dfList)

        #Splits the treatment codes up into lists
        treatcodes = tdf[4].values
        for i in range(len(treatcodes)):
            if isstring(treatcodes[i]):
                treatcodes[i] = list(treatcodes[i])
        tdf[4] = treatcodes

        tdf = tdf.explode(4)

        if "Application Description" in self.df2.index:

            #creates a dataframe to get attributes from the treatment code
            treatIndex = self.df2.index.get_loc("Application Description") + 1
            treatIds = self.df2.iloc[treatIndex]
            treatIds = treatIds.dropna().values
            
            treatId_df = self.df2.iloc[treatIndex+1:treatIndex+8]
 #checks to see if the columns already match to prevent entries that were left blank
            treatId_df = treatId_df.iloc[:,:len(treatIds)]
            treatId_df.columns = treatIds
            dateList = []
            methodList = []
            placementList = []
            timingList = []
            stageList = []
            #gets the data from the code using the new dataframe
            for i in range(len(tdf.index)):
                code = tdf[4].values[i]
                if not pandas.isnull(code) and code in treatId_df.columns:
                    if "Application Date" in treatId_df.index: 
                        dateList.append(treatId_df.loc["Application Date"][code])
                    elif "Application Date:" in treatId_df.index:
                        dateList.append(treatId_df.loc["Application Date:"][code])
                    else: 
                        dateList.append(np.NaN)
                    if "Application Method" in treatId_df.index:
                        methodList.append(treatId_df.loc["Application Method"][code])
                    elif "Application Method:" in treatId_df.index:
                        methodList.append(treatId_df.loc["Application Method:"][code])
                    else:
                        methodList.append(np.NaN)
                    if "Application Placement" in treatId_df.index: 
                        placementList.append(treatId_df.loc["Application Placement"][code])
                    elif "Application Placement:" in treatId_df.index: 
                        placementList.append(treatId_df.loc["Application Placement:"][code])
                    else: 
                        placementList.append(np.NaN)
                    if "Application Timing" in treatId_df.index:
                        timingList.append(treatId_df.loc["Application Timing"][code])
                    elif "Application Timing:" in treatId_df.index:
                        timingList.append(treatId_df.loc["Application Timing:"][code])
                    else:
                        timingList.append(np.NaN)
                    if "Growth Stage" in treatId_df.index:
                        stageList.append(treatId_df.loc["Growth Stage"][code])
                    elif "Crop Stage At Each Application" in treatId_df.index:
                        stageList.append(treatId_df.loc["Crop Stage At Each Application"][code])
                    else:
                        stageList.append(np.NaN)
                else: 
                    dateList.append(np.NaN)
                    methodList.append(np.NaN)
                    placementList.append(np.NaN)
                    timingList.append(np.NaN)
                    stageList.append(np.NaN)
            tdf.columns = ["Product", "rate", "rate_unit", "app_code"]
            tdf.insert(4, "app_date",dateList)
            tdf.insert(5, "app_method", methodList)
            tdf.insert(6, "app_placement", placementList)
            tdf.insert(7, "app_timing", timingList)
            tdf.insert(3, "growth_stage", stageList)
            tdf.insert(0, "trial_id", np.NaN)
            tdf.index.name = "treatment_id"
        #if nothing is in the code index, fill the dataframe with blank values
        else:
            tdf.insert(4, "app_date", np.NaN)
            tdf.insert(5, "app_method", np.NaN)
            tdf.insert(6, "app_placement", np.NaN)
            tdf.insert(7, "app_timing", np.NaN)
            tdf.insert(3, "growth_stage", np.NaN)
            tdf.insert(0, "trail_id", np.NaN)
            tdf.index.name = "treatment_id"

        return tdf

    def __getcrop_dict(self):
         # prints parent directory

        try:          
            path = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + "/lpi-arm-field-trials-manager/static/arm_crop_codes.json"
            with open(path, "r") as file:
                data = json.load(file)
        except:
            path = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + "/static/arm_crop_codes.json"
            with open(path, "r") as file:
                data = json.load(file)

        
        return data

    def __getcrop_codes(self):
        
        data = self.__getcrop_dict()

        codes = []
        for i in range(len(data)):
            codes.append(data[i]["code"])
        return codes

    def __get_crop(self):
        cropIdList = []
        if "Crop Type, Code" in self.df.index:
            for i in self.df.loc["Crop Type, Code"][:1].values.flatten().tolist():
                if isstring(i):
                    cropIdList.append(i)
        elif "Crop ID Code" in self.df.index:
            for i in self.df.loc["Crop ID Code"].values.flatten().tolist():
                if isstring(i):
                    cropIdList.append(i)
        elif "Crop Code" in self.df.index:
            for i in self.df.loc["Crop Code"][:1].values.flatten().tolist():
                if isstring(i):
                    cropIdList.append(i)
        else: 
            crop = None
            return crop
        #takes the most common crop in the list as the main crop id
        crop = max(set(cropIdList), key=cropIdList.count)

        idDict = self.__cropCodes
        #if the list contains a seaqence from the IDS
        for i in idDict:
            if i in crop:
                crop = i
        return crop 

    def __get_crops(self):

        cropNameList = []
        cropIdList = []
        cleanIdList = []
        #makes a list of the different crops names in the trail
        if "Crop Name" in self.df.index: 
            for i in self.df.loc["Crop Name"]:
                if i not in cropNameList and isstring(i):
                    cropNameList.append(i)
        else: 
            cropNameList = pandas.DataFrame([np.NaN] * self.df.loc["No."][5:]).values

        if len(cropNameList) == 1:
            cropNameList = cropNameList[0]
        #returns a list if more then one crop in trail

        #makes a list of the different crop ids
        if "Crop Type, Code" in self.df.index:
            for i in self.df.loc["Crop Type, Code"][:1].values.flatten().tolist():
                if i not in cropIdList and isstring(i):
                    cropIdList.append(i)
        elif "Crop ID Code" in self.df.index:
            for i in self.df.loc["Crop ID Code"].values.flatten().tolist():
                if i not in cropIdList and isstring(i):
                    cropIdList.append(i)
        elif "Crop Code" in self.df.index:
            for i in self.df.loc["Crop Code"].values.flatten().tolist():
                if i not in cropIdList and isstring(i):
                    cropIdList.append(i)
        else:
            cropIdList = pandas.DataFrame([np.NaN] * self.df.loc["No."][5:]).values
        if len(cropIdList) > 1:
            for i in cropIdList:
                if "," in i:
                    cleanIdList.append(i.split(",")[1].replace(" ",""))
        else:
            cleanIdList = cropIdList[0]
        
        return cropNameList, cleanIdList

    def __get_meta_measures(self):
        #adds all atributes to the list if they are not a string 
        attributeList = []
        if "Description" in self.df.index:   
            for i in self.df.loc["Description"]:
                if isstring(i):
                    attributeList.append(i)
        elif "Rating Type" in self.df.index: 
            for i in self.df.loc["Rating Type"]:
                if isstring(i):
                    attributeList.append(i)
        return attributeList

    def __get_measures(self):

        size = len(self.df.loc["No."][5:])

        
        if "Rating Type" in self.df.index: 
            if self.df.index.values.tolist().count("Rating Type") > 1:
                type = self.df.loc["Rating Type"].head(1)
                type = type.iloc[:, 5:]
                type = type.transpose()
            else:
                type = self.df.loc["Rating Type"]
                type = type.loc[6:]
                type = type.transpose()
        else: 
            type = pandas.DataFrame([np.NaN] * size)
        if "Part Rated" in self.df.index:
            part = self.df.loc["Part Rated"].head(1)
            part = part.iloc[:, 5:]
            part = part.transpose()
        else:    
            part = pandas.DataFrame([np.NaN] * size)
        #if part contains , split the values and get first
        if isstring(part.values[0][0]) and "," in part.values[0][0]:
            tmp = []
            for i in range(len(part.values)):
                if not pandas.isnull(part.values[i][0]):
                    tmp.append(part.values[i][0].split(",")[0])
                else: 
                    tmp.append(np.NaN)
            part = pandas.DataFrame(tmp)
        if "Rating Unit" in self.df.index:
            if self.df.index.values.tolist().count("Rating Unit") > 1:
                unit = self.df.loc["Rating Unit"].head(1)
                unit = unit.loc[:,6:]
                unit = unit.transpose()
            else: 
                unit = self.df.loc["Rating Unit"]
                unit = unit.loc[6:]
                unit = unit.transpose()
        elif "Rating Unit/Min/Max" in self.df.index:
            unit = self.df.loc["Rating Unit/Min/Max"].head(1)
            unit = unit.loc[:,6:]
            unit = unit.transpose()
            tmp = []
            #splits the units by , and takes the first value
            for i in range(len(unit.values)):
                if not pandas.isnull(unit.values[i][0]):
                    tmp.append(unit.values[i][0].split(',')[0])
                else:
                    tmp.append(np.NaN)
            unit = pandas.DataFrame(tmp)
        else: 
            #creates an empty df of NaN if "Units" is not found
            unit = pandas.DataFrame([np.NaN] * size) 

        if "Rating Date" in self.df.index:
            date = self.df.loc["Rating Date"]
            date = date.iloc[5:]
        elif "Data Entry Date" in self.df.index: #If no rating date exists, get the entry date 
            date = self.df.loc["Data Entry Date"]
            date = date.iloc[5:]
        else: 
            date = pandas.DataFrame([np.NaN] * size) 
        if "Crop Type, Code" in self.df.index: 
            name = self.df.loc["Crop Type, Code"]
            if len(name.index) > 1:
                name = name[:1]
            name = name.squeeze()
            name = name[5:]
            tmp = []
            #indexes the code to get the name
            for i in name:
                count = 0
                if isstring(i):
                    tmp.append(i)
            name = pandas.Series(tmp)
        elif "Crop ID Code" in self.df.index: 
            name = self.df.loc["Crop ID Code"]
            if len(name.index) > 1 and len(name.index) <3:
                name = name[:1]
            name = name.squeeze()
            name = name[5:].values
            tmp = []
            #indexes the code to get the name
            for i in name:
                count = 0
                if isstring(i):
                    tmp.append(i)
            name = pandas.Series(tmp)
        elif "Crop Code" in self.df.index: 
            name = self.df.loc["Crop Code"][:1]
            name = name.squeeze()
            name = name[5:].values
            tmp = []
            #indexes the code to get the name
            for i in name:
                count = 0
                if isstring(i):
                    tmp.append(i)
            name = pandas.Series(tmp)
        else: 
            name = pandas.DataFrame([np.NaN] * size)
        if "Pest Name" in self.df.index: 
            pest = self.df.loc["Pest Name"]
            pest = pest.iloc[5:]
        else: 
            pest = pandas.DataFrame([np.NaN] * size)
        measureID = self.df.loc["No."]
        measureID = measureID.iloc[5:]
        
        df = pandas.DataFrame(type)
        df.insert(0, "Trial ID", np.NaN)
        df.insert(1, "Measure ID", measureID.values)
        df.insert(2, "Crop Name", name.values)
        df.insert(3, "Pest Name", pest.values)
        df.insert(3, "Part Rated", part.values)
        df.insert(4, "Rating Date", date.values)
        df.insert(6, "Unit", unit.values)


        return df


    def __get_treatments(self):

        treatments = []
        for i in range(self.__get_trialcount()):
            i += 1
            if i not in treatments:
                treatments.append(self.df.loc[i][1])

        return treatments

    def __get_trialcount(self):
        #traverses through the index to get integers that corispond to trail number
        trialNum = 0
        lastTrial = 0
        #checks to see if the number is one greater then the last trail number
        #this is to prevent unrelated integers in the index from breaking the code
        for i in self.df.index:
            if isinstance(i, int) and i == lastTrial +1:
                trialNum += 1
                lastTrial = i

        return trialNum

    def __get_values(self):
        measureIds = self.df.loc["No."][5:].values

        repNum = self.metadata["Num Replications"]
        trialNum = self.metadata["Trial Samples"]
        measureNum = len(measureIds)
        dfList = []
        #gets a list of dataframes for each measurment section 
        for i in range(trialNum):
            pos = self.df.index.get_loc(i+1) 
            plot_ids = self.df.iloc[pos:pos+repNum]
            temp = plot_ids.iloc[:,range(4,5+measureNum)]
            dfList.append(temp)
        #adds the dataframes into one large frame and sets the plot id as the index
        tdf = pandas.concat(dfList)

        columns = measureIds.tolist()
        columns.insert(0,"plot_id")
        tdf.columns = columns #sets measure ID to column names

        #For loop generates a list of the tratement ids 
        treatmentIDs = []
        ID = 1
        count = 0
        for i in range(tdf.shape[0]):
            count+=1
            if count > repNum:
                ID+=1
                count = 1
            treatmentIDs.append(ID)
        #inserts the treatement ids into the column 
        tdf.insert(measureNum+1,'Treatment_id',treatmentIDs)
        
        #melts the column   
        tdf = pandas.melt(tdf, id_vars=["plot_id","Treatment_id"], var_name="Measure_ID", value_name="Value")
        #inserts the trial id column
        tdf.insert(4,"Trial_id", None)


        return(tdf)
        
    def __get_trial(self):

        fileName = self.file.split("/")[-1]
        id = None
        # columns = [id, fileName, self.metadata["Protocol ID"]]
        columns = [id, fileName, self.metadata["Protocol"]]
        columnlabels = ["trial_uid","file_name","protocol_uid"]

        table = [columnlabels,columns]
        tdf = pandas.DataFrame(table)

        return tdf
