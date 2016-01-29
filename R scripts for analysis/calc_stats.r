calc_stats <<- function(
                               data_table="HMP_WGS.data.quantile_norm.txt",
                               input_type="file",
                               metadata_table="HMP_WGS.meta_data.tab_delim.txt.enviroment_package.groups.txt",
                               metadata_column=8,
                               stat_test="Kruskal-Wallis", # c("Kruskal-Wallis", "t-test-paired", "Wilcoxon-paired", "t-test-unpaired", "Mann-Whitney-unpaired-Wilcoxon", "ANOVA-one-way")
                               file_out="default",
                               append_group_headers=TRUE,
                               order_by=NULL,
                               order_decreasing=FALSE,
                               ...)
{

# tests ("Kruskal-Wallis", )
  
  require(matR)

  # read in the abundance data
  if( identical(input_type,"file") ){
    data_matrix <- data.matrix(read.table(
                                          data_table,
                                          row.names=1,
                                          header=TRUE,
                                          sep="\t",
                                          comment.char="",
                                          quote="",
                                          check.names=FALSE
                                          )
                               )
  } else if (identical(input_type,"r_table")) {
    data_matrix <- data_table       
  } else {
    stop("data_table value is not valid, must be file or r_table")
  }
  
  csvfile <- function(id) {
    if (id < 10) { 
        paste0(0,0,id,".csv")
    } else if (id < 100) {
        paste0(0,id,".csv")
    } else paste0(id,".csv")
}
  
  
  
  
  # Here, make sure that the data are sorted COLUMNWISE by id
  data_matrix <-  data_matrix[,order(colnames(data_matrix))]
  
  # read in the metadata
  metadata_matrix <- as.matrix(
                               read.table(
                                          metadata_table,
                                          row.names=1,
                                          header=TRUE,
                                          sep="\t",
                                          colClasses = "character",
                                          check.names=FALSE,
                                          comment.char = "",
                                          quote="",
                                          fill=TRUE,
                                          blank.lines.skip=FALSE
                                          )
                               )
  # make sure that the color matrix is sorted (ROWWISE) by id
  metadata_matrix <-  metadata_matrix[order(rownames(metadata_matrix)),]

  # retrieve the selected grouping
  #groups.list <- as.list(metadata_matrix[,metadata_column])
  groups.list <- (metadata_matrix[,metadata_column])
  names(groups.list) <- rownames(metadata_matrix) 
 
# sigtest to perform stats
# place selected stat in variable for use below
# my_stat = "Kruskal-Wallis"
# perform stat tests (uses matR)
  my_stats <- sigtest(data_matrix, groups.list, stat_test)

# Create headers for the data columns
  for (i in 1:dim(data_matrix)[2]){
    if ( append_group_headers==TRUE ){ # append group to data column header if selected
       colnames(data_matrix)[i] <- paste( colnames(data_matrix)[i], "::", (groups.list)[i], sep="" )
    }else{
       colnames(data_matrix)[i] <- colnames(data_matrix)[i]
    }
  }
  for (i in 1:dim(my_stats$mean)[2]){
    colnames(my_stats$mean)[i] <- paste( colnames(my_stats$mean)[i], "::group_mean", sep="" )
  }
  for (i in 1:dim(my_stats$sd)[2]){
    colnames(my_stats$sd)[i] <- paste( colnames(my_stats$sd)[i], "::group_sd", sep="" )
  }
  my_stats.statistic <- as.matrix(my_stats$statistic)
  colnames(my_stats.statistic) <- paste(stat_test, "::stat", sep="")
  my_stats.p <- as.matrix(my_stats$p.value)
  colnames(my_stats.p) <- paste(stat_test, "::p", sep="")
  my_stats.fdr <- as.matrix(p.adjust(my_stats$p.value))
  colnames(my_stats.fdr) <- paste(stat_test, "::fdr", sep="")

# generate a summary object - used to generate the plots, and can be used to create a flat file output
  my_stats.summary <- cbind(data_matrix, my_stats$mean, my_stats$sd, my_stats.statistic, my_stats.p, my_stats.fdr)

# make sure that order_by value, if other than NULL is supplied, is valid
  if (is.null(order_by)){ # use last column by default, or specified column otherwise
    order_by <- ( ncol(my_stats.summary) )
  } else {
    if (is.integer(order_by)){
      if ( order_by > ncol(my_stats.summary) ){
        stop( paste(
                    "\n\norder_by (", order_by,") must be an integer between 1 and ",
                    ncol(my_stats.summary),
                    " (max number of columns in the output)\n\n",
                    sep="",
                    collaps=""
                    ) )
      }
    }
  }

  # order the data by the selected column - placing ordered data in a new object
  my_stats.summary.ordered <- my_stats.summary[ order(my_stats.summary[,order_by], decreasing=order_decreasing), ]


  
  # create name for the output file
  if ( identical(file_out, "default") ){
      file_out = paste(data_table, ".", stat_test, ".", colnames(metadata_matrix)[metadata_column], ".STATS_RESULTS.txt", sep="", collapse="")
  }
  
  # flat file output of the summary file
  write.table(my_stats.summary.ordered, file = file_out, col.names=NA, sep="\t", quote=FALSE)
  
 }
