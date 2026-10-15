# _Comparison of BMI in Olympic Triathletes and Weightlifters for men and women_

## _Description_
Body mass index (BMI) is a measure of body fat based on height and weight. Because of scarce input data BMI can't distinguish between body fat and muscle mass, therefore it is a useful tool to measure muscle mass in athletes.

This project aims to answer the research question:<br>
Do Olympic triathletes and weightlifters differ significantly in BMI, how large is this difference for men and women, and does the difference itself differ between the sexes?

## _Dataset_
The Dataset containing data on all Olympic games from Athens 1896 to Rio 2016 was obtained from Kaggle. It can be downoloaded here: https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results/data 

## _Installation_

1. Make sure you have Python 3 installed. 
2. Additionally NumPy, Matplotlib and Scipy packages are required:
```bash
pip install numpy
pip install matplotlib
pip install scipy
```

3. Clone the repository
```bash
git 
cd 
```
**Alternatively, download the repository as a ZIP file:**
* Press green button "<> Code"
* Click "Download ZIP"

## _Usage_

1. Open the repository in your IDE (e.g. VS Code)
2. Run the code
    * It will ask for a pathway to the file "athlete_events.csv"
    * Program automatically cleans the dataset and stores it in new file "cleaned_athelete_events.csv"
    * A plot will be generated and saved as "BMI_hist.png"
