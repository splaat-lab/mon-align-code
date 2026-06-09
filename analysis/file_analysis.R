source("analysis/mfa_theme.R")


file_stats <- read_csv("data/file_stats.csv", show_col_types = F, lazy=F)


file_stats$phones_per_second = (file_stats$nonsilence_count) / (file_stats$duration - file_stats$silence_duration)
file_stats$snr = file_stats$s_intensity - file_stats$silence_intensity


ggplot(data=file_stats, aes(x=duration)) + geom_histogram()
ggplot(data=file_stats, aes(x=phones_per_second)) + geom_histogram()
ggplot(data=file_stats, aes(x=snr)) + geom_histogram()


file_stats$weighting = file_stats$primary_environment_count + (file_stats$secondary_environment_count/2)

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

filtered_files %>% subset(weighting > 10) %>% arrange(desc(weighting)) %>% View