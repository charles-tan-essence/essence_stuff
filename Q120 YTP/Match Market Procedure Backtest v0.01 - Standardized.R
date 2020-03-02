
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

############################################
############################################
#We are going to compare Time-based regression and CausalImpact for back-testing below.
#User needs to input the pre-test and test dates in test_period and
#the regions assigned to exposed and control in geo_assign below.
#Both are done at 95% confidence level.

#In this section, we will evaluate if the methods (correctly) predict a lift or not 
#when there should/ shouldn't be.
############################################

###user input
pre_period_start <- "2018-12-01"
treatment_start <- "2019-04-01"
treatment_end <- "2019-05-31"

exposed_regions <- c('Tokyo', 'Kanagawa Prefecture', 'Osaka Prefecture')
control_regions <- c('Miyagi Prefecture', 'Ibaraki Prefecture', 'Hokkaido Prefecture', 'Shizuoka Prefecture',
                     'Chiba Prefecture', 'Hiroshima Prefecture', 'Kyoto Prefecture', 'Fukuoka Prefecture',
                     'Saitama Prefecture')

############################################

# define test period from dates from user input
test_period = c(pre_period_start, treatment_start, treatment_end)
pre.period <- as.Date(c(test_period[1],toString(as.Date(test_period[2])-1)))
pre.period
post.period <- as.Date(c(test_period[2],test_period[3]))
post.period
time.points <- seq.Date(as.Date(test_period[1]), to=as.Date(test_period[3]), by = 1)

# compile exposed and control regions in to regions
regions <- c(exposed_regions, control_regions)

# create geo_group vector
geo_group <- rep(1, length(exposed_regions))
control_geo_group <- seq(2, length(control_regions) + 1)

geo_group <- c(geo_group, control_geo_group)

geo_assign <- data.frame("geo"=regions,
                         "geo.group"=geo_group)

#############################################

raw_data<-read.csv('signups.csv', header=T)
colnames(raw_data)<-c("date","geo","Signups")
raw_data$date <- as.Date(raw_data$date, format="%Y-%m-%d")
head(raw_data)

# filter for test dates
# filter for test geos
data <- raw_data[raw_data$date>=test_period[1] & raw_data$date<=test_period[3],]
data <- data[data$geo %in% geo_assign$geo,]
data <- left_join(data, geo_assign, by=c('geo'= 'geo'))

agg_data <- aggregate(Signups ~ date + geo.group, data, sum)
agg_data <- agg_data[order(agg_data$date),]
agg_data

casted_data <- acast(agg_data, date~geo.group)
casted_data$date <- as.Date(casted_data$date, format="%Y-%m-%d")
casted_data

# TODO: GET THE CASTED DATA TO BE RUN IN CAUSALIMPACT

#impact <- CausalImpact(casted_data, pre.period, post.period, alpha=0.05, model.args=list(niter=5000))
#plot(impact)
#summary(impact, "report")
#plot(impact$model$bsts.model, "coefficients")
#ggplot(data=obj_ci,aes(x=date,y=Signups,group=as.factor(geo.group), colour=as.factor(geo.group)))+
#  geom_line()+
#  geom_point()