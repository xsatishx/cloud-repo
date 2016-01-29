calculate_pco <- function(
                            file_in,
                            input_dir = "./",
                            input_type = "file",
                            output_PCoA_dir = "./",
                            print_dist = 1,
                            output_DIST_dir = "./",
                            dist_method = "euclidean",
                            headers = 1,
                            debug=FALSE
                            )

{
  # load packages
  suppressPackageStartupMessages(library(matlab))      
  suppressPackageStartupMessages(library(ecodist))
  #suppressPackageStartupMessages(library(Cairo))
  #suppressPackageStartupMessages(library(gplots))

  # define sub functions
  func_usage <- function() {
    writeLines("
     You supplied no arguments

     DESCRIPTION: (calculate_pco.r):
     This script will perform a PCoA analysis on the inputdata
     using the selected distance metric.  Output always produces a
     *.PCoA file that has the normalized eigenvalues (top n lines)
     and eigenvectors (bottom n x m matris, n lines) where n is the
     number of variables (e.g.subsystems), and m the number of
     samples. You can also choose to produce *.DIST files that contain
     the distance matrix used to generate the PCoA.

     USAGE: plot_pca(
                            file_in = no default arg                               # (string)  input data file
                            input_type = \"file\"                                   # (string) file or r_matrix
                            input_dir = \"./\"                                       # (string)  directory(path) of input
                            output_PCoA_dir = \"./\"                                 # (string)  directory(path) for output PCoA file
                            print_dist = 0                                         # (boolean) print the DIST file (distance matrix)
                            output_DIST_dir = \"./\"                                 # (string)  directory(path) for output DIST file 
                            dist_method = \"bray-curtis\"                            # (string)  distance/dissimilarity metric,
                                          (choose from one of the following options)
                                          \"euclidean\" | \"maximum\"     | \"canberra\"    |
                                          \"binary\"    | \"minkowski\"   | \"bray-curtis\" |
                                          \"jacccard\"  | \"mahalanobis\" | \"sorensen\"    |
                                          \"difference\"| \"manhattan\"
                            headers = 0                                            # (booealan) print headers in output PCoA file 
                            )\n"
               )
    stop("calculate_pco stopped\n\n")
  }
  
  find_dist <- function(my_data, dist_method)
    {
      switch(dist_method,
             "euclidean" = dist(my_data, method = "euclidean"), 
             "maximum" = dist(my_data, method = "maximum"),
             "manhattan" = dist(my_data, method = "manhattan"),
             "canberra" = dist(my_data, method = "canberra"),
             "binary" = dist(my_data, method = "binary"),
             "minkowski" = dist(my_data, method = "minkowski"),
             
             #"bray-curtis" = distance(my_data, method = "bray-curtis"), # could not handle large data 1-12-12
             
             "bray-curtis" = bcdist(my_data), # 1-12-12
             #"bray-curtis" = vegdist(my_data, method="bray"), # 1-12-12
             #"bray-curtis" = designdist(my_data, method = "(A+B-2*J)/(A+B)") # 1-12-12
             
             "jaccard" = distance(my_data, method = "jaccard"),
             "mahalanobis" = distance(my_data, method = "mahalanobis"),
             "sorensen" = distance(my_data, method = "sorensen"),
             "difference" = distance(my_data, method = "difference")
             # unifrac
             # weighted_unifrac

             # distance methods with {stats}dist: dist(x, method = "euclidean", diag = FALSE, upper = FALSE, p = 2)
             #      euclidean maximum manhattan canberra binary minkowski

             # distance methods with {ecodist}distance: distance(x, method = "euclidean")
             #      euclidean bray-curtis manhattan mahalanobis jaccard "simple difference" sorensen

             )
    }


  # stop and give the usage if the proper number of arguments is not given
  if ( nargs() == 0 ){
    func_usage()
  }

  # load data

  #writeLines("FILE-IN")
  #writeLines(file_in)
  #input_data_path = gsub(" ", "", paste(input_dir, file_in))
  #writeLines("INPUT-DATA-PATH")
  #writeLines(input_data_path)
  #my_data <<- flipud(rot90(data.matrix(read.table(input_data_path, row.names=1, header=TRUE, sep="\t", comment.char="", quote="")))) # edited on 12-14-12, stop character conversions in column names
  
  if( debug==TRUE ){print("MADE IT HERE 1")}
  
  if ( identical(input_type, "file") ){
    if( debug==TRUE ){print("MADE IT HERE 2a")}
    input_data_path = gsub(" ", "", paste(input_dir, file_in))
    my_data <<- flipud(rot90(data.matrix(read.table(input_data_path, row.names=1, check.names=FALSE, header=TRUE, sep="\t", comment.char="", quote=""))))
  } else if ( identical(input_type, "r_matrix") ) {
    if( debug==TRUE ){print("MADE IT HERE 2.b")}
    my_data <<- flipud(rot90(file_in))
  } else {
    if( debug==TRUE ){print("MADE IT HERE 2.c")}
    stop("input_type value is not valid, must be file or r_matrix")
  }
  
  if( debug==TRUE ){print("MADE IT HERE 3")}
  
  
  num_data_rows = dim(my_data)[1] # substitute 0 for NA's if they exist in the data
  num_data_cols = dim(my_data)[2]
  for (row_num in (1:num_data_rows)){
    for (col_num in (1:num_data_cols)){
      #my_data[row_num, col_num] = as.integer(my_data[row_num, col_num]) # added 1-12-12 to fix "Error in vector("double", length) : vector size cannot be NA ...
      if (is.na(my_data[row_num, col_num])){
        my_data[row_num, col_num] <<- 0
      }
    }
  }

  if( debug==TRUE ){print("MADE IT HERE 4")}
  
  # a bit for naming outputs
  if( identical(input_type, "r_matrix") ){
    file_in.name <- deparse(substitute(file_in))
  } else {
    file_in.name <- file_in
  }
   
  # calculate distance matrix
  dist_matrix <<- find_dist(my_data, dist_method)
  DIST_file_out <- gsub(" ", "", paste(output_DIST_dir, file_in.name, ".", dist_method, ".DIST"))
  if (print_dist > 0) { write_file(file_name = DIST_file_out, data = data.matrix(dist_matrix)) }

  if( debug==TRUE ){print("MADE IT HERE 5")}

  # perform the pco
  my_pco <<- pco(dist_matrix)

  if( debug==TRUE ){print("MADE IT HERE 6")}

  # scale eigen values from 0 to 1, and label them
  eigen_values <<- my_pco$values
  scaled_eigen_values <<- (eigen_values/sum(eigen_values))
  for (i in (1:dim(as.matrix(scaled_eigen_values))[1])) {names(scaled_eigen_values)[i]<<-gsub(" ", "", paste("PCO", i))}
  scaled_eigen_values <<- data.matrix(scaled_eigen_values)
  #for (i in (1:dim(as.matrix(scaled_ev))[1])) dimnames(scaled_ev)[i]<<-gsub(" ", "", paste("PCO", i))

  if( debug==TRUE ){print("MADE IT HERE 7")}

  # label the eigen vectors
  eigen_vectors <<- data.matrix(my_pco$vectors) 
  dimnames(eigen_vectors)[[1]] <<- dimnames(my_data)[[1]]

  if( debug==TRUE ){print("MADE IT HERE 8")}

  # write eigen values and then eigen vectors to file_out
  PCoA_file_out = gsub(" ", "", paste(output_PCoA_dir, file_in.name, ".", dist_method, ".PCoA"))

  if ( headers == 1 ){
    write(file = PCoA_file_out, paste("# file_in    :", file_in.name,
            "\n# dist_method:", dist_method,
            "\n#________________________________",
            "\n# EIGEN VALUES (scaled 0 to 1) >",
            "\n#________________________________"),
          append=FALSE)
    write.table(scaled_eigen_values, file=PCoA_file_out, col.names=FALSE, row.names=TRUE, append = TRUE, sep="\t", eol="\n")
  }else{
    write.table(scaled_eigen_values, file=PCoA_file_out, col.names=FALSE, row.names=TRUE, append = FALSE, sep="\t", eol="\n")
  }
  
  if( debug==TRUE ){print("MADE IT HERE 9")}
  
  if ( headers == 1 ){
    write(file = PCoA_file_out, paste("#________________________________",
            "\n# EIGEN VECTORS >",
            "\n#________________________________"),
          append=TRUE)
  }

  if( debug==TRUE ){print("MADE IT HERE 10")}

  #write.table(eigen_vectors, file=PCoA_file_out, col.names=FALSE, row.names=TRUE, append = TRUE, sep="\t")
  write.table(eigen_vectors, file=PCoA_file_out, col.names=FALSE, row.names=TRUE, append = TRUE, sep="\t", eol="\n")
  
  if( debug==TRUE ){print("MADE IT HERE 11")}
  
}


write_file <- function(file_name, data) {
  write.table(data, file=file_name, col.names=NA, row.names=TRUE, append = FALSE, sep="\t", quote = FALSE, eol="\n")
}

