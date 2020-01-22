
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
#the regions assigned to exposed and control in geoassign below.
#Both are done at 95% confidence level.

#In this section, we will evaluate if the methods (correctly) predict a lift or not 
#when there should/ shouldn't be.
############################################

###user input
test_period = c("2018-12-01","2019-04-01","2019-05-31")
geoassign<-data.frame("geo"=c('Tokyo', 'Kanagawa Prefecture', 'Osaka Prefecture', 
                              'Miyagi Prefecture', 'Ibaraki Prefecture', 'Hokkaido Prefecture', 'Shizuoka Prefecture',
                              'Chiba Prefecture', 'Hiroshima Prefecture', 'Kyoto Prefecture', 'Fukuoka Prefecture',
                              'Saitama Prefecture'),
                      "geo.group"=c(1,1,1,2,3,4,5,6,7,8,9,10)) #set exposed and control markets

###

#Back-testing with Time-based Regression
data<-read.csv('signups.csv', header=T)
colnames(data)<-c("date","geo","Signups")
data$date <- as.Date(data$date, format="%Y-%m-%d")
head(data)

data2<-data[data$date>=test_period[1] & data$date<=test_period[3],]
head(data2)
obj.gts<-GeoTimeseries(data2,metrics=c("Signups"))
head(obj.gts)
aggregate(obj.gts,by='.weekindex')
plot(obj.gts)
obj.per<-ExperimentPeriods(test_period)
obj.per

geoassign  
obj.ga<-GeoAssignment(geoassign)
obj.ga

obj.gts2 <- obj.gts[obj.gts$geo %in% geoassign$geo ,]
head(obj.gts2)
obj<-GeoExperimentData(obj.gts2, periods=obj.per, geo.assignment=obj.ga)
head(obj)
aggregate(obj,by=c('period','geo.group'))

obj.tbr<-DoTBRAnalysis(obj,response="Signups",model='tbr1',
                       pretest.period=0,
                       intervention.period=1,
                       cooldown.period=NULL,
                       control.group=2,
                       treatment.group=1)
summary(obj.tbr)
head(obj.tbr)
plot(obj.tbr)
#obj.tbr[obj.tbr$period==1,]

#Back-testing with CausalImpact
obj_ci<-aggregate(obj,by=c('date','geo.group'))
obj_ci
pre.period <- as.Date(c(test_period[1],toString(as.Date(test_period[2])-1)))
pre.period
post.period <- as.Date(c(test_period[2],test_period[3]))
post.period
time.points <- seq.Date(as.Date(test_period[1]), by = 1, length.out = nrow(obj_ci)/2)
max(time.points)
ci_data <- zoo(cbind(obj_ci[obj_ci$geo.group==1,]$Signups,
                     obj_ci[obj_ci$geo.group==2,]$Signups,
                     obj_ci[obj_ci$geo.group==3,]$Signups,
                     obj_ci[obj_ci$geo.group==4,]$Signups,
                     obj_ci[obj_ci$geo.group==5,]$Signups,
                     obj_ci[obj_ci$geo.group==6,]$Signups,
                     obj_ci[obj_ci$geo.group==7,]$Signups,
                     obj_ci[obj_ci$geo.group==8,]$Signups,
                     obj_ci[obj_ci$geo.group==9,]$Signups,
                     obj_ci[obj_ci$geo.group==10,]$Signups), time.points)
ci_data
print(ci_data)
impact <- CausalImpact(ci_data, pre.period, post.period, alpha=0.05, model.args=list(niter=5000))
plot(impact)
summary(impact)
ggplot(data=obj_ci,aes(x=date,y=Signups,group=as.factor(geo.group), colour=as.factor(geo.group)))+
  geom_line()+
  geom_point()