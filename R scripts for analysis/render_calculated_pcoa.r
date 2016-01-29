# This script uses matR to generate 2 or 3 dimmensional pcoas

# table_in is the abundance array as tab text -- columns are samples(metagenomes) rows are taxa or functions
# color_table and pch_table are tab tables, with each row as a metagenome, each column as a metadata 
# grouping/coloring. These tables are used to define colors and point shapes for the plot
# It is assumed that the order of samples (left to right) in table_in is the same
# as the order (top to bottom) in color_table and pch_table

# basic operation is to produce a color-less pcoa of the input data

# user can also input a table to specify colors
# This table can contain colors (as hex or nominal) or can contain metadata
# This is a PCoA plotting functions that can handle a number of different scenarios
# It always requires a *.PCoA file (like that produce by AMETHST/plot_pco.r)
# It can handle metadata as a table - producing plots for all or selected metadata columns (metadata used to generate colors automatically)
# It can handle an amthst groups file as metadata (metadata used to generate colors automatically)
# It can handle a list of colors - using them to pain the points directly
# It can handle the case when there is no metadata - painting all of points the same
# users can also specify a pch table to control the shape of plotted icons (this feature may not be ready yet)
# CHANGE OVER v12 - you can select which samples (rows in the eigen vector matrix) with "plot_samples" variable

render_calcualted_pcoa <- function(
                            PCoA_in="", # annotation abundance table (raw or normalized values)
                            image_out="default",
                            figure_main ="principal coordinates",
                            components=c(1,2,3), # R formated string telling which coordinates to plot, and how many (2 or 3 coordinates)
                            plot_samples="all", # "all" or a vector of samples (rows) to plot
                            label_points=FALSE, # default is off
                            metadata_table=NA, # matrix that contains colors or metadata that can be used to generate colors
                            metadata_column_index=1, # column of the color matrix to color the pcoa (colors for the points in the matrix) -- rows = samples, columns = colorings
                            amethst_groups=NA,        
                            color_list=NA, # use explicit list of colors - trumps table if both are supplied
                            pch_behavior="default", #  "default" use pch_default for all; "auto" automatically assign pch from table; "asis" use integer values in the column
                            pch_default=16,
                            pch_table="default",
                            pch_column=1,
                            pch_labels="default",
                            image_width_in=22,
                            image_height_in=17,
                            image_res_dpi=300,
                            width_legend = 0.2, # fraction of width used by legend
                            width_figure = 0.8, # fraction of width used by figure
                            title_cex = "default", # cex for the title of title of the figure, "default" for auto scaling
                            legend_cex = "default", # cex for the legend, default for auto scaling
                            figure_cex = 2, # cex for the figure
                            figure_symbol_cex=2,
                            vert_line="dotted", # "blank", "solid", "dashed", "dotted", "dotdash", "longdash", or "twodash"
                            bar_cex = "default",
                            bar_vert_adjust = 0,  
                            use_all_metadata_columns=FALSE, # option to overide color_column -- if true, plots are generate for all of the metadata columns
                            debug=FALSE
                            )
  
{
  
  require(matR)
  require(scatterplot3d)
  
  argument_list <- is.na(c(metadata_table,amethst_groups,color_list)) # check that incompatible options were not selected
  argument_test = length(argument_list[argument_list==TRUE])

  if(debug==TRUE){print(paste("argument_test:", argument_test))}
  if(debug==TRUE){print(paste("length argument_test == TRUE:", length(argument_test==TRUE)))}
  
  #if ( 3 - length(subset(argument_test, argument_test==TRUE) ) > 1){
  if ( argument_test != 2){
    stop(
         paste(
               "\n\nOnly one of these can have a non NA value:\n",
               "     metadata_table: ", metadata_table,"\n",
               "     amethst_groups: ", amethst_groups, "\n",
               "     color_list    : ", color_list, "\n\n",
               sep="", collapse=""
               )
         )
  }

  
  ######################
  ######## MAIN ########
  ######################

  # load data - everything is sorted by id
  my_data <- load_pcoa_data(PCoA_in) # import PCoA data from *.PCoA file --- this is always done

  # load data - everything is sorted by id
  eigen_values <- my_data$eigen_values
  eigen_vectors <- my_data$eigen_vectors
  # get the sample names for ordering data, colors, and pch later
  sample_names <- rownames(eigen_vectors)
  sample_names <- gsub("\"", "", sample_names)
  
  # make sure everything is sorted by id
  if(debug==TRUE){sample_names.test1<<-sample_names}
  
  if(debug==TRUE){sample_names.test2<<-sample_names}
  ##eigen_vectors <- eigen_vectors[ order(sample_names), ]
  ##eigen_values <- eigen_values[ order(sample_names) ]
  ##sample_names <- sample_names[ order(sample_names) ]
  #eigen_vectors <- eigen_vectors[ order(eigen_values), ]
  #eigen_values <- eigen_values[ order(eigen_values) ]
  #sample_names <- sample_names[ order(eigen_values) ]
  
  if(debug==TRUE){
    eigen_vectors.test<<-eigen_vectors
    eigen_values.test<<-eigen_values  
  }
  
  #eigen_vectors <- eigen_vectors[ order(rownames(my_data$eigen_vectors)), ]
  #eigen_values <- eigen_values[ order(rownames(my_data$eigen_vectors)) ] # order will reflect id
  
  num_samples <- ncol(my_data$eigen_vectors)

  
  #if ( debug == TRUE ){ print(paste("num_samples: ", num_samples)) } 

  if(debug==TRUE){print("made it here 1")}

  # CHECK FOR LEVELS OF PCH AS FACTOR _ DEFINE TWO TYPES OF LEGENDS
  # load pch - handles table or integer(pch_default)




  
  # somwhere here logic for three pch options
  #  pch_behavior = c("default", "auto", "asis")


  if(debug==TRUE){print("ABOUT TO LOAD PCH")}
  pch_object <- load_pch(pch_behavior, pch_default, pch_table, pch_column, pch_labels, sample_names, num_samples, rownames(my_data$eigen_vectors), debug) 

  if(debug==TRUE){ pch_object.test <<- pch_object}
#return(list( "plot_pch_values"=plot_pch_values, "pch.levels"=pch_levels, "pch.labels"=pch_labels) )
  
  plot_pch <- pch_object$plot_pch_vector
  pch_levels <- pch_object$pch_levels
  pch_labels <- pch_object$pch_labels

  if(debug==TRUE){
    print(paste("first_data_sample:", sample_names[1]))
    print(paste("last_data_sample :", sample_names[length(sample_names)]))
    print(paste("first_pch_sample :", names(plot_pch)[1]))
    print(paste("first_pch_sample :", names(plot_pch)[length(plot_pch)]))
    print(paste("first_pch_value  :", (plot_pch)[1]))
    print(paste("last_pch_value  :", (plot_pch)[length(plot_pch)]))
  }
  

  if(debug==TRUE){print("made it here 2")}

                                        #if(debug==TRUE){print(paste("main.pch_levels", pch_levels))}
  #if(debug==TRUE){print(paste("main.pch_labels", pch_labels))}
 
  
  
  if(debug==TRUE){print(paste("2.pch_levels", pch_levels))}
  if(debug==TRUE){print(paste("2.pch_labels", pch_labels))}

  
  #####################################################################################
  ########## PLOT WITH NO METADATA OR COLORS SPECIFIED (all point same color) #########
  #####################################################################################
  if ( argument_test==3 ){ # create names for the output files

    if(debug==TRUE){print("Rendering without metadata")}
    
    if ( identical(image_out, "default") ){
      image_out = paste( PCoA_in,".NO_COLOR.PCoA.png", sep="", collapse="" )
      figure_main = paste( PCoA_in, ".NO_COLOR.PCoA", sep="", collapse="" )
    }else{
      image_out = paste(image_out, ".png", sep="", collapse="")
      figure_main = paste( image_out,".PCoA", sep="", collapse="")
    }
    
    column_levels <- "data" # assign necessary defaults for plotting
    num_levels <- 1
    color_levels <- 1
    ncol.color_matrix <- 1
    pcoa_colors <- "black"   

    create_plot( # generate the plot
                PCoA_in,
                ncol.color_matrix,
                eigen_values, eigen_vectors, components, plot_samples,
                column_levels, num_levels, color_levels, pcoa_colors, plot_pch, pch_labels, pch_levels,
                image_out,figure_main,
                image_width_in, image_height_in, image_res_dpi,
                width_legend, width_figure,
                title_cex, legend_cex, figure_cex, figure_symbol_cex, bar_cex, bar_vert_adjust, label_points, vert_line, debug
                )
  }
  #####################################################################################
  #####################################################################################


  
  #####################################################################################
  ########### PLOT WITH AMETHST GROUPS (colors generated by load_metadata) ############
  #####################################################################################
  if ( identical( is.na(amethst_groups), FALSE ) ){ # create names for the output files

    if(debug==TRUE){print("Rendering with amethst_groups")}
    
    if ( identical(image_out, "default") ){
      image_out = paste( PCoA_in,".AMETHST_GROUPS.PCoA.png", sep="", collapse="" )
      figure_main = paste( PCoA_in, ".AMETHST_GROUPS.PCoA", sep="", collapse="" )
    }else{
      image_out = paste(image_out, ".png", sep="", collapse="")
      figure_main = paste( image_out,".PCoA", sep="", collapse="")
    }

    con_grp <- file(amethst_groups) # get metadata and generate colors from amethst groups file
    open(con_grp)
    line_count <- 1
    groups.list <- vector(mode="character")
    while ( length(my_line <- readLines(con_grp,n = 1, warn = FALSE)) > 0) {
      new_line <- my_line
      split_line <- unlist(strsplit(my_line, split=","))
      split_line.list <- rep(line_count, length(split_line))
      names(split_line.list) <- split_line
      groups.list <- c(groups.list, split_line.list)
      line_count <- line_count + 1
    }
    close(con_grp)
    if ( length(groups.list) != length(unique(names(groups.list))) ){
      stop("One or more groups have redundant entries - this is not allowed for coloring the PCoA")
    }
    metadata_column <- matrix(groups.list, ncol=1)

    suppressWarnings( numericCheck <- as.numeric(metadata_column) ) # check to see if metadata are numeric, and sort accordingly
    if( is.na(numericCheck[1])==FALSE ){
      column_name = colnames(metadata_column)[1]
      row_names = rownames(metadata_column)
      metadata_column <- matrix(numericCheck, ncol=1)
      colnames(metadata_column) <- column_name
      rownames(metadata_column) <- row_names
    }
    #sample_names
    metadata_column <- metadata_column[ sample_names,,drop=FALSE ] # order the metadata by sample 1d
    #metadata_column <- metadata_column[ order(rownames(metadata_column)),,drop=FALSE ] # order the metadata by value
    color_column <- create_colors(metadata_column, color_mode = "auto")

    column_levels <- levels(as.factor(as.matrix(metadata_column))) 
    num_levels <- length(column_levels)
    color_levels <- col.wheel(num_levels)
    ncol.color_matrix <- 1
    
    colnames(metadata_column) <- "amethst_metadata"
    column_levels <- column_levels[ order(column_levels) ] # NEW (order by levels values)
    color_levels <- color_levels[ order(column_levels) ] # NEW (order by levels values)

    pcoa_colors <- as.character(color_column[,1]) # convert colors to a list after they've been used to sort the eigen vectors
    
    create_plot( # generate the plot
                PCoA_in,
                ncol.color_matrix,
                eigen_values, eigen_vectors, components, plot_samples,
                column_levels, num_levels, color_levels, pcoa_colors, plot_pch, pch_labels, pch_levels,
                image_out,figure_main,
                image_width_in, image_height_in, image_res_dpi,
                width_legend, width_figure,
                title_cex, legend_cex, figure_cex, figure_symbol_cex, bar_cex, bar_vert_adjust, label_points, vert_line, debug
                )
    
  }
  #####################################################################################
  #####################################################################################

  if(debug==TRUE){print("made it here 3")}

  if(debug==TRUE){print(paste("3.pch_levels", pch_levels))}
  if(debug==TRUE){print(paste("3.pch_labels", pch_labels))}
  
  #####################################################################################
  ############ PLOT WITH LIST OF COLORS (colors generated by load_metadata) ###########
  #####################################################################################
  if ( identical( is.na(color_list), FALSE ) ){ # create names for the output files

    if(debug==TRUE){print("Rendering with color_list")}
    
    if ( identical(image_out, "default") ){
      image_out = paste( PCoA_in,".color_List.PCoA.png", sep="", collapse="" )
      figure_main = paste( PCoA_in, ".color_list.PCoA", sep="", collapse="" )
    }else{
      image_out = paste(image_out, ".png", sep="", collapse="")
      figure_main = paste( image_out,".PCoA", sep="", collapse="")
    }

    column_levels <- levels(as.factor(as.matrix(color_list))) # get colors directly from list of colors
    num_levels <- length(column_levels)
    color_levels <- col.wheel(num_levels)
    #color_levels <- col.wheel(num_levels)
    ncol.color_matrix <- 1
    pcoa_colors <- color_list
    
    create_plot( # generate the plot
                PCoA_in,
                ncol.color_matrix,
                eigen_values, eigen_vectors, components, plot_samples,
                column_levels, num_levels, color_levels, pcoa_colors, plot_pch, pch_labels, pch_levels,
                image_out,figure_main,
                image_width_in, image_height_in, image_res_dpi,
                width_legend, width_figure,
                title_cex, legend_cex, figure_cex, figure_symbol_cex, bar_cex, bar_vert_adjust, label_points, vert_line, debug
                )
  }
  #####################################################################################
  #####################################################################################

  
  if(debug==TRUE){print("made it here 4")}

  if(debug==TRUE){print(paste("4.pch_levels", pch_levels))}
  if(debug==TRUE){print(paste("4.pch_labels", pch_labels))}
  
  #####################################################################################
  ########### PLOT WITH METADATA_TABLE (colors produced from color_matrix) ############
  ######## CAN HANDLE PLOTTING ALL OR A SINGLE SELECTED METADATA TABLE COLUMN #########
  #####################################################################################
  if ( identical( is.na(metadata_table), FALSE ) ){

    metadata_matrix <- as.matrix( # Load the metadata table (same if you use one or all columns)
                              read.table(
                                         file=metadata_table,row.names=1,header=TRUE,sep="\t",
                                         colClasses = "character", check.names=FALSE,
                                         comment.char = "",quote="",fill=TRUE,blank.lines.skip=FALSE
                                         )
                              )   
    #metadata_matrix <- metadata_matrix[ order(rownames(metadata_matrix)),,drop=FALSE ]  # make sure that the metadata matrix is sorted (ROWWISE) by id
    metadata_matrix <- metadata_matrix[ sample_names,,drop=FALSE ]  # make sure that the metadata matrix is sorted (ROWWISE) by id
    
    if(debug==TRUE){print("made it here 5")}
    
    if ( use_all_metadata_columns==TRUE ){ # AUTOGENERATE PLOTS FOR ALL COLUMNS IN THE METADATA FILE - ONE PLOT PER METADATA COLUMN

      if(debug==TRUE){print("Rendering with metadata_matrix, all columns")}
      
      ncol.color_matrix <- ncol( metadata_matrix) # get then number of columns in the metadata data file = number of plots
      for (i in 1:ncol.color_matrix){ # loop to process through all columns

        if(debug==TRUE){print("made it here 6")}
        
        metadata_column <- metadata_matrix[ ,i,drop=FALSE ] # get column i from the metadata matrix
        if(debug==TRUE){ test1<<-metadata_column }

        if(debug==TRUE){print("made it here 7")}
        if(debug==TRUE){print(paste("7.pch_levels", pch_levels))}
        if(debug==TRUE){print(paste("7.pch_labels", pch_labels))}
       
        
        image_out = paste(PCoA_in,".", colnames(metadata_column), ".pcoa.png", sep="", collapse="") # generate name for plot file
        figure_main = paste( PCoA_in,".", colnames(metadata_column),".PCoA", sep="", collapse="") # generate title for the plot
        
        suppressWarnings( numericCheck <- as.numeric(metadata_column) ) # check to see if metadata are numeric, and sort accordingly
        if( is.na(numericCheck[1])==FALSE ){
          column_name = colnames(metadata_column)[1]
          row_names = rownames(metadata_column)
          metadata_column <- matrix(numericCheck, ncol=1)
          colnames(metadata_column) <- column_name
          rownames(metadata_column) <- row_names
        }

        if(debug==TRUE){print("made it here 8")}
        if(debug==TRUE){print(paste("8.pch_levels", pch_levels))}
        if(debug==TRUE){print(paste("8.pch_labels", pch_labels))}
       

        
        if(debug==TRUE){ test2<<-metadata_column }
        
        metadata_column <- metadata_column[ sample_names,,drop=FALSE ] # order the metadata by value
        #metadata_column <- metadata_column[ order(rownames(metadata_column)),,drop=FALSE ] # order the metadata by value
        if(debug==TRUE){ test3<<-metadata_column }
        
        color_column <- create_colors(metadata_column, color_mode = "auto") # set parameters for plotting
        ncol.color_matrix <- 1 
        column_factors <- as.factor(metadata_column) 
        column_levels <- levels(as.factor(metadata_column))
        num_levels <- length(column_levels)
        color_levels <- col.wheel(num_levels)

        rownames(eigen_vectors) <- gsub("\"", "", rownames(eigen_vectors)) # make sure that vectors are sorted identically to the colors
        eigen_vectors <- eigen_vectors[ rownames(color_column), ]

        if(debug==TRUE){print("made it here 9")}
        if(debug==TRUE){print(paste("9.pch_levels", pch_levels))}
        if(debug==TRUE){print(paste("9.pch_labels", pch_labels))}
       
        
        #plot_pch <- plot_pch[ rownames(color_column) ]# make sure pch is sorted identically to colors
        
        pcoa_colors <- as.character(color_column[,1]) # convert colors to a list after they've been used to sort the eigen vectors
  
        if(debug==TRUE){
          test.color_column <<- color_column
          test.pcoa_colors <<- pcoa_colors
        }


        if(debug==TRUE){print("made it here 10")}
        if(debug==TRUE){print(paste("10.pch_levels", pch_levels))}
        if(debug==TRUE){print(paste("10.pch_labels", pch_labels))}
       

        
        create_plot( # generate the plot
                    PCoA_in,
                    ncol.color_matrix,
                    eigen_values, eigen_vectors, components, plot_samples,
                    column_levels, num_levels, color_levels, pcoa_colors, plot_pch, pch_labels, pch_levels,
                    image_out,figure_main,
                    image_width_in, image_height_in, image_res_dpi,
                    width_legend, width_figure,
                    title_cex, legend_cex, figure_cex, figure_symbol_cex, bar_cex, bar_vert_adjust, label_points, vert_line, debug
                    )        
      }
      
      
    }else if ( use_all_metadata_columns==FALSE ){ # ONLY CREATE A PLOT FOR THE SELECTED COLUMN IN THE METADATA FILE

      if(debug==TRUE){print("Rendering with metadata_matrix, single column")}
      
      metadata_column <- metadata_matrix[ ,metadata_column_index, drop=FALSE ] # get column i from the metadata matrix

      # name single extracted column correctly
      if(debug==TRUE){test.metadata_matrix <<- metadata_matrix}

      metadata_column_names <- colnames(metadata_matrix)
      if(debug==TRUE){print("LINE 430")}

      if(debug==TRUE){print(paste("metadata_column_index:", metadata_column_index))}
      if( is.integer(metadata_column_index)==TRUE){
        column_name <- colnames(metadata_matrix)[metadata_column_index]
        if(debug==TRUE){print(paste("column_name  (is int):", column_name))}  
      }else{
        column_name <- metadata_column_index
        if(debug==TRUE){print(paste("column_name (not int):", column_name))}
      }

      if(debug==TRUE){ test.metadata_column <<- metadata_column }
      
      if ( identical(image_out, "default") ){
        image_out = paste(PCoA_in,".", column_name, ".pcoa.png", sep="", collapse="") # generate name for plot file
        figure_main = paste( PCoA_in,".", column_name,".PCoA", sep="", collapse="") # generate title for the plot
        #image_out = paste(PCoA_in,".", colnames(metadata_column), ".pcoa.png", sep="", collapse="") # generate name for plot file
        #figure_main = paste( PCoA_in,".", colnames(metadata_column),".PCoA", sep="", collapse="") # generate title for the plot
      }else{
        image_out = paste(image_out, ".png", sep="", collapse="")
        figure_main = paste( image_out,".PCoA", sep="", collapse="")
      }
      
      suppressWarnings( numericCheck <- as.numeric(metadata_column) ) # check to see if metadata are numeric, and sort accordingly
      if( is.na(numericCheck[1])==FALSE ){
        #column_name = colnames(metadata_column)[1]
        row_names = rownames(metadata_column)
        metadata_column <- matrix(numericCheck, ncol=1)
        colnames(metadata_column) <- column_name
        rownames(metadata_column) <- row_names
      }

      if(debug==TRUE){ test2<<-metadata_column }
      
      #metadata_column <- metadata_column[ order(metadata_column),,drop=FALSE ] # order the metadata by value
      metadata_column <- metadata_column[ sample_names,,drop=FALSE ] # order the metadata by value
      if(debug==TRUE){ test3<<-metadata_column }
      
      color_column <- create_colors(metadata_column, color_mode = "auto") # set parameters for plotting
      ncol.color_matrix <- 1 
      column_factors <- as.factor(metadata_column) 
      column_levels <- levels(as.factor(metadata_column))
      num_levels <- length(column_levels)
      color_levels <- col.wheel(num_levels)
      rownames(eigen_vectors) <- gsub("\"", "", rownames(eigen_vectors)) # make sure that vectors are sorted identically to the colors
      eigen_vectors <- eigen_vectors[ rownames(color_column), ]        
      pcoa_colors <- as.character(color_column[,1]) # convert colors to a list after they've been used to sort the eigen vectors
      create_plot( # generate the plot
                  PCoA_in,
                  ncol.color_matrix,
                  eigen_values, eigen_vectors, components, plot_samples,
                  column_levels, num_levels, color_levels, pcoa_colors, plot_pch, pch_labels, pch_levels,
                  image_out,figure_main,
                  image_width_in, image_height_in, image_res_dpi,
                  width_legend, width_figure,
                  title_cex, legend_cex, figure_cex, figure_symbol_cex, bar_cex, bar_vert_adjust, label_points, vert_line, debug
                  )
      
    }else{
      stop(paste("invalid value for use_all_metadata_columns(", use_all_metadata_columns,") was specified, please try again", sep="", collapse=""))
    }
  }
  
}
#####################################################################################

######################
###### END MAIN ######
######################
  
######################
######## SUBS ########
######################

#######################
######## SUB(1): Function to import the data from a pre-calculated PCoA
######################
load_pcoa_data <- function(PCoA_in){

  #print("loading PCoA")
  
  con_1 <- file(PCoA_in)
  con_2 <- file(PCoA_in)
  # read through the first time to get the number of samples
  open(con_1);
  num_values <- 0
  data_type = "NA"
  while ( length(my_line <- readLines(con_1,n = 1, warn = FALSE)) > 0) {
    if ( length( grep("PCO", my_line) ) == 1  ){
      num_values <- num_values + 1
    }
  }
  close(con_1)
  # create object for values
  eigen_values <- matrix("", num_values, 1)
  dimnames(eigen_values)[[1]] <- 1:num_values
  eigen_vectors <- matrix("", num_values, num_values)
  dimnames(eigen_vectors)[[1]] <- 1:num_values
  # read through a second time to populate the R objects
  value_index <- 1
  vector_index <- 1
  open(con_2)
  current.line <- 1
  data_type = "NA"
  while ( length(my_line <- readLines(con_2,n = 1, warn = FALSE)) > 0) {
    if ( length( grep("#", my_line) ) == 1  ){
      if ( length( grep("EIGEN VALUES", my_line) ) == 1  ){
        data_type="eigen_values"
      } else if ( length( grep("EIGEN VECTORS", my_line) ) == 1 ){
        data_type="eigen_vectors"
      }
    }else{
      split_line <- noquote(strsplit(my_line, split="\t"))
      if ( identical(data_type, "eigen_values")==TRUE ){
        dimnames(eigen_values)[[1]][value_index] <- noquote(split_line[[1]][1])
        eigen_values[value_index,1] <- noquote(split_line[[1]][2])       
        value_index <- value_index + 1
      }
      if ( identical(data_type, "eigen_vectors")==TRUE ){
        dimnames(eigen_vectors)[[1]][vector_index] <- noquote(split_line[[1]][1])
        for (i in 2:(num_values+1)){
          eigen_vectors[vector_index, (i-1)] <- as.numeric(noquote(split_line[[1]][i]))
        }
        vector_index <- vector_index + 1
      }
    }
  }
  close(con_2)
  # finish labeling of data objects
  dimnames(eigen_values)[[2]] <- "EigenValues"
  dimnames(eigen_vectors)[[2]] <- dimnames(eigen_values)[[1]]
  class(eigen_values) <- "numeric"
  class(eigen_vectors) <- "numeric"
  # write imported data to global objects
  #eigen_values <<- eigen_values
  #eigen_vectors <<- eigen_vectors
  return(list(eigen_values=eigen_values, eigen_vectors=eigen_vectors))
  
}
######################
######################
######################


## ######################
## # SUB(2): Function to load the metadata/ generate or import colors for the points
## ######################
## #load_metadata <- function(metadata_table, metadata_column, color_list, amethst_groups){
## load_metadata <- function(metadata_table, ...){
  
##   if ( identical( is.na(metadata_table), FALSE ) ){ # HANDLE METADATA TABLE for generating colors
##     metadata_matrix <- as.matrix( # Import metadata table, use it to generate colors
##                               read.table(
##                                          file=metadata_table,row.names=1,header=TRUE,sep="\t",
##                                          colClasses = "character", check.names=FALSE,
##                                          comment.char = "",quote="",fill=TRUE,blank.lines.skip=FALSE
##                                          )
##                               )   
##     metadata_matrix <- metadata_matrix[ order(rownames(metadata_matrix)),,drop=FALSE ]  # make sure that the metadata matrix is sorted (ROWWISE) by id
##     return(metadata_matrix)
    
##   } else if ( identical( is.na(amethst_groups), FALSE ) ){ # HANDLE AMETHST GROUPS for generating colors

##     con_grp <- file(amethst_groups)
##     open(con_grp)
##     line_count <- 1
##     groups.list <- vector(mode="character")
##     while ( length(my_line <- readLines(con_grp,n = 1, warn = FALSE)) > 0) {
##       new_line <- my_line
##       split_line <- unlist(strsplit(my_line, split=","))
##       split_line.list <- rep(line_count, length(split_line))
##       names(split_line.list) <- split_line
##       groups.list <- c(groups.list, split_line.list)
##       line_count <- line_count + 1
##     }
##     close(con_grp)
##     if ( length(groups.list) != length(unique(names(groups.list))) ){
##       stop("One or more groups have redundant entries - this is not allowed for coloring the PCoA")
##     }
##     metadata_matrix <- matrix(groups.list, ncol=1)
##     metadata_matrix <- metadata_matrix[ order(metadata_matrix),,drop=FALSE ] # order by metadata value
##     colnames(metadata_matrix) <- "amethst_metadata"
##     #column_levels <<- levels(metadata_column)
##     #num_levels <<- length(column_levels)
##     #color_levels <<- col.wheel(num_levels)
##     #ncol.color_matrix <<- 1
##     #pcoa_colors <<- color_list
##     return(metadata_matrix)
    
##   }else if ( identical( is.na(color_list), FALSE ) ){ # HANDLE COLOR LIST; use list of color if it is supplied
    
##     column_levels <<- levels(as.factor(as.matrix(color_list)))
##     num_levels <<- length(column_levels)
##     color_levels <<- col.wheel(num_levels)
##     ncol.color_matrix <<- 1
##     pcoa_colors <<- color_list
   
##   }else{ # HANDLE NO INPUT METADATA OR COLORS; use a default of black if no table or list is supplied
                                     
##     column_levels <<- "data"
##     num_levels <<- 1
##     color_levels <<- 1
##     ncol.color_matrix <<- 1
##     pcoa_colors <<- "black"    

##   }
## }
## ######################
## ######################

  
######################
# SUB(3): Function to import the pch information for the points # load pch matrix if one is specified
######################
load_pch <- function(pch_behavior, pch_default, pch_table, pch_column, pch_labels, sample_names, num_samples, my_names, debug){

  
#pch_behavior=c("default", "auto", "asis")
  #my_names <- gsub("\"", "", my_names)
  
  if(debug==TRUE){print(rep("LOADING PCH",50))}
  
  if(debug==TRUE){print(paste("class(my_names): ", class(my_names), sep=""))}

  if(debug==TRUE){print(paste("(preloop) PCH_BEHAVIOR: ", pch_behavior))}
  
  if( identical(pch_behavior,"default") ){

    if(debug==TRUE){print(paste("(in loop) PCH_BEHAVIOR: ", pch_behavior))}
    
    my_names <- gsub("\"", "", my_names)
    pch_matrix <- data.matrix(matrix(rep(pch_default, num_samples), ncol=1))
    #pch_matrix <- pch_matrix[order(rownames(pch_matrix)),]
    #pch_matrix <- pch_matrix[ order(sample_names), ]
    plot_pch <- pch_matrix[ , 1, drop=FALSE]
    plot_pch_vector <- as.vector(plot_pch)
    pch_labels <- levels(as.factor(plot_pch_vector))
    #names(plot_pch_vector) <- my_names
    pch_levels <- pch_labels
    pch_labels <- pch_labels
    if(debug==TRUE){
      print(paste("plot_pch_vector: ", class(plot_pch_vector)))
      print(plot_pch_vector)
      plot_pch_vector.test <<- plot_pch_vector
    }
   
  }else if ( identical(pch_behavior,"asis") ){

    if(debug==TRUE){print(paste("(in loop) PCH_BEHAVIOR: ", pch_behavior))}
    
    pch_matrix <- data.matrix(read.table(pch_table, row.names=1, header=TRUE, sep="\t", comment.char="", quote="", check.names=FALSE))

    #my_names <- gsub("\"", "", my_names)


    #pch_matrix <- pch_matrix[ order(rownames(pch_matrix)), ]
    if(debug==TRUE){pch_matrix.test1<<-pch_matrix}
    pch_matrix <- pch_matrix[ sample_names, ]
    if(debug==TRUE){pch_matrix.test2<<-pch_matrix}
    plot_pch <- pch_matrix[ , pch_column, drop=FALSE ]
    #plot_pch <- pch_matrix[ order(pch_column), drop=FALSE]
    plot_pch_vector <- as.vector(plot_pch)
    names(plot_pch_vector) <- sample_names
    pch_levels <- levels(as.factor(plot_pch_vector))
    if(debug==TRUE){pch_levels.test<<-pch_levels}
    #pch_labels <- pch_labels
    if(debug==TRUE){pch_labels.test<<-pch_labels}
    if(debug==TRUE){plot_pch_vector.test<<-plot_pch_vector}
    if(debug==TRUE){print(paste("ASIS.pch_labels", pch_labels))}
    if(debug==TRUE){print(paste("ASIS.pch_levels", pch_levels))}
    
    if( length(pch_levels)!=length(pch_labels) ){ stop("you have (", length(pch_labels), ") labels in pch_labels for (", length(pch_levels),") unique factor levels") }
   
    if(debug==TRUE){
      print(paste("plot_pch_vector class: ", class(plot_pch_vector)))
      print(paste("plot_pch_vector: ",plot_pch_vector))
      plot_pch_vector.test <<- plot_pch_vector
    }
    
  }else if( identical(pch_behavior, "auto") ){

    if(debug==TRUE){print(paste("(in loop) PCH_BEHAVIOR: ", pch_behavior))}

    # pch_matrix <- data.matrix(read.table(pch_table, row.names=1, header=TRUE, sep="\t", comment.char="", quote="", check.names=FALSE))

      pch_matrix <- as.matrix( # Load the metadata table (same if you use one or all columns)
                              read.table(
                                         file=pch_table,row.names=1,header=TRUE,sep="\t",
                                         colClasses = "character", check.names=FALSE,
                                         comment.char = "",quote="",fill=TRUE,blank.lines.skip=FALSE
                                         )
                              )   

    if(debug==TRUE){ pch_matrix.test <<- pch_matrix }
    pch_temp <- create_pch(pch_matrix, pch_column, sample_names, debug)
    plot_pch_vector <- as.vector(pch_temp$my_pch)
    pch_levels <- pch_temp$pch_levels
    pch_labels <- names(pch_levels)  
    
  }else{
    stop(paste("( ",pch_behavior, " )", "is an invalid pch_behavior option value - try \"default\", \"asis\", or \"auto\""))
  }
                                    
  if( length(plot_pch_vector) != num_samples ){
    stop(paste("The number of samples in pch column ( ", length(plot_pch), " ) does not match number of samples ( ", num_samples, " )"))
  }

  return(list( "plot_pch_vector"=plot_pch_vector, "pch_levels"=pch_levels, "pch_labels"=pch_labels) )
}
######################
######################


######################
# SUB(4): Sub to provide scaling for title and legened cex
######################
calculate_cex <- function(my_labels, my_pin, my_mai, reduce_by=0.30, debug){
  
  # get figure width and height from pin
  my_width <- my_pin[1]
  my_height <- my_pin[2]
  
  # get margine from mai
  my_margin_bottom <- my_mai[1]
  my_margin_left <- my_mai[2]
  my_margin_top <- my_mai[3]
  my_margin_right <- my_mai[4]
  
  #if(debug==TRUE){
  #  print(paste("my_pin: ", my_pin, sep=""))
  #  print(paste("my_mai: ", my_mai, sep=""))
  #}
  
  # find the longest label (in inches), and figure out the maximum amount of length scaling that is possible
  label_width_max <- 0
  for (i in 1:length(my_labels)){  
    label_width <- strwidth(my_labels[i],'inches')
    if ( label_width > label_width_max){ label_width_max<-label_width  }
  }
  label_width_scale_max <- ( my_width - ( my_margin_right + my_margin_left ) )/label_width_max
  ## if(debug==TRUE){ 
  ##                 cat(paste("\n", "my_width: ", my_width, "\n", 
  ##                           "label_width_max: ", label_width_max, "\n",
  ##                           "label_width_scale_max: ", label_width_scale_max, "\n",
  ##                           sep=""))  
  ##                 }
  
  
  # find the number of labels, and figure out the maximum height scaling that is possible
  label_height_max <- 0
  for (i in 1:length(my_labels)){  
    label_height <- strheight(my_labels[i],'inches')
    if ( label_height > label_height_max){ label_height_max<-label_height  }
  }
  adjusted.label_height_max <- ( label_height_max + label_height_max*0.4 ) # fudge factor for vertical space between legend entries
  label_height_scale_max <- ( my_height - ( my_margin_top + my_margin_bottom ) ) / ( adjusted.label_height_max*length(my_labels) )
  ## if(debug==TRUE){ 
  ##                 cat(paste("\n", "my_height: ", my_height, "\n", 
  ##                           "label_height_max: ", label_height_max, "\n", 
  ##                           "length(my_labels): ", length(my_labels), "\n",
  ##                           "label_height_scale_max: ", label_height_scale_max, "\n",
  ##                           sep="" )) 
  ##                 }
  
  # max possible scale is the smaller of the two 
  scale_max <- min(label_width_scale_max, label_height_scale_max)
  # adjust by buffer
  #scale_max <- scale_max*(100-buffer/100) 
  adjusted_scale_max <- ( scale_max * (1-reduce_by) )
  #if(debug==TRUE){ print(cat("\n", "adjusted_scale_max: ", adjusted_scale_max, "\n", sep=""))  }
  return(adjusted_scale_max)
  
}

######################
######################

######################
# SUB(5): Fetch par values of the current frame - use to scale cex
######################
par_fetch <- function(){
    my_pin<-par('pin')
    my_mai<-par('mai')
    my_mar<-par('mar')
    return(list("my_pin"=my_pin, "my_mai"=my_mai, "my_mar"=my_mar))    
}
######################
######################





######################
# SUB(6): Workhorse function that creates the plot
######################
create_plot <- function(
                        PCoA_in,
                        ncol.color_matrix,
                        eigen_values, eigen_vectors, components, plot_samples,
                        column_levels, num_levels, color_levels, pcoa_colors, plot_pch, pch_labels, pch_levels,
                        image_out,figure_main,
                        image_width_in, image_height_in, image_res_dpi,
                        width_legend, width_figure,
                        title_cex, legend_cex, figure_cex, figure_symbol_cex, bar_cex, bar_vert_adjust, label_points, vert_line, debug
                        ){

  if(debug==TRUE){print("creating figure")}
  
  png( # initialize the png 
      filename = image_out,
      width = image_width_in,
      height = image_height_in,
      res = image_res_dpi,
      units = 'in'
      )

  # LAYOUT CREATION HAS TO BE DICTATED BY PCH TO A DEGREE _ NUM LEVELS (1 or more)
  # Determine num levels for pch
  num_pch <- length(levels(as.factor(plot_pch)))
  # CREATE THE LAYOUT
  if ( num_pch > 1 ){
    my_layout <- layout( matrix(c(1,1,2,3,4,3,5,5), 4, 2, byrow=TRUE ), widths=c(0.5,0.5), heights=c(0.1,0.8,0.3,0.1) )
  }else{
    my_layout <- layout(  matrix(c(1,1,2,3,4,4), 3, 2, byrow=TRUE ), widths=c(width_legend,width_figure), heights=c(0.1,0.8,0.1) )
    # requires an extra plot.new() to skip over pch legend (frame 4 or none )
  }
                                        # my_layout <- layout(  matrix(c(1,1,2,3,4,3,5,5), 4, 2, byrow=TRUE ), widths=c(width_legend,width_figure), heights=c(0.1,0.4,0.8,0.4,0.1) ) # for auto pch legend
  layout.show(my_layout)

  # PLOT THE TITLE (layout frame 1)
  par( mai = c(0,0,0,0) )
  par( oma = c(0,0,0,0) )
  plot.new()
  if ( identical(title_cex, "default") ){ # automatically scale cex for the legend
    if(debug==TRUE){print("autoscaling the title cex")}
    title_par <- par_fetch()
    title_cex <- calculate_cex(figure_main, title_par$my_pin, title_par$my_mai, reduce_by=0.10)
  }
  text(x=0.5, y=0.5, figure_main, cex=title_cex)
  
  # PLOT THE LEGEND (layout frame 2)
  plot.new()
  if ( identical(legend_cex, "default") ){ # automatically scale cex for the legend
    if(debug==TRUE){print("autoscaling the legend cex")}
    legend_par <- par_fetch()
    legend_cex <- calculate_cex(column_levels, legend_par$my_pin, legend_par$my_mai, reduce_by=0.40)
  }
  legend( x="center", y="center", legend=column_levels, pch=15, col=color_levels, cex=legend_cex)

  # PLOT THE PCoA FIGURE (layout frame 3)
  # set par options (Most of the code in this section is copied/adapted from Dan Braithwaite's pco plotting in matR)

  #par(op)
  par <- list ()
  #par$mar <- par()['mar']
  #par$oma <- par()['oma']
  #par$mar <- c(4,4,4,4)
  #par$mar <- par(op)['mar']
  #par$oma <- par(op)['oma']
  #par$oma <- c(1,1,1,1)
  #par$mai <- c(1,1,1,1)
  par$main <- ""#figure_main
  #par$labels <- if (length (names (x)) != 0) names (x) else samples (x)
  if ( label_points==TRUE ){
    #par$labels <-  rownames(eigen_vectors)
    if ( identical(plot_samples, "all") ){
      par$labels <-  rownames(eigen_vectors)
    }else{
      par$labels <- plot_samples
    }
  } else {
    par$labels <- NA
  }
  
  
  
  
  
  #if (length (groups (x)) != 0) par$labels <- paste (par$labels, " (", groups (x), ")", sep = "")
  par [c ("xlab", "ylab", if (length (components) == 3) "zlab" else NULL)] <- paste ("PC", components, ", R^2 = ", format (eigen_values [components], dig = 3), sep = "")
  #col <- if (length (groups (x)) != 0) groups (x) else factor (rep (1, length (samples (x))))
  #levels (col) <- colors() [sample (length (colors()), nlevels (col))]
  #g <- as.character (col)
  #par$pch <- 19
  par$cex <- figure_cex
  #par$oma <- c(1,1,1,1)
  #par$mai <- c(1,1,1,1)
  # main plot paramters - create the 2d or 3d plot
  i <- eigen_vectors [ ,components [1]]
  j <- eigen_vectors [ ,components [2]]
  k <- if (length (components) == 3) eigen_vectors [ ,components [3]] else NULL
  
  # only use selected samples if that option is selected
  if ( identical(plot_samples, "all") ){}else{
    names(i)<-rownames(eigen_vectors)
    names(j)<-rownames(eigen_vectors)
    names(k)<-rownames(eigen_vectors)
    i <- i[ plot_samples ]
    j <- j[ plot_samples ]
    k <- if (length (components) == 3) k[ plot_samples ] else NULL
  }
  if(debug==TRUE){ii<<-i; jj<<-j}
  
  if (is.null (k)) {
    #par$col <- col

     par$cex <- figure_cex
     
     #if( debug==TRUE ){ print(paste("class "
     #par$col <- pcoa_colors ####<--------------
     if ( identical(plot_samples, "all") ){
        par$col <- pcoa_colors
      }else{
        names(pcoa_colors) <- rownames(eigen_vectors)
        par$col <- pcoa_colors[ plot_samples ]
      }
      if( debug==TRUE ){ print(paste("length par$col:", length(par$col))) }
      if( debug==TRUE ){ print(paste("par$col:", par$col)) }
     
     #if(debug==TRUE){print(paste("func_pch: ",plot_pch, sep="")}
     #par$pch <- plot_pch
     if ( identical(plot_samples, "all") ){
       par$pch <- plot_pch
     }else{
       names(plot_pch) <- rownames(eigen_vectors)
       par$pch <- plot_pch[ plot_samples ]
     }
     if( debug==TRUE ){ print(paste("length par$pch:", length(par$pch))) }
     if( debug==TRUE ){ print(paste("par$pch:", par$pch)) }
    
    #par$cex.symbols <- figure_symbol_cex
    #par <- resolveMerge (list (...), par)
     xcall (plot, x = i, y = j, with = par, without = "labels")
     xcall (points, x = i, y = j, with = par, without = "labels")
     grid ()
  } else {
    # parameter "color" has to be specially handled.
    # "points" above wants "col", scatterplot3d wants "color", and we
    # want the user not to worry about it...
    # par$color <- col
    #par$cex <- figure_cex
    
    
    #par$color <- pcoa_colors
    if ( identical(plot_samples, "all") ){
      par$color <- pcoa_colors
    }else{
      names(pcoa_colors) <- rownames(eigen_vectors)
      par$color <- pcoa_colors[ plot_samples ]
    }
    if( debug==TRUE ){ print(paste("length par$color:", length(par$color))) }
    if( debug==TRUE ){ print(paste("par$color:", par$color)) }
    
    #if(debug==TRUE){print(paste("func_pch: ",plot_pch, sep="")}
    
    #par$pch <- plot_pch
    if ( identical(plot_samples, "all") ){
      par$pch <- plot_pch
    }else{
      names(plot_pch) <- rownames(eigen_vectors)
      par$pch <- plot_pch[ plot_samples ]
    }
    if( debug==TRUE ){ print(paste("length par$pch:", length(par$pch))) }
    if( debug==TRUE ){ print(paste("par$pch:", par$pch)) }

    par$cex.symbols <- figure_symbol_cex
    par$type <- "h"
    par$lty.hplot <- vert_line
    par$axis <- TRUE
    par$box <- FALSE
    #par <- resolveMerge (list (...), par)
    reqPack ("scatterplot3d")
    xys <- xcall (scatterplot3d, x = i, y = j, z = k, with = par,
                  without = c ("cex", "labels")) $ xyz.convert (i, j, k)
                  #without = c ("labels")) $ xyz.convert (i, j, k)
    i <- xys$x ; j <- xys$y
  }
  text (x = i, y = j, labels = par$labels, pos = 4, cex = par$cex)
  #invisible (P)
  #})

  # PCH LEGEND (4 or doesn't exist) ############ <-

  if (num_pch>1){
    #par( mai = c(0,0,0,0) )
    #par( oma = c(0,0,0,0) )
    plot.new()
    par_legend_par <- par_fetch()
    par_legend_cex <- calculate_cex(column_levels, par_legend_par$my_pin, par_legend_par$my_mai, reduce_by=0.40)
    #my_pch_levels <<- as.integer(levels(as.factor(plot_pch)))


    if(debug==TRUE){print("made it here 11")}
    if(debug==TRUE){print(paste("11.pch_levels", pch_levels))}
    if(debug==TRUE){print(paste("11.pch_labels", pch_labels))}
       
    #if( identical(pch_behavior, "default") ){
    #  pch_legend_text <- rep("pch",num_pch)
    #}else{
      #pch_legend_text<-pch_labels[ order(pch_labels) ]
    #  pch_legend_text <- pch_labels
    #  if ( length(pch_legend_text)!=num_pch ){
    #    stop(paste("length(pch_legend_text) (", length(pch_legend_text), ") and num of unique pch entries (", num_pch,") is not the same."))
    #  }
    #}


    #pch_legend_pch <- as.integer(levels(as.factor(plot_pch)))
    #ordered_pch_legend_pch <- pch_legend_pch[ order(pch_legend_pch) ]
    pch_levels <- as(pch_levels, "numeric")
    legend( x="center", y="center", legend=pch_labels, pch=pch_levels, cex=par_legend_cex, pt.cex=par_legend_cex)
    #legend( x="center", y="center", legend=pch_legend_text, pch=ordered_pch_legend_pch, cex=par_legend_cex, pt.cex=par_legend_cex)
    #legend( x="center", legend="TEST", cex=par_legend_cex, pt.cex=par_legend_cex)
  }

  # PLOT THE COLOR BAR (frame 4 or 5)
  #par( mar = c(2,2,2,2) )
  #par( oma = c(1,1,1,1) )
  bar_x <- 1:num_levels
  bar_y <- 1
  bar_z <- matrix(1:num_levels, ncol=1)
  image(x=bar_x,y=bar_y,z=bar_z,col=color_levels,axes=FALSE,xlab="",ylab="")
  loc <- par("usr")
  if( identical(bar_cex,"default") ){
    bar_texts <- paste(column_levels[1], column_levels[num_levels])
    bar_par <- par_fetch()
    bar_cex <- calculate_cex(bar_texts, bar_par$my_pin, bar_par$my_mai, reduce_by=0.10)
  }
  text(loc[1], (loc[1]+bar_vert_adjust), column_levels[1], pos = 4, xpd = T, cex=bar_cex, adj=c(0,0))
#1 3
  
  text(loc[2], (loc[1]+bar_vert_adjust), column_levels[num_levels], pos = 2, xpd = T, cex=bar_cex, adj=c(0,0))

  #text(loc[2], (loc[1]+bar_vert_adjust), paste(column_levels[num_levels],":1",sep=""), pos = 2, xpd = T, cex=bar_cex, adj=c(0,0))
  #text(loc[2], (loc[2]+bar_vert_adjust), paste(column_levels[num_levels],":2",sep=""), pos = 2, xpd = T, cex=bar_cex, adj=c(0,0))
  #text(loc[2], (loc[3]+bar_vert_adjust), paste(column_levels[num_levels],":3",sep=""), pos = 2, xpd = T, cex=bar_cex, adj=c(0,0))
  #text(loc[2], (loc[4]+bar_vert_adjust), paste(column_levels[num_levels],":4",sep=""), pos = 2, xpd = T, cex=bar_cex, adj=c(0,0))
  
                                        #text(loc[1], loc[2], column_levels[1], pos = 4, xpd = T, cex=bar_cex, adj=c(0,0))
  #text(loc[2], loc[2], column_levels[num_levels], pos = 2, xpd = T, cex=bar_cex, adj=c(0,1))
  
  graphics.off()
}
######################
######################


######################
# SUB(7): Handle partially formatted metadata to produce colors for a single column in a metadata table
######################
## column_color <- function( color_matrix, my_color_mode="auto", my_column ){
##   ncol.color_matrix <<- ncol(color_matrix)
##   plot_colors.matrix <<- create_colors(color_matrix, color_mode=my_color_mode)
##   column_factors <<- as.factor(color_matrix[,my_column])
##   column_levels <<- levels(as.factor(color_matrix[,my_column]))
##   num_levels <<- length(column_levels)
##   color_levels <<- col.wheel(num_levels)
##   pcoa_colors <<- plot_colors.matrix[,my_column]
## }
######################
######################

  
######################
# SUB(8): Create optimal contrast color selection using a color wheel
# adapted from https://stat.ethz.ch/pipermail/r-help/2002-May/022037.html 
######################
col.wheel <- function(num_col, my_cex=0.75) {
  cols <- rainbow(num_col)
  col_names <- vector(mode="list", length=num_col)
  for (i in 1:num_col){
    col_names[i] <- getColorTable(cols[i])
  }
  cols
}
######################
######################


######################
# SUB(9): The inverse function to col2rgb()
# adapted from https://stat.ethz.ch/pipermail/r-help/2002-May/022037.html
######################
rgb2col <- function(rgb) {
  rgb <- as.integer(rgb)
  class(rgb) <- "hexmode"
  rgb <- as.character(rgb)
  rgb <- matrix(rgb, nrow=3)
  paste("#", apply(rgb, MARGIN=2, FUN=paste, collapse=""), sep="")
}
######################
######################

  
######################
# SUB(10): Convert all colors into format "#rrggbb"
# adapted from https://stat.ethz.ch/pipermail/r-help/2002-May/022037.html
######################
getColorTable <- function(col) {
  rgb <- col2rgb(col);
  col <- rgb2col(rgb);
  sort(unique(col))
}
######################
######################


######################
# SUB(11): Automtically generate colors from metadata with identical text or values
######################
create_colors <- function(metadata_column, color_mode = "auto"){ # function to     
  my_data.color <- data.frame(metadata_column)
  #ids <- rownames(metadata_column)
  #color_categories <- colnames(metadata_column)
  #for ( i in 1:dim(metadata_matrix)[2] ){
  column_factors <- as.factor(metadata_column[,1])
  column_levels <- levels(as.factor(metadata_column[,1]))
  num_levels <- length(column_levels)
  color_levels <- col.wheel(num_levels)
  levels(column_factors) <- color_levels
  my_data.color[,1]<-as.character(column_factors)
  #}

  
  return(my_data.color)
}
######################
######################


######################
# SUB(12): Automtically generate pch from metadata with identical text or values
######################
create_pch <- function(metadata_table, metadata_column, sample_names, debug){ # function to     
 #return(list("my_pch"=my_pch, "pch_levels"=pch_levels, "pch_levels_text"=pch_levels_text))

  
  #pch_matrix <- data.matrix(metadata_table)
  if(debug==TRUE){metadata_table.test <<- metadata_table}
  
  plot_pch <- metadata_table[ sample_names, metadata_column, drop=FALSE ]
  plot_pch_vector <- as.vector(plot_pch)

  if(debug==TRUE){plot_pch_vector.test <<- plot_pch_vector}
  
  names(plot_pch_vector) <- sample_names
  pch_labels <- levels(as.factor(plot_pch_vector))
  
  num_labels <- length(pch_labels)

  if( num_labels>25 ){ stop("too many pch levels - must be 25 or less") }

  pch_levels <- 1:num_labels
  names(pch_levels) <- pch_labels
  if(debug==TRUE){ pch_levels.test <<- pch_levels }

  my_pch <- integer()
  for (i in 1:nrow(plot_pch)){
    my_pch <- c(my_pch, pch_levels[ as.character( plot_pch[i,metadata_column] ) ])
    if(debug==TRUE){ print(paste("my_pch: ", my_pch)) }
  }

  if(debug==TRUE){ my_pch.test <<- my_pch; pch_levels.test <<- pch_levels}
  
  return(list("my_pch"=my_pch, "pch_levels"=pch_levels))
}
######################
######################

    
## create_colors <- function(metadata_matrix, color_mode = "auto"){ # function to     
##   #my_data.color <- data.frame(metadata_matrix)
##   my_data.color <- vector(length=nrow(metadata_matrix), mode="character")
##   ids <- rownames(metadata_matrix)
##   color_categories <- colnames(metadata_matrix)
##   for ( i in 1:dim(metadata_matrix)[2] ){
##     column_factors <- as.factor(metadata_matrix[,i])
##     column_levels <- levels(as.factor(metadata_matrix[,i]))
##     num_levels <- length(column_levels)
##     color_levels <- col.wheel(num_levels)
##     levels(column_factors) <- color_levels
##     my_data.color[i] <- as.character(column_factors)
##   }
##   return(my_data.color)
## }
######################
######################


## ######################
## # SUB(10): Plot operations for a single metadata column
## ######################

## plot_column <- function(
##                         metadata_matrix,i,
##                         PCoA_in,
##                         ncol.color_matrix,
##                         eigen_values, eigen_vectors, components,
##                         plot_pch,
##                         image_width_in, image_height_in, image_res_dpi,
##                         width_legend, width_figure,
##                         title_cex, legend_cex, figure_cex, bar_cex, label_points
##                         )
## {
##   metadata_column <- metadata_matrix[ ,i,drop=FALSE ] # get column i from the metadata matrix
  
##   suppressWarnings( numericCheck <- as.numeric(metadata_column) ) # check to see if metadata are numeric, and sort accordingly
##   if( is.numeric(numericCheck[1]) ){
##     column_name = colnames(metadata_column)[1]
##     row_names = rownames(metadata_column)
##     metadata_column <- matrix(numericCheck, ncol=1)
##     colnames(metadata_column) <- column_name
##     rownames(metadata_column) <- row_names
##   }

##   metadata_column <- metadata_column[ order(metadata_column),,drop=FALSE ] # order the metadata by value
  
##   color_column <- create_colors(metadata_matrix=metadata_column, color_mode = "auto")
##   #pcoa_colors <<- #color_column[ ,1,drop=FALSE ]
##   ncol.color_matrix <- 1 
##   column_factors <- as.factor(metadata_column) 
##   column_levels <- levels(as.factor(metadata_column))
##   num_levels <- length(column_levels)
##   color_levels <- col.wheel(num_levels)
##   pcoa_colors <- color_column #[,1, drop=FALSE]

##   image_out = paste(PCoA_in,".", colnames(metadata_column), ".pcoa.png", sep="", collapse="") # generate name for plot file
##   figure_main = paste( PCoA_in,".", colnames(metadata_column),".PCoA", sep="", collapse="") # generate title for the plot

##   #rownames(eigen_vectors) <<- noquote(rownames(eigen_vectors))
##   # test2 <- test2[rownames(test1),,drop=FALSE]
##   # eigen_vectors <<- eigen_vectors[ rownames(color_column),,drop=FALSE ] # sort vectors by ordering of colors
##   #test2[match(row.names(test2), row.names(test1)),1,drop=FALSE]


## ###### HERE
  
##   #vector_rownames <<- rownames(eigen_vectors)
##   #vector_colnames <<- colnames(eigen_vectors)
##   #color_column <<- as.matrix(color_column)
##   #rownames(eigen_vectors) <<-

##   #test_2 <- eigen_vectors
##   #rownames(test_2) <- gsub("\"", "", rownames(test_2))

##   rownames(eigen_vectors) <- gsub("\"", "", rownames(eigen_vectors))
  
##   #eigen_vectors[ match(rownames(eigen_vectors), rownames(pcoa_colors)),1,drop=FALSE]
##   #eigen_vectors[ match(rownames(pcoa_colors), rownames(eigen_vectors)),1,drop=FALSE]
##   eigen_vectors <- eigen_vectors[ rownames(pcoa_colors), ]
##   #eigen_vectors[ rownames(pcoa_colors)),]
  
##   create_plot( # generate the  plot
##               PCoA_in,
##               ncol.color_matrix,
##               eigen_values, eigen_vectors, components,
##               column_levels, num_levels, color_levels, pcoa_colors, plot_pch,
##               image_out,figure_main,
##               image_width_in, image_height_in, image_res_dpi,
##               width_legend, width_figure,
##               title_cex, legend_cex, figure_cex, bar_cex, label_points              
##               ) 
## }



  
######################
###### END SUBS ######
######################

