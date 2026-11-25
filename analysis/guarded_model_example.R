# Example of a deliberately guarded R analysis of APPROVED private joins.
# NOT a reproduced publication result. R execution is blocked until mappings
# are adjudicated and original outcome/model definitions are approved by lab.
#
# Run only with private input and private output paths:
# Rscript analysis/guarded_model_example.R /abs/private/join.csv /abs/private/model.csv

args <- commandArgs(trailingOnly=TRUE)
if (length(args)!=2) stop('Usage: Rscript guarded_model_example.R PRIVATE_INPUT.csv PRIVATE_OUTPUT.csv')
input <- normalizePath(args[[1]], mustWork=TRUE)
output <- args[[2]]
if (!grepl('(^|/)(private|restricted)(/|$)', output)) {
    stop('Refusing to write potentially participant-linked results outside a private/restricted directory')
}
d <- read.csv(input, check.names=FALSE, stringsAsFactors=FALSE)
required <- c('Version.ID','User.ID','version_enc','mapping_status_source',
              'serv_qual','first_mean_saturation_0_255',
              'first_mean_brightness_0_255','age','robot_comfort')
missing <- setdiff(required, names(d))
if(length(missing)>0) stop(paste('Missing required fields:',paste(missing,collapse=', ')))
if(any(is.na(d$mapping_status_source)) || any(d$mapping_status_source!='Matched')) {
    stop('Session mapping audit not cleared; refusing inferential analysis')
}
if(anyDuplicated(d[c('Version.ID','User.ID')])>0) stop('Duplicate participant keys')
# Avatar appearance is present only for participants with selected avatars.
# Restrict to create_av; do not misuse no_av missing values as zeros.
subset <- d[d$version_enc=='create_av', , drop=FALSE]
vars <- c('serv_qual','first_mean_saturation_0_255','first_mean_brightness_0_255','age','robot_comfort')
for (x in vars) subset[[x]] <- suppressWarnings(as.numeric(subset[[x]]))
subset <- subset[complete.cases(subset[vars]), , drop=FALSE]
if(nrow(subset)<30L) stop('Insufficient complete cases for this illustrative fit')
model <- lm(serv_qual ~ first_mean_saturation_0_255 + first_mean_brightness_0_255 + age + robot_comfort, data=subset)
coef <- as.data.frame(summary(model)$coefficients)
coef$feature <- rownames(coef)
coef$n_complete <- nrow(subset)
coef$model_scope <- 'create_av_only_exploratory'
dir.create(dirname(output), recursive=TRUE, showWarnings=FALSE)
write.csv(coef, output, row.names=FALSE)
cat('Wrote exploratory model to private output. Do not interpret as causal or independently validated.\n')
