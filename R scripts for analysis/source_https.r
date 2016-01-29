source_https <- function(url, ...) {
    require(RCurl)
    sapply(c(url, ...), function(u) {
        eval(parse(text = getURL(u, followlocation = TRUE, cainfo = system.file("CurlSSL", "cacert.pem", package = "RCurl"))), envir = .GlobalEnv)
    })
}
