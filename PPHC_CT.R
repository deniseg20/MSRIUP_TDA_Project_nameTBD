#Installing Packages
install.packages(c("censusxy", "tidycensus"))
install.packages('remotes')
library(remotes)
library(tidycensus)
library(dplyr)
remotes::install_github("chris-prener/censusxy")
library(censusxy)
library(cxy)

install.packages("sf")
install.packages("censusxy", dependencies = TRUE)

#Data for Planned Parenthood Locations in California
California_PP_Locations<-read.csv("California_PP_Locations.csv")

#Making above data into a dataframe
Cali_df=data.frame(California_PP_Locations)

#Uploading the Census API key
census_api_key("55c35b09ace2b43863def77951088362efb26d99", install = TRUE,overwrite=TRUE)

#Creating a function to get the census information for each function
geo_code<-function(address_x)
  cxy_oneline(address = address_x, return = "geographies", vintage = "Current_Current")

#Making each entry of the Cali_df dataframe into a string to it can be put into above function
Cali_df_strings<-apply(Cali_df, 1, as.character)

#Creating a matrix from the strings
CDS_matrix=matrix(Cali_df_strings)

#Retrieving the census information for each location using the apply function and each string row of above function
PPHC_CT=apply(CDS_matrix,1,geo_code)

#Creating a function to get the census tracts
get_tract<-function(n)
  PPHC_CT[[n]]$geographies.Census.Tracts.BASENAME

#Creating a dataframe of each census tract 
PPHC_CT_2=lapply(1:110,get_tract)
PPHC_CT_2m=matrix(PPHC_CT_2,110,1)

##Final
PPHC_CT_df=data.frame(PPHC_CT_2m)

geo_code("7475 Camino Arroyo,,Gilroy" )