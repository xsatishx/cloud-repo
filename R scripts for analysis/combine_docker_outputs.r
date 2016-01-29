# R "workflow" to process the outputs from the the docker file processing to gnerate visualizations

# assume that you start in 
#   /PATH/
# and that all of the file paths follow this pattern:
#   /PATH/ERRXXXXXX/star_2_pass/genes.fpkm_tracking
# XXXXXX is unique, thes rest is not so use the ERR portion of the path to name the data
# and that the paths_file looks like this:
#  ERR188021
#  ERR188022
#  ERR188023
#   ...
# The script will prefix this with "./" and add "/star_2_pass/genes.fpkm_tracking" to the end to get paths for the individual files
# Typical usage
# setwd(/Users/kevin/Documents/Projects/Geuvadis_data/All_666/results.as_of.1-4-15)
# source(source("~/git/CDIS_GEUVADIS_analysis/combine_docker_outputs.r"))
# combine_docker_outputs(paths_file="1-4-12.completed_list", output_prefix="1-4-12.completed", export_R_table=TRUE)

############################################################################################################################
############################################################################################################################
### FIST IMPORT PACKAGES AND FUNCTIONS
############################################################################################################################
############################################################################################################################

# install and source R packages and functions if option is true - must be done for the other functions to work

############################################################################################################################
############################################################################################################################

############################################################################################################################
############################################################################################################################
### IMPORT DATA INTO AN R MATRIX
############################################################################################################################
############################################################################################################################

  # NOTES
  #   - transfer
  #   - scripts(create CDIS repo)
  #   - do it (use first part of path)

  # dev dir with sample data
  # setwd("~/Documents/Projects/Taiwan")
  # setwd("/Users/kevin/Documents/Projects/Taiwan/sample_data")


  # select the type of data to compile from the results
  #my_dataype ="FPKM"
  # other possibilities are
  # tracking_id
  # class_code
  # nearest_ref_id
  # gene_id
  # gene_short_name
  # tss_id
  # locus
  # length
  # coverage
  # FPKM
  # FPKM_conf_lo
  # FPKM_conf_hi
  # FPKM_status


combine_docker_outputs <- function(paths_file="test_list", my_dataype="FPKM", output_prefix="my_data", load_prereqs=FALSE, export_R_table=FALSE, debug=FALSE){
    
    # option to load prereqs
    if( load_prereqs==TRUE ){
        source("~/git/install_r_prereqs.r")
        install_r_prereqs()
    }

    my_ids <- readIDs(paths_file)  
    
    # names for log and output
    log_file <- paste("R_compile.", my_dataype, ".log.txt", sep="")
    output_name <- paste(output_prefix, ".combined_", my_dataype, ".txt", sep ="")

    # import list of ids
    # my_ids <- readIDs("stuti_results.done_11-10-15")
    # my_ids <- readIDs("test_list")

    # create matrix to hold data and vector to hold colnames
    FPKM_matrix <- matrix()
    FPKM_colnames <- vector(mode="character")
    
    for (i in 1:length(my_ids)){
        
        my_file=paste("./", my_ids[i], "/star_2_pass/genes.fpkm_tracking", sep="")
        
        if(debug==TRUE){print(paste("made it here (0)"))}
        
        if(debug==TRUE){print(paste(my_ids[i], sep=""))}  
        
        if(debug==TRUE){print(paste("made it here (0.1)"))}
        
        #if( file.exists(paste("./", my_ids[i], sep="")) != FALSE ){
        if( file.exists(my_file) != FALSE ){

            if(debug==TRUE){print(paste("FILE_STATUS: ", file.exists(paste(my_file, sep=""))))}
            if(debug==TRUE){print(paste("FILE_NAME  : ", my_file, sep=""))}
            ### shell version of check:
            ### for i in `cat stuti_results.done_11-10-15`; do if [ -f ".$i" ];then echo ".$i exists"; fi; done

            if(debug==TRUE){print(paste("made it here (0.2)"))}
            
            #my_data_temp <- import_metadata(paste("./", my_ids[i], sep=""))
            my_data_temp <- import_metadata(my_file)
             
            if(debug==TRUE){print(paste("made it here (0.3)"))}
            
            # Add name of current file to the colnames vector
            split_path_string <- unlist(strsplit(my_ids[i], split="/"))
            my_data_name <- split_path_string[1]

            if(debug==TRUE){print(paste("made it here (0.4)"))}
            my_rownames <- row.names(my_data_temp) # NOT HUMAN READABLE
            # my_rownames <- my_data_temp[,"gene_short_name"] # NOT UNIQUE
            # COMPROMISE - UNIQUE AND CAN GET READABLE NAME EASILY
            unique_rownames <- vector(mode="character")
            for ( j in 1:length(my_rownames) ){
                unique_rownames <- c(unique_rownames, paste(my_data_temp[j,"gene_short_name"], "_", my_rownames[j], sep=""))
            }

            if(debug==TRUE){print(paste("made it here (0.5)"))}
            # replace original rownames with concatenated ones   
            row.names(my_data_temp) <- unique_rownames
    
            if(debug==TRUE){print(paste("made it here (1)"))}
  
            if( i==1 ){ # import first sample data
                FPKM_matrix <- my_data_temp[ , my_dataype, drop=FALSE] # matrix(my_data_temp[,my_dataype])
                row.names(FPKM_matrix) <- unique_rownames 
                FPKM_colnames <- my_data_name
                if(debug==TRUE){print(paste("made it here (2)"))}
                if(debug==TRUE){print(paste("i: ", i))}
                #cat("World",file="outfile.txt",append=TRUE)
                cat(paste(my_ids[i], "PROCESSED"), sep="\n", file=log_file, append=FALSE)
            }else{ # import all other datasets - subloop to take care of the last
                # Import the data into an R matrix
                if(debug==TRUE){print(paste("made it here (3)"))}
                #FPKM_matrix <- matrix(my_data_temp[,my_dataype])
                #row.names(FPKM_matrix) <- unique_rownames
                FPKM_matrix <- merge(FPKM_matrix, my_data_temp[, my_dataype], by="row.names", all=TRUE) # This does not handle metadata yet
                rownames(FPKM_matrix) <- FPKM_matrix$Row.names
                FPKM_matrix$Row.names <- NULL
                FPKM_colnames <- c(FPKM_colnames, my_data_name)
                if(debug==TRUE){print(paste("col_names:", FPKM_colnames))}
                # subloop to add the column names when on the last sample (make this a sub)
                cat(paste(my_ids[i], "PROCESSED"), sep="\n", file=log_file, append=TRUE)
                if( i == length(my_ids) ){ # take care of the last sample (add column headers)
                    if(debug==TRUE){print(paste("made it here (4)"))}
                    if(debug==TRUE){print(paste("col_names:", FPKM_colnames))}
                    # add column names
                    colnames(FPKM_matrix) <- FPKM_colnames
                    # replace introduced NAs with 0
                    FPKM_matrix[is.na(FPKM_matrix)] <- 0
                    # order data by row name
                    ordered_rownames <- order(rownames(FPKM_matrix))
                    FPKM_matrix <- FPKM_matrix[ordered_rownames,]
                    # export to flat file
                    export_data(FPKM_matrix, output_name)
                    # return data object here
                }
            }

        }else{
    
            cat(paste(my_file, "DOES NOT EXIST"), sep="\n", file=log_file, append=TRUE)
            # subloop to add the column names when on the last sample (make this a sub)
            if( i == length(my_ids) ){ # take care of the last sample (add column headers)
                # add column names
                colnames(FPKM_matrix) <- FPKM_colnames
                # replace introduced NAs with 0
                FPKM_matrix[is.na(FPKM_matrix)] <- 0
                # order data by row name
                ordered_rownames <- order(rownames(FPKM_matrix))
                FPKM_matrix <- FPKM_matrix[ordered_rownames,]
                # export to flat file
                export_data(FPKM_matrix, output_name)
                # return data object here
            }
    
        }
  
    }
    
   # write summary to log
    cat(
        paste(
            "##############################################################\n",
            "###################### INPUT PARAMETERS ######################\n",
            "paths_file:              "    , paths_file, "\n",
            "my_dataype:              "    , my_dataype, "\n",
            "output_prefix:           " , output_prefix, "\n",
            "load_prereqs:            "  , load_prereqs, "\n",
            "export_R_table:          ", export_R_table, "\n",
            "debug:                   "         , debug, "\n",
            "####################### OUTPUT SUMMARY #######################\n",
            "output file:             ", output_name, "\n",
            sep="", collapse=""
        ),
        append=TRUE,
        file=log_file
    )

    # export table as an R object, send message to user
    if( export_R_table==TRUE ){
        output_object_name <- paste(output_prefix, ".combined_", my_dataype, sep ="")
        do.call("<<-",list(output_object_name, FPKM_matrix))
        cat(
            paste(
                "otuput R dataframe:      ", output_object_name, "\n",
                sep="", collapse=""
            ),
            append=TRUE,
            file=log_file
        )
        cat(
            paste(
                "otuput R dataframe:      ", output_object_name, "\n",
                sep="", collapse=""
            )
        )
    }
    
                    
}


# Fix col_names


# sub to read a list of IDs (adapted from matR: https://github.com/MG-RAST/matR)
readIDs<- function (filename, ...) 
    {
        y <- read.table(filename, colClasses = "character", sep = "\t", 
                        ...)
        if (nrow(y) > 1) {
            if (ncol(y) > 1) {
                if (ncol(y) > 2) {
                    warning("Your list has more than two columns, only the first two are used")
                }
                res <- as.character(y[, 1])
                names(res) <- as.character(y[, 2])
                res <- res[order(res)]
                res
            }
            else {
                res <- as.character(y[, 1])
                res <- res[order(res)]
                res
            }
        }
        else {
            warning("There was just one id in your list?")
            res <- unlist(y[1, ], use.names = FALSE)
            res
        }
    }


# sub to import numerical data
import_data <- function(file_name)
    {
        data.matrix(read.table(file_name, row.names=1, header=TRUE, sep="\t", comment.char="", quote="", check.names=FALSE))
    }

# function to eport data in a format that can be easily read back into R
export_data <- function(data_object, file_name){
    write.table(data_object, file=file_name, sep="\t", col.names = NA, row.names = TRUE, quote = FALSE, eol="\n")
}
    
# sub to import mixed data (numerical and text) - can be useed for data or metadata
import_metadata <- function(group_table){ #, group_column, sample_names){
    metadata_matrix <- as.matrix( # Load the metadata table (same if you use one or all columns)
        read.table(
            file=group_table,row.names=1,header=TRUE,sep="\t",
            colClasses = "character", check.names=FALSE,
            comment.char = "",quote="",fill=TRUE,blank.lines.skip=FALSE
        )
    )
}

  
  
  
  
  
  
