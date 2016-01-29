#setwd("~/Documents/Projects/import_metadata/")

import_metadata <- function(group_table){ #, group_column, sample_names){
    metadata_matrix <- as.matrix( # Load the metadata table (same if you use one or all columns)
        read.table(
            file=group_table,row.names=1,header=TRUE,sep="\t",
            colClasses = "character", check.names=FALSE,
            comment.char = "",quote="",fill=TRUE,blank.lines.skip=FALSE
        )
    )
    
    #metadata_matrix <- metadata_matrix[ order(sample_names),,drop=FALSE ]
    #group_names <- metadata_matrix[ order(sample_names), group_column,drop=FALSE ]
    #return(group_names)
}


## import_metadata <- function( id_list, output_name="my_metadata", debug=FALSE, my_auth_file=NA, log_file="default" ){ 
  
##   library(RCurl)
##   library(RJSONIO)
##   library(matlab)
  
##   if( is.na(my_auth_file)==FALSE ){
##     stop("The my_auth_file option is not support yet" )
##   }
  
  
##   # sub to export data
##   export_data <- function(data_object, file_name){
##     write.table(data_object, file=file_name, sep="\t", col.names = NA, row.names = TRUE, quote = FALSE, eol="\n")
##   }
  
  
##   id_list <- scan(file=id_list, comment.char="#", what="character", blank.lines.skip=TRUE)
    
##   num_entries <- length(id_list)
##   if( num_entries <= 1 ){
##     stop("There must be two or more metagnomes in your list")
##   }
  
##   #id_metadata_matrix <- matrix(data=NA, nrow=num_entries, ncol=2) 
  
##   for ( i in 1:num_entries){

##     print(paste("Retrieving metadata for sample (", i, ") of", num_entries))
    
##     # This bit is for auth of private data -- needs work - syntax is not correct
##     if ( is.na(my_auth_file)==TRUE ){
##       api_call <- paste("http://api.metagenomics.anl.gov/1/metadata/export/", id_list[i], sep="")
##     }else{
##       stop("auth not enabled in this script yet")
##       #library(matR)
##       #auth_key <- my_key <- msession$setAuth(file=my_auth_file)
##       #api_call <- paste("http://api.metagenomics.anl.gov/1/metadata/export/", id_list[i], "&auth=", auth_key, sep="")
##     }
  
##     if(debug==TRUE){print(api_call)}
    
##     if( i == 1 ){ # what to do for the first entry
      
##       first_call <- fromJSON(httpGET(api_call))
##       flattened_first_call <- unlist(first_call, recursive=TRUE)
##       metadata_matrix <- matrix(flattened_first_call)
##       rownames(metadata_matrix) <- names(flattened_first_call)
##       colnames(metadata_matrix) <- id_list[i]
##       metadata_matrix <- data.frame(metadata_matrix)
      
##     }else{ # what do do for the second entry
    
##       next_call <- fromJSON(httpGET(api_call))
##       flattened_next_call <- unlist(next_call, recursive=TRUE)
      
##       temp_metadata_matrix <- matrix(flattened_next_call)
##       rownames(temp_metadata_matrix) <- names(flattened_next_call)
##       colnames(temp_metadata_matrix) <- id_list[i]
##       temp_metadata_matrix <- data.frame(temp_metadata_matrix)
      
##       metadata_matrix <- merge(temp_metadata_matrix,metadata_matrix,by="row.names",all=TRUE)
##       rownames(metadata_matrix) <- metadata_matrix$Row.names
##       metadata_matrix$Row.names <- NULL
##     }
    
##   }
  
##   # change type back to matrix
##   metadata_matrix <- as.matrix(metadata_matrix)
  
##   # remove any carriage returns and tabs
##   metadata_matrix <- gsub("\n", "", metadata_matrix)
##   metadata_matrix <- gsub("\r", "", metadata_matrix)
##   metadata_matrix <- gsub("\t", "", metadata_matrix)

##   metadata_matrix <- rot90(metadata_matrix)
##   #return(metadata_matrix)
  
##   # print output to file
##   output_file_name = paste(output_name, ".txt", sep="")
##   export_data(metadata_matrix, output_file_name)
  
##   # create output object
##   #assign(x=metadata_matrix, value=output_name)
##   do.call("<<-",list(output_name, metadata_matrix)) 
  
##   # name the log file
##   if( identical(log_file, "default")==TRUE ){ 
##     log_file_name <- paste(output_name, ".import_metadata.log", sep="") 
##   }else{
##     log_file_name <- log_file
##   }
  
##   writeLines(
##     paste(
##       "##############################################################\n",
##       "#################### import_metadata SUMMARY ####################\n",
##       "id_list:        ", id_list, "\n",
##       "num_metagenomes   ", num_entries, "\n",
##       "my_auth_file:     ", my_auth_file, "\n",
##       "debug:            ", debug, "\n",
##       "##############################################################\n",
##       "output_object:    ", output_name, "\n",
##       "otuput_file:      ", output_file_name, "\n",
##       "log_file:         ", log_file_name, "\n",
##       "##############################################################",
##       sep="", collapse=""
##     )
##     #con=log_file
##   )
    
##   writeLines(
##     paste(
##       "##############################################################\n",
##       "#################### import_metadata SUMMARY ####################\n",
##       "id_list:        ", id_list, "\n",
##       "num_metagenomes   ", num_entries, "\n",
##       "my_auth_file:     ", my_auth_file, "\n",
##       "debug:            ", debug, "\n",
##       "##############################################################\n",
##       "output_object:    ", output_name, "\n",
##       "otuput_file:      ", output_file_name, "\n",
##       "log_file:         ", log_file_name, "\n",
##       "##############################################################",
##       sep="", collapse=""
##     ),
##     con=log_file
##   )
  

## }


# name the output object
#assign(new_object_name, object)


