#Installing Packages
#install.packages(c("censusxy", "tidycensus"))
#install.packages('remotes')

library(remotes)
library(tidycensus)
library(dplyr)
remotes::install_github("chris-prener/censusxy")
library(censusxy)
library(tidyr)

#install.packages("sf")
#install.packages("censusxy", dependencies = TRUE)

#Data for Planned Parenthood Locations in California
California_PP_Locations<-read.csv("California_PP_Locations.csv")

#Making above data into a dataframe
Cali_df=data.frame(California_PP_Locations)



#Uploading the Census API key
census_api_key("55c35b09ace2b43863def77951088362efb26d99", install = TRUE,overwrite=TRUE)

#Creating a function to get the census information for each function
geo_code<-function(address_x)
  cxy_oneline(address = address_x, return = "geographies", vintage = "Current_Current")

geo_code_locations<-function(address_y)
  cxy_oneline(address = address_y, return = "locations")


#Making each entry of the Cali_df dataframe into a string to it can be put into above function
Cali_df_strings<-apply(Cali_df, 1, as.character)

#Creating a matrix from the strings
CDS_matrix=matrix(Cali_df_strings)

#Retrieving the census information for each location using the apply function and each string row of above function
PPHC_CT=apply(CDS_matrix,1,geo_code)
PPHC_Lat=apply(CDS_matrix,1,geo_code_locations)

#Creating a function to get the census tracts
get_tract<-function(m)
  PPHC_CT[[m]]$geographies.Census.Tracts.NAME

get_county<-function(n)
  PPHC_CT[[n]]$geographies.Counties.NAME

get_coordsx<-function(p)
  PPHC_Lat[[p]]$coordinates.x

get_coordsy<-function(q)
  PPHC_Lat[[q]]$coordinates.y

#Creating a dataframe of each census tract 
PPHC_CT_2=lapply(1:110,get_tract)
PPHC_County=lapply(1:110,get_county)
PPHC_coordinates_x=lapply(1:110,get_coordsx)
PPHC_coordinates_y=lapply(1:110,get_coordsy)

CT_County_PPHC=cbind(Cali_df_strings,PPHC_CT_2,PPHC_County,PPHC_coordinates_x,PPHC_coordinates_y)

##Unedited (missing two values)
PPHC_CT_County=data.frame(CT_County_PPHC)

###Final with edits
PPHC_CT_County[12,1]<-'49092 Las Cruces St, Coachella, CA 92236'
PPHC_CT_County[12,2]<-geo_code('49092 Las Cruces St, Coachella, CA 92236')$geographies.Census.Tracts.NAME
PPHC_CT_County[12,3]<-geo_code('49092 Las Cruces St, Coachella, CA 92236')$geographies.Counties.NAME
PPHC_CT_County[12,4]<-geo_code_locations('49092 Las Cruces St, Coachella, CA 92236')$coordinates.x
PPHC_CT_County[12,5]<-geo_code_locations('49092 Las Cruces St, Coachella, CA 92236')$coordinates.y

PPHC_CT_County[60,1]<-'2907 CA-82, Redwood City, CA 94061'
PPHC_CT_County[60,2]<-geo_code('2907 CA-82, Redwood City, CA 94061')$geographies.Census.Tracts.NAME
PPHC_CT_County[60,3]<-geo_code('2907 CA-82, Redwood City, CA 94061')$geographies.Counties.NAME
PPHC_CT_County[60,4]<-geo_code_locations('2907 CA-82, Redwood City, CA 94061')$coordinates.x
PPHC_CT_County[60,5]<-geo_code_locations('2907 CA-82, Redwood City, CA 94061')$coordinates.y

PPHC_CT_County[94,1]<-'1200 Hillcrest, Thousand Oaks, CA 91320'
PPHC_CT_County[94,2]<-geo_code('1200 Hillcrest, Thousand Oaks, CA 91320')$geographies.Census.Tracts.NAME
PPHC_CT_County[94,3]<-geo_code('1200 Hillcrest, Thousand Oaks, CA 91320')$geographies.Counties.NAME
PPHC_CT_County[94,4]<-geo_code_locations('1200 Hillcrest, Thousand Oaks, CA 91320')$coordinates.x
PPHC_CT_County[94,5]<-geo_code_locations('1200 Hillcrest, Thousand Oaks, CA 91320')$coordinates.y

PPHC_CT_County_Coords<-PPHC_CT_County%>%
  unite('Coordinates',4:5, sep=" ")

colnames(PPHC_CT_County_Coords)<-c('Address','Census Tract','County','Coordinates (Long, Lat)')

PPHCS_in_Counties=PPHC_CT_County_Coords%>%
  group_by(County)%>%
  summarize(count=n())

PPHCS_in_Counties

PPHC_CT_County_Coords_str<-apply(PPHC_CT_County_Coords,1,as.character)
PPHC_CT_County_Coords_df<-data.frame(PPHC_CT_County_Coords_str)
colnames(PPHC_CT_County_Coords_df)<-paste0('PPHC Location', 1:ncol(PPHC_CT_County_Coords_df))
rownames(PPHC_CT_County_Coords_df)<-c('Address', 'Census Tract', 'County','Coordinates')
write.csv(PPHC_CT_County_Coords_df, "PPHC_Location_information.csv", row.names=FALSE)
