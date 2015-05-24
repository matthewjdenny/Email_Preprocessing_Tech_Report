#data integrity main function

Check_Email_Integrity <- function(addresses = ManagerEmails, filestocheck = FilesToCheck, vocab = Vocabulary, wordmatrix = WordMatrix, edgematrix = EdgeMatrix, filenames = FileNames, sender = Sender,stoplist = Stoplist, index = 1 , textfromemail = FALSE){
    
    #if there is not text to check against provided, then open the text document in its folder
    if(textfromemail == FALSE){
        p1 <- pipe(paste("edit \"", filenames[filestocheck[index]] ,"\" ", sep = ""), "r")
        close(p1)
        print(paste("opening file number ", index, "file number: ", filestocheck[index]))
        send <- sender[filestocheck[index]][[1]]
        from <- addresses[send]
        already <- F
        for(i in 1:length(edgematrix[1,])){
            if(edgematrix[filestocheck[index],i] > 0){
                if(already == F){
                    to <- addresses[i]
                    already <- T
                }else{
                    to <- c(to, addresses[i])
                }
            }
        }
        print(paste("sender: ", from))
        for(i in 1:length(to)){
            print(paste("to: ", to[i]))
        }
        
    }
    
    #if there is text to check against then tokenize it and check against it. 
    if(textfromemail != FALSE){
        already <- F
        #get all words from word matrix
        for(i in 1:length(wordmatrix[1,])){
            if(wordmatrix[filestocheck[index],i] > 0){
                #print(i)
                #print(vocab[i])
                if(already == F){
                    Words <- vocab[i]
                    Count <- wordmatrix[filestocheck[index],i]
                    already <- T
                }else{
                    Words <- c(Words, vocab[i])
                    Count <- c(Count, wordmatrix[filestocheck[index],i])
                }
            }
        }
        WordandCount <- cbind(Words, Count)
        #print(WordandCount)
        #for(i in 1:length(WordandCount[,1])){
        #    print(WordandCount[i,])
        #}
        
        
        #take the input text, remove stopwords and put it into a two column matrix for comparison
        textfromemail <- tolower(textfromemail)
        email_vector <- strsplit(textfromemail, "[^a-zA-Z]+", perl = T)
        email_vector <- email_vector[[1]]
        #remove stopwords
        already <- F
        for(i in 1:length(email_vector)){
            Stopword <- F
            for(l in 1:length(stoplist)){
                if(as.character(stoplist[l]) == as.character(email_vector[i])){
                    Stopword <- T
                    #print(paste("found stopword: ", email_vector[i]))
                }
            }
            if(!Stopword){
                if(!already){
                    Reduced <- email_vector[i]
                    already <- T
                }else{
                    Reduced <- c(Reduced, email_vector[i])
                }
            }
        }
        email_vector <- Reduced
        Excluded<-c() 
        #compare email and input words
        already <- F
        for(j in 1:length(email_vector)){
            inWordandCount <- F
            for(k in 1:length(WordandCount[,1])){
                if(email_vector[j] == WordandCount[k,1]){
                    WordandCount[k,2] <- (as.numeric(WordandCount[k,2]) - 1)
                    inWordandCount <- T
                }
            }
            if(!inWordandCount){
                if(!already){
                    Excluded <- email_vector[j]
                    already <- T
                }else{
                    Excluded <- c(Excluded, email_vector[j])
                }
            }
        }
        
        #print out those that do not match:
        print("Excluded from word matrix: ")
        already <- F
        for(i in 1:length(Excluded)){
            if(!already){
                printexcluded <- Excluded[i]
                already <- T
            }else{
                printexcluded <- paste(printexcluded, " ", Excluded[i], sep = "")
            }
        }
        print(printexcluded)
        print(" ")
        print("Included in Word Matrix but not in input text: ")
        already <- F
        badinclude <- ""
        for(i in 1: length(WordandCount[,1])){
            if(WordandCount[i,2] != 0){
                if(!already){
                    badinclude <- paste(WordandCount[i,1]," : ", WordandCount[i,2], sep= "")
                    already <- T
                }else{
                    badinclude <- paste(badinclude,"   ", WordandCount[i,1]," : ", WordandCount[i,2], sep= "")
                }
            }
        }
        print(badinclude)
        
    }
        
    
    
    
}

