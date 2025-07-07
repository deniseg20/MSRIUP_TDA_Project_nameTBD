#library for packages
install.packages("rjson")
library(rjson)
library(censusxy)
library(remotes)
library(tidycensus)
library(dplyr)

#Opening and transforming FQHC csv file
FQHC_Locations<-read.csv("fqhc_data.csv")

#Merging the addresses together
FQHC_Locations2<-paste(FQHC_Locations$Street.Address..sort.descending,FQHC_Locations$Suite..sort.descending,FQHC_Locations$City..sort.descending,sep=",")
FQHC_Locations2

#Creating a matrix to apply geocode function
FQHC_Matrix=matrix(FQHC_Locations2)

#Retrieving the census information for each location using the apply function and each string row of above function
FQHC_CT=apply(FQHC_Matrix,1,geo_code)

#Creating a function to get the census tracts
get_tract2<-function(n)
  FQHC_CT[[n]]$geographies.Census.Tracts.BASENAME

#Creating a dataframe of each census tract 
FQHC_CT_2=lapply(1:62,get_tract2)
FQHC_CT_2m=matrix(FQHC_CT_2,62,1)


##Final
FQHC_CT_df=data.frame(FQHC_CT_2m)