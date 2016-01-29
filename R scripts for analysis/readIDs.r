# create readIDs
# adapted from matR (https://github.com/MG-RAST/matR)
readIDs <- function (filename, ...) 
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
