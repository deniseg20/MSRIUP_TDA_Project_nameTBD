#library for packages
install.packages("rjson")
library(rjson)
library(censusxy)
library(remotes)
library(tidycensus)
library(dplyr)

library(remotes)
library(tidycensus)
library(dplyr)
remotes::install_github("chris-prener/censusxy")
library(censusxy)
library(tidyr)

#Opening and transforming FQHC csv file
FQHC_Locations<-read.csv("fqhc_data_cleaned.csv")
FQHC_Locations<-data.frame(FQHC_Locations)

#Merging the addresses together
FQHC_Locations2<-paste(FQHC_Locations$street_address,FQHC_Locations$city,FQHC_Locations$county,sep=",")
FQHC_Locations2b<-data.frame(FQHC_Locations2)

#API code for census
census_api_key("55c35b09ace2b43863def77951088362efb26d99", install = TRUE,overwrite=TRUE)

#Creating a matrix to apply geocode function
FQHC_Matrix=matrix(FQHC_Locations2)


#geocode functions again
geo_code<-function(address_x)
  cxy_oneline(address = address_x, return = "geographies", vintage = "Current_Current")

geo_code_locations<-function(address_y)
  cxy_oneline(address = address_y, return = "locations")

#Retrieving the census information for each location using the apply function and each string row of above function
FQHC_CT=apply(FQHC_Matrix,1,geo_code)
FQHC_Lat=apply(FQHC_Matrix,1,geo_code_locations)


#Creating a function to get the census tracts
get_tract2<-function(m)
 FQHC_CT[[m]]$geographies.Census.Tracts.NAME

get_county2<-function(n)
  FQHC_CT[[n]]$geographies.Counties.NAME

get_coordsx2<-function(p)
  FQHC_Lat[[p]]$coordinates.x

get_coordsy2<-function(q)
  FQHC_Lat[[q]]$coordinates.y

#Creating a dataframe of each census tract 
FQHC_CT_2=lapply(1:303,get_tract2)
FQHC_County=lapply(1:303,get_county2)
FQHC_coordinates_x=lapply(1:303,get_coordsx2)
FQHC_coordinates_y=lapply(1:303,get_coordsy2)

CT_County_FQHC=cbind(FQHC_Locations2,FQHC_CT_2,FQHC_County,FQHC_coordinates_x,FQHC_coordinates_y)

##Final
FQHC_CT_County=data.frame(CT_County_FQHC)

###edits
FQHC_CT_County[2,1]<-'1000 Newbury Rd , Newbury Park'
FQHC_CT_County[2,2]<-geo_code('1000 Newbury Rd , Newbury Park')$geographies.Census.Tracts.NAME
FQHC_CT_County[2,3]<-geo_code('1000 Newbury Rd , Newbury Park')$geographies.Counties.NAME
FQHC_CT_County[2,4]<-geo_code_locations('1000 Newbury Rd , Newbury Park')$coordinates.x
FQHC_CT_County[2,5]<-geo_code_locations('1000 Newbury Rd , Newbury Park')$coordinates.y


FQHC_CT_County[28,2]<-'Census Tract 101.02'
FQHC_CT_County[28,3]<-'Glenn County'
FQHC_CT_County[28,4]<- -122.16719365581686
FQHC_CT_County[28,5]<- 39.73606045832499
##Using the coordinate points long,lat (-122.16719365581686, 39.73606045832499)

FQHC_CT_County[29,1]<-'12520 Palm Dr,Desert Hot Springs,Riverside'
FQHC_CT_County[29,2]<-geo_code('12520 Palm Dr,Desert Hot Springs,Riverside')$geographies.Census.Tracts.NAME
FQHC_CT_County[29,3]<-geo_code('12520 Palm Dr,Desert Hot Springs,Riverside')$geographies.Counties.NAME
FQHC_CT_County[29,4]<-geo_code_locations('12520 Palm Dr,Desert Hot Springs,Riverside')$coordinates.x
FQHC_CT_County[29,5]<-geo_code_locations('12520 Palm Dr,Desert Hot Springs,Riverside')$coordinates.y

FQHC_CT_County[36,2]<-'Census Tract 751'
FQHC_CT_County[36,3]<-'Orange County'
FQHC_CT_County[36,4]<- -117.8840219213762
FQHC_CT_County[36,5]<- 33.760330457389124
##Using the coordinate points long,lat (-117.8840219213762, 33.760330457389124)

FQHC_CT_County[47,2]<-'Census Tract 123.01'
FQHC_CT_County[47,3]<-'Imperial County'
FQHC_CT_County[47,4]<- -115.96979636802175
FQHC_CT_County[47,5]<- 33.27578824630402
##Using the coordinate points long,lat (-115.96979636802175, 33.27578824630402)

FQHC_CT_County[58,2]<-'Census Tract 112'
FQHC_CT_County[58,3]<-'Mendocino County'
FQHC_CT_County[58,4]<- -123.37925193281991
FQHC_CT_County[58,5]<- 39.013228618214114
##Using the coordinate points long,lat (-123.37925193281991, 39.013228618214114)

FQHC_CT_County[268,2]<-'Census Tract 16.01'
FQHC_CT_County[268,3]<-'Tulare County'
FQHC_CT_County[268,4]<- -119.20688550534067
FQHC_CT_County[268,5]<- 36.30359020549037
##Using the coordinate points long,lat (-119.20688550534067, 36.30359020549037)

FQHC_CT_County[61,2]<-'Census Tract 4.07'
FQHC_CT_County[61,3]<-'Kings County'
FQHC_CT_County[61,4]<- -119.78243951883161
FQHC_CT_County[61,5]<- 36.301761974181254
##Using the coordinate points long,lat (-119.78243951883161, 36.301761974181254)

FQHC_CT_County[80,2]<-'Census Tract 123.02'
FQHC_CT_County[80,3]<-'Shasta County'
FQHC_CT_County[80,4]<- -122.45400323399872
FQHC_CT_County[80,5]<- 40.474643758031405
##Using the coordinate points long,lat (-123.37925193281991, 39.013228618214114)

FQHC_CT_County[93,2]<-'Census Tract 4613'
FQHC_CT_County[93,3]<-'Los Angeles County'
FQHC_CT_County[93,4]<- -118.13165056124248
FQHC_CT_County[93,5]<- 34.176943470115226
##Using the coordinate points long,lat (-123.37925193281991, 39.013228618214114)

FQHC_CT_County[110,2]<-'Census Tract 7.02'
FQHC_CT_County[110,3]<-'Tulare County'
FQHC_CT_County[110,4]<- -119.096302430689
FQHC_CT_County[110,5]<- 36.417195790277766
##Using the coordinate points long,lat (-119.096302430689, 36.417195790277766)

FQHC_CT_County[117,2]<-'Census Tract 105'
FQHC_CT_County[117,3]<-'Mendocino County'
FQHC_CT_County[117,4]<- -123.80308133511406
FQHC_CT_County[117,5]<- 39.43040121063343
##Using the coordinate points long,lat (-123.80308133511406, 39.43040121063343)

FQHC_CT_County[120,2]<-'Census Tract 3240.04'
FQHC_CT_County[120,3]<-'Contra Costa County'
FQHC_CT_County[120,4]<- -122.05326339815562
FQHC_CT_County[120,5]<- 37.94543718505401
##Using the coordinate points long,lat (-122.05326339815562, 37.94543718505401)

FQHC_CT_County[124,2]<-'Census Tract 45'
FQHC_CT_County[124,3]<-'Kern County'
FQHC_CT_County[124,4]<- -119.69524381679629
FQHC_CT_County[124,5]<- 35.61654785289368
##Using the coordinate points long,lat (-119.69524381679629, 35.61654785289368)

FQHC_CT_County[128,2]<-'Census Tract 2524.02'
FQHC_CT_County[128,3]<-'Solano County'
FQHC_CT_County[128,4]<- -122.06998450320577
FQHC_CT_County[128,5]<- 38.2364874667983
##Using the coordinate points long,lat (-122.06998450320577, 38.2364874667983)

FQHC_CT_County[157,2]<-'Census Tract 10'
FQHC_CT_County[157,3]<-'Fresno County'
FQHC_CT_County[157,4]<- -119.79114024559233
FQHC_CT_County[157,5]<- 36.700676121605106
##Using the coordinate points long,lat (-119.79114024559233, 36.700676121605106)

FQHC_CT_County[158,2]<-'Census Tract 20.15'
FQHC_CT_County[158,3]<-'Santa Barbara County'
FQHC_CT_County[158,4]<- -120.43481965578637
FQHC_CT_County[158,5]<- 34.908893447787236
##Using the coordinate points long,lat (-120.43481965578637, 34.908893447787236)

FQHC_CT_County[171,2]<-'Census Tract 9.01'
FQHC_CT_County[171,3]<-'Tulare County'
FQHC_CT_County[171,4]<- -119.41165820941589
FQHC_CT_County[171,5]<- 36.35596105556
##Using the coordinate points long,lat (-119.41165820941589, 36.35596105556)

FQHC_CT_County[179,1]<-'33025 Rd 159, Ivanhoe, CA 93235'
FQHC_CT_County[179,2]<-geo_code('33025 Rd 159, Ivanhoe, CA 93235')$geographies.Census.Tracts.NAME
FQHC_CT_County[179,3]<-geo_code('33025 Rd 159, Ivanhoe, CA 93235')$geographies.Counties.NAME
FQHC_CT_County[179,4]<-geo_code_locations('33025 Rd 159, Ivanhoe, CA 93235')$coordinates.x
FQHC_CT_County[179,5]<-geo_code_locations('33025 Rd 159, Ivanhoe, CA 93235')$coordinates.y

FQHC_CT_County[206,1]<-'4177 Avenue 368, Kingsburg, CA 93631'
FQHC_CT_County[206,2]<-geo_code('4177 Avenue 368, Kingsburg, CA 93631')$geographies.Census.Tracts.NAME
FQHC_CT_County[206,3]<-geo_code('4177 Avenue 368, Kingsburg, CA 93631')$geographies.Counties.NAME
FQHC_CT_County[206,4]<-geo_code_locations('4177 Avenue 368, Kingsburg, CA 93631')$coordinates.x
FQHC_CT_County[206,5]<-geo_code_locations('4177 Avenue 368, Kingsburg, CA 93631')$coordinates.y

FQHC_CT_County[212,2]<-'Census Tract 76.07'
FQHC_CT_County[212,3]<-'Ventura County'
FQHC_CT_County[212,4]<- -118.89987906265183
FQHC_CT_County[212,5]<- 34.26811812410631
##Using the coordinate points long,lat (-118.89987906265183, 34.26811812410631)

FQHC_CT_County[238,2]<-'Census Tract 4003'
FQHC_CT_County[238,3]<-'Alameda County'
FQHC_CT_County[238,4]<- -118.89987906265183
FQHC_CT_County[238,5]<- 34.26811812410631
##Using the coordinate points long,lat (-122.26133753981296, 37.839297988412305)

FQHC_CT_County[244,2]<-'Census Tract 444.03'
FQHC_CT_County[244,3]<-'Riverside County'
FQHC_CT_County[244,4]<- -116.63881091050678
FQHC_CT_County[244,5]<- 33.55722902897
##Using the coordinate points long,lat (-116.63881091050678, 33.55722902897)

FQHC_CT_County[268,2]<-'Census Tract 4.07'
FQHC_CT_County[268,3]<-'Kings County'
FQHC_CT_County[268,4]<- -119.20688550534067
FQHC_CT_County[268,5]<- 36.30156742820797
##Using the coordinate points long,lat (-119.20688550534067, 36.30156742820797)

FQHC_CT_County[297,1]<-'9416 Rd 238, Terra Bella, CA 93270'
FQHC_CT_County[297,2]<-geo_code('9416 Rd 238, Terra Bella, CA 93270')$geographies.Census.Tracts.NAME
FQHC_CT_County[297,3]<-geo_code('9416 Rd 238, Terra Bella, CA 93270')$geographies.Counties.NAME
FQHC_CT_County[297,4]<-geo_code_locations('9416 Rd 238, Terra Bella, CA 93270')$coordinates.x
FQHC_CT_County[297,5]<-geo_code_locations('9416 Rd 238, Terra Bella, CA 93270')$coordinates.y

rownames(FQHC_CT_County) <- NULL
rownames(FQHC_CT_County) <- 1:nrow(FQHC_CT_County)



#Bringing together the coordinates
FQHC_CT_County_Coords<-FQHC_CT_County%>%
  unite('Coordinates',4:5,remove=TRUE, sep=" ")

colnames(FQHC_CT_County_Coords)<-c('Address','Census Tract','County','Coordinates (Long, Lat)')
FQHC_CT_County_Coords<-FQHC_CT_County_Coords[-244,]

#FQHCs in the county

FQHCS_in_Counties=FQHC_CT_County_Coords%>%
  group_by(County)%>%
  summarize(count=n())

sum(FQHCS_in_Counties$count)

FQHC_CT_County_Coords_str<-apply(FQHC_CT_County_Coords,1,as.character)
FQHC_CT_County_Coords_df<-data.frame(FQHC_CT_County_Coords_str)
FQHC_CT_County_Coords_df2<-data.frame(FQHC_CT_County_Coords)

colnames(FQHC_CT_County_Coords_df)<-paste0('FQHC Location', 1:ncol(FQHC_CT_County_Coords_df))
rownames(FQHC_CT_County_Coords_df)<-c('Address', 'Census Tract', 'County','Coordinates')
write.csv(FQHC_CT_County_Coords_df, "FQHC_Location_information.csv", row.names=FALSE)
