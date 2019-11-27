
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

data_raw = read.csv('signups.csv', header=T, encoding='UTF-8')
#data_raw = read.csv('signups_agg_control.csv', header=T, encoding='UTF-8')
colnames(data_raw)[1] <- 'Day'
print(head(data_raw))

data_raw$Day <- as.Date(data_raw$Day, format="%Y-%m-%d")
data <- data_raw[complete.cases(data_raw), ]
data <- data[order(data$Region), ]
data$region_ID <- cumsum(!duplicated(data$Region))
region_names <- ddply(data, .(data$region_ID, data$Region), nrow)
region_names <- region_names[, c('data$region_ID', 'data$Region')]
region_names
#write.csv(region_names, 'region_id.csv')

data_period <- c('2018-11-23', '2019-11-23')
head(data)
mm <- best_matches(data = data,
                   id_variable = "region_ID",
                   date_variable = "Day",
                   matching_variable = "Signups",
                   parallel = TRUE,
                   warping_limit = 1, 
                   dtw_emphasis = 1, #setting dtw_emphasis to 1 ensures scores are output- no impact to chosen control
                   matches = length(unique(data$Region)), # retrieve scores for all markets for each market
                   start_match_period = data_period[1],
                   end_match_period = data_period[2])
head(mm$BestMatches)
mm <- merge(x=mm$BestMatches, y=region_names, by.x='region_ID', by.y='data$region_ID', all.x=TRUE)
mm <- mm[, c('region_ID', 'BestControl', 'RelativeDistance', 'Correlation', 'rank', 'data$Region')]
colnames(mm)[colnames(mm) == 'data$Region'] <- 'Region'
mm <- merge(x=mm, y=region_names, by.x='BestControl', by.y='data$region_ID', all.x=TRUE)
colnames(mm)[colnames(mm) == 'data$Region'] <- 'ComparedRegion'
head(mm)
mm <- mm[order(mm$Region, mm$rank),]
head(mm)
write.csv(mm, 'MM_results.csv', row.names=FALSE)
#write.csv(mm, 'MM_results_agg_control.csv', row.names=FALSE)
