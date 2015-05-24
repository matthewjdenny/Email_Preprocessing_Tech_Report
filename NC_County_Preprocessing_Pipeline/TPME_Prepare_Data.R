#prepare data for analysis with model
library("slam")
rm(list = ls())

county <- commandArgs(T)
setwd(paste("/home/neha/Desktop/PINL/email_parser/",county[1],sep=""))


if(county[2] == "all"){
#======== Jackson COunty =========#
author_attributes =  read.csv("authors.txt", header= F, stringsAsFactors = F)
document_edge_matrix = read.csv("edge_matrix.csv", header= F, stringsAsFactors = F)
document_edge_matrix = document_edge_matrix[,-1]
#print(dim(document_edge_matrix))
document_edge_matrix[,1] <- document_edge_matrix[,1] + 1 #make sure that authors are indexed starting at 1
document_word_matrix = read.csv("word_matrix.csv", header= F, stringsAsFactors = F)
#print(dim(document_word_matrix))
document_word_matrix = document_word_matrix[,-1]
summary = read.csv("summary.csv", header= F, stringsAsFactors = F)
#print(dim(summary))
summary = summary[,-1]
#print(apply(document_word_matrix,1,sum))
vocabulary = read.csv("vocab.txt", header= F, stringsAsFactors = F)
remove <- which(apply(document_word_matrix,1,sum) == 0)
if( length(remove)  > 0){
	document_edge_matrix <- document_edge_matrix[-remove,]
	document_word_matrix <- document_word_matrix[-remove,]
	summary <-  summary[-remove,]
}

document_word_matrix <- as.simple_triplet_matrix(document_word_matrix)
document_edge_matrix <- as.simple_triplet_matrix(document_edge_matrix)
filename <- paste(county[1],"_all.Rdata",sep="")
save(list = ls(),file = filename)
#===================================#
setwd("/home/neha/Desktop/PINL/email_parser/")
}




if(county[2] == "internal"){
#======== Jackson COunty =========#
author_attributes =  read.csv("internal_emails_data.csv", header= T, stringsAsFactors = F)
document_edge_matrix = read.csv("edge_matrix_internal.csv", header= F, stringsAsFactors = F)
document_edge_matrix = document_edge_matrix[,-1]
document_edge_matrix[,1] <- document_edge_matrix[,1] + 1 #make sure that authors are indexed starting at 1

document_edge_matrix_to = read.csv("edge_matrix_internal_to.csv", header= F, stringsAsFactors = F)
document_edge_matrix_to = document_edge_matrix_to[,-1]
document_edge_matrix_to[,1] <- document_edge_matrix_to[,1] + 1 #make sure that authors are indexed starting at 1

document_edge_matrix_cc = read.csv("edge_matrix_internal_cc.csv", header= F, stringsAsFactors = F)
document_edge_matrix_cc = document_edge_matrix_cc[,-1]
document_edge_matrix_cc[,1] <- document_edge_matrix_cc[,1] + 1 #make sure that authors are indexed starting at 1

document_word_matrix = read.csv("word_matrix_internal.csv", header= F, stringsAsFactors = F)
document_word_matrix = document_word_matrix[,-1]
summary_internal = read.csv("summary_internal.csv", header= F, stringsAsFactors = F)
summary_internal = summary_internal[,-1]
print(apply(document_word_matrix,1,sum))
vocabulary = read.csv("vocab_internal.txt", header= F, stringsAsFactors = F)
remove <- which(apply(document_word_matrix,1,sum) == 0)
if( length(remove)  > 0){
	document_edge_matrix <- document_edge_matrix[-remove,]
	document_edge_matrix_to <- document_edge_matrix_to[-remove,]
	document_edge_matrix_cc <- document_edge_matrix_cc[-remove,]
	document_word_matrix <- document_word_matrix[-remove,]
	summary_internal <-  summary_internal[-remove,]
}
print(dim(document_edge_matrix))
print(dim(document_edge_matrix_to))
print(dim(document_edge_matrix_cc))
print(dim(document_word_matrix))
print(dim(summary_internal))
filename <- paste(county[1],"_internal.Rdata",sep="")
save(list = ls(),file = filename)
#===================================#
setwd("/home/neha/Desktop/PINL/email_parser/")

}
