# Script to semi-automate checking for intergrity of email parsing.

rm(list = ls())
library(stringr)

#1. Set working directory
#WD <- "~/Dropbox/PINLab/Projects/Denny_Working_Directory/Processed_Data/Transylvania"
#WD <- "~/Dropbox/PINLab/Projects/Denny_Working_Directory/Processed_Data/Columbus"
#WD <- "~/Dropbox/PINLab/Projects/Denny_Working_Directory/Processed_Data/McDowell"
county<- "Vance"
WD <- paste("/home/neha/Desktop/PINL/email_parser/",county,sep="")
setwd(WD)


#2. Load and clean Data
Stoplist <- read.table(file = "/home/neha/Desktop/PINL/email_parser/additional-stopwords.txt", stringsAsFactors = F)
Stoplist <- as.matrix(Stoplist)
Vocabulary <- read.table(file = "vocab_internal.txt", stringsAsFactors = F)
Vocabulary <- as.matrix(Vocabulary)
ManagerEmails <- read.table(file = "authors_internal.txt", stringsAsFactors = F)
ManagerEmails <- as.matrix(ManagerEmails)
EdgeMatrix <- read.csv(file = "edge_matrix_internal.csv", header = F, stringsAsFactors = F)
EdgeMatrix <- as.matrix(EdgeMatrix)
WordMatrix <- read.csv(file = "word_matrix_internal.csv", header = F, stringsAsFactors = F)
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
indext <-2
#try with 20 email
FilesToCheck <- GetSample(20)
print(FilesToCheck)
#FilesToCheck <- c(106 ,576 ,563 ,575 ,793 ,590 ,9 ,214 ,611 ,472 ,635 ,499 ,259 ,843 ,267 ,762 ,261 ,243 ,170)
print(FileNames[FilesToCheck[indext]])
print(FileNames[FilesToCheck[indext+1]])
#4. Compare Emails and check their integrity
source("/home/neha/Desktop/PINL/email_parser/Check_Data_Integrity_Main_Function.R")

Text <- "
RE: Hello Yes it will work.  I\'ll see ya then.  Linda



Linda S. Fry, MSW

Director, Vance County Department of Social Services

linda.fry@vance.nc.gov

252-492-5001  Extension: 3236



"

Check_Email_Integrity(index = indext)
Check_Email_Integrity(index = indext,textfromemail = Text)


#make sure to include subject line


filename <- paste(county,"_Data_Integrity.Rdata",sep="")
# Save your work
save(list = ls(), file = filename)
WD <- "/home/neha/Desktop/PINL/email_parser/"
setwd(WD)
#save(list = ls(), file = "Columbus_Data_Integrity.Rdata")
#save(list = ls(), file = "McDowell_Data_Integrity.Rdata")
