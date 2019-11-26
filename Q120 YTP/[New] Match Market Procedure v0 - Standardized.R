
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

#read in dataset
ConversionsRaw <- read.csv("signups.csv",header=T)
ConversionsRaw <- ConversionsRaw[ , c("Day", "Region", "Signups")]
head(ConversionsRaw)

ConversionsRaw$Day<-as.Date(ConversionsRaw$Day, format="%Y-%m-%d")
ConversionsData <- ConversionsRaw[complete.cases(ConversionsRaw), ]
ConversionsData<-ConversionsData[order(ConversionsData$Region),]
ConversionsData$CountryID <- cumsum(!duplicated(ConversionsData$Region))
region_names<-ddply(ConversionsData, .(ConversionsData$CountryID, ConversionsData$Region), nrow)
region_names<-region_names[-3]
names(region_names)<-c("CountryID","Region")
region_names
#write.csv(region_names,"region_names.csv")


############################################ 
#This section will return us the RelativeDistance and Correlation computation 
#as well as BestControl markets for each region.
############################################

###user input
data_period = c("2018-11-23", "2019-11-23") #select period of data to focus
###

#output dtw relative distance and correlation scores for all regions
mm <- best_matches(data = ConversionsData,
                   id_variable = "CountryID",
                   date_variable = "Day",
                   matching_variable = "Signups",
                   parallel = TRUE,
                   warping_limit = 1, 
                   dtw_emphasis = 1, #setting dtw_emphasis to 1 ensures scores are output- no impact to chosen control
                   matches = length(unique(ConversionsData$Region)), # retrieve scores for all markets for each market
                   start_match_period = data_period[1],
                   end_match_period = data_period[2])

head(mm$BestMatches)
#write.csv(mm$BestMatches, "YTPJPQ319_MatchScores.csv") #to create log of MMT scores


############################################ 
#Applying flags for following constraints to market dataset:
#- Top 30 percentile lowest dtw distance scores across all geos considered
#- Correlation of >90%
#- Average Correlation of Population >50%

#This section will return us the recommended exposed and control markets.
############################################

###user input
RD_cutoff = 30 #set cutoff percentile for ave relative distance
corr_cutoff = 0.5 #set cutoff value for ave correlation of population
n = 13 #set desired number of exposed markets
###

length(mm$BestMatches)
mm$BestMatches['corr_tag_90']<-ifelse(mm$BestMatches$Correlation >=0.9, 1,0)
mm$BestMatches['corr_tag_80']<-ifelse(mm$BestMatches$Correlation >=0.8, 1,0)
mm$BestMatches = mutate(mm$BestMatches, percentile_rank = ntile(mm$BestMatches$RelativeDistance,100))
meandf<-aggregate(mm$BestMatches[,c('Correlation','RelativeDistance')], list(mm$BestMatches$CountryID), mean)
head(meandf)
meandf = mutate(meandf, percentile_rank_RD = ntile(meandf$RelativeDistance,100))
meandf = mutate(meandf, percentile_rank_Corr = ntile(meandf$Correlation,100))
meandf['pop_ave_dtw_topP']<-ifelse(meandf$percentile_rank_RD < RD_cutoff, 1,0)
meandf['pop_ave_corr_more']<-ifelse(meandf$Correlation > corr_cutoff, 1,0)
length(meandf)
colnames(meandf)[colnames(meandf)=="Group.1"]<-"CountryID"
newdf <- meandf[,c(1,6,7)]
MatchScores2 <- merge(mm$BestMatches, newdf, by="CountryID")
head(MatchScores2)
colnames(MatchScores2)

#write.csv(MatchScores2,"YTPJPQ319_MatchScores.csv")

MatchScores3<-MatchScores2[MatchScores2$corr_tag_90==1 & MatchScores2$pop_ave_corr_more==1 & MatchScores2$pop_ave_dtw_topP==1,]
head(MatchScores3)
nrow(MatchScores3)
summary(MatchScores3)

ChosenMarkets<-data.frame(table(MatchScores3$CountryID))
names(ChosenMarkets)[1]<-"CountryID"
ChosenMarkets<-merge(ChosenMarkets,region_names,by="CountryID")
head(ChosenMarkets)

exposed <- ChosenMarkets[rev(order(ChosenMarkets$Freq)),]
exposed2 <- exposed[1:n,1]
exposed_data <- MatchScores3[MatchScores3$CountryID %in% exposed2 ,]
exposed_data
control_mix<-data.frame(table(exposed_data$BestControl))
names(region_names)[1]<-"Var1"
control_mix<-merge(control_mix,region_names,by="Var1")
exposed[1:n,] #list n possible exposed markets with the highest number of potential control pairs
control_mix[control_mix$Freq==n,] #list control markets common across exposed

############################################
#We are going to compare Time-based regression and CausalImpact for back-testing below.
#User needs to input the pre-test and test dates in test_period and
#the regions assigned to exposed and control in geoassign below.
#Both are done at 95% confidence level.

#In this section, we will evaluate if the methods (correctly) predict a lift or not 
#when there should/ shouldn't be.
############################################

###user input
test_period = c("2019-03-01","2019-05-01","2019-05-31")
geoassign<-data.frame("geo"=c("Tokyo","Saitama Prefecture","Osaka Prefecture",
                              "Aichi Prefecture","Chiba Prefecture","Ibaraki Prefecture","Kanagawa Prefecture"),
                      "geo.group"=c(1,1,1,2,2,2,2)) #set exposed and control markets

###

#Back-testing with Time-based Regression
data<-ConversionsRaw
colnames(data)<-c("date","geo","Signups")
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
post.period <- as.Date(c(test_period[2],test_period[3]))
time.points <- seq.Date(as.Date(test_period[1]), by = 1, length.out = nrow(obj_ci)/2)
max(time.points)
ci_data <- zoo(cbind(obj_ci[obj_ci$geo.group==1,]$Signups, obj_ci[obj_ci$geo.group==2,]$Signups), time.points)
ci_data
impact <- CausalImpact(ci_data, pre.period, post.period, alpha = 0.05, model.args = list(niter = 5000))
plot(impact)
summary(impact)
ggplot(data=obj_ci,aes(x=date,y=Signups,group=as.factor(geo.group), colour=as.factor(geo.group)))+
  geom_line()+
  geom_point()