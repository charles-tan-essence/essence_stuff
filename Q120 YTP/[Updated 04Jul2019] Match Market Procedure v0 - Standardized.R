
############################################
#title: "Match Market Selection - YTP JP Q319"
#author: "Kenneth Koh & Hui Xiang Chua"
#date: "June 17, 2019"
#--------------------------------------------
#Objective: To maximize comparability of Match Market a standardized framework in which we evaluate causal effects using geographically segregated control holdout

#Workflow Documentation:
  
#Market Selection:
#1. From Time-series Data and a single KPI, we select candidates for control holdout based on the following priorities
#- Top 30 percentile lowest dtw distance scores across all geos considered
#- Correlation of >90%
#- Correlation with Population >50%
#2. Within these constraints, we select 2 or more exposed markets with the highest number of shared control holdouts possible (recommended 5-20 control regions, but minimally 3 control markets in countries where control regions may be limited)

#Control Market Validation:
#1. To safeguard against false positive from control selection error - Segment the pre-period data into a 2 : 1 ratio and run Causal Impact at 90% significance - there should be no significant lift

#Inputs requirements:
#1. Daily time-series data for KPI variable/conversions (segmented by geo)
#- e.g. Day, Region, Signups
#2. Minimum 90 day period for pre-period data
#3. Post-period analysed should minimally follow a 1:2 ratio with pre-period data input

#Variables that require user inputs have been commented with ###user input. Ctrl+F to see.
###########################################

###user input
setwd("C:/Users/charles.tan/Documents/GitHub/Essence_stuff/Q120 YTP") #set working directory
###

#import libaries
libs <- c("zoo", 
          "dtw",
          "MarketMatching",
          "Rcpp",
          "CausalImpact",
          "lubridate",
          "tidyverse",
          "ggplot2",
          "reshape2",
          "plyr",
          "pivottabler",
          "dplyr",
          "GeoexperimentsResearch")
for (lib in libs) {
  if (!require(lib, character.only = TRUE)) {
    install.packages(lib)
    require(lib, character.only = TRUE)
  }
}

#if installing GeoexperimentsResearch fails, run the code below
#install.packages("githubinstall")
#library(githubinstall)
#githubinstall("GeoexperimentsResearch")
#library(GeoexperimentsResearch)

davs_raw = read.csv('dav_data.csv', header=T, encoding='UTF-8')
colnames(davs_raw)[1] <- 'date'
print(head(davs_raw))

davs_raw$date <- as.Date(davs_raw$date, format="%Y-%m-%d")
davs_data <- davs_raw[complete.cases(davs_raw), ]
davs_data <- davs_data[order(davs_data$region_name), ]
davs_data$region_ID <- cumsum(!duplicated(davs_data$region_name))
region_names <- ddply(davs_data, .(davs_data$region_ID, davs_data$region_name), nrow)
region_names <- region_names[, c('davs_data$region_ID', 'davs_data$region_name')]
#write.csv(region_names, 'region_id.csv')

data_period <- c('2019-09-27', '2019-10-02')

mm <- best_matches(data = davs_data,
                   id_variable = "region_name",
                   date_variable = "date",
                   matching_variable = "total",
                   parallel = TRUE,
                   warping_limit = 1, 
                   dtw_emphasis = 1, #setting dtw_emphasis to 1 ensures scores are output- no impact to chosen control
                   matches = length(unique(davs_data$region_name)), # retrieve scores for all markets for each market
                   start_match_period = data_period[1],
                   end_match_period = data_period[2])

mm <- merge(x=mm$BestMatches, y=region_names, by.x='region_name', by.y='davs_data$region_ID', all.x=TRUE)

write.csv(mm, 'MM_results.csv')
