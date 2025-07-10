#Installind and loading packages
install.packages('geosphere')
library(dplyr)
library(geosphere)

#Function to calculate the distances
haversine_distance <- function(lat1, lon1, lat2, lon2) {
  # Convert degrees to radians
  lat1_rad <- lat1 * pi / 180
  lon1_rad <- lon1 * pi / 180
  lat2_rad <- lat2 * pi / 180
  lon2_rad <- lon2 * pi / 180
  
  # Calculate differences
  dlat <- lat2_rad - lat1_rad
  dlon <- lon2_rad - lon1_rad
  
  # Haversine formula
  a <- sin(dlat/2)^2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)^2
  c <- 2 * atan2(sqrt(a), sqrt(1-a))
  
  # Earth's radius in kilometers
  R <- 6371
  distance <- R * c
  
  return(distance)
}

calculate_distance_geosphere <- function(lat1, lon1, lat2, lon2) {
  # Returns distance in meters, convert to kilometers
  distance_m <- distHaversine(c(lon1, lat1), c(lon2, lat2))
  return(distance_m / 1000)
}

#Finding the neighbors using the above distance calculations and defining the parameters
find_nearest_neighbors <- function(target_lat, target_lon, locations_df, n = 25, method = "haversine") {
  # Input validation
  if (missing(target_lat) || missing(target_lon) || missing(locations_df)) {
    stop("Missing required parameters: target_lat, target_lon, and locations_df")
  }
  
  if (target_lat < -90 || target_lat > 90) {
    stop("Invalid latitude. Must be between -90 and 90")
  }
  
  if (target_lon < -180 || target_lon > 180) {
    stop("Invalid longitude. Must be between -180 and 180")
  }
  
  if (!all(c("latitude", "longitude") %in% names(locations_df))) {
    stop("locations_df must contain 'latitude' and 'longitude' columns")
  }
  
  if (n > nrow(locations_df)) {
    warning(paste("Requested", n, "neighbors but only", nrow(locations_df), "locations available"))
    n <- nrow(locations_df)
  }
}

#Chosen methods to calculate the distance
if (method == "haversine") {
  distances <- mapply(haversine_distance, 
                      target_lat, target_lon,
                      locations_df$latitude, locations_df$longitude)
} else if (method == "geosphere") {
  distances <- mapply(calculate_distance_geosphere,
                      target_lat, target_lon,
                      locations_df$latitude, locations_df$longitude)
} else {
  stop("Method must be 'haversine' or 'geosphere'")

#Sorting and putting neighbors into a dataframe
result <- locations_df %>%
  mutate(
    distance_km = distances,
    distance_miles = distance_km * 0.621371
  ) %>%
  arrange(distance_km) %>%
  head(n) %>%
  mutate(rank = row_number())

return(result)
}

#Neighbor results in a table
print_neighbors <- function(neighbors_df, target_name = "Target Location") {
  cat("=== 25 Nearest Neighbors to", target_name, "===\n\n")
  
  # Print header
  cat(sprintf("%-4s %-20s %-10s %-11s %-12s %-12s\n", 
              "Rank", "Location", "Latitude", "Longitude", "Dist (km)", "Dist (mi)"))
  cat(paste(rep("-", 75), collapse = ""), "\n")
  
  # Print each neighbor
  for (i in 1:nrow(neighbors_df)) {
    cat(sprintf("%-4d %-20s %-10.4f %-11.4f %-12.2f %-12.2f\n",
                neighbors_df$rank[i],
                substr(neighbors_df$name[i], 1, 20),  # Truncate long names
                neighbors_df$latitude[i],
                neighbors_df$longitude[i],
                neighbors_df$distance_km[i],
                neighbors_df$distance_miles[i]))
  }
  
  cat("\n")
}

#Summary of the neighbors
get_neighbor_summary <- function(neighbors_df) {
  summary_stats <- list(
    closest_location = neighbors_df$name[1],
    closest_distance_km = neighbors_df$distance_km[1],
    farthest_distance_km = max(neighbors_df$distance_km),
    average_distance_km = mean(neighbors_df$distance_km),
    median_distance_km = median(neighbors_df$distance_km),
    total_neighbors = nrow(neighbors_df)
  )
  
  return(summary_stats)
}

#Creating the dataframe of locations

PPHC_Location_Coords<-PPHC_CT_County_Coords[,-2]
PPHC_Location_Coords<-PPHC_Location_Coords[,-2]

PPHC_CT_County_Coords