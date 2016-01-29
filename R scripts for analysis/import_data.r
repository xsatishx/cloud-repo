import_data <- function(file_name)
{
  data.matrix(read.table(file_name, row.names=1, header=TRUE, sep="\t", comment.char="", quote="", check.names=FALSE))
}
