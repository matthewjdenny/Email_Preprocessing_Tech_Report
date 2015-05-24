# Script to semi-automate checking for intergrity of email parsing.

rm(list = ls())
library(stringr)

#1. Set working directory
WD <- "~/Dropbox/PINLab/Projects/Denny_Working_Directory/Processed_Data/Transylvania"
WD <- "~/Dropbox/PINLab/Projects/Denny_Working_Directory/Processed_Data/Columbus"
WD <- "~/Dropbox/PINLab/Projects/Denny_Working_Directory/Processed_Data/McDowell"
setwd(WD)


#2. Load and clean Data
Stoplist <- read.table(file = "/Users/matthewjdenny/Dropbox/PINLab/Projects/Denny_Working_Directory/Parsing_Scripts/additional-stopwords.txt", stringsAsFactors = F)
Stoplist <- as.matrix(Stoplist)
Vocabulary <- read.table(file = "vocab.txt", stringsAsFactors = F)
Vocabulary <- as.matrix(Vocabulary)
ManagerEmails <- read.table(file = "McDowell_Emails.txt", stringsAsFactors = F)
ManagerEmails <- as.matrix(ManagerEmails)
EdgeMatrix <- read.csv(file = "edge-matrix.csv", header = F, stringsAsFactors = F)
EdgeMatrix <- as.matrix(EdgeMatrix)
WordMatrix <- read.csv(file = "word-matrix.csv", header = F, stringsAsFactors = F)
FileNames <- WordMatrix[,1]
WordMatrix <- WordMatrix[,-1]
Sender <- as.vector(as.numeric(EdgeMatrix[,2]))
EdgeMatrix <- EdgeMatrix[,-(1:2)]

plusone <- function(n){
    n <- n + 1
    return(n)
}

#increment by 1 as index starts at 0
Sender <- lapply(Sender, plusone)
Sender <- as.vector(Sender)

#once we have already saved our work all we need to do is do the file.
#load(file = "Transylvania_Data_Integrity.Rdata")



#3. Draw a random sample of emails

GetSample <- function(numsamples, numfiles= length(FileNames)){
    #randomly samples without replacement from a vector with length equal to the number of files
    set.seed(1234)
    samplespace <- c(1:numfiles)
    Sample <- sample(samplespace, numsamples, replace = FALSE)
    return(Sample)
}

#try with 20 emails
FilesToCheck <- GetSample(20)


#4. Compare Emails and check their integrity
source("~/Dropbox/PINLab/Projects/Denny_Working_Directory/Parsing_Scripts/Check_Data_Integrity_Main_Function.R")

#4.1 Copy the code out of the 
Check_Email_Integrity(index = 1)

Check_Email_Integrity(index = 1,textfromemail = Text)


#make sure to include subject line
Text <- " 

"



# Save your work
save(list = ls(), file = "Transylvania_Data_Integrity.Rdata")
save(list = ls(), file = "Columbus_Data_Integrity.Rdata")
save(list = ls(), file = "McDowell_Data_Integrity.Rdata")
