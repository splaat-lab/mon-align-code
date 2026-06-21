source("analysis/mfa_theme.R")


file_stats <- read_csv("data/file_stats.csv", show_col_types = F, lazy=F)


file_stats$phones_per_second = (file_stats$nonsilence_count) / (file_stats$duration - file_stats$silence_duration)
file_stats$snr = file_stats$s_intensity - file_stats$silence_intensity


ggplot(data=file_stats, aes(x=duration)) + geom_histogram()
ggplot(data=file_stats, aes(x=phones_per_second)) + geom_histogram()
ggplot(data=file_stats, aes(x=snr)) + geom_histogram()

file_stats$weighting = file_stats$primary_environment_count + (file_stats$secondary_environment_count/2)

annotator_file_stats = file_stats
annotator_file_stats$cohort = 0
annotator_file_stats$annotator = 0
annotator_file_stats$extra = F

file_stats %>% subset(duration >= 10 | phones_per_second >= 14 | no_surrounding_silence | audio_peaked) %>% nrow

filtered_files = file_stats %>% subset(duration < 10 & phones_per_second < 14 & !no_surrounding_silence & !audio_peaked)
nrow(subset(file_stats, phones_per_second >= 14))
nrow(subset(file_stats, !has_s))
nrow(subset(file_stats, no_surrounding_silence))
nrow(subset(file_stats, audio_peaked))
nrow(subset(file_stats, duration >= 10))


ggplot(data=filtered_files, aes(x=duration)) + geom_histogram()
ggplot(data=filtered_files, aes(x=phones_per_second)) + geom_histogram()
ggplot(data=filtered_files, aes(x=snr)) + geom_histogram()
ggplot(data=filtered_files, aes(x=primary_environment_count)) + geom_histogram()
ggplot(data=filtered_files, aes(x=secondary_environment_count)) + geom_histogram()
ggplot(data=filtered_files, aes(x=weighting)) + geom_histogram()
filtered_files %>% arrange(snr) %>% View
file_stats %>% arrange(desc(phones_per_second)) %>% View
filtered_files %>% subset(phones_per_second < 6) %>% View
file_stats %>% subset(file == "4446-2271-0001") %>% View
filtered_files %>% subset(primary_environment_count > 8) %>% arrange(desc(primary_environment_count), desc(secondary_environment_count)) %>% View
file_stats %>% subset(duration < 10 & !no_surrounding_silence & !audio_peaked & weighting > 15) %>% arrange(desc(weighting)) %>% View

everyone_files = c("1995-1837-0012", "237-126133-0015", "3570-5695-0006")

filtered_files = subset(filtered_files, !file %in% everyone_files)

everyone_files = subset(file_stats, file %in% everyone_files)
everyone_files$cohort = 0
write_csv(everyone_files, "data/everyone_files.csv")

overlapped_files = filtered_files %>% arrange(desc(weighting)) %>% slice_head(n=40)
shuffled_overlappaed = overlapped_files %>% slice_sample(prop=1)

for (i in 1:8){
  print(i)
  initial_index = 1 + ((i-1)*5)
  end_index = (i*5)
  print(initial_index)
  print(end_index)
  s = overlapped_files %>% slice(initial_index:end_index)
  print(nrow(s))
  #print(overlapped_files %>% slice())
  write_csv(s, paste("data/c",as.character(i), "_files.csv",sep=''))
  annotator_file_stats[annotator_file_stats$file %in% s$file,]$cohort = i
}

random_files = filtered_files %>% subset(!file %in% overlapped_files$file) %>% slice_sample(prop=1)

filtered_files %>% subset(weighting > 10)  %>% arrange(desc(weighting)) %>% View

for (i in 1:40){
  print(i)
  est_cohort = i /5
  if (est_cohort != trunc(i/5)){
    est_cohort = trunc(i/5) + 1
  }
  initial_index = 1 + ((i-1)*41)
  end_index = (i*41)
  print(initial_index)
  print(end_index)
  s = random_files %>% slice(initial_index:end_index)
  print(nrow(s))
  #print(overlapped_files %>% slice())
  write_csv(s, paste("data/a",as.character(i), "_files.csv",sep=''))
  annotator_file_stats[annotator_file_stats$file %in% s$file,]$annotator = i
  annotator_file_stats[annotator_file_stats$file %in% s$file,]$cohort = est_cohort
}
unattested = random_files %>% slice(end_index+1:n())

filtered_out_files <- file_stats %>% subset(!file %in% filtered_files$file) %>% slice_sample(prop=1)

extra = rbind(unattested, filtered_out_files)


for (i in 1:40){
  print(i)
  est_cohort = i /5
  if (est_cohort != trunc(i/5)){
    est_cohort = trunc(i/5) + 1
  }
  print(est_cohort)
  initial_index = 1 + ((i-1)*24)
  end_index = (i*24)
  print(initial_index)
  print(end_index)
  s = extra %>% slice(initial_index:end_index)
  print(nrow(s))
  
  #print(overlapped_files %>% slice())
  write_csv(s, paste("data/a",as.character(i), "_extra_files.csv",sep=''))
  annotator_file_stats[annotator_file_stats$file %in% s$file,]$annotator = i
  annotator_file_stats[annotator_file_stats$file %in% s$file,]$cohort = est_cohort
  annotator_file_stats[annotator_file_stats$file %in% s$file,]$extra = T
}

# COHORT ANALYSIS 
annotator_file_stats %>% subset(!extra & annotator == 0) %>% group_by(cohort) %>% summarise(total_duration=sum(duration), speech_duration=sum(duration) - sum(silence_duration), total_weight=sum(weighting), n())
annotator_file_stats %>% subset(!extra) %>% group_by(cohort) %>% summarise(total_duration=sum(duration), speech_duration=sum(duration) - sum(silence_duration), total_weight=sum(weighting), n())


# ANNOTATOR ANALYSIS
annotator_analysis = annotator_file_stats %>% subset(!extra) %>% group_by(cohort, annotator) %>% summarise(total_duration=sum(duration), speech_duration=sum(duration) - sum(silence_duration), total_weight=sum(weighting), n())

annotator_analysis %>% subset(annotator != 0)  %>% group_by(cohort) %>% summarise(total_duration=mean(total_duration), speech_duration=mean(speech_duration), total_weight=mean(total_weight), n())

# Everyone files

everyone_files %>% group_by(cohort)  %>% summarise(total_duration=sum(duration), speech_duration=sum(duration) - sum(silence_duration), total_weight=sum(weighting), n())

# average minutes of audio
275/60
