# install and soure R packages
install_r_prereqs <- function(){
    install.packages("RCurl")
    install.packages("devtools")
    install.packages("RJSONIO")
    library(devtools)
    install_github(repo="MG-RAST/matR", dependencies=FALSE, ref="early-release")
    library(RCurl)
    library(RJSONIO)
    library(matR)
    dependencies()
}
############################################################################################################################
