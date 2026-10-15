#imports libraries


import csv 
from pathlib import Path
import statistics
import math
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

#cleaning the dataset
def clean_data():

    clean_data=[]
    dropped_lines=0
    entries=set() #creates a set to store athletes ID and games they participated in

    try:
        filepath=input("Enter the pathway to 'athlete_events.csv' file:\n")
        with open (filepath, "r") as file: #opens the file
            data=list(csv.reader(file)) #reads the file and saves in variable

            for index, line in enumerate(data): #iterates over dataset lines
                if index==0: 
                    clean_header=[line[0], line[1], line[2], line[4], line[5], line[8], line[9], line[12]] #removes unnecessary headers from dataset
                    clean_data.append(clean_header) #adds cleaned header to clean dataset
                    continue
                new_athlete=False #variable to check if athlete is good to add to list
                if line[0]!="NA" and line[1]!="NA" and line[2]!="NA" and line[4]!="NA" and line[5]!="NA" and line[8]!="NA" and line[9]!="NA" and line[12]!="NA": #checks if necessary columns are filled
                    if (line[0], line[8]) in entries: #checks for duplicates aka if the combination of athletes ID and games of participation are already present in cleaned data
                        dropped_lines+=1 #if present counts the dropped line 
                    else:
                        new_athlete=True #indicates that athlete is valid
                        entries.add((line[0], line[8])) #adds the ID + games to the set
                else:
                    dropped_lines+=1 #if some on entries are empty counts the line as dropped
                    
                if new_athlete: #if athlete is valid 
                    clean_data.append([line[0], line[1], line[2], line[4], line[5], line[8], line[9], line[12]]) #appends the line with necessary columns to the cleaned data

                 
            with open("cleaned_athelete_events.csv", "w") as file: #opens a new file and saves cleaned dataset there
                writer=csv.writer(file)
                writer.writerows(clean_data)
           
        return clean_data, dropped_lines #returns the cleaned data and number of dropped lines
    
    
    except FileNotFoundError: #reports error if file is not found
        print("File couldn't be found!")
        return None, dropped_lines
    except: #informs user that file failed to open
        print("Failed to open the original file!")
        return None, dropped_lines

#function to calculate the BMI
def calculate_BMI(height, weight):
    height_m=height/100 #converts height from cm to m
    return weight/(height_m**2) #returns the BMI

def compute_stats (samples, BMI):
    #creates the variables
    averages={}
    uncertainties={}  
    removed_athletes=0

    for s in samples: #iterates over 4 samples
        for athlete in samples[s]: #iterates over each athlete
            BMI[s].append(calculate_BMI(float(athlete[3]), float(athlete[4]))) #calculates the BMI passing the weight and height as arguments, saves value to the BMI list

    for s in samples: #iterates over subsamples
        for index, value in enumerate(BMI[s]): #iterates over the BMI values
            if float(value)<16: #if BMI is too little (less than 16) - removes the athlete and informs user
                print("Implausible athlete:")
                print(samples[s][index])
                print(f"BMI:{value}")
                del samples[s][index]
                del BMI[s][index]
                removed_athletes+=1
    print(f"{removed_athletes} athlete removed")           
    
    for s in samples: #iterates over 4 samples
        averages[s]=statistics.mean(BMI[s]) #calculates average for each sample
        uncertainties[s]=statistics.stdev(BMI[s])/math.sqrt(len(BMI[s])) #calculate the uncertainty (error of the mean) for each sample
        
    return averages, uncertainties

#Conducts the t-test
def t_test(a,b):

    result=stats.ttest_ind(a, b, equal_var=False) #t-test for athletes

    alpha=0.01 #significance level
    
    if result.pvalue<alpha: #checks if difference in  samples is significant
        significance = True
    else:
       significance = False
    
    return significance, result.pvalue 
    
def main():
    a=Path("cleaned_athelete_events.csv") #path to the cleaned dataset
    cleaning_performed=False
    cleaned_data=None
    if a.exists(): #if data already cleaned, opens the file and saves data into a variable
        try:   
            with open(a, "r") as f: 
                cleaned_data=list(csv.reader(f))
        except FileNotFoundError:
                print("File couldn't be found!")
        except:
            print("Failed to open cleaned file!")
    else: #cleans the dataset if not done yet
        cleaned_data, dropped_lines =clean_data()
        cleaning_performed=True

    if cleaned_data==None or len(cleaned_data) <= 1:
        print("Failed to open the file!")
        return
    samples={} #a dict to store 4 sample lists

    #creates an empty list for each sports and both genders
    samples["triathlon_m"]=[]
    samples["triathlon_f"]=[]
    samples["weightlifting_m"]=[]
    samples["weightlifting_f"]=[]

    #the same is done for BMI values
    BMI={}
    for s in samples: #iterating over sample dict to reuse the keys
        BMI[s]=[]
    
        
    #iterates over dataset
    for index, line in enumerate(cleaned_data):
        if index==0: #skips the header
            continue

        #checks if athlete belongs to any of categories, appends them
        if line[7].lower()=="triathlon" and line[2].lower()=="m":
            samples["triathlon_m"].append(line)
        elif line[7].lower()=="triathlon" and line[2].lower()=="f":
            samples["triathlon_f"].append(line)
        elif line[7].lower()=="weightlifting" and line[2].lower()=="m":
            samples["weightlifting_m"].append(line)
        elif line[7].lower()=="weightlifting" and line[2].lower()=="f":
            samples["weightlifting_f"].append(line)
    
    min_years={} #creates a dict to store year of first event for each sport
    for s in samples: 
        years=[]
        for athlete in samples[s]:    
            years.append(int(athlete[6])) #adds to list the year of each event present in subsamples
        min_years[s]=min(years) #finds the year of first sports event for each subsample


    if min_years["triathlon_m"]<min_years["weightlifting_m"]: #checks what sport was introduced earlier
        year_m=min_years["weightlifting_m"] #assigns the latest year as the bottom range of year selection
    else:
        year_m=min_years["triathlon_m"]

    if min_years["triathlon_f"]<min_years["weightlifting_f"]: #checks what sport was introduced earlier
            year_f=min_years["weightlifting_f"] #assigns the latest year as the bottom range of year selection
    else:
            year_f=min_years["triathlon_f"]

    for s in samples: #iterates over samples
            keep=[] #a list for values that need to be kept 
            for athlete in samples[s]: #iterates over athletes in subsample
                if athlete[2].lower()=="m": #checks if its a male
                    if int(athlete[6])>=year_m: #checks if year of athletes performance fits into the range
                        keep.append(athlete) #keeps the athlete in subsample
                else:
                    if int(athlete[6])>=year_f:
                        keep.append(athlete)
            samples[s]=keep
    
    

    averages, uncertainties = compute_stats(samples, BMI) #calls the function to calculate the averages and uncertainty

    

        
    difference_m=abs(averages["triathlon_m"]-averages["weightlifting_m"]) #calculates the difference between weightlifters and triathletes 
    u_difference_m=math.sqrt(uncertainties["triathlon_m"]**2+uncertainties["weightlifting_m"]**2) #calculating the uncertainty for difference
    significance_m, pvalue_m = t_test(BMI["triathlon_m"], BMI["weightlifting_m"]) #calculating if the difference is significant

    difference_f=abs(averages["triathlon_f"]-averages["weightlifting_f"])
    u_difference_f=math.sqrt(uncertainties["triathlon_f"]**2+uncertainties["weightlifting_f"]**2)
    significance_f, pvalue_f= t_test(BMI["triathlon_f"], BMI["weightlifting_f"])
    
    difference_mf=abs(difference_m-difference_f)
    u_difference_mf=math.sqrt(u_difference_m**2+u_difference_f**2)
    z_mf=difference_mf/u_difference_mf

    #OUTPUT
    #prints the overview on athlete count in every category
    if cleaning_performed:
        print(f"After cleaning the dataset {dropped_lines} lines were dropped.")
    print("---- Number of Athletes -----")
    print(f"Triathlon:\n Men: {len(samples['triathlon_m'])}\n Female: {len(samples['triathlon_f'])}\n")
    print(f"Weightlifting:\n Men: {len(samples['weightlifting_m'])}\n Female: {len(samples['weightlifting_f'])}\n")


    print("---- Average BMI -----")
    for s in samples: #iterates over samples
        print(f"Average BMI for {s}: {averages[s]:.3f} ± {uncertainties[s]:.3f}\n") #prints the average count for each sample

    print("---- T-test Results -----")
    print(f"The difference in BMI of male triathletes and weightlifters is {difference_m:.3f} ± {u_difference_m:.3f}")
    if significance_m:
        print(f"Significant difference for men P-value: {pvalue_m:.3e}\n")
    else:
        print(f"Not significant difference for men. P-value: {pvalue_m:.3e}\n")
    
    print(f"The difference in BMI of female triathletes and weightlifters is {difference_f:.3f} ± {u_difference_f:.3f}")
    if significance_f:
        print(f"Significant difference for female. P-value: {pvalue_f:.3e} \n")
    else:
        print(f"Not significant difference for female. P-value: {pvalue_f:.3e} \n")


    print(f"The difference for male and female athletes differed by {difference_mf:.3f} ± {u_difference_mf:.3f}")
    if z_mf>2.576:
        print(f"Men and female differ significantly. Z-value: {z_mf:.3f}\n")
    else:
        print(f"Men and female don't differ significantly. Z-value: {z_mf:.3f}\n")

    print("\n---- Validity Check -----")
    
    assert len(samples["triathlon_f"])==len(BMI["triathlon_f"]) #comparison in programm run correctly
    print(f"Height: {samples['triathlon_f'][0][3]} Weight: {samples['triathlon_f'][0][4]} BMI: {BMI['triathlon_f'][0]}") #prints some values to check if program works correctly



    #VISUALISATION
    min_bmi=[] 
    max_bmi=[]
    
    #iterates over the BMI subsamples and finds the lowest and highest value in each
    for value in BMI:
        min_bmi.append(min(BMI[value]))
        max_bmi.append(max(BMI[value]))
        
    lower_range=math.floor(min(min_bmi)) #rounds down the lowest BMI value
    upper_range=math.ceil(max(max_bmi)) #rounds up the highest BMI value
    
    bin_range=np.arange(lower_range, upper_range+1, 1) #creates a list with bins of width 1, ranged from lowest to highest BMI
    
    fig, axs = plt.subplots(1, 2, figsize=(10, 5), sharey=True) #creates 2 subplots
    fig.suptitle("Density Distribution of Triathlete and Weightlifter BMI", weight="bold")
        
    #formatting of first figure
    axs[0].set(xlabel=("BMI (kg/m²)"))
    axs[0].set(ylabel=("Fraction of Athletes per 1 kg/m²"))
    axs[0].set_title("Male")
    
    axs[0].hist(BMI["triathlon_m"], label=f"Male triathletes\n x̄={averages["triathlon_m"]:.2f} ± {uncertainties["triathlon_m"]:.2f}", bins=bin_range, color="#76C0EC",alpha=0.5, density=True)
    axs[0].axvline(averages["triathlon_m"], color="#76C0EC", linestyle="--")
    axs[0].hist(BMI["weightlifting_m"], label=f"Male weightlifters\n x̄={averages["weightlifting_m"]:.2f} ± {uncertainties["weightlifting_m"]:.2f}", bins=bin_range, color="#425B9A", alpha=0.7, density=True)
    axs[0].axvline(averages["weightlifting_m"], color="#425B9A", linestyle="--")

    #formatting of second figure
    axs[1].set(xlabel=("BMI (kg/m²)"))
    axs[1].set_title("Female")
    
    axs[1].hist(BMI["triathlon_f"], label=f"Female triathletes\n x̄={averages["triathlon_f"]:.2f} ± {uncertainties["triathlon_f"]:.2f}", bins=bin_range, color="#F39399", alpha=0.7, density=True)
    axs[1].axvline(averages["triathlon_f"], color="#F39399", linestyle="--")
    axs[1].hist(BMI["weightlifting_f"], label=f"Female weightlifters\n x̄={averages["weightlifting_f"]:.2f} ± {uncertainties["weightlifting_f"]:.2f}", bins=bin_range, color="#CF4173", alpha=0.7, density=True)
    axs[1].axvline(averages["weightlifting_f"], color="#CF4173", linestyle="--")
    #plotting the legend
    axs[0].legend()
    axs[1].legend()

    #saving&showing the figure
    plt.tight_layout()
    plt.savefig("BMI_hist.png", dpi=300)
    plt.show()
    

main()

